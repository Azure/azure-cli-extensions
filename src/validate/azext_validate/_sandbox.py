# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Process-level guard used while az validate loads and parses a checked command.

The guard uses a Python audit hook (PEP 578). While a guard is active on the current thread,
operations that the checked command must never trigger are blocked:

* network access (sockets, urllib, http.client);
* running programs (subprocess, os.system, os.exec*, os.spawn*, os.startfile, pty);
* interactive input (input(), getpass);
* in "parse" mode, opening any file outside the Python installation and import roots, and any
  file-system change. In "load" mode, writes are allowed only inside the CLI config directory
  (index caches, as `az <command> --help` would write) and Python bytecode caches.

Blocked operations raise SandboxViolation (a PermissionError) and are recorded, so callers and
tests can see exactly what was attempted. The hook is installed once per process and is inert
when no guard is active.
"""

import contextlib
import os
import re
import sys
import threading


class _State:  # pylint: disable=too-few-public-methods
    guard = None  # process-wide while active: core may load modules on worker threads


_state = _State()
_reentry = threading.local()
_installed = False
_install_lock = threading.Lock()

_NETWORK_EVENTS = {
    'socket.connect', 'socket.bind', 'socket.getaddrinfo', 'socket.gethostbyname',
    'socket.gethostbyaddr', 'socket.sendto', 'socket.sendmsg', 'urllib.Request', 'http.client.connect',
    'ftplib.connect', 'smtplib.connect', 'poplib.connect', 'imaplib.open', 'nntplib.connect',
    'telnetlib.Telnet.open', 'webbrowser.open',
}
_EXEC_EVENTS = {
    'subprocess.Popen', 'os.system', 'os.exec', 'os.spawn', 'os.posix_spawn', 'os.startfile',
    'os.fork', 'os.forkpty', 'pty.spawn', 'os.kill', 'os.killpg',
}
_INPUT_EVENTS = {'builtins.input', 'getpass.getpass'}
_FS_CHANGE_EVENTS = {
    'os.remove', 'os.rename', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.chown', 'os.link', 'os.symlink',
    'os.truncate', 'os.utime', 'shutil.rmtree', 'shutil.move', 'shutil.copyfile', 'shutil.copytree',
}
_FS_LIST_EVENTS = {'os.listdir', 'os.scandir', 'glob.glob', 'glob.glob/2'}

_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC


class SandboxViolation(PermissionError):
    """Raised when the checked command would cause a blocked operation."""

    def __init__(self, event, detail=''):
        super().__init__('az validate blocked {}'.format(event))
        self.event = event
        self.detail = detail


def _norm(path):
    try:
        return os.path.normcase(os.path.realpath(os.fspath(path)))
    except Exception:  # pylint: disable=broad-except
        return None


def _is_under(path, root):
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def _is_write(mode, flags):
    if isinstance(mode, str) and any(c in mode for c in 'wax+'):
        return True
    return isinstance(flags, int) and bool(flags & _WRITE_FLAGS)


# Files core may rewrite while loading a command table (the same caches `az <command> --help` updates).
_LOAD_WRITABLE = re.compile(r'^(commandIndex|extensionIndex|helpIndex|extensionHelpIndex|versionCheck)\.json$|^az\.sess$',
                            re.I)
_TWO_PATH_EVENTS = {'os.rename', 'os.link', 'os.symlink', 'shutil.copyfile', 'shutil.copytree', 'shutil.move'}


def _is_bytecode(norm):
    return '__pycache__' in norm or norm.endswith(('.pyc', '.pyc.tmp'))


class _Guard:
    def __init__(self, mode, read_roots, config_dir=None, list_only=()):
        self.mode = mode
        self.read_roots = read_roots
        self.list_only = list_only  # directories whose names may be listed, but not their files read
        self.config_dir = config_dir
        self.violations = []
        self.paths = []   # diagnostics only; never output

    def block(self, event, detail=''):
        self.violations.append((event, detail))
        raise SandboxViolation(event, detail)

    def block_path(self, event, detail, norm):
        self.paths.append(norm)
        self.block(event, detail)

    def may_write(self, norm):
        if _is_bytecode(norm):
            return True
        return (self.mode == 'load' and self.config_dir is not None and
                os.path.dirname(norm) == self.config_dir and bool(_LOAD_WRITABLE.match(os.path.basename(norm))))

    def may_read(self, norm):
        return any(_is_under(norm, r) for r in self.read_roots)

    def check_open(self, args):
        path, mode, flags = (list(args) + [None, None, None])[:3]
        if isinstance(path, int) or path is None:
            return  # an existing file descriptor; opening it was already checked
        norm = _norm(path)
        if norm is None:
            self.block('open', 'unresolvable path')
        if _is_write(mode, flags):
            if not self.may_write(norm):
                self.block_path('open', 'write', norm)
            return
        if not self.may_read(norm):
            self.block_path('open', 'read', norm)

    def check_fs_change(self, event, args):
        paths = [a for a in (args[:2] if event in _TWO_PATH_EVENTS else args[:1]) if isinstance(a, (str, bytes))]
        norms = [_norm(p) for p in paths]
        if not norms or any(n is None for n in norms):
            self.block(event)
        if event == 'os.mkdir' and self.mode == 'load' and all(_is_under(n, self.config_dir or '\0') for n in norms):
            return
        if all(self.may_write(n) for n in norms):
            return
        self.block(event)

    def check_list(self, event, args):
        target = args[0] if args else None
        if isinstance(target, bytes):
            target = os.fsdecode(target)
        if isinstance(target, str):
            if event.startswith('glob'):
                target = os.path.dirname(target) or '.'
            norm = _norm(target)
            if norm and (self.may_read(norm) or norm in self.list_only):
                return
        self.block(event)


def exempt_thread():
    """Exempt the calling thread: az validate's own metadata downloads, which have their own host
    allow-list and deadline and may outlive the check that started them."""
    _reentry.exempt = True


def _hook(event, args):
    active = _state.guard
    if active is None or getattr(_reentry, 'active', False) or getattr(_reentry, 'exempt', False):
        return
    _reentry.active = True
    try:
        if event == 'open':
            active.check_open(args)
        elif event in _NETWORK_EVENTS or event in _EXEC_EVENTS or event in _INPUT_EVENTS:
            active.block(event)
        elif event in _FS_CHANGE_EVENTS:
            active.check_fs_change(event, args)
        elif event in _FS_LIST_EVENTS:
            active.check_list(event, args)
    finally:
        _reentry.active = False


def _install():
    global _installed  # pylint: disable=global-statement
    with _install_lock:
        if not _installed:
            sys.addaudithook(_hook)
            _installed = True


def _import_roots():
    """Directories Python imports from, excluding the working directory."""
    cwd = _norm(os.getcwd())
    roots = set()
    for entry in list(sys.path) + [sys.prefix, sys.base_prefix, sys.exec_prefix]:
        if not entry or not isinstance(entry, str):
            continue
        norm = _norm(entry)
        if not norm or norm == cwd or not os.path.isdir(norm):
            continue
        roots.add(norm)
    return tuple(sorted(roots))


def _listable_cwd():
    """The working directory, if it is on sys.path (`python -m azure.cli` puts it there).

    Package-metadata lookups during module loading list every sys.path entry. Listing the working
    directory is allowed while loading; reading files in it is not.
    """
    cwd = _norm(os.getcwd())
    for entry in sys.path:
        if isinstance(entry, str) and (entry in ('', '.') or _norm(entry) == cwd):
            return (cwd,) if cwd else ()
    return ()


class _NoStdin:
    """Replaces sys.stdin while guarded: never blocks, never reads the real stream."""

    encoding = 'utf-8'

    def isatty(self):
        return False

    def fileno(self):
        raise OSError('stdin is not available to az validate')

    def _blocked(self, *_args, **_kwargs):
        active = _state.guard
        if active is not None:
            active.violations.append(('stdin.read', ''))
        raise SandboxViolation('stdin.read')

    read = readline = readlines = __iter__ = _blocked


@contextlib.contextmanager
def guard(mode, config_dir=None, load_read_roots=()):
    """Block forbidden operations in this process while the context is active.

    :param mode: 'load' while command tables load; 'parse' while the checked command is parsed.
    :param config_dir: the Azure CLI config directory. In 'load' mode it may be read, and core's
        index caches in it may be rewritten.
    :param load_read_roots: more directories readable in 'load' mode (extension directories).
    """
    if mode not in ('load', 'parse'):
        raise ValueError(mode)
    _install()
    cfg = _norm(config_dir) if config_dir else None
    roots = _import_roots()
    if mode == 'load':
        extra = [_norm(r) for r in list(load_read_roots) + [cfg] if r]
        roots = tuple(sorted(set(roots) | {r for r in extra if r}))
    current = _Guard(mode, roots, cfg, list_only=_listable_cwd() if mode == 'load' else ())
    previous = _state.guard
    old_stdin = sys.stdin
    _state.guard = current
    sys.stdin = _NoStdin()
    try:
        yield current
    finally:
        sys.stdin = old_stdin
        _state.guard = previous
