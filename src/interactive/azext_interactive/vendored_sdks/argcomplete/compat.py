# https://github.com/kislyuk/argcomplete/blob/v1.12.3/argcomplete/compat.py
from __future__ import absolute_import, division, print_function, unicode_literals

import locale
import sys

sys_encoding = locale.getpreferredencoding()

USING_PYTHON2 = True if sys.version_info < (3, 0) else False

if USING_PYTHON2:
    str = unicode  # noqa
else:
    str = str


def ensure_bytes(x, encoding=sys_encoding):
    if not isinstance(x, bytes):
        x = x.encode(encoding)
    return x


def ensure_str(x, encoding=sys_encoding):
    if not isinstance(x, str):
        x = x.decode(encoding)
    return x
