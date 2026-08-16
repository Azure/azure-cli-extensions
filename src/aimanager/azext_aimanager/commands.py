# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_aimanager._client_factory import (
    cf_ai_managers,
    cf_ai_manager_namespaces,
    cf_model_deployments,
)


def load_command_table(self, _):

    ai_managers_sdk = CliCommandType(
        operations_tmpl="azext_aimanager.vendored_sdks.v2026_05_02_preview.operations._operations#AIManagersOperations.{}",
        operation_group="ai_managers",
        client_factory=cf_ai_managers
    )

    ai_manager_namespaces_sdk = CliCommandType(
        operations_tmpl="azext_aimanager.vendored_sdks.v2026_05_02_preview.operations._operations#AIManagerNamespacesOperations.{}",
        operation_group="ai_manager_namespaces",
        client_factory=cf_ai_manager_namespaces
    )

    model_deployments_sdk = CliCommandType(
        operations_tmpl="azext_aimanager.vendored_sdks.v2026_05_02_preview.operations._operations#ModelDeploymentsOperations.{}",
        operation_group="model_deployments",
        client_factory=cf_model_deployments
    )

    # aimanager command group
    with self.command_group("aimanager", ai_managers_sdk, client_factory=cf_ai_managers) as g:
        g.custom_command("create", "create_aimanager", supports_no_wait=True)
        g.custom_command("update", "update_aimanager", supports_no_wait=True)
        g.custom_show_command("show", "show_aimanager")
        g.custom_command("list", "list_aimanager")
        g.custom_command("delete", "delete_aimanager", supports_no_wait=True, confirmation=True)
        g.custom_command("get-credentials", "aimanager_get_credentials")
        g.wait_command("wait")

    # aimanager namespace command group
    with self.command_group("aimanager namespace", ai_manager_namespaces_sdk, client_factory=cf_ai_manager_namespaces) as g:
        g.custom_command("add", "add_aimanager_namespace", supports_no_wait=True)
        g.custom_command("update", "update_aimanager_namespace", supports_no_wait=True)
        g.custom_show_command("show", "show_aimanager_namespace")
        g.custom_command("list", "list_aimanager_namespace")
        g.custom_command("delete", "delete_aimanager_namespace", supports_no_wait=True, confirmation=True)
        g.custom_command("get-credentials", "aimanager_namespace_get_credentials")
        g.wait_command("wait")

    # aimanager namespace modeldeployment command group
    with self.command_group("aimanager namespace modeldeployment", model_deployments_sdk,
                            client_factory=cf_model_deployments) as g:
        g.custom_command("add", "add_modeldeployment", supports_no_wait=True)
        g.custom_command("update", "update_modeldeployment", supports_no_wait=True)
        g.custom_show_command("show", "show_modeldeployment")
        g.custom_command("list", "list_modeldeployment")
        g.custom_command("delete", "delete_modeldeployment", supports_no_wait=True, confirmation=True)
        g.custom_wait_command("wait", "show_modeldeployment")
