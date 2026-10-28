# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Check commands and scripts and build the result document."""

import threading
import time

from . import _sandbox, _shell
from ._engine import (Finding, Outcome, InnerCli, build_args, parse_command, PlaceholderArg)
from ._extmeta import (MetadataStore, MetadataUnavailable, metadata_loader_factory, _extensions_under, _may_be_flag,
                       _core_injected_options)

SCHEMA_VERSION = '1.0'
_UNKNOWN_CODES = ('UnknownCommand', 'MissingSubcommand')


def _atoms(errors):
    """Errors as (code, parameter) pairs, so verdicts from two sources can be compared."""
    atoms = set()
    for e in errors:
        params = list(e.get('parameters') or []) or ([e['parameter']] if e.get('parameter') else [None])
        for p in params:
            atoms.add((e['code'], p))
    return atoms


def _run_parallel(fn, items, timeout):
    """Run fn(item) for each item in daemon threads; wait at most `timeout` seconds in total."""
    def run(item):
        _sandbox.exempt_thread()
        try:
            fn(item)
        except Exception:  # pylint: disable=broad-except
            pass
    threads = [threading.Thread(target=run, args=(i,), daemon=True) for i in items]
    for t in threads:
        t.start()
    deadline = time.monotonic() + timeout
    for t in threads:
        t.join(max(0.0, deadline - time.monotonic()))


def _relax_flag_positionals(out, meta, args):
    """Published metadata doesn't say which options are flags, so an option that may be one is built to
    take an optional value, and a flag just before a positional argument takes it. If that may have
    happened, don't report the positional as missing."""
    if not isinstance(meta, dict) or out.status != 'invalid':
        return
    params = [p for p in meta.get('parameters') or [] if isinstance(p, dict) and p.get('name')]
    positional = {'<{}>'.format(p['name'].upper()) for p in params if not p.get('options')}
    all_options, maybe_flag = set(), set()
    for p in params:
        opts = [o for o in p.get('options') or [] if isinstance(o, str)]
        all_options.update(opts)
        if opts and p['name'] != 'yes' and _may_be_flag(p):
            maybe_flag.update(opts)

    def resolve(token):
        if token in all_options:
            return token
        matches = [o for o in all_options if token.startswith('--') and o.startswith(token)]
        return matches[0] if len(matches) == 1 else None

    plain = [a if isinstance(a, str) and not isinstance(a, PlaceholderArg) else None for a in args]
    swallowed = False
    for i, tok in enumerate(plain):
        if tok and tok.startswith('-') and '=' not in tok and resolve(tok) in maybe_flag and i + 1 < len(args):
            nxt = plain[i + 1]
            if nxt is None or not nxt.startswith('-'):
                swallowed = True
    if not positional or not swallowed:
        return
    kept = []
    for e in out.errors:
        if e['code'] == 'MissingRequiredArgument' and e.get('parameters'):
            rest = [n for n in e['parameters'] if n not in positional]
            if not rest:
                continue
            if len(rest) != len(e['parameters']):
                e = Finding(e['code'], 'Missing required arguments: {}.'.format(', '.join(rest)),
                            **{k: v for k, v in e.items() if k not in ('code', 'message', 'parameters')})
                e['parameters'] = rest
        kept.append(e)
    if len(kept) != len(out.errors):
        out.errors = kept
        out.status = 'invalid' if kept else 'valid'
        out.info.append(Finding('MetadataLimits', 'A positional argument may have been read as the value of a '
                                'flag, because published metadata does not say which parameters are flags; it was '
                                'not reported as missing.'))


def _option_groups(meta, name):
    """The option names of each parameter of a metadata command, including deprecated names and the
    options core adds to it."""
    if not isinstance(meta, dict):
        return []
    params = [p for p in meta.get('parameters') or [] if isinstance(p, dict) and p.get('name')]
    groups = []
    for p in params:
        opts = [o for o in p.get('options') or [] if isinstance(o, str)]
        opts += [d['target'] for d in p.get('options_deprecate_info') or []
                 if isinstance(d, dict) and isinstance(d.get('target'), str) and d['target'] not in opts]
        if opts:
            groups.append(opts)
    for opt in sorted(_core_injected_options(name or '', params)):
        if not any(opt in g for g in groups):
            groups.append([opt])
    return groups


def _match_option(token, groups):
    """The option group a token names: an exact option, or a '--' prefix of exactly one option string (as
    argparse counts them, so a prefix of two names of one parameter is ambiguous). None otherwise."""
    for g in groups:
        if token in g:
            return g
    hits = [g for g in groups for o in g if token.startswith('--') and o.startswith(token)]
    return hits[0] if len(hits) == 1 else None


