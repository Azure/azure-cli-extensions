# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Tokenise Bash or PowerShell text and find the az invocations in it, without evaluating anything.

Nothing here expands variables, runs substitutions or touches the file system. The supported
grammar is deliberately small; anything outside it is reported as unsupported so the caller can
return `unchecked` instead of guessing.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional

BASH = 'bash'
POWERSHELL = 'powershell'

# A template placeholder such as <resource-group>, <SKU NAME>, <a|b> or <<name>>.
_ANGLE_RE = re.compile(r'<<[A-Za-z0-9_][A-Za-z0-9_ .:/-]{0,80}>>|<[A-Za-z0-9_][^<>\n\r]{0,80}?>')
# A {name} template, as used in documentation resource IDs: /subscriptions/{subscription-id}/...
_BRACE_RE = re.compile(r'\{[A-Za-z_][A-Za-z0-9_ .-]{0,60}\}')
_NAME_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
_BASH_ASSIGN_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])?\+?=')

_BASH_SKIP_WORDS = {'if', 'then', 'else', 'elif', 'do', 'while', 'until', '!', 'time', '{', '}', 'fi',
                    'done', 'esac', 'sudo', 'command', 'exec', 'nohup', 'builtin', 'env', 'eval_skip'}
_BASH_HEADER_WORDS = {'for', 'select', 'case', 'function'}
_PS_SKIP_WORDS = {'if', 'elseif', 'else', 'while', 'do', 'until', 'foreach', 'for', 'switch', 'try',
                  'catch', 'finally', 'return', 'throw', 'begin', 'process', 'end', '&', '.'}


class ShellSyntaxError(Exception):
    def __init__(self, reason, line, column):
        super().__init__(reason)
        self.reason = reason
        self.line = line
        self.column = column


@dataclass
class Placeholder:
    kind: str   # angle, variable, braced-variable, substitution, template, at-file
    text: str   # the placeholder as written, safe to show (no command text or file contents)


@dataclass
class Word:  # pylint: disable=too-many-instance-attributes
    text: str                 # value after quote removal; expansions keep their source text
    line: int
    column: int
    quoted: bool = False
    placeholders: List[Placeholder] = field(default_factory=list)
    whole: bool = False       # the entire word is one placeholder
    unquoted_angle: bool = False
    substitutions: List['Fragment'] = field(default_factory=list)

    @property
    def is_placeholder(self):
        return bool(self.placeholders)


@dataclass
class Operator:
    op: str
    line: int
    column: int


@dataclass
class Redirect:
    op: str
    target: Optional[Word]
    line: int
    column: int


@dataclass
class Unsupported:
    construct: str
    line: int
    column: int


@dataclass
class Fragment:
    """Source text that must be scanned for commands, with its position in the original input."""
    text: str
    line: int
    column: int


@dataclass
class Invocation:
    """One `az ...` simple command found in the input."""
    words: List[Word]          # words after `az`
    line: int
    column: int
    redirects: List[Redirect] = field(default_factory=list)
    unsupported: List[Unsupported] = field(default_factory=list)
    nested: bool = False       # found inside $(...) or backticks
    suspicious_operators: List[str] = field(default_factory=list)  # operators that may belong in a value


@dataclass
class ScanResult:
    invocations: List[Invocation] = field(default_factory=list)
    other_commands: int = 0    # simple commands that aren't az
    unsupported: List[Unsupported] = field(default_factory=list)  # constructs outside any az command
    misplaced_az: List[Word] = field(default_factory=list)  # `az` used as an argument (e.g. xargs az)
    has_shell_operators: bool = False


class _Cursor:
    def __init__(self, text, line, column):
        self.text = text
        self.i = 0
        self.line = line
        self.col = column

    def peek(self, k=0):
        j = self.i + k
        return self.text[j] if j < len(self.text) else ''

    def startswith(self, s):
        return self.text.startswith(s, self.i)

    def advance(self, n=1):
        for _ in range(n):
            if self.i >= len(self.text):
                return
            if self.text[self.i] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.i += 1

    @property
    def eof(self):
        return self.i >= len(self.text)


# ---------------------------------------------------------------------------------------------
# Bash
# ---------------------------------------------------------------------------------------------

