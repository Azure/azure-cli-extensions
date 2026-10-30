# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from azure.core.exceptions import HttpResponseError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.parser import AzCliCommandParser
from azure.cli.core.azclierror import (
    ForbiddenError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    ResourceNotFoundError,
    UnknownError,
)
from azext_aks_preview import ContainerServiceCommandsLoader, register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.azuremanagedlustre._helpers import (
    check_if_extension_is_installed,
    get_azure_managed_lustre_extension_client,
)
from azext_aks_preview.azuremanagedlustre._validators import (
    _get_vm_sku_architectures,
    validate_azure_managed_lustre_node_compatibility,
    validate_azure_managed_lustre_params,
)
from azext_aks_preview.azuremanagedlustre.aml_ops import (
    perform_disable_azure_managed_lustre,
    perform_enable_azure_managed_lustre,
)
from azext_aks_preview.custom import aks_create, aks_update
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterCreateDecorator,
    AKSPreviewManagedClusterModels,
    AKSPreviewManagedClusterUpdateDecorator,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockCmd


HELPERS = "azext_aks_preview.azuremanagedlustre._helpers"
OPS = "azext_aks_preview.azuremanagedlustre.aml_ops"
DECORATOR = "azext_aks_preview.managed_cluster_decorator"
VALIDATORS = "azext_aks_preview.azuremanagedlustre._validators"


class AzureManagedLustreHelpersTestCase(unittest.TestCase):
    def setUp(self):
        self.cmd = Mock()
        self.client = Mock()
        self.custom = Mock()
        self.client_patch = patch(
            HELPERS + ".get_azure_managed_lustre_extension_client",
            return_value=(self.client, self.custom),
        )

    def test_get_extension_client_reuses_module_loader(self):
        factory = Mock()
        with patch(HELPERS + ".get_k8s_extension_module", side_effect=[factory, self.custom]) as loader:
            client, custom = get_azure_managed_lustre_extension_client(self.cmd)
        self.assertEqual([call.args[0] for call in loader.call_args_list], [
            "azext_k8s_extension._client_factory", "azext_k8s_extension.custom",
        ])
        factory.cf_k8s_extension_operation.assert_called_once_with(self.cmd.cli_ctx)
        self.assertIs(client, factory.cf_k8s_extension_operation.return_value)
        self.assertIs(custom, self.custom)

    def test_missing_cli_extension_is_reported(self):
        with patch(HELPERS + ".get_k8s_extension_module", side_effect=UnknownError("Install k8s-extension")):
            with self.assertRaisesRegex(UnknownError, "Install k8s-extension"):
                get_azure_managed_lustre_extension_client(self.cmd)

    def test_installed_extension_type_is_case_insensitive(self):
        self.custom.show_k8s_extension.return_value.extension_type = "Microsoft.AzureManagedLustre"
        with self.client_patch:
            self.assertTrue(check_if_extension_is_installed(self.cmd, "rg", "cluster"))
        self.custom.show_k8s_extension.assert_called_once_with(
            self.client, "rg", "cluster", "azurelustre", "managedClusters"
        )

    def test_missing_extension(self):
        self.custom.show_k8s_extension.side_effect = ResourceNotFoundError("not found")
        with self.client_patch:
            self.assertFalse(check_if_extension_is_installed(self.cmd, "rg", "cluster"))

    def test_name_collision_is_rejected(self):
        self.custom.show_k8s_extension.return_value.extension_type = "microsoft.other"
        with self.client_patch, self.assertRaisesRegex(InvalidArgumentValueError, "microsoft.other"):
            check_if_extension_is_installed(self.cmd, "rg", "cluster")

    def test_service_errors_are_not_treated_as_missing(self):
        self.custom.show_k8s_extension.side_effect = HttpResponseError("Forbidden")
        with self.client_patch, self.assertRaisesRegex(HttpResponseError, "Forbidden"):
            check_if_extension_is_installed(self.cmd, "rg", "cluster")


