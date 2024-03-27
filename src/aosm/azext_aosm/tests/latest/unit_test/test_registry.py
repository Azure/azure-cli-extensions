# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from unittest import TestCase
from unittest.mock import Mock, patch, mock_open
import logging
import sys
import json

from azext_aosm.common.registry import (
    ContainerRegistry,
    UniversalRegistry,
    AzureContainerRegistry,
    ContainerRegistryHandler,
    REGISTRY_CLASS_TO_TYPE,
)
from knack.util import CLIError
from azure.cli.core.azclierror import ClientRequestError


class TestRegistry(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        self.registry = ContainerRegistry(registry_name="registry.example.com")

    def test_to_dict(self):
        """Test the to_dict method."""
        registry_name = "registry.example.com"
        registry = AzureContainerRegistry(registry_name=registry_name)
        expected_output = {
            "type": REGISTRY_CLASS_TO_TYPE[type(registry)],
            "registry_name": registry_name,
        }
        output_dict = registry.to_dict()
        self.assertEqual(output_dict, expected_output)

    def test_from_dict(self):
        """Test the from_dict method."""

        registry_dict = {
            "type": "AzureContainerRegistry",
            "registry_name": "registry.azurecr.io",
        }

        registry = ContainerRegistry.from_dict(registry_dict)

        self.assertIsInstance(registry, AzureContainerRegistry)
        self.assertEqual(registry.registry_name, "registry.azurecr.io")

        registry_dict = {
            "type": "UniversalRegistry",
            "registry_name": "registry.example.com",
        }

        registry = ContainerRegistry.from_dict(registry_dict)

        self.assertIsInstance(registry, UniversalRegistry)
        self.assertEqual(registry.registry_name, "registry.example.com")

    def test_from_dict_missing_field(self):
        registry_dict = {
            "type": "AzureContainerRegistry"
            # Missing "registry_name" field
        }

        with self.assertRaises(ValueError):
            ContainerRegistry.from_dict(registry_dict)

    def test_add_namespace(self):
        """Test the add_namespace method."""

        namespace_to_add = "Test_namespace"

        self.registry.add_namespace(namespace_to_add)

        assert namespace_to_add in self.registry.registry_namespaces


class TestUniversalRegistry(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        self.registry = UniversalRegistry(registry_name="ghcr.io")
        self.registry.add_namespace("")

    def test_find_image_existing_image(self):
        image = "myimage"
        version = "1.0.0"

        # Mock the call_subprocess_raise_output function
        mocked_output = "some output"
        mocked_call_subprocess_raise_output = Mock(return_value=mocked_output)

        with patch(
            "azext_aosm.common.registry.call_subprocess_raise_output",
            mocked_call_subprocess_raise_output,
        ):
            result = self.registry.find_image(image, version)

        self.assertEqual(result, (self.registry, ""))

    def test_find_image_cli_error(self):
        image = "myimage"
        version = "1.0.0"

        # Mock the call_subprocess_raise_output function to raise a CLIError
        mocked_error = CLIError()
        mocked_call_subprocess_raise_output = Mock(side_effect=mocked_error)

        with patch(
            "azext_aosm.common.registry.call_subprocess_raise_output",
            mocked_call_subprocess_raise_output,
        ):
            result = self.registry.find_image(image, version)
        self.assertEqual(result, (None, None))


class TestAzureContainerRegistry(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        self.registry = AzureContainerRegistry(registry_name="registry.azurecr.io")
        self.registry.add_namespace("")

    def test_find_image_existing_image(self):
        image = "myimage"
        version = "1.0.0"

        # Mock the call_subprocess_raise_output function
        mocked_output = "some output"
        mocked_call_subprocess_raise_output = Mock(return_value=mocked_output)

        with patch(
            "azext_aosm.common.registry.call_subprocess_raise_output",
            mocked_call_subprocess_raise_output,
        ):
            result = self.registry.find_image(image, version)

        self.assertEqual(result, (self.registry, ""))

    def test_find_image_cli_error(self):
        image = "myimage"
        version = "1.0.0"

        # Mock the call_subprocess_raise_output function to raise a CLIError
        mocked_error = CLIError()
        mocked_call_subprocess_raise_output = Mock(side_effect=mocked_error)

        with patch(
            "azext_aosm.common.registry.call_subprocess_raise_output",
            mocked_call_subprocess_raise_output,
        ):
            result = self.registry.find_image(image, version)
        self.assertEqual(result, (None, None))


class TestRegistryHandler(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)

        self.registry_name_1 = "registry.azurecr.io"
        self.registry_name_2 = "registry.example.com/sample"
        self.registry_name_3 = "registry.example.com"

        self.registry_handler = ContainerRegistryHandler(
            image_sources=[
                self.registry_name_1,
                self.registry_name_2,
                self.registry_name_3,
            ]
        )

    def test_create_registry_list(self):
        registry_list = self.registry_handler.registry_list

        # There are two unique registries (registry.example.com and registry.azurecr.io)
        self.assertEqual(len(registry_list), 2)

        registry_count = 0
        acr_registry_count = 0

        for registry in registry_list:
            self.assertIn(registry.registry_name, self.registry_handler.image_sources)

            if isinstance(registry, AzureContainerRegistry):
                acr_registry_count += 1
            elif isinstance(registry, ContainerRegistry):
                registry_count += 1
            else:
                self.fail("Unexpected registry type")

        self.assertEqual(registry_count, 1)
        self.assertEqual(acr_registry_count, 1)

    def test_find_registry_for_image(self):
        # Create a mock object to replace the find_image method
        mock_find_image_ACR = Mock()
        mock_find_image_ACR.return_value = (
            AzureContainerRegistry(self.registry_name_1),
            "",
        )
        mock_find_image_universal_registry = Mock()
        mock_find_image_universal_registry.return_value = (
            UniversalRegistry(self.registry_name_2),
            "sample",
        )
        with patch(
            "azext_aosm.common.registry.AzureContainerRegistry.find_image",
            mock_find_image_ACR,
        ):
            registry_1, namespace = self.registry_handler.find_registry_for_image(
                "image1", "1.0.0"
            )

        self.assertEqual(registry_1.registry_name, self.registry_name_1)
        self.assertEqual(namespace, "")

        with patch(
            "azext_aosm.common.registry.UniversalRegistry.find_image",
            mock_find_image_universal_registry,
        ):

            registry_2, namespace = self.registry_handler.find_registry_for_image(
                "image2", "1.0.0"
            )

        self.assertEqual(registry_2.registry_name, self.registry_name_2)
        self.assertEqual(namespace, "sample")
