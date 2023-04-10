def loadtesting_data_plane_client(cli_ctx, _, subscription=None):
    """Initialize Log Analytics data client for use with CLI."""
    from azure.cli.core._profile import Profile
    from azext_load.vendored_sdks.loadtesting import LoadTestRunClient
    #from azure.identity import DefaultAzureCredential
    profile = Profile(cli_ctx=cli_ctx)
    cred, _, _ = profile.get_login_credentials(
        subscription_id=subscription
    )
    #create uri from r-id
    return LoadTestRunClient(endpoint = "e91964d6-832c-46de-98fe-e2620d702cdf.eastus.cnt-prod.loadtesting.azure.com", credential=cred)


def admin_data_plane_client(cli_ctx, subscription=None):
    """Initialize Log Analytics data client for use with CLI."""
    from azext_load.vendored_sdks.loadtesting import LoadTestAdministrationClient
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cli_ctx)
    cred,_,_ = profile.get_login_credentials(
    )
    #dp_uri = call show(id)
    
    return LoadTestAdministrationClient(endpoint="e91964d6-832c-46de-98fe-e2620d702cdf.eastus.cnt-prod.loadtesting.azure.com", credential = cred)

def cf_load(cli_ctx, _):
    return loadtesting_data_plane_client(cli_ctx, _)

def cf_admin(cli_ctx, _):
    return admin_data_plane_client(cli_ctx, _)