def _scan_balanced(cur, open_ch, close_ch, dialect):
    """Advance past a balanced region whose opener was already consumed; return its source text."""
    start = cur.i
    depth = 1
    line, col = cur.line, cur.col
    while not cur.eof:
        ch = cur.peek()
        if ch == '\\' and dialect == BASH:
            cur.advance(2)
            continue
        if ch == '`' and dialect == POWERSHELL:
            cur.advance(2)
            continue
        if ch == "'":
            cur.advance()
            while not cur.eof and cur.peek() != "'":
                cur.advance()
            if cur.eof:
                raise ShellSyntaxError('unclosed single quote', line, col)
            cur.advance()
            continue
        if ch == '"':
            cur.advance()
            while not cur.eof and cur.peek() != '"':
                if cur.peek() in ('\\', '`'):
                    cur.advance()
                cur.advance()
            if cur.eof:
                raise ShellSyntaxError('unclosed double quote', line, col)
            cur.advance()
            continue
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                inner = cur.text[start:cur.i]
                cur.advance()
                return inner
        cur.advance()
    raise ShellSyntaxError("unclosed '{}'".format(open_ch), line, col)


def _bash_dollar(cur, word, buf, in_dquote):
    """Handle `$` at the cursor. Appends source text to buf and records placeholders."""
    line, col = cur.line, cur.col
    nxt = cur.peek(1)
    if cur.startswith('$(('):
        cur.advance(3)
        inner = _scan_balanced(cur, '(', ')', BASH)
        if cur.peek() == ')':
            cur.advance()
        text = '$((' + inner + '))'
        word.placeholders.append(Placeholder('arithmetic', '$((...))'))
        buf.append(text)
        return
    if nxt == '(':
        cur.advance(2)
        sub_line, sub_col = cur.line, cur.col
        inner = _scan_balanced(cur, '(', ')', BASH)
        word.substitutions.append(Fragment(inner, sub_line, sub_col))
        word.placeholders.append(Placeholder('substitution', '$(...)'))
        buf.append('$(' + inner + ')')
        return
    if nxt == '{':
        cur.advance(2)
        inner_line, inner_col = cur.line, cur.col
        inner = _scan_balanced(cur, '{', '}', BASH)
        name = _NAME_RE.match(inner)
        word.placeholders.append(Placeholder('braced-variable', '${' + (name.group(0) if name else '...') + '}'))
        # ${X:-$(az ...)}: commands nested in the expansion still run.
        if '$(' in inner or '`' in inner:
            try:
                for item in _lex_bash(inner, inner_line, inner_col):
                    if isinstance(item, Word):
                        word.substitutions.extend(item.substitutions)
            except ShellSyntaxError:
                pass
        buf.append('${' + inner + '}')
        return
    if nxt == "'" and not in_dquote:
        # ANSI-C quoting $'...': decode the simple escapes, keep the rest literally.
        cur.advance(2)
        out = []
        while not cur.eof and cur.peek() != "'":
            if cur.peek() == '\\' and cur.peek(1):
                esc = cur.peek(1)
                out.append({'n': '\n', 't': '\t', '\\': '\\', "'": "'", '"': '"'}.get(esc, '\\' + esc))
                cur.advance(2)
                continue
            out.append(cur.peek())
            cur.advance()
        if cur.eof:
            raise ShellSyntaxError("unclosed $' quote", line, col)
        cur.advance()
        word.quoted = True
        buf.append(''.join(out))
        return
    m = _NAME_RE.match(cur.text, cur.i + 1)
    if m:
        cur.advance(1 + len(m.group(0)))
        word.placeholders.append(Placeholder('variable', '$' + m.group(0)))
        buf.append('$' + m.group(0))
        return
    if nxt and nxt in '@*#?$!-0123456789':
        cur.advance(2)
        word.placeholders.append(Placeholder('variable', '$' + nxt))
        buf.append('$' + nxt)
        return
    cur.advance()
    buf.append('$')


def _bash_backtick(cur, word, buf):
    line, col = cur.line, cur.col
    cur.advance()
    sub_line, sub_col = cur.line, cur.col
    start = cur.i
    while not cur.eof and cur.peek() != '`':
        if cur.peek() == '\\':
            cur.advance()
        cur.advance()
    if cur.eof:
        raise ShellSyntaxError('unclosed backtick', line, col)
    inner = cur.text[start:cur.i]
    cur.advance()
    word.substitutions.append(Fragment(inner, sub_line, sub_col))
    word.placeholders.append(Placeholder('substitution', '`...`'))
    buf.append('`' + inner + '`')


