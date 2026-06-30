import logging
import sys
import types
import unittest
from inspect import ArgInfo
from pathlib import Path
from types import MappingProxyType
from unittest.mock import patch


def _prepare_stubs():
    azure = sys.modules.setdefault('azure', types.ModuleType('azure'))
    azure.cli = sys.modules.setdefault('azure.cli', types.ModuleType('azure.cli'))
    azure.cli.core = sys.modules.setdefault('azure.cli.core', types.ModuleType('azure.cli.core'))

    if not hasattr(azure.cli.core, 'AzCommandsLoader'):
        class AzCommandsLoader:  # pylint: disable=too-few-public-methods
            pass

        azure.cli.core.AzCommandsLoader = AzCommandsLoader

    azure.cli.core.azclierror = sys.modules.setdefault(
        'azure.cli.core.azclierror', types.ModuleType('azure.cli.core.azclierror')
    )
    if not hasattr(azure.cli.core.azclierror, 'CLIError'):
        class CLIError(Exception):
            pass

        azure.cli.core.azclierror.CLIError = CLIError

    knack = sys.modules.setdefault('knack', types.ModuleType('knack'))
    knack.log = sys.modules.setdefault('knack.log', types.ModuleType('knack.log'))
    knack.prompting = sys.modules.setdefault('knack.prompting', types.ModuleType('knack.prompting'))
    knack.help_files = sys.modules.setdefault('knack.help_files', types.ModuleType('knack.help_files'))

    knack.log.get_logger = getattr(knack.log, 'get_logger', lambda _name: logging.getLogger(_name))
    knack.prompting.prompt_y_n = getattr(knack.prompting, 'prompt_y_n', lambda *_args, **_kwargs: True)
    if not hasattr(knack.prompting, 'NoTTYException'):
        class NoTTYException(Exception):
            pass

        knack.prompting.NoTTYException = NoTTYException
    knack.help_files.helps = getattr(knack.help_files, 'helps', {})


_prepare_stubs()
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from azext_vm_repair.repair_utils import _get_function_param_dict  # pylint: disable=wrong-import-position


class TestGetFunctionParamDict(unittest.TestCase):
    def test_converts_proxy_locals_to_dict_and_masks_secure_values(self):
        proxy_locals = MappingProxyType({
            'cmd': object(),
            'vm_name': 'vm1',
            'repair_password': 'password',
            'repair_username': 'username',
            'encrypt_recovery_key': 'recovery',
        })

        with patch('inspect.getargvalues', return_value=ArgInfo([], None, None, proxy_locals)):
            values = _get_function_param_dict(frame=object())

        self.assertIsInstance(values, dict)
        self.assertNotIn('cmd', values)
        self.assertEqual(values['vm_name'], 'vm1')
        self.assertEqual(values['repair_password'], '********')
        self.assertEqual(values['repair_username'], '********')
        self.assertEqual(values['encrypt_recovery_key'], '********')


if __name__ == '__main__':
    unittest.main()