class AzureManagedLustreValidatorsTestCase(unittest.TestCase):
    def setUp(self):
        architecture_patch = patch(
            VALIDATORS + "._get_vm_sku_architectures",
            return_value={"standard_d2s_v5": "x64", "standard_d2ps_v5": "arm64"},
        )
        architecture_patch.start()
        self.addCleanup(architecture_patch.stop)

    def test_conflicting_flags(self):
        with self.assertRaises(MutuallyExclusiveArgumentError):
            validate_azure_managed_lustre_params(True, True)

    def test_disable_requires_installed_extension(self):
        with self.assertRaisesRegex(InvalidArgumentValueError, "resource was not found"):
            validate_azure_managed_lustre_params(False, True, False)

    def test_valid_parameters(self):
        for enable, disable, installed in [
            (False, False, None), (True, False, False), (True, False, True), (False, True, True),
        ]:
            with self.subTest(enable=enable, disable=disable, installed=installed):
                validate_azure_managed_lustre_params(enable, disable, installed)

    def test_supported_node_pool(self):
        cluster = SimpleNamespace(
            location="eastus",
            agent_pool_profiles=[SimpleNamespace(os_sku="Ubuntu2404", vm_size="Standard_D2s_v5")],
        )
        validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_unsupported_node_pool_os_skus(self):
        for os_sku in ["Flatcar", "Ubuntu2604"]:
            with self.subTest(os_sku=os_sku):
                cluster = SimpleNamespace(
                    location="eastus",
                    agent_pool_profiles=[SimpleNamespace(os_sku=os_sku, vm_size="Standard_D2s_v5")],
                )
                with self.assertRaisesRegex(InvalidArgumentValueError, "none of the cluster's node pools"):
                    validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_azure_linux_3_node_pool_architecture(self):
        cluster = SimpleNamespace(
            location="eastus",
            agent_pool_profiles=[SimpleNamespace(os_sku="AzureLinux3", vm_size="Standard_D2ps_v5")],
        )
        with patch(
            "azext_aks_preview.azuremanagedlustre._validators._get_vm_sku_architectures",
            return_value={"standard_d2ps_v5": "arm64"},
        ):
            with self.assertRaisesRegex(InvalidArgumentValueError, "ARM64"):
                validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

        with patch(
            "azext_aks_preview.azuremanagedlustre._validators._get_vm_sku_architectures",
            return_value={"standard_d2ps_v5": "x64"},
        ):
            validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_ubuntu_2204_node_pool_architecture(self):
        cluster = SimpleNamespace(
            location="eastus",
            agent_pool_profiles=[SimpleNamespace(os_sku="Ubuntu2204", vm_size="Standard_D2ps_v5")],
        )
        with patch(
            "azext_aks_preview.azuremanagedlustre._validators._get_vm_sku_architectures",
            return_value={"standard_d2ps_v5": "arm64"},
        ):
            with self.assertRaisesRegex(InvalidArgumentValueError, "ARM64"):
                validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_azure_linux_alias_uses_kubernetes_version(self):
        for kubernetes_version, should_raise in [("1.31.9", True), ("1.32.0", True)]:
            with self.subTest(kubernetes_version=kubernetes_version):
                cluster = SimpleNamespace(
                    location="eastus",
                    kubernetes_version=kubernetes_version,
                    agent_pool_profiles=[SimpleNamespace(os_sku="AzureLinux", vm_size="Standard_D2ps_v5")],
                )
                with patch(
                    "azext_aks_preview.azuremanagedlustre._validators._get_vm_sku_architectures",
                    return_value={"standard_d2ps_v5": "arm64"},
                ):
                    if should_raise:
                        with self.assertRaisesRegex(InvalidArgumentValueError, "ARM64"):
                            validate_azure_managed_lustre_node_compatibility(Mock(), cluster)
                    else:
                        validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_unknown_azure_linux_3_node_pool_architecture(self):
        cluster = SimpleNamespace(
            location="eastus",
            agent_pool_profiles=[SimpleNamespace(os_sku="AzureLinux3", vm_size="Standard_Unknown")],
        )
        with patch(
            "azext_aks_preview.azuremanagedlustre._validators._get_vm_sku_architectures",
            return_value={},
        ):
            with self.assertRaisesRegex(InvalidArgumentValueError, "architecture couldn't be determined"):
                validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_os_aliases_resolve_before_architecture_validation(self):
        cases = [
            ("Ubuntu", "1.34.0", None, "arm64", True),
            ("uBuNtU", "1.34", None, "arm64", True),
            (None, "1.34.0", None, "arm64", True),
            ("Ubuntu", "1.34.0", None, "x64", False),
            (None, "1.34.0", None, "x64", False),
            ("Ubuntu", "1.35.0", None, "arm64", False),
            (None, "1.35.0", None, "arm64", False),
            ("Ubuntu", "1.24.9", None, "arm64", True),
            ("Ubuntu", "1.24.9", None, "x64", False),
            ("Ubuntu", "1.35.0", "1.34.9", "arm64", True),
            ("AzureLinux", "1.31.9", "1.32.0", "arm64", True),
            ("azurelinux", "1.32", None, "arm64", True),
            ("AzureLinux", "v1.32.0-preview.1", None, "arm64", True),
        ]
        for os_sku, cluster_version, pool_version, architecture, should_raise in cases:
            with self.subTest(os_sku=os_sku, cluster_version=cluster_version,
                              pool_version=pool_version, architecture=architecture):
                cluster = SimpleNamespace(
                    location="eastus", kubernetes_version=cluster_version,
                    agent_pool_profiles=[SimpleNamespace(
                        os_sku=os_sku, orchestrator_version=pool_version, vm_size="Standard_D2ps_v5",
                    )],
                )
                with patch(VALIDATORS + ".cf_managed_clusters") as client, patch(
                    VALIDATORS + "._get_vm_sku_architectures",
                    return_value={"standard_d2ps_v5": architecture},
                ):
                    if should_raise:
                        with self.assertRaisesRegex(InvalidArgumentValueError, "ARM64"):
                            validate_azure_managed_lustre_node_compatibility(Mock(), cluster)
                    else:
                        validate_azure_managed_lustre_node_compatibility(Mock(), cluster)
                client.assert_not_called()

    def test_os_aliases_use_regional_default_when_version_is_omitted(self):
        for os_sku, default_version, architecture, should_raise in [
            ("AzureLinux", "1.32", "arm64", True),
            ("AzureLinux", "1.32", "x64", False),
            ("AzureLinux", "1.31", "arm64", True),
            ("Ubuntu", "1.34", "arm64", True),
            (None, "1.34", "arm64", True),
            (None, "1.35", "arm64", False),
        ]:
            with self.subTest(os_sku=os_sku, default_version=default_version, architecture=architecture):
                cmd = Mock()
                cluster = SimpleNamespace(
                    location="eastus",
                    agent_pool_profiles=[SimpleNamespace(os_sku=os_sku, vm_size="Standard_D2ps_v5")],
                )
                with patch(VALIDATORS + ".cf_managed_clusters") as client, patch(
                    VALIDATORS + "._get_vm_sku_architectures",
                    return_value={"standard_d2ps_v5": architecture},
                ):
                    client.return_value.list_kubernetes_versions.return_value = SimpleNamespace(values_property=[
                        SimpleNamespace(version="1.36", is_default=False),
                        SimpleNamespace(version=default_version, is_default=True),
                    ])
                    if should_raise:
                        with self.assertRaisesRegex(InvalidArgumentValueError, "ARM64"):
                            validate_azure_managed_lustre_node_compatibility(cmd, cluster)
                    else:
                        validate_azure_managed_lustre_node_compatibility(cmd, cluster)
                    client.assert_called_once_with(cmd.cli_ctx)
                    client.return_value.list_kubernetes_versions.assert_called_once_with("eastus")
                self.assertFalse(hasattr(cluster, "kubernetes_version"))

    def test_unresolved_alias_version_is_not_treated_as_compatible(self):
        cluster = SimpleNamespace(
            location="eastus",
            agent_pool_profiles=[SimpleNamespace(os_sku="AzureLinux", vm_size="Standard_D2ps_v5")],
        )
        for versions in [
            None, [], [SimpleNamespace(version="1.34", is_default=False)],
            [SimpleNamespace(version=None, is_default=True)],
            [SimpleNamespace(version=version, is_default=True) for version in ["1.34", "1.35"]],
        ]:
            with self.subTest(versions=versions), patch(VALIDATORS + ".cf_managed_clusters") as client:
                client.return_value.list_kubernetes_versions.return_value = SimpleNamespace(values_property=versions)
                with self.assertRaisesRegex(InvalidArgumentValueError, "--kubernetes-version"):
                    validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_default_version_lookup_error_is_propagated(self):
        cluster = SimpleNamespace(
            location="eastus",
            agent_pool_profiles=[SimpleNamespace(os_sku="AzureLinux", vm_size="Standard_D2ps_v5")],
        )
        with patch(VALIDATORS + ".cf_managed_clusters") as client:
            client.return_value.list_kubernetes_versions.side_effect = HttpResponseError("Forbidden")
            with self.assertRaisesRegex(HttpResponseError, "Forbidden"):
                validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_default_version_is_looked_up_once_for_multiple_alias_pools(self):
        cluster = SimpleNamespace(
            location="eastus",
            agent_pool_profiles=[
                SimpleNamespace(os_sku=os_sku, vm_size="Standard_D2ps_v5")
                for os_sku in ["AzureLinux", None]
            ],
        )
        with patch(VALIDATORS + ".cf_managed_clusters") as client, patch(
            VALIDATORS + "._get_vm_sku_architectures", return_value={"standard_d2ps_v5": "arm64"},
        ):
            client.return_value.list_kubernetes_versions.return_value = SimpleNamespace(values_property=[
                SimpleNamespace(version="1.34", is_default=True),
            ])
            with self.assertRaisesRegex(InvalidArgumentValueError, "ARM64"):
                validate_azure_managed_lustre_node_compatibility(Mock(), cluster)
            client.return_value.list_kubernetes_versions.assert_called_once_with("eastus")

    def test_compatible_pool_is_sufficient_after_resolving_aliases(self):
        for os_sku in ["Ubuntu", None, "AzureLinux"]:
            with self.subTest(os_sku=os_sku):
                cluster = SimpleNamespace(
                    location="eastus", kubernetes_version="1.34",
                    agent_pool_profiles=[
                        SimpleNamespace(os_sku=os_sku, vm_size="Standard_D2ps_v5"),
                        SimpleNamespace(os_sku="Ubuntu2404", vm_size="Standard_D2ps_v5"),
                    ],
                )
                with patch(VALIDATORS + ".cf_managed_clusters") as client:
                    validate_azure_managed_lustre_node_compatibility(Mock(), cluster)
                client.assert_not_called()

    def test_invalid_alias_version_is_not_treated_as_compatible(self):
        for version in ["invalid", "1", "1.x"]:
            with self.subTest(version=version):
                cluster = SimpleNamespace(
                    location="eastus", kubernetes_version=version,
                    agent_pool_profiles=[SimpleNamespace(os_sku="AzureLinux", vm_size="Standard_D2ps_v5")],
                )
                with self.assertRaisesRegex(InvalidArgumentValueError, "Kubernetes version"):
                    validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_explicit_supported_linux_os_architecture_matrix(self):
        supported = {
            ("Ubuntu2004", "x64"), ("Ubuntu2204", "x64"),
            ("Ubuntu2404", "x64"), ("Ubuntu2404", "arm64"), ("AzureLinux3", "x64"),
        }
        for os_sku in [
            "Ubuntu2004", "Ubuntu2204", "Ubuntu2404", "AzureLinux3", "AzureLinux",
            "CBLMariner", "Mariner", "Flatcar", "Ubuntu2604", "Windows2022", "UnknownOS",
        ]:
            for architecture in ["x64", "arm64", "unknown", None]:
                with self.subTest(os_sku=os_sku, architecture=architecture):
                    cluster = SimpleNamespace(
                        location="eastus", kubernetes_version="1.31.9",
                        agent_pool_profiles=[SimpleNamespace(
                            os_sku=os_sku, os_type="Linux", vm_size="Standard_Test",
                        )],
                    )
                    with patch(
                        VALIDATORS + "._get_vm_sku_architectures",
                        return_value={"standard_test": architecture},
                    ):
                        if (os_sku, architecture) in supported:
                            validate_azure_managed_lustre_node_compatibility(Mock(), cluster)
                        else:
                            with self.assertRaises(InvalidArgumentValueError):
                                validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_unsupported_mixed_pools_do_not_count_as_compatible(self):
        for windows_sku in ["Windows2022", None, "Ubuntu2404"]:
            with self.subTest(windows_sku=windows_sku):
                cluster = SimpleNamespace(
                    location="eastus", kubernetes_version="1.34",
                    agent_pool_profiles=[
                        SimpleNamespace(os_sku="Ubuntu2204", os_type="Linux", vm_size="Standard_D2ps_v5"),
                        SimpleNamespace(os_sku=windows_sku, os_type="Windows", vm_size="Standard_D2s_v5"),
                    ],
                )
                with self.assertRaisesRegex(InvalidArgumentValueError, "none of the cluster's node pools"):
                    validate_azure_managed_lustre_node_compatibility(Mock(), cluster)
                cluster.agent_pool_profiles.append(SimpleNamespace(
                    os_sku="Ubuntu2404", os_type="Linux", vm_size="Standard_D2ps_v5",
                ))
                validate_azure_managed_lustre_node_compatibility(Mock(), cluster)

    def test_supported_pool_is_sufficient_when_another_architecture_is_unknown(self):
        cluster = SimpleNamespace(location="eastus", agent_pool_profiles=[
            SimpleNamespace(os_sku="Ubuntu2204", vm_size="Standard_Unknown"),
            SimpleNamespace(os_sku="Ubuntu2404", vm_size="Standard_D2ps_v5"),
        ])
        validate_azure_managed_lustre_node_compatibility(Mock(), cluster)


