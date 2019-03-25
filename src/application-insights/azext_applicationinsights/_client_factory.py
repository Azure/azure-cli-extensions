# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def applicationinsights_data_plane_client(cli_ctx, _, subscription=None):
    """Initialize Log Analytics data client for use with CLI."""
    from .vendored_sdks.applicationinsights import ApplicationInsightsDataClient
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cli_ctx)
    cred, _, _ = profile.get_login_credentials(
        resource="https://api.applicationinsights.io",
        subscription_id=subscription
    )
    return ApplicationInsightsDataClient(cred)


def applicationinsights_mgmt_plane_client(cli_ctx, _, subscription=None):
    """Initialize Log Analytics mgmt client for use with CLI."""
    from .vendored_sdks.mgmt_applicationinsights import ApplicationInsightsManagementClient
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cli_ctx)
    # Use subscription from resource_id where possible, otherwise use login.
    if subscription:
        cred, _, _ = profile.get_login_credentials(subscription_id=subscription)
        return ApplicationInsightsManagementClient(
            cred,
            subscription
        )
    cred, sub_id, _ = profile.get_login_credentials()
    return ApplicationInsightsManagementClient(
        cred,
        sub_id
    )


def cf_query(cli_ctx, _, subscription=None):
    return applicationinsights_data_plane_client(cli_ctx, _, subscription=subscription).query


def cf_metrics(cli_ctx, _, subscription=None):
    return applicationinsights_data_plane_client(cli_ctx, _, subscription=subscription).metrics


def cf_events(cli_ctx, _, subscription=None):
    return applicationinsights_data_plane_client(cli_ctx, _, subscription=subscription).events


def cf_components(cli_ctx, _, subscription=None):
    return applicationinsights_mgmt_plane_client(cli_ctx, _, subscription=subscription).components


def cf_api_key(cli_ctx, _, subscription=None):
    return applicationinsights_mgmt_plane_client(cli_ctx, _, subscription=subscription).api_keys
