# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib.util
import os
import sys
import types
import unittest
from unittest.mock import patch


def install_fake_knack_modules():
    knack_module = types.ModuleType('knack')
    knack_log_module = types.ModuleType('knack.log')
    knack_util_module = types.ModuleType('knack.util')

    class CLIError(Exception):
        pass

    class FakeLogger:  # pylint: disable=too-few-public-methods
        def warning(self, *args, **kwargs):
            pass

    knack_log_module.get_logger = lambda *_args, **_kwargs: FakeLogger()
    knack_util_module.CLIError = CLIError
    knack_module.log = knack_log_module
    knack_module.util = knack_util_module

    sys.modules['knack'] = knack_module
    sys.modules['knack.log'] = knack_log_module
    sys.modules['knack.util'] = knack_util_module
    return CLIError


def install_fake_appservice_modules(create_file_share):
    azure_module = types.ModuleType('azure')
    cli_module = types.ModuleType('azure.cli')
    command_modules = types.ModuleType('azure.cli.command_modules')
    appservice_module = types.ModuleType('azure.cli.command_modules.appservice')
    appservice_custom_module = types.ModuleType('azure.cli.command_modules.appservice.custom')

    def create_functionapp(cmd, resource_group_name, name, storage_account, **kwargs):
        return {
            'resource_group_name': resource_group_name,
            'name': name,
            'storage_account': storage_account,
            'share_result': appservice_custom_module.create_file_share(
                cmd.cli_ctx,
                resource_group_name,
                storage_account,
                kwargs.get('share_name', 'content-share'))
        }

    appservice_custom_module.create_functionapp = create_functionapp
    appservice_custom_module.create_file_share = create_file_share
    appservice_module.custom = appservice_custom_module
    command_modules.appservice = appservice_module
    cli_module.command_modules = command_modules
    azure_module.cli = cli_module

    sys.modules['azure'] = azure_module
    sys.modules['azure.cli'] = cli_module
    sys.modules['azure.cli.command_modules'] = command_modules
    sys.modules['azure.cli.command_modules.appservice'] = appservice_module
    sys.modules['azure.cli.command_modules.appservice.custom'] = appservice_custom_module
    return appservice_custom_module


def load_custom_module():
    module_name = 'test_functionapp_custom'
    custom_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'custom.py'))
    spec = importlib.util.spec_from_file_location(module_name, custom_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeHttpError(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code


class TestFunctionAppCreateRetry(unittest.TestCase):
    def setUp(self):
        self._module_backup = {
            key: value for key, value in sys.modules.items()
            if key == 'knack' or key.startswith('knack.') or key == 'azure' or key.startswith('azure.')
        }
        self.CLIError = install_fake_knack_modules()

    def tearDown(self):
        for key in list(sys.modules):
            if key == 'knack' or key.startswith('knack.') or key == 'azure' or key.startswith('azure.'):
                sys.modules.pop(key)
        sys.modules.update(self._module_backup)

    def test_create_functionapp_retries_file_share_creation_on_403(self):
        attempts = []

        def create_file_share(*_args, **_kwargs):
            attempts.append(True)
            if len(attempts) < 3:
                raise FakeHttpError(403, 'Forbidden')
            return 'share-created'

        core_custom = install_fake_appservice_modules(create_file_share)
        custom = load_custom_module()

        sleep_calls = []
        with patch.object(custom.time, 'sleep', side_effect=sleep_calls.append):
            result = custom.create_functionapp(types.SimpleNamespace(cli_ctx='cli'), 'rg', 'func', 'storage')

        self.assertEqual(result['share_result'], 'share-created')
        self.assertEqual(len(attempts), 3)
        self.assertEqual(sleep_calls, [5, 10])
        self.assertIs(core_custom.create_file_share, create_file_share)

    def test_create_functionapp_raises_helpful_error_after_exhausting_403_retries(self):
        attempts = []

        def create_file_share(*_args, **_kwargs):
            attempts.append(True)
            raise FakeHttpError(403, 'Forbidden')

        install_fake_appservice_modules(create_file_share)
        custom = load_custom_module()

        with patch.object(custom.time, 'sleep'):
            with self.assertRaises(self.CLIError) as ex:
                custom.create_functionapp(types.SimpleNamespace(cli_ctx='cli'), 'rg', 'func', 'storage')

        self.assertEqual(len(attempts), len(custom.FILE_SHARE_CREATE_RETRY_DELAYS) + 1)
        self.assertIn('virtual network or firewall rules have not finished propagating', str(ex.exception))

    def test_create_functionapp_does_not_retry_non_403_errors(self):
        attempts = []

        def create_file_share(*_args, **_kwargs):
            attempts.append(True)
            raise FakeHttpError(500, 'Internal Server Error')

        install_fake_appservice_modules(create_file_share)
        custom = load_custom_module()

        with patch.object(custom.time, 'sleep') as sleep_mock:
            with self.assertRaises(FakeHttpError):
                custom.create_functionapp(types.SimpleNamespace(cli_ctx='cli'), 'rg', 'func', 'storage')

        self.assertEqual(len(attempts), 1)
        sleep_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