class AzureManagedLustreSkuPermissionsTestCase(unittest.TestCase):
    def test_resource_group_scoped_caller_denied_subscription_sku_read(self):
        response = Mock(status_code=403, headers={})
        errors = [ForbiddenError("AuthorizationFailed"), HttpResponseError("AuthorizationFailed", response=response)]
        for error in errors:
            with self.subTest(error=type(error).__name__), patch(
                "azure.cli.command_modules.vm.aaz.latest.vm.ListSkus",
            ) as command:
                def denied_page():
                    yield {"name": "Disk", "resourceType": "disks", "locations": ["eastus"]}
                    raise error

                command.return_value.return_value = denied_page()
                with self.assertRaisesRegex(ForbiddenError, "Microsoft.Compute/skus/read") as raised:
                    _get_vm_sku_architectures(Mock(), "eastus")
                self.assertIn("subscription scope", str(raised.exception))
                self.assertIn("CLI caller", str(raised.exception))
                self.assertIs(raised.exception.__cause__, error)

    def test_other_sku_service_errors_are_preserved(self):
        error = HttpResponseError("Service unavailable", response=Mock(status_code=503, headers={}))
        with patch("azure.cli.command_modules.vm.aaz.latest.vm.ListSkus") as command:
            command.return_value.side_effect = error
            with self.assertRaises(HttpResponseError) as raised:
                _get_vm_sku_architectures(Mock(), "eastus")
        self.assertIs(raised.exception, error)

    def test_sku_lookup_filters_region_and_normalizes_architecture(self):
        with patch("azure.cli.command_modules.vm.aaz.latest.vm.ListSkus") as command:
            command.return_value.return_value = [
                {"name": "Standard_Test", "resourceType": "virtualMachines", "locations": ["EastUS"],
                 "capabilities": [{"name": "CpuArchitectureType", "value": "Arm64"}]},
                {"name": "Other_Region", "resourceType": "virtualMachines", "locations": ["westus"],
                 "capabilities": [{"name": "CpuArchitectureType", "value": "x64"}]},
                {"name": "Disk", "resourceType": "disks", "locations": ["eastus"]},
            ]
            self.assertEqual(_get_vm_sku_architectures(Mock(), "eastus"), {"standard_test": "arm64"})


