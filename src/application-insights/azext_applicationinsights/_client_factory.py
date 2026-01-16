# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def applicationinsights_mgmt_plane_client(cli_ctx, **kwargs):
    """Initialize Log Analytics mgmt client for use with CLI."""
    from .vendored_sdks.mgmt_applicationinsights import ApplicationInsightsManagementClient
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx, ApplicationInsightsManagementClient, **kwargs)


def cf_components(cli_ctx, _):
    return applicationinsights_mgmt_plane_client(cli_ctx, api_version='2018-05-01-preview').components


def cf_api_key(cli_ctx, _):
    return applicationinsights_mgmt_plane_client(cli_ctx).api_keys


def cf_export_configuration(cli_ctx, _):
    return applicationinsights_mgmt_plane_client(cli_ctx).export_configurations


def cf_web_test(cli_ctx, _):
    return applicationinsights_mgmt_plane_client(cli_ctx, api_version='2022-06-15').web_tests
