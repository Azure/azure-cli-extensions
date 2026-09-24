# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

logger = get_logger(__name__)


def create_devops_pipeline(
        cmd,
        functionapp_name=None,
        organization_name=None,
        project_name=None,
        repository_name=None,
        overwrite_yaml=None,
        allow_force_push=None,
        github_pat=None,
        github_repository=None
):
    from .azure_devops_build_interactive import AzureDevopsBuildInteractive
    azure_devops_build_interactive = AzureDevopsBuildInteractive(cmd, logger, functionapp_name,
                                                                 organization_name, project_name, repository_name,
                                                                 overwrite_yaml, allow_force_push,
                                                                 github_pat, github_repository)
    return azure_devops_build_interactive.interactive_azure_devops_build()


def delete_always_ready_settings(cmd, resource_group_name, name, setting_names):
    import json
    from azure.cli.core.util import send_raw_request
    from azure.cli.core.commands.client_factory import get_subscription_id

    subscription_id = get_subscription_id(cmd.cli_ctx)
    api_version = '2023-12-01'
    site_url_base = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}?api-version={}'
    site_url = site_url_base.format(subscription_id, resource_group_name, name, api_version)
    request_url = cmd.cli_ctx.cloud.endpoints.resource_manager + site_url

    response = send_raw_request(cmd.cli_ctx, "GET", request_url)
    functionapp = response.json()

    always_ready_config = (functionapp.get("properties", {})
                           .get("functionAppConfig", {})
                           .get("scaleAndConcurrency", {})
                           .get("alwaysReady", []))

    # Use case-insensitive comparison: Azure Functions names are case-insensitive,
    # and the ARM API may normalize names (e.g. to lowercase) on storage.
    setting_names_lower = {n.lower() for n in setting_names}
    updated_always_ready_config = [
        x for x in always_ready_config
        if x.get("name", "").lower() not in setting_names_lower
    ]

    (functionapp.setdefault("properties", {})
                .setdefault("functionAppConfig", {})
                .setdefault("scaleAndConcurrency", {})["alwaysReady"]) = updated_always_ready_config

    body = json.dumps(functionapp)
    result_response = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=body)
    result = result_response.json()

    return (result.get("properties", {})
            .get("functionAppConfig", {})
            .get("scaleAndConcurrency", {}))
