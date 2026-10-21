# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Guard that ``azext_chaos/aaz/`` contains no hand-edited ``pre_operations`` /
``post_operations`` method bodies.

Hand-editing the aaz/ tree is forbidden — aliases, renames, and help text
belong in the aaz-dev workspace editor; behavioral hooks belong in
:mod:`azext_chaos.custom` subclasses registered in
:mod:`azext_chaos.commands`.

See ``automation/cli-extension/src/chaos/README.md`` §"Modifying the
AAZ-generated code".
"""

import pathlib
import re
import unittest


class TestAazPristine(unittest.TestCase):
    def test_no_pre_post_operations_bodies_in_aaz(self):
        aaz_root = pathlib.Path(__file__).resolve().parents[2] / 'aaz' / 'latest' / 'chaos'
        self.assertTrue(aaz_root.is_dir(), f'aaz root not found at {aaz_root}')

        non_pass_re = re.compile(
            r'@register_callback\s*\n\s*def (?:pre|post)_operations\(self\):\s*\n'
            r'((?:[ \t]+.*\n)+)',
            re.MULTILINE,
        )
        bad = []
        for py in aaz_root.rglob('*.py'):
            text = py.read_text(encoding='utf-8')
            for body in non_pass_re.findall(text):
                stripped = body.strip()
                if stripped and stripped != 'pass':
                    bad.append(str(py.relative_to(aaz_root)))
                    break
        self.assertFalse(
            bad,
            'aaz/ files MUST NOT contain hand-written pre/post_operations bodies. '
            'Move logic to a custom.py subclass and register it in commands.py. '
            f'Offenders: {bad}'
        )


if __name__ == '__main__':
    unittest.main()
