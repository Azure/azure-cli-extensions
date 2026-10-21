# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
import unittest


class Python312CompatTests(unittest.TestCase):
    """Guard against (re)introducing Python APIs removed or deprecated in Python 3.12+.

    This is a static, dependency-free scan of the shipped extension source (the
    ``azext_vm_repair`` package, excluding the ``tests`` tree). It fails if any
    banned pattern is present, which keeps the extension forward-compatible with
    Python 3.12 and newer.
    """

    # azext_vm_repair package root. This file lives at
    # azext_vm_repair/tests/latest/test_py312_compat.py, so three dirname() calls
    # walk up to the azext_vm_repair/ package directory.
    PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # (compiled regex, human-readable reason) for patterns banned in shipped code.
    BANNED_PATTERNS = [
        (re.compile(r'\bdatetime\.utcnow\s*\('),
         'datetime.utcnow() is deprecated in Python 3.12; use datetime.now(timezone.utc)'),
        (re.compile(r'\.utcfromtimestamp\s*\('),
         'datetime.utcfromtimestamp() is deprecated in Python 3.12; use datetime.fromtimestamp(ts, timezone.utc)'),
        (re.compile(r'\bimport\s+imp\b'),
         "the 'imp' module was removed in Python 3.12; use importlib"),
        (re.compile(r'\bimport\s+asyncore\b'),
         "the 'asyncore' module was removed in Python 3.12; use asyncio"),
        (re.compile(r'\bimport\s+asynchat\b'),
         "the 'asynchat' module was removed in Python 3.12; use asyncio"),
        (re.compile(r'\bfrom\s+distutils\b|\bimport\s+distutils\b'),
         "'distutils' was removed in Python 3.12; use the 'packaging' library"),
        (re.compile(r'\bpkgutil\.(?:get_loader|find_loader|ImpImporter)\b'),
         'pkgutil.get_loader/find_loader/ImpImporter are deprecated in Python 3.12 and '
         'removed in 3.14; use importlib.util (e.g. importlib.util.find_spec)'),
        (re.compile(r'\bplatform\.dist\s*\('),
         "platform.dist() was removed in Python 3.8; use the 'distro' library"),
    ]

    def _iter_source_files(self):
        for root, _, files in os.walk(self.PACKAGE_ROOT):
            # Only scan shipped code, not the test tree itself.
            if 'tests' in root.split(os.sep):
                continue
            for name in files:
                if name.endswith('.py'):
                    yield os.path.join(root, name)

    def test_no_python312_removed_or_deprecated_apis(self):
        offenders = []
        for path in self._iter_source_files():
            with open(path, encoding='utf-8') as handle:
                for lineno, line in enumerate(handle, start=1):
                    for pattern, reason in self.BANNED_PATTERNS:
                        if pattern.search(line):
                            rel = os.path.relpath(path, self.PACKAGE_ROOT)
                            offenders.append('{}:{}: {}'.format(rel, lineno, reason))
        self.assertEqual(
            offenders, [],
            'Found Python 3.12+ incompatible API usage in shipped code:\n' + '\n'.join(offenders)
        )


if __name__ == '__main__':
    unittest.main()
