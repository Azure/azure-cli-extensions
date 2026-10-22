import unittest
from argparse import Namespace
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from knack.util import CLIError
from azure.cli.core.mock import DummyCli

from ... import _validators as validators


class TestFunctionappValidators(unittest.TestCase):
    def test_validate_create_raises_for_linux_consumption_dotnet_ten(self):
        namespace = Namespace(
            cmd=SimpleNamespace(cli_ctx=DummyCli()),
            runtime='dotnet-isolated',
            runtime_version='10.0',
            os_type='Linux',
            consumption_plan_location='eastus',
            resource_group_name='rg',
            plan=None
        )

        with self.assertRaises(CLIError):
            validators.validate_dotnet_ten_runtime_for_create(namespace)

    @patch('azext_functionapp._validators._get_plan')
    def test_validate_create_raises_for_linux_y1_plan_dotnet_ten(self, get_plan):
        get_plan.return_value = SimpleNamespace(
            reserved=True,
            sku=SimpleNamespace(name='Y1')
        )
        namespace = Namespace(
            cmd=SimpleNamespace(cli_ctx=DummyCli()),
            runtime='dotnet-isolated',
            runtime_version='10.0',
            os_type='Linux',
            consumption_plan_location=None,
            resource_group_name='rg',
            plan='plan1'
        )

        with self.assertRaises(CLIError):
            validators.validate_dotnet_ten_runtime_for_create(namespace)

    def test_validate_create_allows_other_versions(self):
        namespace = Namespace(
            cmd=SimpleNamespace(cli_ctx=DummyCli()),
            runtime='dotnet-isolated',
            runtime_version='8.0',
            os_type='Linux',
            consumption_plan_location='eastus',
            resource_group_name='rg',
            plan=None
        )

        validators.validate_dotnet_ten_runtime_for_create(namespace)

    @patch('azext_functionapp._validators._get_plan')
    @patch('azext_functionapp._validators.web_client_factory')
    def test_validate_config_set_raises_for_linux_y1(self, web_client_factory, get_plan):
        web_client = MagicMock()
        web_client_factory.return_value = web_client
        web_client.web_apps.get.return_value = SimpleNamespace(
            reserved=True,
            server_farm_id='/subscriptions/s1/resourceGroups/rg/providers/Microsoft.Web/serverfarms/plan1'
        )
        get_plan.return_value = SimpleNamespace(
            reserved=True,
            sku=SimpleNamespace(name='Y1')
        )
        namespace = Namespace(
            cmd=SimpleNamespace(cli_ctx=DummyCli()),
            linux_fx_version='DOTNET-ISOLATED|10.0',
            resource_group_name='rg',
            name='func1',
            slot=None
        )

        with self.assertRaises(CLIError):
            validators.validate_dotnet_ten_linux_fx_version_for_config_set(namespace)

    @patch('azext_functionapp._validators.web_client_factory')
    def test_validate_config_set_allows_other_linux_fx_version(self, web_client_factory):
        namespace = Namespace(
            cmd=SimpleNamespace(cli_ctx=DummyCli()),
            linux_fx_version='DOTNET-ISOLATED|8.0',
            resource_group_name='rg',
            name='func1',
            slot=None
        )

        validators.validate_dotnet_ten_linux_fx_version_for_config_set(namespace)
        web_client_factory.assert_not_called()


if __name__ == '__main__':
    unittest.main()
