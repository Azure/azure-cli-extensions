# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import os
import sys
from pathlib import Path
from unittest import TestCase
import tempfile
from azext_aosm.common.exceptions import (
    TemplateValidationError
)
from azext_aosm.inputs.helm_chart_input import HelmChartInput
from azure.cli.testsdk import live_only
from azure.cli.core.azclierror import InvalidArgumentValueError

code_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(code_directory, "../.."))
helm_charts_directory = os.path.join(parent_directory, "mock_cnf", "helm-charts")
MOCK_NF_AGENT_HELM_CHART = os.path.join(helm_charts_directory, "nf-agent-cnf-0.1.0.tgz")

VALID_CHART_NAME = "nf-agent-cnf"
INVALID_VALUES_CHART_NAME = "nf-agent-cnf-invalid-values"
INVALID_NO_VALUES_CHART_NAME = "nf-agent-cnf-no-values"


class TestHelmChartInput(TestCase):
    """Test the HelmChartInput class."""

    def setUp(self):
        # Prints out info logs in console if fails
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)


    @live_only()  # to avoid 'CannotOverwriteExistingCassetteException' when run from recording
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

        # A valid template does not raise exceptions or return anything.
        helm_chart_input.validate_template()

    @live_only()  # to avoid 'CannotOverwriteExistingCassetteException' when run from recording
    def test_validate_template_invalid_chart(self):
        """Test validating an invalid Helm chart using helm template."""

        helm_chart_input = HelmChartInput(
            artifact_name="test-invalid",
            artifact_version="1.0.0",
            chart_path=Path(
                os.path.join(
                    helm_charts_directory,
                    INVALID_VALUES_CHART_NAME,
                )
            ),
        )

        self.assertRaises(TemplateValidationError, helm_chart_input.validate_template)

    @live_only()  # to avoid 'CannotOverwriteExistingCassetteException' when run from recording
    def test_validate_values(self):
        """Test validating whether values exist in a helm chart.
            The validation for checking values.yaml exists happens in the helm chat input init,
            so we just need to instantiate the helm chart to test that.
        """

        HelmChartInput(
            artifact_name="test-invalid",
            artifact_version="1.0.0",
            chart_path=Path(
                os.path.join(
                    helm_charts_directory,
                    VALID_CHART_NAME,
                )
            ),
            default_config={},
            default_config_path={}
        )

        # Use an Invalid chart (because it does not have values.yaml in it),
        # but provide a default config path which will override those values.

        override_path = os.path.join(
            helm_charts_directory,
            INVALID_VALUES_CHART_NAME,
            'values.yaml'
        )
        HelmChartInput(
            artifact_name="test-default-values",
            artifact_version="1.0.0",
            chart_path=Path(
                os.path.join(
                    helm_charts_directory,
                    INVALID_VALUES_CHART_NAME,
                )
            ),
            default_config={},
            default_config_path=override_path
        )

    @live_only()  # to avoid 'CannotOverwriteExistingCassetteException' when run from recording
    def test_create_helm_chart_input_with_invalid_values(self):
        """Test validating a helm chart with values.yaml missing.
            The validation for checking values.yaml exists happens in the helm chat input init,
            so we just need to instantiate the helm chart to test that.
        """

        with self.assertRaises(InvalidArgumentValueError):
            HelmChartInput(
                artifact_name="test-invalid",
                artifact_version="1.0.0",
                chart_path=Path(
                    os.path.join(
                        helm_charts_directory,
                        INVALID_NO_VALUES_CHART_NAME,
                    )
                ),
                default_config={},
                default_config_path=None
            )

    def test_get_schema(self):
        """Test retrieving the schema for the Helm chart."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.chart_path = Path(self.temp_dir.name)

        with open(self.chart_path / "Chart.yaml", "w") as f:
            f.write("name: test-chart\nversion: 1.0.0")

        with open(self.chart_path / "values.yaml", "w") as f:
            f.write("key: value")

        helm_chart_input = HelmChartInput(
            artifact_name="test-schema",
            artifact_version="1.0.0",
            chart_path=self.chart_path,
        )
        # # NOTE: temporarly commented out as we have commented out the code for using the values.schema.json
        # # Test case when values.schema.json exists in the chart.
        # with open(self.chart_path / "values.schema.json", "w") as f:
        #     json.dump({"key": "value"}, f)
        # schema = helm_chart_input.get_schema()
        # self.assertEqual(schema, {"key": "value"})

        # # Test case when values.schema.json does not exist in the chart.
        # os.remove(self.chart_path / "values.schema.json")
        schema = helm_chart_input.get_schema()
        expected_schema = {
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"],
        }
        self.assertEqual(schema, expected_schema)

        self.temp_dir.cleanup()