def _extension_only_value_errors(meta_out, groups, resolved, args, local):
    """Value errors metadata reports for options that core rejects and only the extension accepts. Core
    can't check those values, so metadata's verdict on them stands."""
    names, rejected = set(), False
    for code, token in resolved:
        if code != 'UnrecognizedArgument':
            continue
        rejected = True
        if token:
            names.update(_match_option(token, groups) or [])
    if rejected:
        # Core doesn't name a token such as '-jabc' (it may be a value); argparse reads it as '-j abc'.
        for a in args:
            if isinstance(a, str) and not isinstance(a, PlaceholderArg) and len(a) > 2 and \
                    a[0] == '-' and a[1].isalpha() and a[:2] not in local.known_options:
                names.update(_match_option(a[:2], groups) or [])
    seen = _atoms(local.errors)
    return [e for e in meta_out.errors
            if e['code'] in ('MissingValue', 'InvalidValue', 'InvalidChoice') and e.get('parameter') in names and
            (e['code'], e['parameter']) not in seen]


def _drop_incomplete_subcommand_lists(local, kind, value):
    """A group's subcommands are listed when nothing is close. Drop the list when extensions that aren't
    installed may add subcommands to that group: the index knows the group, or there is no index."""
    for e in local.errors:
        if not getattr(e, 'all_subcommands', False):
            continue
        depth = len((e.get('group') or 'az').split()) - 1
        if kind == 'index-unavailable' or (kind in ('command', 'group') and len(value[1].split()) >= depth):
            e.pop('suggestions', None)


def _bounded(fn, timeout):
    """Run fn in a daemon thread; give up after `timeout` seconds (the thread is abandoned)."""
    box = {}

    def run():
        _sandbox.exempt_thread()
        try:
            box['value'] = fn()
        except BaseException as ex:  # pylint: disable=broad-except
            box['error'] = ex
    t = threading.Thread(target=run, daemon=True)
    t.start()
    t.join(max(0.0, timeout))
    if t.is_alive():
        raise MetadataUnavailable('MetadataUnavailable', 'Metadata lookup took too long.')
    if 'error' in box:
        raise box['error']
    return box.get('value')


