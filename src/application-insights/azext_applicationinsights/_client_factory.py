# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

class _Track1Credential:  # pylint: disable=too-few-public-methods

    def __init__(self, credential, resource):
        """Track 1 credential that can be fed into Track 1 SDK clients. Exposes signed_session protocol.
        :param credential: Track 2 credential that exposes get_token protocol
        :param resource: AAD resource
        """
        self._credential = credential
        self._resource = resource

    def signed_session(self, session=None):
        import requests
        from azure.cli.core.auth.util import resource_to_scopes
        session = session or requests.Session()
        token = self._credential.get_token(*resource_to_scopes(self._resource))
        header = "{} {}".format('Bearer', token.token)
        session.headers['Authorization'] = header
        return session


def applicationinsights_data_plane_client(cli_ctx, _, subscription=None):
    """Initialize Log Analytics data client for use with CLI."""
    from .vendored_sdks.applicationinsights import ApplicationInsightsDataClient
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cli_ctx)
    # Note: temporarily adapt track2 auth to track1 by the guidance:
    # https://github.com/Azure/azure-cli/pull/29631#issuecomment-2716799520
    # need to be removed after migrated by codegen
    cred, _, _ = profile.get_login_credentials(subscription_id=subscription)
    return ApplicationInsightsDataClient(
        _Track1Credential(cred, cli_ctx.cloud.endpoints.app_insights_resource_id),
        base_url=f'{cli_ctx.cloud.endpoints.app_insights_resource_id}/v1'
    )


def applicationinsights_mgmt_plane_client(cli_ctx, **kwargs):
    """Initialize Log Analytics mgmt client for use with CLI."""
    from .vendored_sdks.mgmt_applicationinsights import ApplicationInsightsManagementClient
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx, ApplicationInsightsManagementClient, **kwargs)


def cf_query(cli_ctx, _):
    return applicationinsights_data_plane_client(cli_ctx, _).query


def cf_metrics(cli_ctx, _):
    return applicationinsights_data_plane_client(cli_ctx, _).metrics


def cf_events(cli_ctx, _):
    return applicationinsights_data_plane_client(cli_ctx, _).events


def cf_components(cli_ctx, _):
    return applicationinsights_mgmt_plane_client(cli_ctx, api_version='2018-05-01-preview').components


def cf_api_key(cli_ctx, _):
    return applicationinsights_mgmt_plane_client(cli_ctx).api_keys


def cf_export_configuration(cli_ctx, _):
    return applicationinsights_mgmt_plane_client(cli_ctx).export_configurations


def cf_web_test(cli_ctx, _):
    return applicationinsights_mgmt_plane_client(cli_ctx, api_version='2022-06-15').web_tests