_BASH_REDIRECT_RE = re.compile(r'(?:[0-9]+|&)?(?:>>|>&|>\||<>|<&|>|<)(?:-|[0-9]+)?')


def _lex_bash(text, line=1, column=1):  # pylint: disable=too-many-branches,too-many-statements
    cur = _Cursor(text, line, column)
    items = []
    while not cur.eof:
        ch = cur.peek()
        if ch in ' \t\r':
            cur.advance()
            continue
        if ch == '\\' and cur.peek(1) == '\n':
            cur.advance(2)
            continue
        if ch == '\n':
            items.append(Operator('\n', cur.line, cur.col))
            cur.advance()
            continue
        if ch == '#':
            while not cur.eof and cur.peek() != '\n':
                cur.advance()
            continue
        matched = False
        for op in ('&&', '||', ';;', '|&', '|', ';', '&', '(', ')'):
            if cur.startswith(op):
                if op == '&' and cur.peek(1) == '>':
                    break
                items.append(Operator(op, cur.line, cur.col))
                cur.advance(len(op))
                matched = True
                break
        if matched:
            continue
        if cur.startswith('<<<') or (cur.startswith('<<') and not _ANGLE_RE.match(cur.text, cur.i)):
            items.append(Unsupported('heredoc' if not cur.startswith('<<<') else 'herestring', cur.line, cur.col))
            if cur.startswith('<<<'):
                cur.advance(3)
                continue
            # Skip the heredoc body: from the next line up to the delimiter line.
            cur.advance(2)
            if cur.peek() == '-':
                cur.advance()
            while cur.peek() in ' \t':
                cur.advance()
            m = re.match(r"['\"]?([A-Za-z0-9_]+)['\"]?", cur.text[cur.i:])
            delim = m.group(1) if m else None
            if m:
                cur.advance(len(m.group(0)))
            if delim:
                nl = cur.text.find('\n', cur.i)
                if nl != -1:
                    end = re.compile(r'^[ \t]*' + re.escape(delim) + r'[ \t]*$', re.M).search(cur.text, nl + 1)
                    stop = end.end() if end else len(cur.text)
                    # Emit a separator for the rest of the heredoc line, then skip the body.
                    rest = cur.text[cur.i:nl]
                    items.extend(_lex_bash(rest, cur.line, cur.col))
                    items.append(Operator('\n', cur.line, cur.col))
                    while cur.i < stop:
                        cur.advance()
            continue
        if cur.startswith('<(') or cur.startswith('>('):
            items.append(Unsupported('process-substitution', cur.line, cur.col))
            cur.advance(2)
            _scan_balanced(cur, '(', ')', BASH)
            continue
        m = _BASH_REDIRECT_RE.match(cur.text, cur.i)
        if m and not (cur.peek() == '<' and _ANGLE_RE.match(cur.text, cur.i)):
            r_line, r_col = cur.line, cur.col
            cur.advance(len(m.group(0)))
            while cur.peek() in ' \t':
                cur.advance()
            target = None
            if not cur.eof and cur.peek() not in '\n;&|()':
                target = _bash_word(cur)
            items.append(Redirect(m.group(0), target, r_line, r_col))
            continue
        items.append(_bash_word(cur))
    return items


