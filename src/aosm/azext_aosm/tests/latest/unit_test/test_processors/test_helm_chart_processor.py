# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
from unittest import TestCase
from unittest.mock import Mock

from azext_aosm.build_processors.helm_chart_processor import HelmChartProcessor

code_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(code_directory, "../.."))
mock_cnf_directory = os.path.join(parent_directory, "mock_cnf")

HELM_TEMPLATE_MOCK_OUTPUT_FILE = "nf-agent-cnf-helm_template_output.yaml"


class TestHelmChartProcessor(TestCase):
    def setUp(self):
        self.helm_chart_processor = HelmChartProcessor(
            name="test-nf-agent-cnf",
            input_artifact=Mock(),
            registry_handler=None,
            expose_all_params=False
        )

    def test_find_chart_images(self):
        with open(
            os.path.join(mock_cnf_directory, HELM_TEMPLATE_MOCK_OUTPUT_FILE),
            "r",
            encoding="utf-8",
        ) as file:
            helm_template_contents = file.read()

        self.helm_chart_processor.input_artifact.helm_template = helm_template_contents
        self.helm_chart_processor.input_artifact.artifact_name = "test-nf-agent-cnf"

        # We want to test a specific private method so disable the pylint warning
        # pylint: disable=protected-access
        collected_images = self.helm_chart_processor._find_chart_images()

        # Assert the expected images are returned
        expected_images = {("pez-nfagent", "879624")}
        self.assertEqual(collected_images, expected_images)
