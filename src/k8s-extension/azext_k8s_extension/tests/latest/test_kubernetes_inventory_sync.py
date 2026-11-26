# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azure.cli.core.azclierror import MutuallyExclusiveArgumentError

from azext_k8s_extension import custom
from azext_k8s_extension.partner_extensions import KubernetesInventorySync

from .MockClasses import MockCommand

EXTENSION_TYPE = "microsoft.kubernetesinventory.sync"
GRAFANA_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg"
    "/providers/Microsoft.Dashboard/grafana/grafana"
)
GRAFANA_SETTINGS = [{"importGrafana": "true", "grafanaResourceId": GRAFANA_ID, "operator.enabled": "true"}]


@patch.object(KubernetesInventorySync, "latest_registered_version", return_value="0.0.7")
@patch.object(KubernetesInventorySync, "import_grafana_dashboards")
@patch.object(custom, "sdk_no_wait")
@patch.object(custom, "validate_cc_registration")
@patch.object(custom, "is_dogfood_cluster", return_value=True)
class TestGrafanaImportOrdering(unittest.TestCase):
    def _create(self, **kwargs):
        return custom.create_k8s_extension(
            MockCommand(), MagicMock(), "rg", "cluster", "inventory", "connectedClusters", EXTENSION_TYPE,
            scope="cluster", configuration_settings=[dict(s) for s in GRAFANA_SETTINGS], **kwargs)

    def _update(self, **kwargs):
        client = MagicMock()
        client.get.return_value = SimpleNamespace(
            extension_type=EXTENSION_TYPE, version="0.0.7", current_version="0.0.7")
        return custom.update_k8s_extension(
            MagicMock(), client, "rg", "cluster", "inventory", "connectedClusters",
            configuration_settings=[dict(s) for s in GRAFANA_SETTINGS], yes=True, **kwargs)

    def test_create_rejected_by_common_validation_does_not_import(self, _, __, sdk_no_wait, import_dashboards, ___):
        with self.assertRaises(MutuallyExclusiveArgumentError):
            self._create(version="0.0.7", auto_upgrade_mode="compatible")
        import_dashboards.assert_not_called()
        sdk_no_wait.assert_not_called()

    def test_update_rejected_by_common_validation_does_not_import(self, _, __, sdk_no_wait, import_dashboards, ___):
        with self.assertRaises(MutuallyExclusiveArgumentError):
            self._update(auto_upgrade_minor_version=True, auto_upgrade_mode="patch")
        import_dashboards.assert_not_called()
        sdk_no_wait.assert_not_called()

    def test_valid_create_imports_and_omits_grafana_settings(self, _, __, sdk_no_wait, import_dashboards, ___):
        self._create(version="0.0.7", auto_upgrade_minor_version=False)
        import_dashboards.assert_called_once()
        self.assertEqual((GRAFANA_ID, "0.0.7"), import_dashboards.call_args.args[1:])
        extension = sdk_no_wait.call_args.args[-1]
        self.assertEqual({"operator.enabled": "true"}, extension.configuration_settings)

    def test_valid_update_imports_installed_version(self, _, __, sdk_no_wait, import_dashboards, ___):
        self._update()
        import_dashboards.assert_called_once()
        self.assertEqual((GRAFANA_ID, "0.0.7"), import_dashboards.call_args.args[1:])
        sdk_no_wait.assert_called_once()


if __name__ == "__main__":
    unittest.main()
