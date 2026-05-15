# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azure.cli.core.azclierror import ValidationError
from azext_containerapp.containerapp_debug_command_decorator import ContainerAppDebugCommandDecorator


class TestDebugCommandUrlBuilding(unittest.TestCase):
    """Unit tests for the debug command URL building with custom image parameters."""

    def _create_decorator_with_params(self, params):
        """Helper to create a decorator instance with mocked params."""
        with mock.patch.object(ContainerAppDebugCommandDecorator, '__init__', lambda self, *a, **kw: None):
            decorator = ContainerAppDebugCommandDecorator()
            decorator.raw_parameters = params
        # Mock get_param to return from our dict
        decorator.get_param = lambda key: params.get(key)
        return decorator

    def _mock_get_url(self, decorator, cmd_mock, **kwargs):
        """Helper to call _get_url with mocked logstream endpoint and subscription."""
        base_endpoint = "https://proxy.example.com/subscriptions/test-sub/resourceGroups/test-rg/containerApps/test-app/revisions/test-rev/replicas/test-replica/logstream"
        with mock.patch.object(decorator, '_get_logstream_endpoint', return_value=base_endpoint):
            with mock.patch('azext_containerapp.containerapp_debug_command_decorator.get_subscription_id', return_value='test-sub'):
                return decorator._get_url(
                    cmd_mock,
                    kwargs.get('resource_group_name', 'test-rg'),
                    kwargs.get('container_app_name', 'test-app'),
                    kwargs.get('revision_name', 'test-rev'),
                    kwargs.get('replica_name', 'test-replica'),
                    kwargs.get('container_name', 'test-container'),
                    kwargs.get('command', '/bin/bash'),
                    kwargs.get('custom_debug_image_name'),
                    kwargs.get('custom_debug_image_entrypoint_command'),
                )

    def test_url_without_custom_image(self):
        """URL should not contain custom image params when not specified."""
        decorator = self._create_decorator_with_params({})
        cmd_mock = mock.MagicMock()
        url = self._mock_get_url(decorator, cmd_mock)

        self.assertIn("targetContainer=test-container", url)
        self.assertNotIn("customDebugImageName", url)
        self.assertNotIn("customDebugImageEntrypointCommand", url)

    def test_url_with_custom_image_only(self):
        """URL should contain customDebugImageName when --image is specified."""
        decorator = self._create_decorator_with_params({})
        cmd_mock = mock.MagicMock()
        url = self._mock_get_url(decorator, cmd_mock, custom_debug_image_name="ubuntu:22.04")

        self.assertIn("customDebugImageName=ubuntu%3A22.04", url)
        self.assertNotIn("customDebugImageEntrypointCommand", url)

    def test_url_with_custom_image_and_entrypoint(self):
        """URL should contain both params when --image and --entrypoint are specified."""
        decorator = self._create_decorator_with_params({})
        cmd_mock = mock.MagicMock()
        url = self._mock_get_url(
            decorator, cmd_mock,
            custom_debug_image_name="mcr.microsoft.com/dotnet/sdk:8.0",
            custom_debug_image_entrypoint_command="/bin/bash",
        )

        self.assertIn("customDebugImageName=mcr.microsoft.com%2Fdotnet%2Fsdk%3A8.0", url)
        self.assertIn("customDebugImageEntrypointCommand=%2Fbin%2Fbash", url)

    def test_url_encodes_special_characters(self):
        """Custom image params should be URL-encoded."""
        decorator = self._create_decorator_with_params({})
        cmd_mock = mock.MagicMock()
        url = self._mock_get_url(
            decorator, cmd_mock,
            custom_debug_image_name="myregistry.azurecr.io/my-image:v1.0",
            custom_debug_image_entrypoint_command="/bin/sh -c 'echo hello'",
        )

        self.assertIn("customDebugImageName=myregistry.azurecr.io%2Fmy-image%3Av1.0", url)
        self.assertIn("customDebugImageEntrypointCommand=%2Fbin%2Fsh+-c+%27echo+hello%27", url)