def _bash_word(cur):  # pylint: disable=too-many-branches
    word = Word('', cur.line, cur.col)
    buf = []
    start_i = cur.i
    while not cur.eof:
        ch = cur.peek()
        if ch == '(' and cur.i > start_i:
            if re.match(r'^[A-Za-z_][A-Za-z0-9_]*\+?=$', ''.join(buf)):
                # Array assignment: ids=($(az vm list ...)). Keep it, and scan it for commands.
                a_line, a_col = cur.line, cur.col + 1
                cur.advance()
                inner = _scan_balanced(cur, '(', ')', BASH)
                try:
                    for item in _lex_bash(inner, a_line, a_col):
                        if isinstance(item, Word):
                            word.substitutions.extend(item.substitutions)
                except ShellSyntaxError:
                    pass
                buf.append('(' + inner + ')')
                continue
            # `name=Dev(No` or `[?contains(`: Bash rejects an unquoted ( inside a word.
            raise ShellSyntaxError("unexpected '(' (quote the value)", cur.line, cur.col)
        if ch in ' \t\r\n;&|()':
            break
        if ch == '<' or ch == '>':
            m = _ANGLE_RE.match(cur.text, cur.i) if ch == '<' else None
            if not m:
                break
            word.unquoted_angle = True
            word.placeholders.append(Placeholder('angle', m.group(0)))
            buf.append(m.group(0))
            cur.advance(len(m.group(0)))
            continue
        if ch == '\\':
            if cur.peek(1) == '\n':
                cur.advance(2)
                continue
            buf.append(cur.peek(1))
            cur.advance(2)
            continue
        if ch == "'":
            line, col = cur.line, cur.col
            cur.advance()
            start = cur.i
            while not cur.eof and cur.peek() != "'":
                cur.advance()
            if cur.eof:
                raise ShellSyntaxError('unclosed single quote', line, col)
            literal = cur.text[start:cur.i]
            buf.append(literal)
            word.quoted = True
            cur.advance()
            continue
        if ch == '"':
            line, col = cur.line, cur.col
            cur.advance()
            word.quoted = True
            while True:
                if cur.eof:
                    raise ShellSyntaxError('unclosed double quote', line, col)
                c = cur.peek()
                if c == '"':
                    cur.advance()
                    break
                if c == '\\' and cur.peek(1) in ('$', '`', '"', '\\', '\n'):
                    if cur.peek(1) != '\n':
                        buf.append(cur.peek(1))
                    cur.advance(2)
                    continue
                if c == '$':
                    _bash_dollar(cur, word, buf, in_dquote=True)
                    continue
                if c == '`':
                    _bash_backtick(cur, word, buf)
                    continue
                buf.append(c)
                cur.advance()
            continue
        if ch == '$':
            _bash_dollar(cur, word, buf, in_dquote=False)
            continue
        if ch == '`':
            _bash_backtick(cur, word, buf)
            continue
        buf.append(ch)
        cur.advance()
    word.text = ''.join(buf)
    raw = cur.text[start_i:cur.i]
    _finish_word(word, raw)
    return word


def _finish_word(word, raw):
    if not word.quoted or '{' in word.text:
        for m in _BRACE_RE.finditer(word.text):
            if not word.text.startswith('$', max(m.start() - 1, 0)) or m.start() == 0:
                word.placeholders.append(Placeholder('template', m.group(0)))
    if not word.unquoted_angle:
        for m in _ANGLE_RE.finditer(word.text):
            word.placeholders.append(Placeholder('angle', m.group(0)))
    if word.text.startswith('@') and len(word.text) > 1:
        word.placeholders.append(Placeholder('at-file', '@...'))
    elif '=@' in word.text and word.text.startswith('-'):
        word.placeholders.append(Placeholder('at-file', '@...'))
    if len(word.placeholders) == 1:
        p = word.placeholders[0]
        stripped = raw.strip('"\'')
        word.whole = (p.kind == 'at-file' or stripped == p.text or
                      (p.kind == 'substitution' and stripped.startswith(('$(', '`')) and
                       stripped.endswith((')', '`'))) or
                      (p.kind == 'braced-variable' and stripped.startswith('${') and stripped.endswith('}')))


# ---------------------------------------------------------------------------------------------
# PowerShell
# ---------------------------------------------------------------------------------------------

_PS_REDIRECT_RE = re.compile(r'(?:[1-6*])?>>|(?:[1-6*])?>(?:&[12])?')


