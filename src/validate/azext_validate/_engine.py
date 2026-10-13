# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Parse a checked command with the installed CLI's own parser, without running anything.

Everything happens in an isolated CLI context (`_InnerCli`) so the checked command can't change
the running `az validate` invocation (output format, --query, telemetry, command log).
"""

import argparse
import contextlib
import copy
import difflib
import io
import logging
import re
import tempfile

from knack.deprecation import Deprecated

from azure.cli.core._session import Session
from azure.cli.core.parser import AzCliCommandParser

from . import _sandbox

SECRET_NAME_RE = re.compile(r'pass(word)?|secret|token|key|credential|connection-string|sas|pwd|cert', re.I)
_GROUP_DESTS = ('_command_package', '_subcommand', '_command')


# ---------------------------------------------------------------------------------------------
# Structured outcomes
# ---------------------------------------------------------------------------------------------

class Finding(dict):
    """One error, warning or info entry. Built only from names and positions, never values."""

    def __init__(self, code, message, **extra):
        super().__init__(code=code, message=message)
        self.all_subcommands = False  # suggestions list a whole group (internal; not in the output)
        for k, v in extra.items():
            if v not in (None, [], ''):
                self[k] = v


class Outcome:  # pylint: disable=too-many-instance-attributes
    def __init__(self):
        self.status = None            # valid | invalid | unchecked
        self.kind = 'command'         # command | help
        self.command_name = None
        self.source = None            # core | extension:<name>
        self.parameters = []          # canonical option names used
        self.placeholders = []        # [{parameter, placeholder?}] values that are placeholders
        self.errors = []
        self.warnings = []
        self.info = []
        self.reason = None            # Finding explaining `unchecked`
        self.extension_name = None
        self.requires_extension = None
        self.blocked = []             # sandbox events (diagnostics; never shown with values)
        # Loading was blocked, and the command is not from core or anything that did load, so only an
        # extension that isn't installed can provide it (internal; not in the output).
        self.blocked_unknown = False
        self.failed_extensions = []   # installed extensions that failed to load during a blocked load (internal)

    def fail(self, finding):
        self.status = 'invalid'
        self.errors.append(finding)
        return self

    def uncheck(self, finding):
        self.status = 'unchecked'
        self.reason = finding
        return self


class _ParseFailure(Exception):
    def __init__(self, finding, span=None):
        super().__init__(finding['code'])
        self.finding = finding
        self.span = span    # the exact argument objects involved, when known (never output)


class _HelpRequested(Exception):
    pass


# ---------------------------------------------------------------------------------------------
# Placeholder-carrying argument strings
# ---------------------------------------------------------------------------------------------

NEUTRAL = 'azvalidateplaceholder'


class PlaceholderArg(str):
    """An argument whose value is unknown (placeholder, variable, substitution or @file)."""

    def __new__(cls, text, word=None, whole=True, source_text=None):
        obj = super().__new__(cls, text)
        obj.word = word
        obj.whole = whole
        obj.source_text = source_text if source_text is not None else (word.text if word is not None else text)
        return obj


def _neutral_text(arg, filler='x'):
    """Replace expansions and template placeholders in a value with a neutral literal."""
    text = arg.source_text
    for p in sorted(arg.word.placeholders, key=lambda x: -len(x.text)):
        if p.kind in ('variable', 'braced-variable'):
            text = re.sub(re.escape(p.text) + r'(?![A-Za-z0-9_])', filler, text)
    text = re.sub(r'\$\((?:[^()]|\([^()]*\))*\)|`[^`]*`|\$\{[^}]*\}', filler, text)
    text = re.sub(r'<[^<>]+>', filler, text)
    return text


def _neutral_query(arg):
    """A --query value with expansions replaced by a neutral identifier, so its syntax can be checked."""
    return _neutral_text(arg, 'x')


class _Tok(str):
    """A distinct object per argument, so a failing argument can be found by identity."""


def build_args(words):
    """Turn shell words into parser arguments. Values with placeholders become PlaceholderArg.

    `--name=value` with a placeholder value is split into two arguments so the flag survives.
    `@file` values never reach the parser as `@...`.
    """
    args = []
    for w in words:
        text = w.text
        if not w.is_placeholder:
            args.append(_Tok(text))
            continue
        if text.startswith('-') and '=' in text:
            opt, _, value = text.partition('=')
            args.append(_Tok(opt))
            if value.startswith('@') or not value:
                args.append(PlaceholderArg(NEUTRAL, w, True, source_text=value))
            else:
                args.append(PlaceholderArg(value, w, False, source_text=value))
            continue
        if w.whole or text.startswith('@'):
            args.append(PlaceholderArg(NEUTRAL, w, True))
        else:
            args.append(PlaceholderArg(text, w, False))
    return args


# ---------------------------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------------------------

def _option_name(action):
    if not action:
        return None
    opts = [o for o in action.option_strings if o.startswith('--')] or list(action.option_strings)
    if opts:
        return max(opts, key=len)
    return '<{}>'.format(str(action.metavar or action.dest).strip('<>').upper())


def _close(value, choices, n=3, cutoff=0.7):
    try:
        return difflib.get_close_matches(str(value), [str(c) for c in choices], n=n, cutoff=cutoff)
    except Exception:  # pylint: disable=broad-except
        return []


_PATH_EXT_RE = re.compile(
    r'\.(json|jsonc|ya?ml|txt|sh|bash|ps1|psm1|xml|pem|crt|cer|key|pfx|p12|zip|tar|gz|bicep|bicepparam|tf|tfvars|csv|ini|'
    r'conf|cfg|env|toml|py|js|ts|html?|md|sql|properties|jar|war|whl|nupkg|cs|cert)$', re.I)


def _looks_like_path(value):
    """Values that name a file. They're never passed to type functions or actions (some read the
    file, and UNC paths would reach the network), and never reported invalid."""
    if not isinstance(value, str) or isinstance(value, PlaceholderArg) or not value or len(value) > 1024:
        return False
    if value.startswith(('\\\\', '//')):          # UNC or device path
        return True
    if '://' in value or '\n' in value or ' ' in value.strip() or value.startswith(('{', '[', '"', "'")):
        return False
    if value.startswith(('./', '../', '.\\', '..\\', '~/', '~\\')) or re.match(r'^[A-Za-z]:[\\/]', value):
        return True
    return bool(_PATH_EXT_RE.search(value)) and not value.startswith('-')


def _names_existing_file(value):
    """True if a value names an existing local file (defence in depth for S4)."""
    if not isinstance(value, str) or isinstance(value, PlaceholderArg) or not value or len(value) > 1024 \
            or '\n' in value or '\0' in value or value.startswith(('\\\\', '//')):
        return False
    import os
    for candidate in (value, os.path.expanduser(value)):
        try:
            if os.path.isfile(candidate):
                return True
        except (OSError, ValueError):
            continue
    return False


class ValidationParser(AzCliCommandParser):
    """AzCliCommandParser that reports problems as data.

    Overrides every path where core or argparse would print, send telemetry, try to install an
    extension, prompt, read @files or exit.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder_params = []
        self.unchecked_values = []
        self._current_span = None

    # -- argparse entry points ----------------------------------------------------------------
    def parse_args(self, args=None, namespace=None):
        # knack's parse_args expands '@file' arguments; never do that.
        namespace, extras = argparse.ArgumentParser.parse_known_args(self, args, namespace)
        if extras:
            raise _ParseFailure(self._unrecognized(namespace, extras), span=list(extras))
        return namespace

    def parse_known_args(self, args=None, namespace=None):
        # Don't record raw arguments on the parser (core keeps them for error recommendations).
        return argparse.ArgumentParser.parse_known_args(self, args, namespace)

    def error(self, message):
        raise _ParseFailure(_classify_argparse_message(message, self))

    def validation_error(self, message):
        raise _ParseFailure(Finding('InvalidArgumentUsage', 'The arguments are not valid together.'))

    def exit(self, status=0, message=None):
        raise _ParseFailure(Finding('InternalError', 'The parser tried to exit.'))

    def print_help(self, file=None):
        raise _HelpRequested()

    def print_usage(self, file=None):
        return None

    def format_help(self):
        raise _HelpRequested()

    def enable_autocomplete(self):
        return None

    # -- values ------------------------------------------------------------------------------
    def _get_values(self, action, arg_strings):
        # Remember the exact argument objects being converted, so a failure can be isolated.
        self._current_span = list(arg_strings)
        return super()._get_values(action, arg_strings)

    def _fail(self, finding):
        return _ParseFailure(finding, span=self._current_span)

    def _get_value(self, action, arg_string):
        if isinstance(action, argparse._SubParsersAction):  # pylint: disable=protected-access
            return arg_string
        if arg_string is action.default:
            return arg_string  # a default, not something the checked command passed
        if isinstance(arg_string, PlaceholderArg):
            if action.dest == '_jmespath_query' and not arg_string.whole and arg_string.word is not None:
                import jmespath
                try:
                    jmespath.compile(_neutral_query(arg_string))
                except Exception:  # pylint: disable=broad-except
                    raise self._fail(Finding('InvalidQuery', 'The JMESPath expression in --query is not valid.',
                                             parameter='--query'))
            if arg_string.word is not None:
                self.placeholder_params.append((action, arg_string))
            return arg_string
        if action.dest not in _GROUP_DESTS and (_looks_like_path(arg_string) or _names_existing_file(arg_string)):
            self.unchecked_values.append((action, 'file'))
            return PlaceholderArg(NEUTRAL)
        try:
            return super()._get_value(action, arg_string)
        except (_ParseFailure, _HelpRequested):
            raise
        except _sandbox.SandboxViolation:
            self.unchecked_values.append((action, 'blocked'))
            return arg_string
        except argparse.ArgumentError as ex:
            raise self._fail(_invalid_value(action, ex))
        except Exception as ex:  # pylint: disable=broad-except
            raise self._fail(_invalid_value(action, ex))

    def _check_value(self, action, value):
        if isinstance(value, PlaceholderArg) or action.choices is None:
            return
        if value in action.choices:
            return
        if action.dest in _GROUP_DESTS:
            group = self.prog[3:].strip() if self.prog.startswith('az') else self.prog
            near = _close(value, action.choices)
            listed_all = False
            if not near and group and len(action.choices) <= 5 and getattr(action, 'azv_complete', False):
                # Nothing is close: in a small group, list its current subcommands instead. Only where the
                # command table holds the whole group: not at the top level, or below an option that came
                # before the command words. The validator drops the list if extensions that aren't installed
                # may add subcommands to the group.
                hidden = getattr(action, 'azv_deprecated', ())
                near = sorted(c for c in action.choices if c not in hidden)
                listed_all = bool(near)
            suggestions = [('az {} {}'.format(group, c)).replace('  ', ' ') for c in near]
            name = '{} {}'.format(group, value).strip()
            finding = Finding(
                'UnknownCommand',
                "'{}' is not a command or group in 'az {}'.".format(value, group).replace('az  ', 'az ')
                if _safe_command_word(value) else "A command word is not recognised in 'az {}'.".format(group),
                group='az {}'.format(group).strip(), token=value if _safe_command_word(value) else None,
                suggestions=suggestions, attemptedCommand=name if _safe_command_word(value) else None)
            finding.all_subcommands = listed_all
            raise _ParseFailure(finding)
        param = _option_name(action)
        choices = [str(c) for c in action.choices]
        msg = "The value for {} is not one of the allowed values.".format(param)
        raise self._fail(Finding('InvalidChoice', msg, parameter=param,
                                 allowedValues=choices if len(choices) <= 30 else choices[:30] + ['...'],
                                 suggestions=_close(value, choices)))

    # -- helpers -----------------------------------------------------------------------------
    def _unrecognized(self, namespace, extras):
        cmd_parser = getattr(namespace, '_parser', None) or self
        known = [o for o in getattr(cmd_parser, '_option_string_actions', {}) if o.startswith('--')]
        params, positions = [], []
        skip_value = False
        for i, tok in enumerate(extras):
            name = tok.split('=', 1)[0] if isinstance(tok, str) and not isinstance(tok, PlaceholderArg) else ''
            # Only something shaped like an option name is reported by name; any other token, even one
            # starting with '-', may be a value (a secret, say) and is only counted.
            if _OPTION_NAME_RE.match(name):
                params.append(name)
                skip_value = '=' not in tok
            elif skip_value:
                skip_value = False
            else:
                positions.append(i)
        by_param = {}
        for p in params:
            close = _close(p, known, n=3, cutoff=0.7)
            if close:
                by_param[p] = close
        if params:
            msg = 'Unrecognized arguments: {}.'.format(', '.join(params))
        else:
            msg = 'Unexpected value(s) that do not belong to any argument.'
        return Finding('UnrecognizedArgument', msg, parameters=params,
                       unexpectedValues=len(positions) or None,
                       suggestions=by_param.get(params[0]) if len(params) == 1 else None,
                       suggestionsByParameter=by_param if len(params) > 1 else None)


