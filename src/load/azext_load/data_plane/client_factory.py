# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.data_plane.utils.utils import get_login_credentials, get_data_plane_scope
from azure.cli.core.util import get_az_user_agent


def admin_data_plane_client(cli_ctx, subscription=None, endpoint=None, credential=None):
    """Initialize Azure Load Testing data Administration client for use with CLI."""
    from azext_load.vendored_sdks.loadtesting import LoadTestAdministrationClient
    from azure.core.pipeline.policies import UserAgentPolicy

    if credential is None:
        credential, _, _ = get_login_credentials(cli_ctx, subscription_id=subscription)

    user_agent_policy = UserAgentPolicy(user_agent=get_az_user_agent())
    credential_scopes = get_data_plane_scope(cli_ctx)
    return LoadTestAdministrationClient(
        endpoint=endpoint, credential=credential, user_agent_policy=user_agent_policy, credential_scopes=credential_scopes  # pylint: disable=C0301
    )


def testrun_data_plane_client(
    cli_ctx, subscription=None, endpoint=None, credential=None
):
    """Initialize Azure Load Testing data Test Run client for use with CLI."""
    from azext_load.vendored_sdks.loadtesting import LoadTestRunClient
    from azure.core.pipeline.policies import UserAgentPolicy

    if credential is None:
        credential, _, _ = get_login_credentials(cli_ctx, subscription_id=subscription)

    user_agent_policy = UserAgentPolicy(user_agent=get_az_user_agent())
    credential_scopes = get_data_plane_scope(cli_ctx)
    return LoadTestRunClient(
        endpoint=endpoint, credential=credential, user_agent_policy=user_agent_policy, credential_scopes=credential_scopes  # pylint: disable=C0301
    )
