# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from unittest import TestCase
from pathlib import Path
import os

from azext_aosm.inputs.helm_chart_input import (
    HelmChartInput,
)

code_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(code_directory, ".."))
helm_charts_directory = os.path.join(parent_directory, "mock_cnf", "helm-charts")

VALID_CHART_NAME = "nf-agent-cnf"
INVALID_CHART_NAME = "nf-agent-cnf-invalid"


class TestHelmChartInput(TestCase):
    """Test the HelmChartInput class."""

    def test_validate_template_valid_chart(self):
        """Test validating a valid Helm chart using helm template."""

        helm_chart_input = HelmChartInput(
            artifact_name="test-valid",
            artifact_version="1.0.0",
            chart_path=Path(
                os.path.join(
                    helm_charts_directory,
                    VALID_CHART_NAME,
                )
            ),
        )

        output = helm_chart_input.validate_template()

        assert output == ""

    def test_validate_template_invalid_chart(self):
        """Test validating an invalid Helm chart using helm template."""

        helm_chart_input = HelmChartInput(
            artifact_name="test-invalid",
            artifact_version="1.0.0",
            chart_path=Path(
                os.path.join(
                    helm_charts_directory,
                    INVALID_CHART_NAME,
                )
            ),
        )

        output = helm_chart_input.validate_template()

        assert output != ""
