# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Published command metadata.

Used only for commands from extensions that aren't installed, when the local parse can't settle a
command. Only two public, read-only endpoints are used. Responses are cached on disk. Any failure means
"unavailable", never an error.
"""

import json
import os
import re
import threading
import time
from urllib.parse import urlparse

INDEX_URL = 'https://azurecliextensionsync.blob.core.windows.net/cmd-index/extensionCommandTree.json'
META_BASE_URL = 'https://azcmdchangemgmt.blob.core.windows.net/cmd-metadata-per-version/azure-cli-extensions'
ALLOWED_HOSTS = frozenset(urlparse(u).hostname for u in (INDEX_URL, META_BASE_URL))
CACHE_TTL_SECONDS = 12 * 3600
TIMEOUT_SECONDS = (3.05, 5)
TOTAL_BUDGET_SECONDS = 12  # all metadata requests in one az validate run

_VERSION_FILE_RE = re.compile(r'^az_(?P<ext>.+)_meta_(?P<ver>[0-9][0-9A-Za-z.]*)\.json$')


class MetadataUnavailable(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class MetadataStore:  # pylint: disable=too-many-instance-attributes
    """Fetch and cache the extension command index and per-extension metadata."""

    def __init__(self, config_dir, offline=False, session=None, now=time.time):
        self.cache_dir = os.path.join(config_dir, 'validate', 'cache')
        self.core_index_path = os.path.join(config_dir, 'extensionCommandTree.json')
        self.offline = offline
        self._session = session
        self._now = now
        self._lock = threading.RLock()
        self._index = None
        self.index_status = None     # fetched | cached | stale-cache | unavailable | offline
        self.requests_made = []      # (host, path) for diagnostics and tests
        self._meta = {}
        self._deadline = None

    def remaining(self):
        """Seconds left in this run's metadata budget."""
        with self._lock:
            if self._deadline is None:
                return TOTAL_BUDGET_SECONDS
            return max(0.0, self._deadline - self._now())

    # -- HTTP --------------------------------------------------------------------------------
    def _get(self, url):
        host = urlparse(url).hostname
        if host not in ALLOWED_HOSTS or not url.startswith('https://'):
            raise MetadataUnavailable('MetadataUnavailable', 'Refusing to contact an unexpected host.')
        import requests
        from azure.cli.core.util import should_disable_connection_verify
        if self._session is None:
            self._session = requests.Session()  # keep-alive across the index, version list and metadata
        session = self._session
        with self._lock:
            if self._deadline is None:
                self._deadline = self._now() + TOTAL_BUDGET_SECONDS
        resp = None
        for attempt in range(2):
            remaining = self._deadline - self._now()
            if remaining <= 0.5:
                raise MetadataUnavailable('MetadataUnavailable', 'Metadata download took too long.')
            self.requests_made.append((host, urlparse(url).path))
            try:
                resp = session.get(url, timeout=(min(TIMEOUT_SECONDS[0], remaining), min(TIMEOUT_SECONDS[1], remaining)),
                                   allow_redirects=False, verify=not should_disable_connection_verify())
                break
            except (requests.ConnectionError, requests.Timeout) as ex:
                if attempt == 1:
                    raise MetadataUnavailable('MetadataUnavailable', 'Metadata could not be downloaded ({}).'.format(
                        type(ex).__name__))
            except Exception as ex:  # pylint: disable=broad-except
                raise MetadataUnavailable('MetadataUnavailable', 'Metadata could not be downloaded ({}).'.format(
                    type(ex).__name__))
        if resp.status_code == 404:
            raise MetadataUnavailable('NotFound', 'No published metadata.')
        if resp.status_code != 200:
            raise MetadataUnavailable('MetadataUnavailable', 'Metadata request failed (HTTP {}).'.format(
                resp.status_code))
        return resp

    # -- cache -------------------------------------------------------------------------------
    def _cache_path(self, name):
        return os.path.join(self.cache_dir, name)

    def _read_cache(self, name, valid=lambda data: isinstance(data, dict)):
        """(data, age in seconds), or (None, None) if missing, unreadable or not the expected shape."""
        path = self._cache_path(name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            age = self._now() - os.path.getmtime(path)
        except (OSError, ValueError):
            return None, None
        return (data, age) if valid(data) else (None, None)

    def _write_cache(self, name, data):
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            path = self._cache_path(name)
            tmp = '{}.{}.tmp'.format(path, os.getpid())
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            os.replace(tmp, path)
        except OSError:
            pass

    # -- index -------------------------------------------------------------------------------
    def index(self):
        with self._lock:
            if self._index is not None or self.index_status:
                return self._index
        # No lock held during network I/O: a stuck request must not block anything else.
        data, age = self._read_cache('extensionCommandTree.json')
        result, status = None, None
        if data is not None and age is not None and age < CACHE_TTL_SECONDS:
            result, status = data, 'cached'
        elif not self.offline:
            try:
                fresh = self._get(INDEX_URL).json()
                if isinstance(fresh, dict):
                    self._write_cache('extensionCommandTree.json', fresh)
                    result, status = fresh, 'fetched'
            except (MetadataUnavailable, ValueError):
                pass
        if result is None:
            if data is None:
                try:
                    with open(self.core_index_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    data = data.get('data', data) if isinstance(data, dict) else None
                except (OSError, ValueError):
                    data = None
            if isinstance(data, dict) and data:
                result, status = data, 'stale-cache'
            else:
                status = 'offline' if self.offline else 'unavailable'
        with self._lock:
            if self._index is None and not self.index_status:
                self._index, self.index_status = result, status
            return self._index

    def find(self, words):
        """Look up command words in the index.

        Returns (kind, value): ('command', (extension, command_name)), ('group', set_of_extensions)
        or (None, None). Raises MetadataUnavailable when there is no index.
        """
        tree = self.index()
        if tree is None:
            raise MetadataUnavailable('ExtensionIndexUnavailable', 'The extension command index is unavailable.')
        node, path = tree, []
        for w in words:
            if not isinstance(node, dict) or w not in node:
                break
            node = node[w]
            path.append(w)
            if isinstance(node, str):
                return 'command', (node, ' '.join(path))
        if path and isinstance(node, dict):
            return 'group', (_extensions_under(node), ' '.join(path))
        return None, None

    # -- per-extension metadata --------------------------------------------------------------
    def extension(self, name):
        """Return (version, commands) for the latest published version of an extension: commands maps
        full name -> metadata."""
        with self._lock:
            if name in self._meta:
                cached = self._meta[name]
                if isinstance(cached, MetadataUnavailable):
                    raise cached
                return cached
        try:
            result = self._load_extension(name)
        except MetadataUnavailable as ex:
            with self._lock:
                self._meta[name] = ex
            raise
        with self._lock:
            self._meta[name] = result
        return result

    def _load_extension(self, name):
        if not re.match(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$', name):
            raise MetadataUnavailable('MetadataUnavailable', 'Unexpected extension name.')
        cache_name = 'ext-{}.json'.format(name)
        data, age = self._read_cache(cache_name, _versioned('commands'))
        if data is not None and age is not None and age < CACHE_TTL_SECONDS:
            return data['version'], data['commands']
        if self.offline:
            if data is not None:
                return data['version'], data['commands']
            raise MetadataUnavailable('MetadataUnavailable', 'Offline; no cached metadata for extension {}.'.format(name))
        try:
            listing = self._get('{}/ext-{}/version_list.txt'.format(META_BASE_URL, name)).text
            version, file_name = _pick_version(name, listing)
            meta = self._get('{}/ext-{}/{}'.format(META_BASE_URL, name, file_name)).json()
        except MetadataUnavailable as ex:
            if data is not None:
                return data['version'], data['commands']
            if ex.code == 'NotFound':
                raise MetadataUnavailable(
                    'ExtensionNotPublished',
                    'Extension {} has no published command metadata, so its parameters were not checked.'.format(name))
            raise
        except ValueError:
            raise MetadataUnavailable('MetadataUnavailable', 'Metadata for extension {} is not valid JSON.'.format(name))
        commands = {}
        _collect_commands(meta, commands)
        self._write_cache(cache_name, {'version': version, 'commands': commands})
        return version, commands


def _extensions_under(node, found=None):
    found = set() if found is None else found
    for v in node.values():
        if isinstance(v, str):
            found.add(v)
        elif isinstance(v, dict):
            _extensions_under(v, found)
    return found


def _versioned(key):
    def valid(data):
        return isinstance(data, dict) and isinstance(data.get('version'), str) and isinstance(data.get(key), dict)
    return valid


def _collect_commands(node, out):
    if not isinstance(node, dict):
        return
    commands, groups = node.get('commands'), node.get('sub_groups')
    for name, cmd in (commands.items() if isinstance(commands, dict) else ()):
        if isinstance(cmd, dict):
            out[name] = cmd
    for sub in (groups.values() if isinstance(groups, dict) else ()):
        _collect_commands(sub, out)


def _pick_version(name, listing):
    """Latest stable version if there is one, else the latest preview (what `az extension add` installs)."""
    from packaging.version import Version, InvalidVersion
    candidates = []
    for line in listing.split():
        m = _VERSION_FILE_RE.match(line.strip())
        if not m or m.group('ext') != name:
            continue
        try:
            candidates.append((Version(m.group('ver')), m.group('ver'), line.strip()))
        except InvalidVersion:
            continue
    if not candidates:
        raise MetadataUnavailable('ExtensionNotPublished', 'No published metadata versions.')
    stable = [c for c in candidates if not c[0].is_prerelease]
    best = max(stable or candidates)
    return best[1], best[2]


# ---------------------------------------------------------------------------------------------
# Build command objects from published metadata
# ---------------------------------------------------------------------------------------------

_TYPES = {'int': int, 'Int': int, 'float': float, 'Float': float}


def _choice_type(choices):
    lookup = {str(c).lower(): c for c in choices}

    def choice(value):
        return lookup.get(str(value).lower(), value)
    choice.__name__ = 'choice'
    return choice


def _may_be_flag(param):
    """Published metadata doesn't say which options take a value. A type other than bool, choices, nargs,
    an id_part or being required shows that one does; any other option may be a flag."""
    return param.get('type') in (None, 'bool') and not any(
        param.get(k) for k in ('required', 'id_part', 'nargs', 'choices'))


def _argument(param, cli_ctx=None):
    from knack.arguments import CLICommandArgument
    from knack.deprecation import Deprecated
    options = list(param.get('options') or [])
    kwargs = {'required': bool(param.get('required', False))}
    if param.get('id_part'):
        kwargs['id_part'] = param['id_part']
    choices = param.get('choices')
    if param['name'] == 'yes':
        kwargs['action'] = 'store_true'
    else:
        # An option that may be a flag takes an optional value; one that needs a value is reported
        # as MissingValue without it, as core does.
        kwargs['nargs'] = param.get('nargs') or ('?' if options and _may_be_flag(param) else None)
        if choices:
            kwargs['choices'] = choices
            kwargs['type'] = _choice_type(choices)
        elif param.get('type') in _TYPES:
            kwargs['type'] = _TYPES[param['type']]
    deprecations = {}
    dep = param.get('deprecate_info')
    if isinstance(dep, dict):
        target = dep.get('target')
        if target in options and len(options) > 1:
            # An old option name for a current argument.
            deprecations[target] = Deprecated(cli_ctx, object_type='option', target=target,
                                              redirect=dep.get('redirect'), hide=bool(dep.get('hide')))
        else:
            deprecations[None] = _MetaDeprecated(target or (options[-1] if options else param['name']),
                                                 dep.get('redirect'))
    for item in param.get('options_deprecate_info') or []:
        if isinstance(item, dict) and item.get('target'):
            if item['target'] not in options:
                options.append(item['target'])
            deprecations[item['target']] = Deprecated(cli_ctx, object_type='option', target=item['target'],
                                                      redirect=item.get('redirect'), hide=bool(item.get('hide')))
    if deprecations:
        kwargs['action'] = _deprecation_action(kwargs.get('action'), deprecations)
        if None in deprecations:
            kwargs['deprecate_info'] = deprecations[None]
    if not options:
        kwargs['metavar'] = '<{}>'.format(param['name'].upper())
        arg = CLICommandArgument(param['name'], **kwargs)
        # knack gives every argument a default option string; core's positional() then clears it.
        arg.type.settings['options_list'] = []
        return arg
    return CLICommandArgument(param['name'], options_list=options, **kwargs)


def _deprecation_action(action, deprecations):
    """An argparse action that records deprecated use the way core's registered arguments do."""
    import argparse
    parent = argparse._StoreTrueAction if action == 'store_true' else argparse._StoreAction  # pylint: disable=protected-access

    class MetadataDeprecationAction(parent):  # pylint: disable=too-few-public-methods
        def __call__(self, parser, namespace, values, option_string=None):
            info = deprecations.get(option_string) or deprecations.get(None)
            if info is not None:
                found = getattr(namespace, '_argument_deprecations', None)
                if found is None:
                    found = []
                    setattr(namespace, '_argument_deprecations', found)
                found.append(info)
            super().__call__(parser, namespace, values, option_string)
    return MetadataDeprecationAction


class _MetaDeprecated:  # pylint: disable=too-few-public-methods
    """Minimal deprecation marker for metadata arguments (reported as a warning when used)."""

    def __init__(self, target, redirect):
        self.target = target
        self.redirect = redirect
        self.expiration = None

    def expired(self):
        return False

    def hidden(self):
        return True


def _core_injected_options(name, params):
    """Options core adds to this command itself (the same rules as azure.cli.core.commands.arm)."""
    injected = set()
    if name.split()[-1] not in ('list', 'show'):
        injected.update(('--change-reference', '--acquire-policy-token'))
    if name.split()[-1] != 'create' and any(p.get('id_part') in ('name', 'resource_name') for p in params):
        injected.add('--ids')
    return injected


def _refuse(*_args, **_kwargs):
    raise RuntimeError('az validate never runs commands')


def _meta_command(loader, name, meta, extension_name):
    """Build one command object from published metadata (arguments are built only when loaded)."""
    from azure.cli.core.commands import AzCliCommand, ExtensionCommandSource
    # Core adds these itself (as it does for installed commands); skip the exported copies.
    params = [p for p in meta.get('parameters', []) if p.get('name')]
    injected = _core_injected_options(name, params)
    params = [p for p in params if not injected.intersection(p.get('options') or [])]

    def _args(params=params):
        return [(p['name'], _argument(p, loader.cli_ctx)) for p in params]
    kwargs = {}
    dep = meta.get('deprecate_info')
    if isinstance(dep, dict):
        kwargs['deprecate_info'] = _MetaDeprecated(dep.get('target') or name, dep.get('redirect'))
    if meta.get('is_preview'):
        from knack.preview import PreviewItem
        kwargs['preview_info'] = PreviewItem(loader.cli_ctx, object_type='command', target=name)
    if meta.get('is_experimental'):
        from knack.experimental import ExperimentalItem
        kwargs['experimental_info'] = ExperimentalItem(loader.cli_ctx, object_type='command', target=name)
    cmd = AzCliCommand(loader, name, _refuse, arguments_loader=_args, confirmation=bool(meta.get('confirmation')),
                       supports_no_wait=False, **kwargs)
    cmd.command_source = ExtensionCommandSource(extension_name=extension_name)
    cmd.has_own_subscription = any('--subscription' in (p.get('options') or []) for p in params)
    return cmd


def _metadata_loader_class(build_table):
    from azure.cli.core import AzCommandsLoader

    class MetadataCommandsLoader(AzCommandsLoader):
        def __init__(self, cli_ctx=None):
            super().__init__(cli_ctx=cli_ctx)
            self.cmd_to_loader_map = {}
            self.loaders = [self]

        def load_command_table(self, args):
            self.command_table.clear()
            self.command_group_table.clear()
            for name, cmd in build_table(self, args):
                self.command_table[name] = cmd
                self.cmd_to_loader_map[name] = [self]
            return self.command_table

        def load_arguments(self, command=None):
            cmd = self.command_table.get(command)
            if cmd is not None:
                cmd.load_arguments()
                if getattr(cmd, 'has_own_subscription', False):
                    cmd.arguments.pop('_subscription', None)

    return MetadataCommandsLoader


def metadata_loader_factory(extension_name, commands):
    """Return a factory that builds a commands loader serving one extension's published metadata."""
    def build(loader, _args):
        for name, meta in commands.items():
            yield name, _meta_command(loader, name, meta, extension_name)
    return _metadata_loader_class(build)