class Validator:  # pylint: disable=too-many-instance-attributes
    def __init__(self, offline=False, metadata_store=None):
        self.inner = InnerCli()
        self.store = metadata_store or MetadataStore(self.inner.config_dir, offline=offline)
        self.offline = offline
        self.extensions_used = {}
        self.metadata_used = {}
        self._installed = None

    # -- public ------------------------------------------------------------------------------
    def check_commands(self, texts, dialect):
        items = []
        for idx, text in enumerate(texts):
            items.extend(self._scan_item(text, dialect, idx, script_mode=False))
        return self._finish(items)

    def check_script(self, text, dialect):
        return self._finish(self._scan_item(text, dialect, 0, script_mode=True))

    # -- scanning ----------------------------------------------------------------------------
    def _scan_item(self, text, dialect, idx, script_mode):
        notes = []
        try:
            scan = _shell.scan(text, dialect)
            syntax_error = None
        except _shell.ShellSyntaxError as ex:
            # Check the complete commands before the error, and report the error for the rest. (Neither
            # shell would run a command on a line it can't parse, but the error makes the result invalid.)
            syntax_error = Outcome().fail(Finding(
                'ShellSyntax', 'The {} text can\'t be parsed: {}.'.format(dialect, ex.reason),
                line=ex.line, column=ex.column))
            scan = _shell.scan_before_error(text, ex, dialect)
            if not scan.invocations:
                return [(idx, ex.line, ex.column, syntax_error, notes)]
            syntax_error = (idx, ex.line, ex.column, syntax_error, None)
        invocations = sorted(scan.invocations, key=lambda i: (i.line, i.column))
        if not invocations:
            if script_mode:
                notes.append(Finding('NoAzCommands', 'No az commands were found.'))
                return [(idx, None, None, None, notes)]
            not_az = Finding('NotAzCommand', 'The input is not an Azure CLI command; it must start with az.')
            return [(idx, 1, 1, Outcome().fail(not_az), notes)]
        if scan.other_commands:
            notes.append(Finding('IgnoredCommands', '{} non-az command(s) were ignored.'.format(scan.other_commands),
                                 count=scan.other_commands))
        for u in scan.unsupported:
            notes.append(Finding('UnsupportedShellSyntax', 'Unsupported {} syntax ({}) was skipped.'.format(
                dialect, u.construct), line=u.line, column=u.column, construct=u.construct))
        for w in scan.misplaced_az:
            notes.append(Finding('AzNotChecked', 'az is used as an argument of another command and was not checked.',
                                 line=w.line, column=w.column))
        rows = []
        for inv in invocations:
            rows.append((idx, inv.line, inv.column, inv, None))
        if rows:
            first = rows[0]
            rows[0] = (first[0], first[1], first[2], first[3], notes)
        if syntax_error is not None:
            rows.append(syntax_error)
        return rows

    # -- checking ----------------------------------------------------------------------------
    def _finish(self, rows):
        outcomes = []
        pending_meta = []
        for idx, line, col, inv, notes in rows:
            if inv is None or isinstance(inv, Outcome):
                outcomes.append((idx, line, col, inv, notes, None))
                continue
            out = self._check_invocation(inv)
            outcomes.append((idx, line, col, out, notes, inv))
            if out.blocked_unknown or (out.status == 'invalid' and out.errors and
                                       not self._uses_installed_extension(out) and
                                       (out.command_name or out.errors[0]['code'] in _UNKNOWN_CODES)):
                pending_meta.append(len(outcomes) - 1)

        if pending_meta:
            self._apply_metadata(outcomes, pending_meta)
        return self._document(outcomes)

    def _check_invocation(self, inv):
        if inv.unsupported:
            return Outcome().uncheck(Finding('UnsupportedShellSyntax',
                                             'The command uses {} syntax that az validate does not support.'.format(
                                                 inv.unsupported[0].construct), construct=inv.unsupported[0].construct))
        if not inv.words:
            return Outcome().fail(Finding('MissingSubcommand', "'az' needs a command."))
        args = build_args(inv.words)
        if isinstance(args[0], PlaceholderArg):
            return Outcome().uncheck(Finding('PlaceholderCommandName',
                                             'The command name is a placeholder, so it can\'t be checked.'))
        try:
            out = parse_command(self.inner, args)
        except Exception as ex:  # pylint: disable=broad-except
            return Outcome().uncheck(Finding('InternalError', 'az validate could not check this command ({}).'.format(
                type(ex).__name__)))
        if any(w.unquoted_angle for w in inv.words):
            out.warnings.append(Finding('UnquotedPlaceholder',
                                        'An unquoted <placeholder> is a redirection in the shell; quote it or replace it '
                                        'before running the command.'))
        for op in dict.fromkeys(inv.suspicious_operators):
            out.warnings.append(Finding('UnquotedOperator',
                                        "The shell treats '{}' as an operator here, which splits the command; if it is "
                                        'part of a value, quote the value.'.format(op), operator=op))
        if out.extension_name:
            self.extensions_used[out.extension_name] = None
        return out

    @staticmethod
    def _uses_installed_extension(out):
        return bool(out.extension_name)

    def _apply_metadata(self, outcomes, positions):
        lookups = {}
        for pos in positions:
            inv = outcomes[pos][5]
            words = [w.text.lower() for w in inv.words if not w.is_placeholder]
            nouns = []
            for w in words:
                if w.startswith('-'):
                    break
                nouns.append(w)
            try:
                kind, value = _bounded(lambda n=nouns: self.store.find(n), self.store.remaining())
            except MetadataUnavailable as ex:
                lookups[pos] = ('index-unavailable', ex)
                continue
            lookups[pos] = (kind, value)

        needed = sorted({t for t in (self._target(outcomes[p][3], *lookups[p]) for p in lookups) if t})
        if needed and not self.offline:
            # Daemon threads with a hard deadline: a stuck download (or DNS lookup) can't hold up the
            # result or the process exit.
            _run_parallel(self._prefetch, needed, self.store.remaining())

        for pos, (kind, value) in lookups.items():
            idx, line, col, local, notes, inv = outcomes[pos]
            new = self._metadata_outcome(local, inv, kind, value)
            outcomes[pos] = (idx, line, col, new, notes, inv)

    def installed_extensions(self):
        """Installed extensions (name -> version), read from their package metadata; nothing is imported."""
        if self._installed is None:
            try:
                from azure.cli.core.extension import get_extensions
                self._installed = {e.name: e.version for e in get_extensions()}
            except Exception:  # pylint: disable=broad-except
                self._installed = {}
        return self._installed

    def _target(self, local, kind, value):
        """The extension whose metadata could change this verdict, or None."""
        if kind not in ('command', 'group'):
            return None
        path = value[1]
        if local.blocked_unknown:
            # Loading was blocked, so the local verdict is unknown: only check an exact command from the index,
            # and only if no extension that failed to load could provide it.
            ext = value[0] if kind == 'command' and self._failed_unrelated(local, path) else None
        elif local.command_name:
            # Core knows the command: only an extension overlaying this exact command matters.
            ext = value[0] if kind == 'command' and path == local.command_name else None
        else:
            group = local.errors[0].get('group') or 'az'
            if len(path.split()) <= len(group.split()) - 1:
                return None
            if kind == 'group':
                ext = next(iter(value[0])) if len(value[0]) == 1 else None
            else:
                ext = value[0]
        if ext and ext in self.installed_extensions():
            # The local parse already loaded the installed extension.
            return None
        return ext

    def _failed_unrelated(self, local, path):
        """True if every installed extension that failed to load is published and adds nothing under the
        command's first word (so it can't be the one that provides the command)."""
        tree = self.store.index() or {}
        published = _extensions_under(tree)
        node = tree.get(path.split()[0])
        owners = _extensions_under(node) if isinstance(node, dict) else ({node} if isinstance(node, str) else set())
        return all(e in published and e not in owners for e in local.failed_extensions)

    def _prefetch(self, name):
        self.store.extension(name)

    def _metadata_outcome(self, local, inv, kind, value):  # pylint: disable=too-many-return-statements,too-many-branches
        overlay = bool(local.command_name)   # core knows the command; an extension may overlay it
        if not overlay:
            _drop_incomplete_subcommand_lists(local, kind, value)
        if kind == 'index-unavailable':
            if local.blocked_unknown:
                return local
            if overlay:
                local.warnings.append(Finding('ExtensionIndexUnavailable',
                                              'The extension index was unavailable, so extensions that change this '
                                              'command were not checked.'))
                return local
            new = Outcome().uncheck(Finding('ExtensionIndexUnavailable',
                                            'The command is not in Azure CLI core or the installed extensions, and the '
                                            'extension index was unavailable to check further.'))
            new.warnings.extend(local.errors)
            return new
        ext = self._target(local, kind, value)
        if ext is None:
            if kind == 'group' and not overlay and not local.blocked_unknown and len(value[0]) > 1:
                local.info.append(Finding('ExtensionGroup', "'az {}' comes from extensions: {}.".format(
                    value[1], ', '.join(sorted(value[0]))), extensions=sorted(value[0])))
            return local
        try:
            version, commands = self.store.extension(ext)
            failure = None
        except MetadataUnavailable as ex:
            failure = ex
        except Exception:  # pylint: disable=broad-except
            failure = MetadataUnavailable('MetadataUnavailable', 'Metadata for extension {} could not be read.'.format(
                ext))
        if failure is not None:
            ex = failure
            if overlay:
                local.warnings.append(Finding('MetadataUnavailable', 'Extension {} changes this command, but its '
                                              'metadata was unavailable.'.format(ext), extension=ext))
                return local
            new = Outcome().uncheck(Finding(ex.code, ex.message, extension=ext))
            new.requires_extension = ext
            new.command_name = value[1] if kind == 'command' else None
            new.source = 'extension:' + ext
            return new
        self.metadata_used[ext] = version
        try:
            meta_out = parse_command(self.inner, build_args(inv.words),
                                     loader_factory=metadata_loader_factory(ext, commands))
        except Exception as ex:  # pylint: disable=broad-except
            return Outcome().uncheck(Finding('InternalError', 'az validate could not check this command against '
                                             'extension metadata ({}).'.format(type(ex).__name__)))
        _relax_flag_positionals(meta_out, commands.get(meta_out.command_name), build_args(inv.words))
        meta_out.source = 'extension:' + ext
        meta_out.requires_extension = ext
        meta_out.extension_name = None
        limits = Finding('MetadataLimits', 'Checked against published metadata for {} {}, which records parameter '
                         'names, required parameters, choices and number types, but not whether a parameter '
                         'without a type takes a value.'.format(ext, version), extension=ext, version=version)
        if overlay:
            # Start from core's verdict and drop only the errors the extension provably resolves:
            # names, choices and required parameters. Value errors come from core's own type checks and
            # actions, which metadata can't reproduce, so they always stand; so do metadata's value errors
            # on options that only the extension has.
            resolvable = {'UnrecognizedArgument', 'InvalidChoice', 'MissingRequiredArgument', 'AmbiguousArgument'}
            meta_atoms = _atoms(meta_out.errors)
            groups = _option_groups(commands.get(meta_out.command_name), meta_out.command_name)
            # An option core doesn't know is resolved only if it's one of the extension's options: metadata may
            # not report a token itself (e.g. one that may be the missing value of the option before it).
            resolved = {a for a in _atoms(local.errors) if a[0] in resolvable and a not in meta_atoms and
                        not (a[0] == 'UnrecognizedArgument' and a[1] and _match_option(a[1], groups) is None)}
            if not resolved:
                return local
            remaining = []
            for e in local.errors:
                if _atoms([e]).issubset(resolved):
                    continue
                if e.get('parameters') and any((e['code'], p) in resolved for p in e['parameters']):
                    e = Finding(e['code'], e['message'], **{k: v for k, v in e.items() if k not in ('code', 'message')})
                    e['parameters'] = [p for p in e['parameters'] if (e['code'], p) not in resolved]
                    e['message'] = '{}: {}.'.format(e['message'].split(':')[0], ', '.join(e['parameters']))
                    by_param = e.pop('suggestionsByParameter', None) or {}
                    e.pop('suggestions', None)
                    if len(e['parameters']) == 1 and by_param.get(e['parameters'][0]):
                        e['suggestions'] = by_param[e['parameters'][0]]
                    elif len(e['parameters']) > 1:
                        kept = {p: s for p, s in by_param.items() if p in e['parameters']}
                        if kept:
                            e['suggestionsByParameter'] = kept
                remaining.append(e)
            params = sorted({p for _, p in resolved if p})
            remaining.extend(_extension_only_value_errors(meta_out, groups, resolved, build_args(inv.words), local))
            local.errors = remaining
            local.status = 'invalid' if remaining else 'valid'
            local.requires_extension = ext
            local.warnings.append(Finding(
                'RequiresExtension', 'Extension {} (not installed; az installs it on first use) accepts {}, '
                'which core alone rejects.'.format(ext, ', '.join(params) or 'this command'), extension=ext,
                parameters=params))
            local.info.append(limits)
            local.parameters = meta_out.parameters or local.parameters
            if local.status == 'valid':
                local.placeholders = meta_out.placeholders or local.placeholders
            return local
        meta_out.info.append(Finding('ExtensionNotInstalled', 'The command comes from extension {}; az installs '
                                     'it on first use.'.format(ext), extension=ext, version=version))
        meta_out.info.append(limits)
        return meta_out

    # -- document ----------------------------------------------------------------------------
    def _document(self, outcomes):
        from azure.cli.core import __version__ as core_version
        results, notes_all = [], []
        counts = {'valid': 0, 'invalid': 0, 'unchecked': 0}
        for idx, line, col, out, notes, _inv in outcomes:
            for n in notes or []:
                n = dict(n)
                n['index'] = idx
                notes_all.append(n)
            if out is None:
                continue
            counts[out.status] += 1
            r = {'index': idx, 'line': line, 'column': col, 'status': out.status}
            if out.kind != 'command':
                r['kind'] = out.kind
            if out.command_name:
                r['commandName'] = out.command_name
            if out.source:
                r['source'] = out.source
            if out.requires_extension:
                r['requiresExtension'] = out.requires_extension
            if out.parameters:
                r['parameters'] = out.parameters
            if out.reason:
                r['reason'] = out.reason
            r['errors'] = out.errors
            r['warnings'] = out.warnings
            if out.info:
                r['info'] = out.info
            if out.placeholders:
                r['placeholders'] = out.placeholders
            results.append(r)
        status = 'invalid' if counts['invalid'] else ('unchecked' if counts['unchecked'] else 'valid')
        doc = {
            'schemaVersion': SCHEMA_VERSION,
            'status': status,
            'isValid': status == 'valid',
            'summary': dict(commands=len(results), **counts),
            'results': results,
        }
        if notes_all:
            doc['notes'] = notes_all
        versions = {'azureCli': core_version, 'validate': _own_version()}
        installed = {}
        for name in sorted(self.extensions_used):
            installed[name] = _installed_version(name)
        if installed:
            versions['extensions'] = installed
        if self.metadata_used:
            versions['extensionMetadata'] = dict(sorted(self.metadata_used.items()))
        doc['versions'] = versions
        if self.store.index_status:
            doc['extensionIndex'] = self.store.index_status
        return doc


def _own_version():
    try:
        from azure.cli.core.extension import get_extension
        return get_extension('validate').version
    except Exception:  # pylint: disable=broad-except
        return None


def _installed_version(name):
    try:
        from azure.cli.core.extension import get_extension
        return get_extension(name).version
    except Exception:  # pylint: disable=broad-except
        return None
