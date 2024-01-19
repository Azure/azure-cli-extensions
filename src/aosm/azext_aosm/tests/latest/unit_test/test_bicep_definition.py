# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from azext_aosm.definition_folder.reader.bicep_definition import BicepDefinitionElement


class TestBicepDefinitionElement(TestCase):
    """Test the Bicep definition element."""

    def test_deploy(self):
        """Test deploying a Bicep definition element."""
        # Set up any mocks.
        # TODO: Implement.

        # Create a Bicep definition element.
        element_path = Path("/element/path")
        definition_element = BicepDefinitionElement(element_path, False)

        # Deploy the element.
        definition_element.deploy()

        # Check results.
        # TODO: Implement.

    def test_delete(self):
        """Test deleting a Bicep definition element."""
        # Set up any mocks.
        # TODO: Implement.

        # Create a Bicep definition element.
        # only_delete_on_clean is True, but this is not checked in the delete method.
        # It is expected to be checked in the owning DefinitionFolder before calling delete.
        element_path = Path("/element/path")
        definition_element = BicepDefinitionElement(element_path, True)

        # Delete the element.
        definition_element.delete()

        # Check results.
        # TODO: Implement.