def _ps_dollar(cur, word, buf):
    nxt = cur.peek(1)
    if nxt == '(':
        cur.advance(2)
        sub_line, sub_col = cur.line, cur.col
        inner = _scan_balanced(cur, '(', ')', POWERSHELL)
        word.substitutions.append(Fragment(inner, sub_line, sub_col))
        word.placeholders.append(Placeholder('substitution', '$(...)'))
        buf.append('$(' + inner + ')')
        return
    if nxt == '{':
        cur.advance(2)
        inner = _scan_balanced(cur, '{', '}', POWERSHELL)
        word.placeholders.append(Placeholder('braced-variable', '${' + inner[:40] + '}'))
        buf.append('${' + inner + '}')
        return
    m = re.compile(r'(?:env:|global:|script:|local:|using:)?[A-Za-z_][A-Za-z0-9_]*', re.I).match(cur.text, cur.i + 1)
    if m:
        cur.advance(1 + len(m.group(0)))
        name = '$' + m.group(0)
        # Member access ($x.Name) and indexing ($x[0]) are part of the expression.
        while cur.peek() == '.' and _NAME_RE.match(cur.text, cur.i + 1):
            mm = _NAME_RE.match(cur.text, cur.i + 1)
            cur.advance(1 + len(mm.group(0)))
            name += '.' + mm.group(0)
        word.placeholders.append(Placeholder('variable', name))
        buf.append(name)
        return
    if nxt in ('_', '?', '$', '^'):
        cur.advance(2)
        word.placeholders.append(Placeholder('variable', '$' + nxt))
        buf.append('$' + nxt)
        return
    cur.advance()
    buf.append('$')


def _lex_powershell(text, line=1, column=1):  # pylint: disable=too-many-branches,too-many-statements
    cur = _Cursor(text, line, column)
    items = []
    while not cur.eof:
        ch = cur.peek()
        if ch in ' \t\r':
            cur.advance()
            continue
        if ch == '`' and cur.peek(1) == '\n':
            cur.advance(2)
            continue
        if ch == '`' and cur.peek(1) == '\r' and cur.peek(2) == '\n':
            cur.advance(3)
            continue
        if ch == '\n':
            items.append(Operator('\n', cur.line, cur.col))
            cur.advance()
            continue
        if cur.startswith('<#'):
            end = cur.text.find('#>', cur.i + 2)
            stop = len(cur.text) if end == -1 else end + 2
            while cur.i < stop:
                cur.advance()
            continue
        if ch == '#':
            while not cur.eof and cur.peek() != '\n':
                cur.advance()
            continue
        if cur.startswith('@"') or cur.startswith("@'"):
            if cur.peek(2) in ('\n', '\r'):
                items.append(Unsupported('here-string', cur.line, cur.col))
                quote = cur.peek(1)
                end = re.compile(r'^' + re.escape(quote) + '@', re.M).search(cur.text, cur.i + 2)
                stop = end.end() if end else len(cur.text)
                while cur.i < stop:
                    cur.advance()
                continue
        if cur.startswith('@(') or cur.startswith('@{'):
            items.append(Unsupported('array-or-hashtable', cur.line, cur.col))
            opener = cur.peek(1)
            cur.advance(2)
            _scan_balanced(cur, opener, ')' if opener == '(' else '}', POWERSHELL)
            continue
        if ch == '@' and _NAME_RE.match(cur.text, cur.i + 1):
            items.append(Unsupported('splatting', cur.line, cur.col))
            cur.advance(1 + len(_NAME_RE.match(cur.text, cur.i + 1).group(0)))
            continue
        if cur.startswith('--%'):
            items.append(Unsupported('stop-parsing', cur.line, cur.col))
            while not cur.eof and cur.peek() != '\n':
                cur.advance()
            continue
        matched = False
        for op in ('&&', '||', '|', ';', '(', ')', '{', '}'):
            if cur.startswith(op):
                items.append(Operator(op, cur.line, cur.col))
                cur.advance(len(op))
                matched = True
                break
        if matched:
            continue
        if ch == '&' and cur.peek(1) in ' \t"\'$':
            items.append(Operator('call', cur.line, cur.col))
            cur.advance()
            continue
        m = _PS_REDIRECT_RE.match(cur.text, cur.i)
        if m:
            r_line, r_col = cur.line, cur.col
            cur.advance(len(m.group(0)))
            while cur.peek() in ' \t':
                cur.advance()
            target = None
            if not cur.eof and cur.peek() not in '\n;|(){}' and '&' not in m.group(0):
                target = _ps_word(cur)
            items.append(Redirect(m.group(0), target, r_line, r_col))
            continue
        items.append(_ps_word(cur))
    return items


