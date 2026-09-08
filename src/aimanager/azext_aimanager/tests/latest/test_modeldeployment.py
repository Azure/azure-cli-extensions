# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.core import MatchConditions

from azext_aimanager import custom
from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


class MockCmd:
    def get_models(self, name, **_):
        return getattr(models, name)


class TestModelDeployment(unittest.TestCase):

    def setUp(self):
        self.cmd = MockCmd()

    def test_manual_scaling(self):
        scale = custom._construct_scaling_profile(self.cmd, replicas=0, required=True)

        self.assertEqual(scale.manual.replicas, 0)
        self.assertIsNone(scale.autoscale)

    def test_scaling_modes_are_mutually_exclusive(self):
        with self.assertRaises(InvalidArgumentValueError):
            custom._construct_scaling_profile(
                self.cmd, replicas=1, min_replicas=1, required=True)

    def test_autoscale_requires_minimum_when_not_already_enabled(self):
        with self.assertRaises(InvalidArgumentValueError):
            custom._construct_scaling_profile(
                self.cmd, max_replicas=3, required=True)

    @patch.object(custom, "sdk_no_wait")
    @patch.object(custom, "_construct_modeldeployment")
    def test_update_preserves_omitted_properties_and_uses_etag(
            self, construct_modeldeployment, sdk_no_wait):
        existing_scale = models.ScalingProfile(
            manual=models.ManualScalingProfile(replicas=2))
        existing_overrides = models.ModelDeploymentOverrides(
            values_property={"engine": "vllm"})
        existing = SimpleNamespace(
            e_tag='"etag-value"',
            properties=SimpleNamespace(
                model_resource_id="/models/model-a",
                model_source_resource_id="/sources/source-a",
                performance_mode="Latency",
                vm_size="Standard_NC24ads_A100_v4",
                scale=existing_scale,
                overrides=existing_overrides,
            ),
        )
        client = MagicMock()
        client.get.return_value = existing
        deployment = object()
        construct_modeldeployment.return_value = deployment
        sdk_no_wait.return_value = "result"

        result = custom.update_modeldeployment(
            self.cmd, client, "rg", "manager", "namespace", "deployment")

        self.assertEqual(result, "result")
        construct_modeldeployment.assert_called_once_with(
            self.cmd,
            "/models/model-a",
            "Standard_NC24ads_A100_v4",
            "/sources/source-a",
            "Latency",
            existing_scale,
            {"engine": "vllm"},
        )
        sdk_no_wait.assert_called_once_with(
            False,
            client.begin_create_or_update,
            "rg",
            "manager",
            "namespace",
            "deployment",
            deployment,
            headers={},
            etag='"etag-value"',
            match_condition=MatchConditions.IfNotModified,
        )


if __name__ == '__main__':
    unittest.main()
