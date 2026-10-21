# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from azure.core.exceptions import HttpResponseError
from azure.cli.core.parser import AzCliCommandParser
from azure.cli.core.azclierror import (
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
    def test_conflicting_flags(self):
        with self.assertRaises(MutuallyExclusiveArgumentError):
            validate_azure_managed_lustre_params(True, True)

    def test_disable_requires_installed_extension(self):
        with self.assertRaisesRegex(InvalidArgumentValueError, "not enabled"):
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
        for kubernetes_version, should_raise in [("1.31.9", False), ("1.32.0", True)]:
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
            ("Ubuntu", "1.24.9", None, "arm64", False),
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
            ("AzureLinux", "1.31", "arm64", False),
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
        perform_disable_azure_managed_lustre(self.cmd, "rg", "cluster")
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
        with self.assertRaisesRegex(HttpResponseError, "Deletion failed"):
            perform_disable_azure_managed_lustre(self.cmd, "rg", "cluster")


class AzureManagedLustreDecoratorTestCase(unittest.TestCase):
    def setUp(self):
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

    def test_update_rejects_ubuntu_alias_on_arm64(self):
        decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
        mc = decorator.context.mc
        mc.kubernetes_version = "1.34.0"
        mc.agent_pool_profiles[0].os_sku = "Ubuntu"
        mc.agent_pool_profiles[0].vm_size = "Standard_D2ps_v5"
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension", return_value=None), patch(
            VALIDATORS + "._get_vm_sku_architectures", return_value={"standard_d2ps_v5": "arm64"},
        ):
            with self.assertRaisesRegex(InvalidArgumentValueError, "ARM64"):
                decorator.update_azure_managed_lustre(mc)
        self.client.begin_create_or_update.assert_not_called()

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
            with self.assertRaisesRegex(InvalidArgumentValueError, "not enabled"):
                decorator.update_azure_managed_lustre(decorator.context.mc)

    def test_update_propagates_lookup_errors_before_cluster_request(self):
        decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension",
                   side_effect=HttpResponseError("Forbidden")):
            with self.assertRaisesRegex(HttpResponseError, "Forbidden"):
                decorator.update_azure_managed_lustre(decorator.context.mc)
        self.client.begin_create_or_update.assert_not_called()

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

    def test_update_preserves_existing_extension_configuration(self):
        decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
        mc = decorator.context.mc
        extension = SimpleNamespace(provisioning_state="Succeeded")
        with patch(DECORATOR + ".get_installed_azure_managed_lustre_extension", return_value=extension), \
                patch(DECORATOR + ".validate_azure_managed_lustre_node_compatibility") as validate:
            self.assertIs(decorator.update_azure_managed_lustre(mc), mc)
        validate.assert_not_called()
        self.assertFalse(decorator.context.get_intermediate("enable_azure_managed_lustre"))
        self.assertFalse(decorator.check_is_postprocessing_required(mc))

    def test_update_rejects_unsuccessful_existing_extension(self):
        for provisioning_state in ["Failed", "Canceled"]:
            with self.subTest(provisioning_state=provisioning_state):
                decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
                extension = SimpleNamespace(provisioning_state=provisioning_state)
                with patch(
                    DECORATOR + ".get_installed_azure_managed_lustre_extension", return_value=extension
                ):
                    with self.assertRaisesRegex(InvalidArgumentValueError, provisioning_state):
                        decorator.update_azure_managed_lustre(decorator.context.mc)
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