class AzureManagedLustreOperationsTestCase(unittest.TestCase):
    def setUp(self):
        self.cmd = Mock()
        self.client = Mock()
        self.custom = Mock()
        self.client_patch = patch(
            OPS + ".get_azure_managed_lustre_extension_client",
            return_value=(self.client, self.custom),
        )
        self.client_patch.start()
        self.addCleanup(self.client_patch.stop)
        self.waiter = Mock(return_value=SimpleNamespace(provisioning_state="Succeeded"))
        self.wait_patch = patch(OPS + ".LongRunningOperation", return_value=self.waiter)
        self.wait_patch.start()
        self.addCleanup(self.wait_patch.stop)

    def test_enable_uses_stable_release_without_pinned_version_or_automatic_upgrades(self):
        perform_enable_azure_managed_lustre(self.cmd, "rg", "cluster")
        self.custom.create_k8s_extension.assert_called_once_with(
            self.cmd, self.client, "rg", "cluster", "azurelustre", "managedClusters",
            "microsoft.azuremanagedlustre", release_train="stable",
            scope="cluster", auto_upgrade_minor_version=False,
        )
        self.waiter.assert_called_once_with(self.custom.create_k8s_extension.return_value)

    def test_enable_propagates_service_error_without_deleting_extension(self):
        self.custom.create_k8s_extension.side_effect = HttpResponseError("Forbidden")
        with self.assertRaisesRegex(HttpResponseError, "Forbidden"):
            perform_enable_azure_managed_lustre(self.cmd, "rg", "cluster")
        self.custom.delete_k8s_extension.assert_not_called()

    def test_enable_reports_unsuccessful_provisioning(self):
        for result in [None, SimpleNamespace(provisioning_state="Failed"),
                       SimpleNamespace(provisioning_state="Canceled")]:
            with self.subTest(result=result):
                self.waiter.return_value = result
                with self.assertRaisesRegex(UnknownError, "did not succeed"):
                    perform_enable_azure_managed_lustre(self.cmd, "rg", "cluster")

    def test_enable_propagates_polling_error(self):
        self.waiter.side_effect = HttpResponseError("Provisioning failed")
        with self.assertRaisesRegex(HttpResponseError, "Provisioning failed"):
            perform_enable_azure_managed_lustre(self.cmd, "rg", "cluster")

    def test_disable_waits_for_deletion(self):
        self.waiter.return_value = None
        with patch(OPS + ".logger") as logger:
            perform_disable_azure_managed_lustre(self.cmd, "rg", "cluster")
        warning = logger.warning.call_args_list[0].args[0]
        self.assertIn("safe teardown guidance", warning)
        self.assertIn("volumes may prevent driver removal", warning)
        completion = logger.warning.call_args_list[-1].args[0]
        self.assertIn("extension resource has been deleted", completion)
        self.assertIn("may be blocked by existing Lustre volumes", completion)
        self.assertIn("please verify completion in the cluster", completion)
        self.assertNotIn("has been disabled", completion)
        self.custom.delete_k8s_extension.assert_called_once_with(
            self.cmd, self.client, "rg", "cluster", "azurelustre", "managedClusters", yes=True
        )
        self.waiter.assert_called_once_with(self.custom.delete_k8s_extension.return_value)

    def test_disable_reports_failed_retrieval(self):
        self.custom.delete_k8s_extension.return_value = None
        with self.assertRaisesRegex(UnknownError, "could not be retrieved"):
            perform_disable_azure_managed_lustre(self.cmd, "rg", "cluster")
        self.waiter.assert_not_called()

    def test_disable_propagates_polling_error(self):
        self.waiter.side_effect = HttpResponseError("Deletion failed")
        with patch(OPS + ".logger") as logger, self.assertRaisesRegex(HttpResponseError, "Deletion failed"):
            perform_disable_azure_managed_lustre(self.cmd, "rg", "cluster")
        self.assertEqual(logger.warning.call_count, 1)

    def test_disable_propagates_service_rejection_without_completion_message(self):
        error = HttpResponseError("Extension deletion rejected: matching PersistentVolumes exist")
        self.custom.delete_k8s_extension.side_effect = error
        with patch(OPS + ".logger") as logger:
            with self.assertRaises(HttpResponseError) as raised:
                perform_disable_azure_managed_lustre(self.cmd, "rg", "cluster")
        self.assertIs(raised.exception, error)
        self.waiter.assert_not_called()
        self.assertEqual(logger.warning.call_count, 1)

    def test_disable_real_waiter_reports_failed_and_canceled_arm_operations(self):
        for state in ["Failed", "Canceled"]:
            with self.subTest(state=state):
                poller = Mock()
                poller.done.return_value = True
                poller.status.return_value = state
                error = HttpResponseError(f"{state}: extension deletion did not complete")
                poller.result.side_effect = error
                self.custom.delete_k8s_extension.return_value = poller
                with patch(OPS + ".LongRunningOperation", LongRunningOperation), patch(OPS + ".logger") as logger:
                    with self.assertRaises(HttpResponseError) as raised:
                        perform_disable_azure_managed_lustre(self.cmd, "rg", "cluster")
                self.assertIs(raised.exception, error)
                poller.result.assert_called_once_with()
                self.assertEqual(logger.warning.call_count, 1)

    def test_enable_and_disable_do_not_execute_kubernetes_tools_or_write_credentials(self):
        with patch("subprocess.Popen", side_effect=AssertionError("Must not execute Kubernetes tools")), \
                patch("tempfile.TemporaryDirectory", side_effect=AssertionError("Must not write kubeconfig")):
            perform_enable_azure_managed_lustre(self.cmd, "rg", "cluster")
            perform_disable_azure_managed_lustre(self.cmd, "rg", "cluster")
        self.assertEqual(self.custom.method_calls, [
            call.create_k8s_extension(
                self.cmd, self.client, "rg", "cluster", "azurelustre", "managedClusters",
                "microsoft.azuremanagedlustre", release_train="stable",
                scope="cluster", auto_upgrade_minor_version=False,
            ),
            call.delete_k8s_extension(
                self.cmd, self.client, "rg", "cluster", "azurelustre", "managedClusters", yes=True,
            ),
        ])