def _ps_word(cur):  # pylint: disable=too-many-branches
    word = Word('', cur.line, cur.col)
    buf = []
    start_i = cur.i
    while not cur.eof:
        ch = cur.peek()
        if ch in ' \t\r\n;|(){}':
            break
        if ch == '>' or (ch == '&' and cur.peek(1) == '&'):
            break
        if ch == '<':
            m = _ANGLE_RE.match(cur.text, cur.i)
            if not m:
                break
            word.unquoted_angle = True
            word.placeholders.append(Placeholder('angle', m.group(0)))
            buf.append(m.group(0))
            cur.advance(len(m.group(0)))
            continue
        if ch == '`':
            if cur.peek(1):
                buf.append({'n': '\n', 't': '\t', '0': '\0'}.get(cur.peek(1), cur.peek(1)))
            cur.advance(2)
            continue
        if ch == "'":
            line, col = cur.line, cur.col
            cur.advance()
            word.quoted = True
            while True:
                if cur.eof:
                    raise ShellSyntaxError('unclosed single quote', line, col)
                if cur.peek() == "'" and cur.peek(1) == "'":
                    buf.append("'")
                    cur.advance(2)
                    continue
                if cur.peek() == "'":
                    cur.advance()
                    break
                buf.append(cur.peek())
                cur.advance()
            continue
        if ch == '"':
            line, col = cur.line, cur.col
            cur.advance()
            word.quoted = True
            while True:
                if cur.eof:
                    raise ShellSyntaxError('unclosed double quote', line, col)
                c = cur.peek()
                if c == '"' and cur.peek(1) == '"':
                    buf.append('"')
                    cur.advance(2)
                    continue
                if c == '"':
                    cur.advance()
                    break
                if c == '`':
                    if cur.peek(1):
                        buf.append({'n': '\n', 't': '\t'}.get(cur.peek(1), cur.peek(1)))
                    cur.advance(2)
                    continue
                if c == '$':
                    _ps_dollar(cur, word, buf)
                    continue
                buf.append(c)
                cur.advance()
            continue
        if ch == '$':
            _ps_dollar(cur, word, buf)
            continue
        buf.append(ch)
        cur.advance()
    word.text = ''.join(buf)
    _finish_word(word, cur.text[start_i:cur.i])
    return word


# ---------------------------------------------------------------------------------------------
# Command extraction
# ---------------------------------------------------------------------------------------------

def _lex(text, dialect, line=1, column=1):
    return _lex_powershell(text, line, column) if dialect == POWERSHELL else _lex_bash(text, line, column)


def _split_simple_commands(items):
    """Group lexer items into simple commands, separated by operators."""
    commands, current = [], []
    for item in items:
        if isinstance(item, Operator) and item.op != 'call':
            if current:
                commands.append(current)
            current = []
            if item.op in ('|', '|&', '&&', '||', ';', '&'):
                commands.append(item)
            continue
        current.append(item)
    if current:
        commands.append(current)
    return commands


def _is_az(word):
    """`az`, `"az"`, `az.cmd` or a path ending in az; quoting doesn't change which program runs."""
    if not isinstance(word, Word) or word.is_placeholder:
        return False
    name = re.split(r'[\\/]', word.text)[-1].lower()
    return name in ('az', 'az.cmd', 'az.exe')


_FILTER_PROGRAMS = {'jq', 'grep', 'egrep', 'sed', 'awk', 'tr', 'cut', 'sort', 'uniq', 'head', 'tail', 'xargs', 'tee',
                    'wc', 'column', 'less', 'more', 'base64', 'cat', 'echo', 'yq', 'python', 'python3', 'findstr',
                    'convertfrom-json', 'convertto-json', 'select-object', 'where-object', 'foreach-object',
                    'format-table', 'format-list', 'out-file', 'set-content', 'add-content', 'out-null', 'sort-object',
                    'select-string', 'measure-object', 'tee-object', 'out-string', 'write-output', 'write-host'}


def _looks_like_split_value(group):
    """True if a command after an operator looks like the rest of an az command, not a program."""
    words = [x for x in group if isinstance(x, Word)]
    if not words:
        return False
    first = words[0].text
    if re.match(r'^[0-9.]', first) or first.startswith('-'):
        return True
    if first.lower() in _FILTER_PROGRAMS or _is_az(words[0]):
        return False
    return any(w.text.startswith('--') for w in words[1:])