_OPTION_NAME_RE = re.compile(r'^(--[a-z0-9][a-z0-9-]*|-[A-Za-z])$')


def _known_option(parser, token):
    name = token.split('=', 1)[0]
    table = getattr(parser, '_option_string_actions', {})
    return name in table or (name.startswith('--') and any(o.startswith(name) for o in table))


def _safe_command_word(value):
    return isinstance(value, str) and not isinstance(value, PlaceholderArg) and \
        bool(re.match(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$', value))


def _invalid_value(action, ex):
    param = _option_name(action)
    type_name = getattr(action.type, '__name__', None) or type(action.type).__name__
    if action.dest == '_jmespath_query' or type_name == 'jmespath_type':
        return Finding('InvalidQuery', 'The JMESPath expression in --query is not valid.', parameter='--query')
    expected = {'int': 'an integer', 'float': 'a number'}.get(type_name)
    msg = 'The value for {} is not valid{}.'.format(param, ' (expected {})'.format(expected) if expected else '')
    return Finding('InvalidValue', msg, parameter=param, expectedType=type_name if expected else None,
                   detail=type(ex).__name__ if not isinstance(ex, argparse.ArgumentError) else None)


def _long_name(name):
    parts = [p for p in name.split('/') if p]
    longs = [p for p in parts if p.startswith('--')]
    return max(longs, key=len) if longs else (parts[0] if parts else name)


_REQUIRED_RE = re.compile(r'^the following arguments are required: (.+)$')
_ONE_OF_RE = re.compile(r'^one of the arguments (.+) is required$')
_AMBIG_RE = re.compile(r'^ambiguous option: (\S+) could match (.+)$')
_ARG_RE = re.compile(r'^argument ([^:]+): (.+)$', re.S)


def _classify_argparse_message(message, parser):
    message = str(message)
    m = _REQUIRED_RE.match(message)
    if m:
        names = [n.strip() for n in m.group(1).split(',')]
        if any(n in _GROUP_DESTS for n in names):
            group = parser.prog[3:].strip() if parser.prog.startswith('az') else parser.prog
            choices = []
            for a in parser._actions:  # pylint: disable=protected-access
                if a.dest in _GROUP_DESTS and a.choices:
                    choices = sorted(a.choices)
            return Finding('MissingSubcommand', "'az {}' is a command group; a subcommand is required.".format(group),
                           group='az {}'.format(group), suggestions=['az {} {}'.format(group, c) for c in choices[:3]])
        return Finding('MissingRequiredArgument', 'Missing required arguments: {}.'.format(', '.join(names)),
                       parameters=[_long_name(n) for n in names])
    m = _ONE_OF_RE.match(message)
    if m:
        names = m.group(1).split()
        return Finding('MissingRequiredArgument', 'One of these arguments is required: {}.'.format(', '.join(names)),
                       parameters=names, oneOf=True)
    m = _AMBIG_RE.match(message)
    if m:
        matches = [x.strip() for x in m.group(2).split(',')]
        return Finding('AmbiguousArgument', "'{}' could match more than one argument.".format(m.group(1)),
                       parameter=m.group(1), suggestions=matches[:3], matches=matches)
    m = _ARG_RE.match(message)
    if m:
        name, detail = m.group(1), m.group(2)
        param = sorted(name.split('/'), key=len)[-1]
        if detail.startswith('expected'):
            # No '<option>=<value>' example: log redactors hide text after a secret-like name and '='.
            return Finding('MissingValue', "{0} needs a value. If the value starts with '-', join it to {0} with "
                           "'=' instead of a space.".format(param), parameter=param)
        if detail.startswith('not allowed with argument'):
            other = detail[len('not allowed with argument'):].strip()
            return Finding('MutuallyExclusiveArguments', '{} cannot be used with {}.'.format(param, other),
                           parameters=[param, other])
        if detail.startswith('ignored explicit argument'):
            return Finding('UnexpectedValue', '{} does not take a value.'.format(param), parameter=param)
        if detail.startswith('invalid choice'):
            return Finding('InvalidChoice', 'The value for {} is not one of the allowed values.'.format(param),
                           parameter=param)
        if detail.startswith('invalid'):
            return Finding('InvalidValue', 'The value for {} is not valid.'.format(param), parameter=param)
        return Finding('InvalidArgumentUsage', '{} is used incorrectly.'.format(param), parameter=param)
    if message.startswith('unrecognized arguments'):
        return Finding('UnrecognizedArgument', 'Unrecognized arguments.')
    return Finding('InvalidArgumentUsage', 'The arguments are not valid.')


# ---------------------------------------------------------------------------------------------
# Actions: placeholders, sandbox and side-effect control
# ---------------------------------------------------------------------------------------------

_WRAPPED = {}


def _contains_placeholder(values):
    if isinstance(values, PlaceholderArg):
        return True
    if isinstance(values, (list, tuple)):
        return any(isinstance(v, PlaceholderArg) for v in values)
    return False


def _wrap_action(action):
    cls = type(action)
    skipped = (argparse._SubParsersAction, argparse._HelpAction)  # pylint: disable=protected-access
    if cls in _WRAPPED.values() or isinstance(action, skipped):
        return
    sub = _WRAPPED.get(cls)
    if sub is None:
        def __call__(self, parser, namespace, values, option_string=None):
            if self.dest == '_subscription':
                # Core's action reads the signed-in profile and logs the value. Store it plainly.
                setattr(namespace, self.dest, values)
                return
            span = getattr(parser, '_current_span', None)
            try:
                return cls.__call__(self, parser, namespace, values, option_string)
            except (_ParseFailure, _HelpRequested):
                raise
            except _sandbox.SandboxViolation:
                setattr(namespace, self.dest, values)
                getattr(parser, 'unchecked_values', []).append((self, 'blocked'))
                return
            except Exception as ex:  # pylint: disable=broad-except
                if not _contains_placeholder(values):
                    raise _ParseFailure(_invalid_value(self, ex), span=span)
            # The value has placeholders: try neutral stand-ins so structural errors (e.g. an unknown
            # field in JSON around a $VAR) are still found; if none parses, say the value wasn't checked.
            for filler in ('x', '0'):
                try:
                    cls.__call__(self, parser, namespace, _neutral_values(values, filler), option_string)
                    return
                except (_ParseFailure, _HelpRequested):
                    raise
                except Exception:  # pylint: disable=broad-except
                    continue
            setattr(namespace, self.dest, values)
            if not _all_whole_placeholders(values):
                getattr(parser, 'unchecked_values', []).append((self, 'placeholder'))
        sub = type('Validated' + cls.__name__, (cls,), {'__call__': __call__})
        _WRAPPED[cls] = sub
    action.__class__ = sub


def _neutral_values(values, filler):
    def one(v):
        if isinstance(v, PlaceholderArg):
            return _neutral_text(v, filler) if not v.whole and v.word is not None else filler
        return v
    if isinstance(values, (list, tuple)):
        return [one(v) for v in values]
    return one(values)


def _all_whole_placeholders(values):
    vals = values if isinstance(values, (list, tuple)) else [values]
    return all(not isinstance(v, PlaceholderArg) or v.whole for v in vals)


# ---------------------------------------------------------------------------------------------
# Isolation
# ---------------------------------------------------------------------------------------------

BLOCKED_CALLS = []


def _never_called(*_args, **_kwargs):
    BLOCKED_CALLS.append(_kwargs.get('extension_name') or 'call')
    raise RuntimeError('az validate must not install extensions or run commands')


@contextlib.contextmanager
def _swap(obj, name, value):
    missing = object()
    old = getattr(obj, name, missing)
    setattr(obj, name, value)
    try:
        yield
    finally:
        if old is missing:
            delattr(obj, name)
        else:
            setattr(obj, name, old)


@contextlib.contextmanager
def isolated(mode, config_dir, load_read_roots=()):
    """Quiet, sandboxed region: no output, logging, telemetry, extension install or execution."""
    import azure.cli.core as core_mod
    import azure.cli.core.extension.dynamic_install as dyn
    import azure.cli.core.extension.operations as ext_ops
    import azure.cli.core.util as core_util
    from azure.cli.core import telemetry

    session = telemetry._session  # pylint: disable=protected-access
    saved = {}
    for k, v in vars(session).items():
        try:
            saved[k] = copy.deepcopy(v)
        except Exception:  # pylint: disable=broad-except
            saved[k] = v
    old_disable = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    sink = io.StringIO()
    with contextlib.ExitStack() as stack:
        stack.enter_context(contextlib.redirect_stdout(sink))
        stack.enter_context(contextlib.redirect_stderr(sink))
        stack.enter_context(_swap(core_mod, 'ALWAYS_LOADED_EXTENSIONS', []))
        stack.enter_context(_swap(dyn, 'try_install_extension', _never_called))
        stack.enter_context(_swap(dyn, '_check_value_in_extensions', _never_called))
        stack.enter_context(_swap(ext_ops, 'add_extension', _never_called))
        stack.enter_context(_swap(core_util, 'run_az_cmd', _never_called))
        try:
            guard = stack.enter_context(_sandbox.guard(mode, config_dir, load_read_roots))
            yield guard
        finally:
            logging.disable(old_disable)
            session.__dict__.clear()
            session.__dict__.update(saved)


class _OffLocalContext:  # pylint: disable=too-few-public-methods
    is_on = False

    def __getattr__(self, name):
        raise AttributeError(name)


def _patched_handle_version_update():
    return None


class InnerCli:  # pylint: disable=too-few-public-methods
    """A second, private CLI context used only to load and parse checked commands."""

    def __init__(self):
        import azure.cli.core.util as core_util
        from azure.cli.core import AzCli, MainCommandsLoader
        from azure.cli.core.azlogging import AzCliLogging
        from azure.cli.core.commands import AzCliCommandInvoker
        from azure.cli.core._config import GLOBAL_CONFIG_DIR, ENV_VAR_PREFIX
        from azure.cli.core._help import AzCliHelp
        from azure.cli.core._output import AzOutputProducer
        # Import modules whose import-time probes (e.g. urllib3's IPv6 check) would otherwise run
        # inside the sandbox, and modules that parse-time type checks import lazily.
        import jmespath  # noqa: F401  pylint: disable=unused-import
        import requests  # noqa: F401  pylint: disable=unused-import
        # tempfile picks its directory on first use by creating and deleting a probe file, which the sandbox
        # would block while an extension loads (some extensions call it at import time).
        try:
            tempfile.gettempdir()
        except OSError:
            pass  # no usable temp directory; an extension that needs one comes back unchecked
        with _swap(core_util, 'handle_version_update', _patched_handle_version_update):
            self.cli = AzCli(cli_name='az', config_dir=GLOBAL_CONFIG_DIR, config_env_var_prefix=ENV_VAR_PREFIX,
                             commands_loader_cls=MainCommandsLoader, invocation_cls=AzCliCommandInvoker,
                             parser_cls=ValidationParser, logging_cls=AzCliLogging,
                             output_cls=AzOutputProducer, help_cls=AzCliHelp, out_file=io.StringIO())
        # Ignore configured defaults (`az config set defaults.group=...`) and parameter persistence,
        # so verdicts don't depend on the local machine.
        self.cli.config.defaults_section_name = '__az_validate_ignores_defaults__'
        self.cli.local_context = _OffLocalContext()
        self.config_dir = self.cli.config.config_dir
        from azure.cli.core import extension as ext_mod
        self.extension_roots = [d for d in [ext_mod.EXTENSIONS_DIR, ext_mod.EXTENSIONS_SYS_DIR] +
                                list(ext_mod.DEV_EXTENSION_SOURCES) if d]

    def new_invoker(self, commands_loader_cls=None):
        cli = self.cli
        inv = cli.invocation_cls(cli_ctx=cli, parser_cls=cli.parser_cls,
                                 commands_loader_cls=commands_loader_cls or cli.commands_loader_cls,
                                 help_cls=cli.help_cls)
        cli.invocation = inv
        cli.data['command'] = 'unknown'
        return inv


# ---------------------------------------------------------------------------------------------
# Parse one command
# ---------------------------------------------------------------------------------------------

def _is_help(args):
    return any(not isinstance(a, PlaceholderArg) and a in ('-h', '--help') for a in args) or \
        (args and args[0] == 'help')


def _deprecated_children(loader):
    """Group words -> names of its deprecated subcommands and subgroups (never suggested)."""
    found = {}
    tables = [(name, getattr(cmd, 'deprecate_info', None)) for name, cmd in loader.command_table.items()]
    tables += [(name, (getattr(grp, 'group_kwargs', None) or {}).get('deprecate_info'))
               for name, grp in loader.command_group_table.items()]
    for name, info in tables:
        if info:
            words = name.split()
            found.setdefault(tuple(words[:-1]), set()).add(words[-1])
    return found


_FAILED_EXTENSION_LOAD = 'MainLoader.OnFailedExtensionLoad'  # azure.cli.core.EVENT_FAILED_EXTENSION_LOAD
_INDEX_SESSIONS = ('INDEX', 'EXTENSION_INDEX', 'HELP_INDEX', 'EXTENSION_HELP_INDEX')


@contextlib.contextmanager
def _discard_indexes_if_blocked(guard):
    """Core rebuilds its command index caches while loading. After a blocked operation the loaded table
    may be incomplete, so the rebuilt caches are neither saved nor kept in memory for the next check;
    `az <command> --help`, which isn't sandboxed, would build complete ones."""
    from azure.cli.core import _session
    sessions = [s for s in (getattr(_session, n, None) for n in _INDEX_SESSIONS) if s is not None]
    before = [copy.deepcopy(s.data) for s in sessions]
    real_save = Session.save

    def save(session):
        if guard.violations:
            return None
        return real_save(session)
    with _swap(Session, 'save', save):
        try:
            yield
        finally:
            if guard.violations:
                for session, data in zip(sessions, before):
                    session.data = data


@contextlib.contextmanager
def _registered(cli, event, handler):
    cli.register_event(event, handler)
    try:
        yield
    finally:
        cli.unregister_event(event, handler)


def _unknown_after_blocked_load(inner, lookup, loaded_top):
    """After a blocked load: True if the command's first word is neither a core command group nor in the
    part of the command table that did load."""
    first = lookup[0].lower() if lookup and not lookup[0].startswith('-') else None
    if not first or first in loaded_top:
        return False
    try:
        from azure.cli.core import CommandIndex
        core_index = CommandIndex(inner.cli).get_packaged_core_index()
    except Exception:  # pylint: disable=broad-except
        return False
    return bool(core_index) and first not in core_index


def _truncate_table(loader, command):
    """Same trimming as AzCliCommandInvoker.execute, so group errors list the right choices."""
    if command in loader.command_table:
        loader.command_table = {command: loader.command_table[command]}
        return
    cmd_table, group_names = {}, set()
    for cmd_name, cmd in loader.command_table.items():
        if command and not cmd_name.startswith(command):
            continue
        cmd_stub = cmd_name[len(command):].strip()
        group_name = cmd_stub.split(' ', 1)[0]
        if group_name not in group_names:
            cmd_table[cmd_name] = cmd
            group_names.add(group_name)
    loader.command_table = cmd_table


def _top_level_only(args):
    """Inner replacement for core's roughly_parse_command while loading a checked command.

    MainCommandsLoader compares this against the loaded table and, when a checked command
    doesn't exist, reloads every module and extension. Reporting only the top-level word makes
    the loader trust the command index, so an unknown subcommand costs one group, not all of az.
    """
    for a in args or []:
        if a and not a.startswith('-'):
            return a.lower()
        break
    return ''


def _option_tokens(parser, finding):
    """Option strings that refer to the finding's parameter in the command parser."""
    names = [finding.get('parameter')] + list(finding.get('parameters') or [])
    table = getattr(parser, '_option_string_actions', {})
    actions = {table[n] for n in names if n and n in table}
    opts = set(n for n in names if n)
    for a in actions:
        opts.update(a.option_strings)
    return opts, actions


def _neutralise(args, parser, finding, span=None):
    """Return new args with the cause of `finding` removed, or None if it can't be isolated."""
    code = finding['code']
    if span:
        ids = {id(s) for s in span}
        if any(id(a) in ids for a in args):
            if code in ('InvalidValue', 'InvalidChoice', 'InvalidQuery'):
                return [PlaceholderArg(NEUTRAL) if id(a) in ids else a for a in args]
            if code == 'UnrecognizedArgument':
                return [a for a in args if id(a) not in ids]
    opts, _ = _option_tokens(parser, finding)
    if code in ('InvalidValue', 'InvalidChoice', 'InvalidQuery') and opts:
        new, i = list(args), 0
        while i < len(new):
            tok = new[i]
            if isinstance(tok, str) and not isinstance(tok, PlaceholderArg) and tok.split('=', 1)[0] in opts:
                if '=' in tok:
                    new[i] = tok.split('=', 1)[0]
                    new.insert(i + 1, PlaceholderArg(NEUTRAL))
                j = i + 1
                while j < len(new) and not (isinstance(new[j], str) and new[j].startswith('-') and
                                            not isinstance(new[j], PlaceholderArg) and len(new[j]) > 1):
                    new[j] = PlaceholderArg(NEUTRAL)
                    j += 1
                i = j
                continue
            i += 1
        return new
    if code in ('UnrecognizedArgument', 'MissingValue', 'AmbiguousArgument', 'UnexpectedValue') and opts:
        new, skip, dash_value = [], False, False
        for tok in args:
            plain = isinstance(tok, str) and not isinstance(tok, PlaceholderArg)
            if dash_value:
                dash_value = False
                # argparse read a value starting with '-' as an option, so the option looked empty.
                # Drop that value too, so it's never reported (or echoed) as an unknown option.
                if plain and tok.startswith('-') and not _known_option(parser, tok):
                    continue
            if skip and not (plain and tok.startswith('-')):
                skip = False
                continue
            skip = False
            if plain and tok.split('=', 1)[0] in opts:
                skip = '=' not in tok and code == 'UnrecognizedArgument'
                dash_value = '=' not in tok and code == 'MissingValue'
                continue
            new.append(tok)
        return new
    return None


def parse_command(inner, args, loader_factory=None):  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
    """Parse one checked command (arguments after `az`). Returns an Outcome."""
    from knack.events import EVENT_INVOKER_POST_CMD_TBL_CREATE
    from azure.cli.core.commands.events import EVENT_INVOKER_PRE_LOAD_ARGUMENTS, EVENT_INVOKER_POST_LOAD_ARGUMENTS
    from azure.cli.core.aaz import has_value  # noqa: F401  pylint: disable=unused-import  (imported before the sandbox)
    import azure.cli.core.util as core_util

    out = Outcome()
    args = list(args)
    if args and not isinstance(args[0], PlaceholderArg) and args[0].lower() == 'help':
        args[0] = '--help'
    lookup = [str(a) for a in args]

    failed_extensions = []

    def _on_failed_extension(_cli_ctx, **kwargs):
        failed_extensions.append(kwargs.get('extension_name'))

    with isolated('load', inner.config_dir, inner.extension_roots) as guard, \
            _swap(core_util, 'roughly_parse_command', _top_level_only), \
            _discard_indexes_if_blocked(guard), \
            _registered(inner.cli, _FAILED_EXTENSION_LOAD, _on_failed_extension):
        inv = inner.new_invoker()
        loader = inv.commands_loader
        if loader_factory is not None:
            loader = loader_factory(inner.cli)
            inv.commands_loader = loader
        loader.load_command_table(lookup)
        loaded_top = {n.split()[0] for n in list(loader.command_table) + list(loader.command_group_table) if n}
        command = inv._rudimentary_get_command(lookup)  # pylint: disable=protected-access
        inv.data['command_string'] = command
        for i, word in enumerate(command.split()):
            if not isinstance(args[i], PlaceholderArg):
                args[i] = word
        _truncate_table(loader, command)
        loader.command_name = command
        inner.cli.raise_event(EVENT_INVOKER_PRE_LOAD_ARGUMENTS, commands_loader=loader)
        loader.load_arguments(command)
        required = _required_args(loader.command_table.get(command))
        inner.cli.raise_event(EVENT_INVOKER_POST_LOAD_ARGUMENTS, commands_loader=loader)
        inner.cli.raise_event(EVENT_INVOKER_POST_CMD_TBL_CREATE, commands_loader=loader)
        ids_check = _made_optional_for_ids(loader.command_table.get(command), required)
        parser = inv.parser
        parser.cli_ctx = inner.cli
        out.blocked.extend(guard.violations)
        if out.blocked:
            # Something during loading tried a blocked operation; the table may be incomplete, so
            # don't risk a false verdict.
            out.blocked_unknown = loader_factory is None and _unknown_after_blocked_load(inner, lookup, loaded_top)
            out.failed_extensions = sorted({e for e in failed_extensions if e})
            return out.uncheck(Finding('InternalError', 'Loading this command needed access that az validate does '
                                       'not allow, so it was not checked.',
                                       blockedEvents=sorted({e for e, _ in out.blocked})))
        if not loader.command_table:
            return out.fail(Finding('UnknownCommand', 'The command is not recognised.',
                                    token=lookup[0] if lookup and _safe_command_word(lookup[0]) else None))
        parser.load_command_table(loader)
        deprecated = _deprecated_children(loader)
        complete = tuple(command.split())  # _truncate_table keeps every subcommand only at this level
        for path, subparsers in parser.subparsers.items():
            subparsers.azv_deprecated = deprecated.get(tuple(path), set())
            subparsers.azv_complete = tuple(path) == complete
        for sub in list(parser.subparser_map.values()):
            for action in sub._actions:  # pylint: disable=protected-access
                _wrap_action(action)

    cmd_obj = loader.command_table.get(command)
    if cmd_obj is not None:
        out.command_name = command
        out.source, out.extension_name = _source_of(cmd_obj)

    with isolated('parse', inner.config_dir) as guard:
        cmd_parser = parser.subparser_map.get(command)
        attempt = list(args)
        namespace = None
        try:
            for _ in range(5):
                try:
                    namespace = parser.parse_args(attempt)
                    _post_parse(inner, namespace, attempt, out, ids_check)
                    break
                except _ParseFailure as ex:
                    finding = ex.finding
                    if any(e['code'] == finding['code'] and e.get('parameter') == finding.get('parameter') and
                           e.get('parameters') == finding.get('parameters') for e in out.errors):
                        break
                    out.fail(finding)
                    namespace = None
                    if cmd_parser is None:
                        break
                    if finding['code'] == 'MissingRequiredArgument' and not finding.get('alternatives'):
                        for action in cmd_parser._actions:  # pylint: disable=protected-access
                            action.required = False
                        continue
                    nxt = _neutralise(attempt, cmd_parser, finding, ex.span)
                    if nxt is None or nxt == attempt:
                        break
                    attempt = nxt
        except _HelpRequested:
            out.kind = 'help'
            out.status = 'valid'
            out.errors = []
            if not out.command_name:
                out.command_name = command or None
        finally:
            out.blocked.extend(guard.violations)
            out.parameters = _used_parameters(cmd_parser or parser, args)
            _placeholder_info(out, parser, cmd_parser)
    if out.status is None:
        out.status = 'valid'
        if cmd_obj is not None and namespace is not None:
            _command_warnings(inner, cmd_obj, namespace, out)
    return out


def _required_args(cmd):
    """Names of the command's required arguments, before core's --ids handling makes some optional."""
    if cmd is None:
        return []
    return [name for name, arg in cmd.arguments.items() if arg.type.settings.get('required')]


def _made_optional_for_ids(cmd, required):
    """What the --ids check needs: required id-part arguments that core made optional when it added
    --ids, as (dest, canonical option), and each option string's canonical (longest) name."""
    check = {'required': [], 'canonical': {}}
    if cmd is None:
        return check
    for name, arg in cmd.arguments.items():
        options = [o for o in (arg.type.settings.get('options_list') or ()) if isinstance(o, str)]
        longs = [o for o in options if o.startswith('--')]
        canonical = max(longs, key=len) if longs else (options[0] if options else '--' + name.replace('_', '-'))
        for o in options:
            check['canonical'][o] = canonical
        if name in required and arg.type.settings.get('id_part') and not arg.type.settings.get('required'):
            check['required'].append((name, canonical))
    return check


def _post_parse(inner, namespace, _args, out, ids_check=None):
    from knack.events import EVENT_INVOKER_POST_PARSE_ARGS
    from knack.util import CLIError
    from azure.cli.core.aaz import has_value
    ids_check = ids_check or {'required': [], 'canonical': {}}
    ids = getattr(namespace, 'ids', getattr(namespace, '_ids', None))
    if ids and _contains_placeholder(ids):
        out.placeholders.append({'parameter': '--ids'})
        return
    try:
        inner.cli.raise_event(EVENT_INVOKER_POST_PARSE_ARGS, command=namespace.command, args=namespace)
    except CLIError as ex:
        text = str(ex)
        m = re.match(r'^\((.+) \| --ids\) are required$', text)
        if m:
            names = [ids_check['canonical'].get(n, n) for n in m.group(1).split()]
            raise _ParseFailure(Finding('MissingRequiredArgument',
                                        'Provide {} or --ids.'.format(' '.join(names)),
                                        parameters=names, alternatives=['--ids']))
        if text.startswith('invalid resource ID') or 'cannot be derived from ID' in text:
            raise _ParseFailure(Finding('InvalidValue', 'A value for --ids is not a valid resource ID for this command.',
                                        parameter='--ids'))
        raise _ParseFailure(Finding('InvalidArgumentUsage', 'The arguments are not valid together.'))
    if not ids:
        # Core's check above tests for None, but AAZ arguments default to an "undefined" marker, so a
        # missing name would otherwise only fail when the command runs.
        names = [opt for dest, opt in ids_check['required']
                 if not isinstance(getattr(namespace, dest, None), PlaceholderArg) and
                 not has_value(getattr(namespace, dest, None))]
        if names:
            raise _ParseFailure(Finding('MissingRequiredArgument', 'Provide {} or --ids.'.format(' '.join(names)),
                                        parameters=names, alternatives=['--ids']))


def _source_of(cmd_obj):
    from azure.cli.core.commands import ExtensionCommandSource
    src = getattr(cmd_obj, 'command_source', None)
    if isinstance(src, ExtensionCommandSource):
        return 'extension:' + src.extension_name, src.extension_name
    return 'core', None


def _used_parameters(cmd_parser, args):
    names = []
    table = getattr(cmd_parser, '_option_string_actions', {})
    for a in args:
        if isinstance(a, PlaceholderArg) or not isinstance(a, str) or not a.startswith('-') or len(a) < 2:
            continue
        key = a.split('=', 1)[0]
        action = table.get(key)
        if action is None:
            matches = [o for o in table if o.startswith(key)] if key.startswith('--') else []
            action = table[matches[0]] if len(matches) == 1 else None
        if action is not None:
            name = _option_name(action)
            if name not in names:
                names.append(name)
    return names


_UNCHECKED_REASONS = {
    'file': 'it names a local file, which az validate does not read',
    'placeholder': 'it contains a placeholder and could not be checked with a stand-in value',
    'blocked': 'checking it would need file, network or other access that az validate does not allow',
}


def _placeholder_info(out, parser, cmd_parser):
    seen, seen_unchecked = set(), set()
    for p in [parser, cmd_parser]:
        if p is None:
            continue
        for action, value in getattr(p, 'placeholder_params', []):
            name = _option_name(action)
            if name in seen:
                continue
            seen.add(name)
            entry = {'parameter': name}
            word = getattr(value, 'word', None)
            if word is not None and value.whole and not SECRET_NAME_RE.search(name or '') and word.placeholders:
                entry['placeholder'] = word.placeholders[0].text
            out.placeholders.append(entry)
        for action, reason in getattr(p, 'unchecked_values', []):
            name = _option_name(action)
            if (name, reason) in seen_unchecked:
                continue
            seen_unchecked.add((name, reason))
            out.info.append(Finding('ValueNotChecked', 'The value for {} was not checked: {}.'.format(
                name, _UNCHECKED_REASONS.get(reason, 'unknown')), parameter=name, reason=reason))


def _command_warnings(inner, cmd, namespace, out):
    from azure.cli.core.commands import ExtensionCommandSource
    from knack.deprecation import resolve_deprecate_info
    from knack.preview import resolve_preview_info
    from knack.experimental import resolve_experimental_info

    if getattr(cmd, 'confirmation', None) and not getattr(namespace, 'yes', False):
        out.warnings.append(Finding('PromptsForConfirmation',
                                    'The command asks for confirmation; add --yes to run it without a prompt.'))
    for item in getattr(namespace, '_argument_deprecations', []) or []:
        out.warnings.append(_status_finding(item, 'argument'))
    if cmd.deprecate_info:
        out.warnings.append(_status_finding(cmd.deprecate_info, 'command'))
    else:
        path = cmd.name.split()[:-1]
        while path:
            info = resolve_deprecate_info(inner.cli, ' '.join(path))
            if isinstance(info, Deprecated):
                out.warnings.append(_status_finding(info, 'group'))
                break
            del path[-1]
    preview = cmd.preview_info
    path = cmd.name.split()[:-1]
    while not preview and path:
        preview = resolve_preview_info(inner.cli, ' '.join(path))
        del path[-1]
    if preview:
        out.warnings.append(Finding('Preview', 'The command is in preview.'))
    experimental = cmd.experimental_info
    path = cmd.name.split()[:-1]
    while not experimental and path:
        experimental = resolve_experimental_info(inner.cli, ' '.join(path))
        del path[-1]
    if experimental:
        out.warnings.append(Finding('Experimental', 'The command is experimental.'))
    for item in getattr(namespace, '_argument_previews', []) or []:
        out.warnings.append(Finding('PreviewArgument', 'Argument {} is in preview.'.format(getattr(item, 'target', '')),
                                    parameter=getattr(item, 'target', None)))
    src = getattr(cmd, 'command_source', None)
    if isinstance(src, ExtensionCommandSource) and src.overrides_command:
        out.warnings.append(Finding('ExtensionOverridesCommand',
                                    'The installed extension {} overrides this core command.'.format(src.extension_name)))


def _status_finding(info, scope):
    target = getattr(info, 'target', None)
    redirect = getattr(info, 'redirect', None)
    from azure.cli.core.breaking_change import UpcomingBreakingChangeTag
    if isinstance(info, UpcomingBreakingChangeTag):
        return Finding('UpcomingBreakingChange', 'A breaking change is announced for {}.'.format(target or scope),
                       target=target)
    code = {'argument': 'DeprecatedArgument', 'command': 'DeprecatedCommand', 'group': 'DeprecatedCommand'}[scope]
    msg = '{} is deprecated'.format(target or 'This ' + scope)
    if redirect:
        msg += "; use '{}' instead".format(redirect)
    return Finding(code, msg + '.', target=target, replacement=redirect,
                   expiration=getattr(info, 'expiration', None))