class TestDebugCommandValidation(unittest.TestCase):
    """Unit tests for client-side validation of custom image parameters."""

    def _create_decorator_with_params(self, params):
        """Helper to create a decorator instance with mocked params."""
        with mock.patch.object(ContainerAppDebugCommandDecorator, '__init__', lambda self, *a, **kw: None):
            decorator = ContainerAppDebugCommandDecorator()
        decorator.get_param = lambda key: params.get(key)
        return decorator

    def test_entrypoint_without_image_raises_validation_error(self):
        """--entrypoint without --image should raise ValidationError."""
        decorator = self._create_decorator_with_params({
            'custom_debug_image_name': None,
            'custom_debug_image_entrypoint_command': '/bin/bash',
            'resource_group_name': 'rg',
            'container_app_name': 'app',
            'revision_name': 'rev',
            'replica_name': 'replica',
            'container_name': 'container',
            'command': '/bin/bash',
        })

        cmd_mock = mock.MagicMock()
        with mock.patch.object(decorator, '_get_url'), \
             mock.patch.object(decorator, '_get_auth_token', return_value='token'), \
             mock.patch('azext_containerapp.containerapp_debug_command_decorator.send_raw_request'):
            with self.assertRaises(ValidationError) as ctx:
                decorator.execute_Command(cmd_mock)
            self.assertIn("--entrypoint requires --image", str(ctx.exception))

    def test_image_without_entrypoint_succeeds(self):
        """--image without --entrypoint should not raise."""
        decorator = self._create_decorator_with_params({
            'custom_debug_image_name': 'ubuntu:22.04',
            'custom_debug_image_entrypoint_command': None,
            'resource_group_name': 'rg',
            'container_app_name': 'app',
            'revision_name': 'rev',
            'replica_name': 'replica',
            'container_name': 'container',
            'command': '/bin/bash',
        })

        cmd_mock = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"status": "ok"}
        with mock.patch.object(decorator, '_get_url', return_value='https://example.com/debug'), \
             mock.patch.object(decorator, '_get_auth_token', return_value='token'), \
             mock.patch('azext_containerapp.containerapp_debug_command_decorator.send_raw_request', return_value=mock_response), \
             mock.patch('azext_containerapp.containerapp_debug_command_decorator.transform_debug_command_output', return_value={"status": "ok"}):
            # Should not raise
            decorator.execute_Command(cmd_mock)

    def test_no_custom_params_succeeds(self):
        """No custom image params should not raise."""
        decorator = self._create_decorator_with_params({
            'custom_debug_image_name': None,
            'custom_debug_image_entrypoint_command': None,
            'resource_group_name': 'rg',
            'container_app_name': 'app',
            'revision_name': 'rev',
            'replica_name': 'replica',
            'container_name': 'container',
            'command': '/bin/bash',
        })

        cmd_mock = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"status": "ok"}
        with mock.patch.object(decorator, '_get_url', return_value='https://example.com/debug'), \
             mock.patch.object(decorator, '_get_auth_token', return_value='token'), \
             mock.patch('azext_containerapp.containerapp_debug_command_decorator.send_raw_request', return_value=mock_response), \
             mock.patch('azext_containerapp.containerapp_debug_command_decorator.transform_debug_command_output', return_value={"status": "ok"}):
            # Should not raise
            decorator.execute_Command(cmd_mock)

    def test_getter_methods(self):
        """Getter methods should return correct param values."""
        decorator = self._create_decorator_with_params({
            'custom_debug_image_name': 'ubuntu:22.04',
            'custom_debug_image_entrypoint_command': '/bin/bash',
        })

        self.assertEqual(decorator.get_argument_custom_debug_image_name(), 'ubuntu:22.04')
        self.assertEqual(decorator.get_argument_custom_debug_image_entrypoint_command(), '/bin/bash')

    def test_getter_methods_return_none_when_not_set(self):
        """Getter methods should return None when params not provided."""
        decorator = self._create_decorator_with_params({})

        self.assertIsNone(decorator.get_argument_custom_debug_image_name())
        self.assertIsNone(decorator.get_argument_custom_debug_image_entrypoint_command())


class TestValidateDebugCustomImageRequiresCommand(unittest.TestCase):
    """Validate that --image/--entrypoint require --command."""

    def _make_namespace(self, **kwargs):
        ns = mock.MagicMock()
        ns.debug_command = kwargs.get('debug_command', None)
        ns.custom_debug_image_name = kwargs.get('custom_debug_image_name', None)
        ns.custom_debug_image_entrypoint_command = kwargs.get('custom_debug_image_entrypoint_command', None)
        ns.revision = kwargs.get('revision', 'rev')
        ns.replica = kwargs.get('replica', 'replica')
        ns.container = kwargs.get('container', 'container')
        ns.name = 'test-app'
        ns.resource_group_name = 'test-rg'
        return ns

    @mock.patch('azext_containerapp._validators._set_debug_defaults')
    def test_image_without_command_raises(self, mock_defaults):
        from azext_containerapp._validators import validate_debug
        ns = self._make_namespace(custom_debug_image_name='ubuntu:22.04')
        with self.assertRaises(ValidationError) as ctx:
            validate_debug(mock.MagicMock(), ns)
        self.assertIn("--image", str(ctx.exception))

    @mock.patch('azext_containerapp._validators._set_debug_defaults')
    def test_entrypoint_without_command_raises(self, mock_defaults):
        from azext_containerapp._validators import validate_debug
        ns = self._make_namespace(custom_debug_image_entrypoint_command='/bin/bash')
        with self.assertRaises(ValidationError) as ctx:
            validate_debug(mock.MagicMock(), ns)
        self.assertIn("--image", str(ctx.exception))

    @mock.patch('azext_containerapp._validators._set_debug_defaults')
    @mock.patch('azext_containerapp._validators._validate_revision_exists')
    @mock.patch('azext_containerapp._validators._validate_replica_exists')
    @mock.patch('azext_containerapp._validators._validate_container_exists')
    def test_image_with_command_passes(self, mock_cont, mock_rep, mock_rev, mock_defaults):
        from azext_containerapp._validators import validate_debug
        ns = self._make_namespace(
            debug_command='/bin/bash',
            custom_debug_image_name='ubuntu:22.04',
        )
        validate_debug(mock.MagicMock(), ns)  # should not raise


if __name__ == '__main__':
    unittest.main()
