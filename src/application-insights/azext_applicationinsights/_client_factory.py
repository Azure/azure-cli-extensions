# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def applicationinsights_data_plane_client(cli_ctx, _):
    """Initialize Log Analytics data client for use with CLI."""
    from .vendored_sdks.applicationinsights import ApplicationInsightsDataClient
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cli_ctx)
    cred, _, _ = profile.get_login_credentials(
        resource="https://api.applicationinsights.io")
    return ApplicationInsightsDataClient(cred)

def applicationinsights_mgmt_plane_client(cli_ctx, _):
    """Initialize Log Analytics data client for use with CLI."""
    from azure.cli.core.commands.client_factory import get_subscription_id
    from .vendored_sdks.mgmt_applicationinsights import ApplicationInsightsManagementClient
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cli_ctx)
    cred, _, _ = profile.get_login_credentials()
    return ApplicationInsightsManagementClient(
        cred,
        get_subscription_id(cli_ctx)    
    )

def cf_query(cli_ctx, _):
    return applicationinsights_data_plane_client(cli_ctx, _).query


def cf_metrics(cli_ctx, _):
    return applicationinsights_data_plane_client(cli_ctx, _).metrics


def cf_events(cli_ctx, _):
    return applicationinsights_data_plane_client(cli_ctx, _).events


def cf_components(cli_ctx, _):
    return applicationinsights_mgmt_plane_client(cli_ctx, _).components
