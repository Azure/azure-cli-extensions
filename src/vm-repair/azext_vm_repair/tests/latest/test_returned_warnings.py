# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest import mock

from azext_vm_repair.command_helper_class import command_helper


class ReturnedWarningsTest(unittest.TestCase):

    # The NVMe-only repair VM warning reached the operator on stderr but never entered the returned
    # JSON, so an automated caller could not tell that the repair VM it just created is one several
    # repair scripts cannot find a disk on.
    def _helper(self):
        # The real __init__/__del__ start a progress controller and emit telemetry; neither is
        # relevant to how the return payload is assembled.
        with mock.patch.object(command_helper, '__init__', return_value=None), \
                mock.patch.object(command_helper, '__del__', lambda self: None):
            helper = command_helper(None, None, 'vm repair create')
        helper.status = 'SUCCESS'
        helper.message = 'done'
        helper.warnings = []
        helper.logger = mock.MagicMock()
        return helper

    def test_no_warnings_key_when_nothing_was_raised(self):
        helper = self._helper()
        self.assertNotIn('warnings', helper.init_return_dict())

    def test_warnings_are_returned_when_raised(self):
        helper = self._helper()
        helper.warnings.append('The repair VM size only supports NVMe.')
        self.assertEqual(['The repair VM size only supports NVMe.'], helper.init_return_dict()['warnings'])

    def test_returned_warnings_are_a_copy(self):
        helper = self._helper()
        helper.warnings.append('first')
        returned = helper.init_return_dict()['warnings']
        helper.warnings.append('second')
        self.assertEqual(['first'], returned)


if __name__ == '__main__':
    unittest.main()
