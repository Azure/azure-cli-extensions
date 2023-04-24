from azext_load.data_plane.util import get_login_credentials


def admin_data_plane_client(cli_ctx, subscription=None, endpoint=None, credential=None):
    """Initialize Azure Load Testing data Administration client for use with CLI."""
    from azure.core.pipeline.policies import UserAgentPolicy
    from azure.cli.core._profile import Profile
    from azext_load.vendored_sdks.loadtesting import LoadTestAdministrationClient

    if credential is None:
        credential, _, _ = get_login_credentials(cli_ctx, subscription_id=subscription)

    user_agent_policy = UserAgentPolicy(user_agent="AZCLI")
    return LoadTestAdministrationClient(
        endpoint=endpoint,
        credential=credential,
        user_agent_policy=user_agent_policy
    )


def testrun_data_plane_client(cli_ctx, subscription=None, endpoint=None, credential=None):
    """Initialize Azure Load Testing data Test Run client for use with CLI."""
    from azure.core.pipeline.policies import UserAgentPolicy
    from azure.cli.core._profile import Profile
    from azext_load.vendored_sdks.loadtesting import LoadTestRunClient

    if credential is None:
        credential, _, _ = get_login_credentials(cli_ctx, subscription_id=subscription)

    user_agent_policy = UserAgentPolicy(user_agent="AZCLI")
    return LoadTestRunClient(
        endpoint=endpoint,
        credential=credential,
        user_agent_policy=user_agent_policy
    )


def cf_admin(cli_ctx, *_, **kwargs):
    return admin_data_plane_client(cli_ctx, **kwargs)


def cf_testrun(cli_ctx, *_, **kwargs):
    return testrun_data_plane_client(cli_ctx, **kwargs)
