# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from unittest import TestCase
import os

from azure.cli.core.azclierror import ValidationError

from azext_aosm.cli_handlers.onboarding_cnf_handler import (
    OnboardingCNFCLIHandler,
)
from azext_aosm.configuration_models.onboarding_cnf_input_config import (
    HelmPackageConfig,
)

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
test_charts_directory = os.path.join(current_directory, "../mock_cnf/helm-charts")


class TestOnboardingCNFCLIHandler(TestCase):
    """Test the OnboardingCNFCLIHandler class."""

    def test_validate_helm_template_valid_chart(self):
        """Test validating a valid Helm chart using helm template."""

        handler = OnboardingCNFCLIHandler()
        handler.config.helm_packages = [
            HelmPackageConfig(
                name="nf-agent-cnf-UNIT-TEST",
                path_to_chart=os.path.join(test_charts_directory, "nf-agent-cnf"),
                default_values="",
                depends_on=[],
            )
        ]
        handler.config.images_source_registry = ""
        handler.config.source_registry_username = ""
        # We want to test a specific private method so disable the pylint warning
        # pylint: disable=protected-access
        handler._validate_helm_template()

    def test_validate_helm_template_invalid_chart(self):
        """Test validating an invalid Helm chart using helm template."""
        handler = OnboardingCNFCLIHandler()
        handler.config.helm_packages = [
            HelmPackageConfig(
                name="nf-agent-cnf-invalid-UNIT-TEST",
                path_to_chart=os.path.join(
                    test_charts_directory, "nf-agent-cnf-invalid"
                ),
                default_values="",
                depends_on=[],
            )
        ]
        handler.config.images_source_registry = ""
        handler.config.source_registry_username = ""
        with self.assertRaises(ValidationError):
            # We want to test a specific private method so disable the pylint warning
            # pylint: disable=protected-access
            handler._validate_helm_template()