class AzureManagedLustreDecoratorTestCase(unittest.TestCase):
    def setUp(self):
        architecture_patch = patch(
            VALIDATORS + "._get_vm_sku_architectures", return_value={"standard_d2s_v5": "x64"},
        )
        self.architectures = architecture_patch.start()
        self.addCleanup(architecture_patch.stop)
        register_aks_preview_resource_type()
        self.cmd = MockCmd(MockCLI())
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = Mock()

    def make_decorator(self, create, **params):
        decorator_type = (
            AKSPreviewManagedClusterCreateDecorator if create else AKSPreviewManagedClusterUpdateDecorator
        )
        raw_params = {"resource_group_name": "rg", "name": "cluster"}
        raw_params.update(params)
        decorator = decorator_type(self.cmd, self.client, raw_params, CUSTOM_MGMT_AKS_PREVIEW)
        decorator.context.attach_mc(self.models.ManagedCluster(location="eastus"))
        decorator.context.mc.agent_pool_profiles = [
            self.models.ManagedClusterAgentPoolProfile(
                name="nodepool1", os_sku="Ubuntu2404", vm_size="Standard_D2s_v5"
            )
        ]
        decorator.context.set_intermediate("subscription_id", "test-subscription")
        return decorator

    def test_command_signatures_keep_feature_opt_in(self):
        for command in [aks_create, aks_update]:
            self.assertIs(inspect.signature(command).parameters["enable_azure_managed_lustre"].default, False)
        self.assertIs(inspect.signature(aks_update).parameters["disable_azure_managed_lustre"].default, False)
        self.assertNotIn("disable_azure_managed_lustre", inspect.signature(aks_create).parameters)

    def test_cli_arguments_are_registered(self):
        self.cmd.cli_ctx.local_context = Mock(is_on=False)
        for command_name in ["aks create", "aks update"]:
            with self.subTest(command=command_name):
                parser = AzCliCommandParser(cli_ctx=self.cmd.cli_ctx)
                self.cmd.cli_ctx.invocation = Mock(parser=parser, data={"command_string": command_name})
                loader = ContainerServiceCommandsLoader(self.cmd.cli_ctx)
                loader.load_command_table(command_name.split())
                command = loader.command_table[command_name]
                command.load_arguments()
                loader.load_arguments(command_name)
                loader._apply_parameter_info(command_name, command)  # pylint: disable=protected-access
                loader.command_table = {command_name: command}
                parser.load_command_table(loader)
                args = command_name.split() + ["--resource-group", "rg", "--name", "cluster"]
                enable = command.arguments["enable_azure_managed_lustre"]
                self.assertEqual(enable.options_list, ["--enable-azure-managed-lustre", "--enable-amlfs"])
                self.assertFalse(parser.parse_args(args).enable_azure_managed_lustre)
                for option in enable.options_list:
                    self.assertTrue(parser.parse_args(args + [option]).enable_azure_managed_lustre)
                if command_name == "aks update":
                    disable = command.arguments["disable_azure_managed_lustre"]
                    self.assertEqual(disable.options_list, ["--disable-azure-managed-lustre", "--disable-amlfs"])
                    self.assertFalse(parser.parse_args(args).disable_azure_managed_lustre)
                    for option in disable.options_list:
                        self.assertTrue(parser.parse_args(args + [option]).disable_azure_managed_lustre)
                else:
                    self.assertNotIn("disable_azure_managed_lustre", command.arguments)

    def test_external_functions(self):
        decorator = self.make_decorator(True)
        functions = decorator.context.external_functions
        self.assertIs(functions.perform_enable_azure_managed_lustre, perform_enable_azure_managed_lustre)
        self.assertIs(functions.perform_disable_azure_managed_lustre, perform_disable_azure_managed_lustre)

    def test_create_preflights_dependency_without_installing(self):
        decorator = self.make_decorator(True, enable_azure_managed_lustre=True)
        mc = decorator.context.mc
        with patch(DECORATOR + ".get_azure_managed_lustre_extension_client") as dependency:
            self.assertIs(decorator.set_up_azure_managed_lustre(mc), mc)
        dependency.assert_called_once_with(self.cmd)
        self.assertTrue(decorator.context.get_intermediate("enable_azure_managed_lustre"))
        self.assertTrue(decorator.check_is_postprocessing_required(mc))

    def test_create_missing_dependency_fails_before_cluster_request(self):
        decorator = self.make_decorator(True, enable_azure_managed_lustre=True)
        with patch(DECORATOR + ".get_azure_managed_lustre_extension_client",
                   side_effect=UnknownError("Install k8s-extension")):
            with self.assertRaisesRegex(UnknownError, "Install k8s-extension"):
                decorator.set_up_azure_managed_lustre(decorator.context.mc)
        self.client.begin_create_or_update.assert_not_called()

    def test_create_rejects_unsupported_aliases_before_cluster_request(self):
        for os_sku, version in [
            ("Ubuntu", "1.34.0"), (None, "1.34.0"), ("AzureLinux", None), (None, None),
        ]:
            with self.subTest(os_sku=os_sku, version=version):
                decorator = self.make_decorator(True, enable_azure_managed_lustre=True)
                mc = decorator.context.mc
                mc.kubernetes_version = version
                mc.agent_pool_profiles[0].os_sku = os_sku
                mc.agent_pool_profiles[0].vm_size = "Standard_D2ps_v5"
                with patch(VALIDATORS + ".cf_managed_clusters") as client, patch(
                    VALIDATORS + "._get_vm_sku_architectures", return_value={"standard_d2ps_v5": "arm64"},
                ), patch(DECORATOR + ".get_azure_managed_lustre_extension_client") as dependency:
                    client.return_value.list_kubernetes_versions.return_value = SimpleNamespace(values_property=[
                        SimpleNamespace(version="1.34", is_default=True),
                    ])
                    with self.assertRaisesRegex(InvalidArgumentValueError, "ARM64"):
                        decorator.set_up_azure_managed_lustre(mc)
                dependency.assert_not_called()
                self.client.begin_create_or_update.assert_not_called()
                self.assertFalse(decorator.context.get_intermediate(
                    "enable_azure_managed_lustre", default_value=False,
                ))

    def test_update_checks_pool_configuration_with_compute_sku_discovery(self):
        decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
        mc = decorator.context.mc
        mc.kubernetes_version = "1.34.0"
        mc.agent_pool_profiles[0].os_sku = "Ubuntu"
        mc.agent_pool_profiles[0].vm_size = "Standard_D2ps_v5"
        self.architectures.return_value = {"standard_d2ps_v5": "arm64"}
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension", return_value=None):
            with self.assertRaisesRegex(InvalidArgumentValueError, "ARM64"):
                decorator.update_azure_managed_lustre(mc)
            mc.agent_pool_profiles[0].os_sku = "Ubuntu2404"
            self.assertIs(decorator.update_azure_managed_lustre(mc), mc)
        self.architectures.assert_called_with(self.cmd.cli_ctx, "eastus")
        self.assertEqual(self.architectures.call_count, 2)
        self.client.begin_create_or_update.assert_not_called()

    def test_update_validates_scaled_to_zero_pool_without_cluster_credentials(self):
        decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
        mc = decorator.context.mc
        mc.agent_pool_profiles[0].count = 0
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension", return_value=None), \
                patch(VALIDATORS + ".cf_managed_clusters") as cluster_client, \
                patch("subprocess.Popen", side_effect=AssertionError("Must not execute Kubernetes tools")), \
                patch("tempfile.TemporaryDirectory", side_effect=AssertionError("Must not write kubeconfig")):
            self.assertIs(decorator.update_azure_managed_lustre(mc), mc)
        cluster_client.assert_not_called()
        self.architectures.assert_called_once_with(self.cmd.cli_ctx, "eastus")
        self.assertTrue(decorator.context.get_intermediate("enable_azure_managed_lustre"))

    def test_omitted_flags_do_not_load_extension_or_request_postprocessing(self):
        for create in [True, False]:
            with self.subTest(create=create):
                decorator = self.make_decorator(create)
                mc = decorator.context.mc
                with patch(DECORATOR + ".get_azure_managed_lustre_extension_client") as dependency, \
                        patch(DECORATOR + ".get_installed_azure_managed_lustre_extension") as installed:
                    setup = decorator.set_up_azure_managed_lustre if create else decorator.update_azure_managed_lustre
                    self.assertIs(setup(mc), mc)
                dependency.assert_not_called()
                installed.assert_not_called()
                self.architectures.assert_not_called()
                self.assertFalse(decorator.check_is_postprocessing_required(mc))

    def test_update_rejects_conflicting_flags_before_lookup(self):
        decorator = self.make_decorator(
            False, enable_azure_managed_lustre=True, disable_azure_managed_lustre=True
        )
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension") as installed:
            with self.assertRaises(MutuallyExclusiveArgumentError):
                decorator.update_azure_managed_lustre(decorator.context.mc)
        installed.assert_not_called()

    def test_update_rejects_disable_when_not_installed(self):
        decorator = self.make_decorator(False, disable_azure_managed_lustre=True)
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension", return_value=None):
            with self.assertRaisesRegex(InvalidArgumentValueError, "resource was not found"):
                decorator.update_azure_managed_lustre(decorator.context.mc)

    def test_update_propagates_lookup_errors_before_cluster_request(self):
        decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension",
                   side_effect=HttpResponseError("Forbidden")):
            with self.assertRaisesRegex(HttpResponseError, "Forbidden"):
                decorator.update_azure_managed_lustre(decorator.context.mc)
        self.client.begin_create_or_update.assert_not_called()

    def test_create_warns_and_continues_when_sku_permission_is_missing(self):
        for error in [
            ForbiddenError("AuthorizationFailed"),
            HttpResponseError("AuthorizationFailed", response=Mock(status_code=403, headers={})),
        ]:
            with self.subTest(error=type(error).__name__):
                decorator = self.make_decorator(True, enable_azure_managed_lustre=True)
                with patch(DECORATOR + ".get_azure_managed_lustre_extension_client") as dependency, \
                        patch(VALIDATORS + "._get_vm_sku_architectures", wraps=_get_vm_sku_architectures), \
                        patch("azure.cli.command_modules.vm.aaz.latest.vm.ListSkus") as command, \
                        patch(VALIDATORS + ".logger.warning") as warning:
                    command.return_value.side_effect = error
                    mc = decorator.context.mc
                    self.assertIs(decorator.set_up_azure_managed_lustre(mc), mc)
                warning.assert_called_once()
                self.assertIn("Architecture compatibility", warning.call_args.args[0])
                self.assertIn("cannot be verified", warning.call_args.args[0])
                self.assertIn("Microsoft.Compute/skus/read", warning.call_args.args[0])
                self.assertIn("Continuing without architecture validation", warning.call_args.args[0])
                dependency.assert_called_once_with(self.cmd)
                self.assertTrue(decorator.context.get_intermediate("enable_azure_managed_lustre"))
                self.assertTrue(decorator.check_is_postprocessing_required(mc))

    def test_create_does_not_skip_os_validation_when_sku_permission_is_missing(self):
        decorator = self.make_decorator(True, enable_azure_managed_lustre=True)
        mc = decorator.context.mc
        mc.agent_pool_profiles[0].os_sku = "AzureLinux"
        mc.kubernetes_version = "1.31"
        self.architectures.side_effect = ForbiddenError("AuthorizationFailed")
        with self.assertRaisesRegex(InvalidArgumentValueError, "none of the cluster's node pools"):
            decorator.set_up_azure_managed_lustre(mc)
        self.architectures.assert_not_called()
        self.client.begin_create_or_update.assert_not_called()

    def test_create_does_not_suppress_other_sku_errors(self):
        for status in [401, 429, 503]:
            with self.subTest(status=status):
                decorator = self.make_decorator(True, enable_azure_managed_lustre=True)
                with patch(VALIDATORS + "._get_vm_sku_architectures", wraps=_get_vm_sku_architectures), \
                        patch("azure.cli.command_modules.vm.aaz.latest.vm.ListSkus") as command, \
                        patch(VALIDATORS + ".logger.warning") as warning:
                    error = HttpResponseError("Service error", response=Mock(status_code=status, headers={}))
                    command.return_value.side_effect = error
                    with self.assertRaises(HttpResponseError) as raised:
                        decorator.set_up_azure_managed_lustre(decorator.context.mc)
                self.assertIs(raised.exception, error)
                warning.assert_not_called()
                self.assertFalse(decorator.context.get_intermediate(
                    "enable_azure_managed_lustre", default_value=False,
                ))
        self.client.begin_create_or_update.assert_not_called()

    def test_update_warns_and_continues_when_sku_permission_is_missing(self):
        decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
        self.architectures.side_effect = ForbiddenError("AuthorizationFailed")
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension", return_value=None), \
                patch(VALIDATORS + ".logger.warning") as warning:
            decorator.update_azure_managed_lustre(decorator.context.mc)
        self.architectures.assert_called_once_with(self.cmd.cli_ctx, "eastus")
        warning.assert_called_once()
        self.assertIn("cannot be verified", warning.call_args.args[0])
        self.assertIn("Microsoft.Compute/skus/read", warning.call_args.args[0])
        self.assertTrue(decorator.context.get_intermediate("enable_azure_managed_lustre"))

    def test_update_sku_service_failure_blocks_enable_before_mutation(self):
        decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
        self.architectures.side_effect = HttpResponseError("SKU service unavailable")
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension", return_value=None):
            with self.assertRaisesRegex(HttpResponseError, "SKU service unavailable"):
                decorator.update_azure_managed_lustre(decorator.context.mc)
        self.architectures.assert_called_once_with(self.cmd.cli_ctx, "eastus")
        self.client.begin_create_or_update.assert_not_called()
        self.assertFalse(decorator.context.get_intermediate("enable_azure_managed_lustre", default_value=False))

    def test_update_prepares_enable_and_disable(self):
        for enable, installed in [(True, False), (False, True)]:
            with self.subTest(enable=enable, installed=installed):
                decorator = self.make_decorator(
                    False, enable_azure_managed_lustre=enable, disable_azure_managed_lustre=not enable
                )
                mc = decorator.context.mc
                extension = SimpleNamespace(provisioning_state="Succeeded") if installed else None
                with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension",
                           return_value=extension) as lookup:
                    self.assertIs(decorator.update_azure_managed_lustre(mc), mc)
                lookup.assert_called_once_with(self.cmd, "rg", "cluster")
                self.assertEqual(decorator.context.get_intermediate("enable_azure_managed_lustre"), enable)
                self.assertEqual(decorator.context.get_intermediate("disable_azure_managed_lustre"), not enable)
                self.assertTrue(decorator.check_is_postprocessing_required(mc))
        self.architectures.assert_called_once_with(self.cmd.cli_ctx, "eastus")

    def test_update_preserves_existing_extension_configuration(self):
        decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
        mc = decorator.context.mc
        extension = SimpleNamespace(provisioning_state="Succeeded")
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension", return_value=extension), \
                patch(DECORATOR + ".validate_azure_managed_lustre_node_compatibility") as validate:
            self.assertIs(decorator.update_azure_managed_lustre(mc), mc)
        validate.assert_not_called()
        self.architectures.assert_not_called()
        self.assertFalse(decorator.context.get_intermediate("enable_azure_managed_lustre"))
        self.assertFalse(decorator.check_is_postprocessing_required(mc))

    def test_update_rejects_unsuccessful_existing_extension(self):
        for provisioning_state in ["Failed", "Canceled", "Creating", "Updating", "Deleting", None]:
            with self.subTest(provisioning_state=provisioning_state):
                decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
                extension = SimpleNamespace(
                    provisioning_state=provisioning_state,
                    configuration_settings={"node.tolerations": "custom"},
                )
                with patch(
                    DECORATOR + ".get_installed_azure_managed_lustre_extension", return_value=extension
                ):
                    with self.assertRaisesRegex(
                        InvalidArgumentValueError, provisioning_state or "Unknown",
                    ) as raised:
                        decorator.update_azure_managed_lustre(decorator.context.mc)
                self.assertIn("az k8s-extension show", str(raised.exception))
                self.assertIn("wait for it to finish", str(raised.exception))
                self.assertIn("preserving existing volumes and configuration", str(raised.exception))
                self.assertNotIn("again to recover", str(raised.exception))
                self.assertEqual(extension.configuration_settings, {"node.tolerations": "custom"})
                self.client.begin_create_or_update.assert_not_called()
                self.assertFalse(decorator.check_is_postprocessing_required(decorator.context.mc))

    def test_postprocessing_performs_requested_operation(self):
        for create, enable in [(True, True), (False, True), (False, False)]:
            with self.subTest(create=create, enable=enable):
                decorator = self.make_decorator(create)
                operation = "enable" if enable else "disable"
                decorator.context.set_intermediate(operation + "_azure_managed_lustre", True)
                functions = decorator.context.external_functions
                with patch.object(functions, "perform_enable_azure_managed_lustre") as install, \
                        patch.object(functions, "perform_disable_azure_managed_lustre") as uninstall, \
                        patch("azure.cli.command_modules.acs.managed_cluster_decorator."
                              "AKSManagedClusterUpdateDecorator.postprocessing_after_mc_created"):
                    decorator.postprocessing_after_mc_created(decorator.context.mc)
                (install if enable else uninstall).assert_called_once_with(self.cmd, "rg", "cluster")
                (uninstall if enable else install).assert_not_called()

    def test_create_installs_lustre_before_container_storage_early_return(self):
        decorator = self.make_decorator(True)
        decorator.context.set_intermediate("enable_azure_managed_lustre", True)
        decorator.context.set_intermediate("enable_azure_container_storage", "ephemeralDisk")
        decorator.context.set_intermediate("container_storage_version", "1")
        functions = decorator.context.external_functions
        with patch.object(functions, "perform_enable_azure_managed_lustre") as install, \
                patch("azure.cli.command_modules.acs.managed_cluster_decorator."
                      "AKSManagedClusterUpdateDecorator.postprocessing_after_mc_created"):
            decorator.postprocessing_after_mc_created(decorator.context.mc)
        install.assert_called_once_with(self.cmd, "rg", "cluster")

    def test_put_waits_for_cluster_before_lustre_even_with_no_wait(self):
        for create in [True, False]:
            with self.subTest(create=create):
                decorator = self.make_decorator(create, no_wait=True)
                decorator.context.set_intermediate("enable_azure_managed_lustre", True)
                mc = decorator.context.mc
                events = []
                cluster = self.models.ManagedCluster(location="eastus")

                def wait_for_cluster(poller):
                    self.assertIs(poller, self.client.begin_create_or_update.return_value)
                    events.append("cluster-ready")
                    return cluster

                def install(cmd, resource_group, cluster_name):
                    self.assertEqual(events, ["cluster-ready"])
                    events.append("extension-installed")

                with patch(DECORATOR + ".LongRunningOperation", return_value=wait_for_cluster), \
                        patch.object(decorator, "immediate_processing_after_request"), \
                        patch.object(decorator.context.external_functions, "perform_enable_azure_managed_lustre",
                                     side_effect=install), \
                        patch("azure.cli.command_modules.acs.managed_cluster_decorator."
                              "AKSManagedClusterUpdateDecorator.postprocessing_after_mc_created"):
                    self.assertIs(decorator.put_mc(mc), cluster)
                self.assertEqual(events, ["cluster-ready", "extension-installed"])