def scan(text, dialect=BASH, line=1, column=1, nested=False, _result=None):
    """Find az invocations in shell text. Raises ShellSyntaxError for unbalanced quotes."""
    result = _result if _result is not None else ScanResult()
    items = _lex(text, dialect, line, column)
    groups = _split_simple_commands(items)
    last_az = None
    for pos, group in enumerate(groups):
        if isinstance(group, Operator):
            result.has_shell_operators = True
            nxt = groups[pos + 1] if pos + 1 < len(groups) else None
            if last_az is not None and isinstance(nxt, list) and _looks_like_split_value(nxt):
                last_az.suspicious_operators.append(group.op)
            continue
        last_az = None
        words = [x for x in group if isinstance(x, Word)]
        redirects = [x for x in group if isinstance(x, Redirect)]
        unsupported = [x for x in group if isinstance(x, Unsupported)]
        # Recurse into substitutions anywhere in the command, including redirect targets.
        for w in words + [r.target for r in redirects if r.target]:
            for frag in w.substitutions:
                scan(frag.text, dialect, frag.line, frag.column, nested=True, _result=result)
        cmd_words = _command_words(words, dialect)
        if cmd_words and _is_az(cmd_words[0]):
            inv = Invocation(cmd_words[1:], cmd_words[0].line, cmd_words[0].column, redirects, unsupported, nested)
            # A redirection followed by more arguments usually means an unquoted < or > in a value.
            first_redirect = next((k for k, x in enumerate(group) if isinstance(x, Redirect)), None)
            if first_redirect is not None and any(isinstance(x, Word) for x in group[first_redirect + 1:]):
                inv.suspicious_operators.append(group[first_redirect].op)
            result.invocations.append(inv)
            last_az = inv
            continue
        if cmd_words:
            result.other_commands += 1
            result.misplaced_az.extend(w for w in cmd_words[1:] if _is_az(w))
        result.unsupported.extend(unsupported)
    return result


def _offset(text, line, column):
    """The index in text of a 1-based line and column, as the lexer counts them."""
    pos = 0
    for _ in range(max(line, 1) - 1):
        nl = text.find('\n', pos)
        if nl == -1:
            return len(text)
        pos = nl + 1
    return min(pos + max(column, 1) - 1, len(text))


def scan_before_error(text, error, dialect=BASH):
    """Scan the complete commands before a syntax error: the text up to the last command separator
    (newline, ';', '&&', '|' and so on) before the error. Returns an empty result if there are none."""
    end = _offset(text, error.line, error.column)
    for _ in range(16):
        try:
            items = _lex(text[:end], dialect)
            seps = [i for i in items if isinstance(i, Operator) and i.op != 'call']
            if not seps:
                return ScanResult()
            cut = _offset(text, seps[-1].line, seps[-1].column)
            return scan(text[:cut], dialect)
        except ShellSyntaxError as ex:
            # An error in the shorter text, e.g. the unclosed '$(' around the first error, which is
            # reported just after its opener: move before it.
            end = min(_offset(text, ex.line, ex.column), end - 1)
            if end <= 0:
                break
    return ScanResult()


def _command_words(words, dialect):
    """Strip assignments, keywords and wrappers so the first word is the program run."""
    i = 0
    if dialect == BASH:
        while i < len(words):
            w = words[i]
            if not w.quoted and _BASH_ASSIGN_RE.match(w.text):
                i += 1
                continue
            if not w.quoted and w.text in _BASH_HEADER_WORDS:
                return []  # for/case/function headers: substitutions were already scanned
            if not w.quoted and w.text in ('export', 'local', 'readonly', 'declare', 'typeset'):
                return []
            if not w.quoted and w.text in _BASH_SKIP_WORDS:
                i += 1
                continue
            if not w.quoted and w.text in ('[', '[[', 'test', 'echo', 'printf'):
                return words[i:i + 1]
            break
    else:
        while i < len(words):
            w = words[i]
            low = w.text.lower()
            if not w.quoted and w.text.startswith('$') and i + 1 < len(words) and \
                    words[i + 1].text in ('=', '+=', '-=') and not words[i + 1].quoted:
                i += 2
                continue
            if not w.quoted and re.match(r'^\$[A-Za-z_][A-Za-z0-9_:]*=$', w.text):
                i += 1
                continue
            if not w.quoted and low in _PS_SKIP_WORDS:
                i += 1
                continue
            break
    return words[i:]
