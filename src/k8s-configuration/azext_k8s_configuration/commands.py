# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_k8s_configuration._client_factory import (
    k8s_configuration_fluxconfig_client,
    k8s_configuration_sourcecontrol_client,
)
from .format import (
    fluxconfig_deployed_object_list_table_format,
    fluxconfig_deployed_object_show_table_format,
    fluxconfig_list_table_format,
    fluxconfig_show_table_format,
    fluxconfig_kustomization_list_table_format,
    fluxconfig_kustomization_show_table_format,
    sourcecontrol_list_table_format,
    sourcecontrol_show_table_format,
)


def load_command_table(self, _):
    flux_configuration_custom_type = CliCommandType(
        operations_tmpl="azext_k8s_configuration.providers.FluxConfigurationProvider#{}",
        client_factory=k8s_configuration_fluxconfig_client,
    )

    source_control_configuration_custom_type = CliCommandType(
        operations_tmpl="azext_k8s_configuration.providers.SourceControlConfigurationProvider#{}",
        client_factory=k8s_configuration_sourcecontrol_client,
    )

    with self.command_group(
        "k8s-configuration flux",
        k8s_configuration_fluxconfig_client,
        custom_command_type=flux_configuration_custom_type,
    ) as g:
        g.custom_command("create", "create_config", supports_no_wait=True)
        g.custom_command("update", "update_config", supports_no_wait=True)
        g.custom_command(
            "list", "list_configs", table_transformer=fluxconfig_list_table_format
        )
        g.custom_show_command(
            "show", "show_config", table_transformer=fluxconfig_show_table_format
        )
        g.custom_command("delete", "delete_config", supports_no_wait=True)

    with self.command_group(
        "k8s-configuration flux kustomization",
        k8s_configuration_fluxconfig_client,
        custom_command_type=flux_configuration_custom_type,
    ) as g:
        g.custom_command("create", "create_kustomization", supports_no_wait=True)
        g.custom_command("update", "update_kustomization", supports_no_wait=True)
        g.custom_command("delete", "delete_kustomization", supports_no_wait=True)
        g.custom_command(
            "list",
            "list_kustomization",
            table_transformer=fluxconfig_kustomization_list_table_format,
        )
        g.custom_show_command(
            "show",
            "show_kustomization",
            table_transformer=fluxconfig_kustomization_show_table_format,
        )

    with self.command_group(
        "k8s-configuration flux deployed-object",
        k8s_configuration_fluxconfig_client,
        custom_command_type=flux_configuration_custom_type,
    ) as g:
        g.custom_command(
            "list",
            "list_deployed_object",
            table_transformer=fluxconfig_deployed_object_list_table_format,
        )
        g.custom_show_command(
            "show",
            "show_deployed_object",
            table_transformer=fluxconfig_deployed_object_show_table_format,
        )

    with self.command_group(
        "k8s-configuration",
        k8s_configuration_sourcecontrol_client,
        custom_command_type=source_control_configuration_custom_type,
    ) as g:
        g.custom_command(
            "create",
            "create_config",
            deprecate_info=self.deprecate(redirect="k8s-configuration flux create"),
        )
        g.custom_command(
            "list",
            "list_configs",
            table_transformer=sourcecontrol_list_table_format,
            deprecate_info=self.deprecate(redirect="k8s-configuration flux list"),
        )
        g.custom_show_command(
            "show",
            "show_config",
            table_transformer=sourcecontrol_show_table_format,
            deprecate_info=self.deprecate(redirect="k8s-configuration flux show"),
        )
        g.custom_command(
            "delete",
            "delete_config",
            confirmation=True,
            deprecate_info=self.deprecate(redirect="k8s-configuration flux delete"),
        )
