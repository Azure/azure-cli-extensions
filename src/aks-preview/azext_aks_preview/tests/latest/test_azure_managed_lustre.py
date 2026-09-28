# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

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
from azext_aks_preview.azuremanagedlustre._validators import validate_azure_managed_lustre_params
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

    def test_enable_matches_requested_installation(self):
        perform_enable_azure_managed_lustre(self.cmd, "rg", "cluster")
        self.custom.create_k8s_extension.assert_called_once_with(
            self.cmd, self.client, "rg", "cluster", "azurelustre", "managedClusters",
            "microsoft.azuremanagedlustre", version="0.6.0", release_train="stable",
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
                self.assertEqual(enable.options_list, ["--enable-azure-managed-lustre"])
                self.assertFalse(parser.parse_args(args).enable_azure_managed_lustre)
                self.assertTrue(parser.parse_args(args + enable.options_list).enable_azure_managed_lustre)
                if command_name == "aks update":
                    disable = command.arguments["disable_azure_managed_lustre"]
                    self.assertEqual(disable.options_list, ["--disable-azure-managed-lustre"])
                    self.assertFalse(parser.parse_args(args).disable_azure_managed_lustre)
                    self.assertTrue(parser.parse_args(args + disable.options_list).disable_azure_managed_lustre)
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

    def test_omitted_flags_do_not_load_extension_or_request_postprocessing(self):
        for create in [True, False]:
            with self.subTest(create=create):
                decorator = self.make_decorator(create)
                mc = decorator.context.mc
                with patch(DECORATOR + ".get_azure_managed_lustre_extension_client") as dependency, \
                        patch(DECORATOR + ".check_if_azure_managed_lustre_is_installed") as installed:
                    setup = decorator.set_up_azure_managed_lustre if create else decorator.update_azure_managed_lustre
                    self.assertIs(setup(mc), mc)
                dependency.assert_not_called()
                installed.assert_not_called()
                self.assertFalse(decorator.check_is_postprocessing_required(mc))

    def test_update_rejects_conflicting_flags_before_lookup(self):
        decorator = self.make_decorator(
            False, enable_azure_managed_lustre=True, disable_azure_managed_lustre=True
        )
        with patch(DECORATOR + ".check_if_azure_managed_lustre_is_installed") as installed:
            with self.assertRaises(MutuallyExclusiveArgumentError):
                decorator.update_azure_managed_lustre(decorator.context.mc)
        installed.assert_not_called()

    def test_update_rejects_disable_when_not_installed(self):
        decorator = self.make_decorator(False, disable_azure_managed_lustre=True)
        with patch(DECORATOR + ".check_if_azure_managed_lustre_is_installed", return_value=False):
            with self.assertRaisesRegex(InvalidArgumentValueError, "not enabled"):
                decorator.update_azure_managed_lustre(decorator.context.mc)

    def test_update_propagates_lookup_errors_before_cluster_request(self):
        decorator = self.make_decorator(False, enable_azure_managed_lustre=True)
        with patch(DECORATOR + ".check_if_azure_managed_lustre_is_installed",
                   side_effect=HttpResponseError("Forbidden")):
            with self.assertRaisesRegex(HttpResponseError, "Forbidden"):
                decorator.update_azure_managed_lustre(decorator.context.mc)
        self.client.begin_create_or_update.assert_not_called()

    def test_update_prepares_enable_and_disable(self):
        for enable, installed in [(True, False), (True, True), (False, True)]:
            with self.subTest(enable=enable, installed=installed):
                decorator = self.make_decorator(
                    False, enable_azure_managed_lustre=enable, disable_azure_managed_lustre=not enable
                )
                mc = decorator.context.mc
                with patch(DECORATOR + ".check_if_azure_managed_lustre_is_installed",
                           return_value=installed) as lookup:
                    self.assertIs(decorator.update_azure_managed_lustre(mc), mc)
                lookup.assert_called_once_with(self.cmd, "rg", "cluster")
                self.assertEqual(decorator.context.get_intermediate("enable_azure_managed_lustre"), enable)
                self.assertEqual(decorator.context.get_intermediate("disable_azure_managed_lustre"), not enable)
                self.assertTrue(decorator.check_is_postprocessing_required(mc))

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
