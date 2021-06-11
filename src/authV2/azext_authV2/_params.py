# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (get_three_state_flag, get_enum_type)
from azure.mgmt.web.models import BuiltInAuthenticationProvider

AUTH_TYPES = {
    'AllowAnonymous': 'na',
    'LoginWithAzureActiveDirectory': BuiltInAuthenticationProvider.azure_active_directory,
    'LoginWithFacebook': BuiltInAuthenticationProvider.facebook,
    'LoginWithGoogle': BuiltInAuthenticationProvider.google,
    'LoginWithMicrosoftAccount': BuiltInAuthenticationProvider.microsoft_account,
    'LoginWithTwitter': BuiltInAuthenticationProvider.twitter}

def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    authV2_name_type = CLIArgumentType(options_list='--authV2-name-name', help='Name of the Authv2.', id_part='name')

    with self.argument_context('webapp auth set') as c:
        c.argument('body', options_list=['--body', '-b'])

    with self.argument_context('webapp auth update') as c:
        c.argument('set_string', options_list=['--set'])
        c.argument('enabled', options_list=['--enabled'])
        c.argument('runtime_version', options_list=['--runtime-version'])
        c.argument('config_file_path', options_list=['--config-file-path'])
        c.argument('unauthenticated_client_action', options_list=['--unauthenticated-client-action'])
        c.argument('redirect_provider', options_list=['--redirect-provider'])
        c.argument('enable_token_store', options_list=['--enable-token-store'])
        c.argument('require_https', options_list=['--require-https'])
        c.argument('proxy_convention', options_list=['--proxy-convention'])
        c.argument('proxy_custom_host_header', options_list=['--proxy-custom-host-header'])
        c.argument('proxy_custom_proto_header', options_list=['--proxy-custom-proto-header'])
    
    with self.argument_context('webapp authlegacy update') as c:
        c.argument('enabled', arg_type=get_three_state_flag(return_label=True))
        c.argument('token_store_enabled', options_list=['--token-store'],
                   arg_type=get_three_state_flag(return_label=True), help='use App Service Token Store')
        c.argument('action', arg_type=get_enum_type(AUTH_TYPES))
        c.argument('runtime_version',
                   help='Runtime version of the Authentication/Authorization feature in use for the current app')
        c.argument('token_refresh_extension_hours', type=float, help="Hours, must be formattable into a float")
        c.argument('allowed_external_redirect_urls', nargs='+', help="One or more urls (space-delimited).")
        c.argument('client_id', options_list=['--aad-client-id'], arg_group='Azure Active Directory',
                   help='Application ID to integrate AAD organization account Sign-in into your web app')
        c.argument('client_secret', options_list=['--aad-client-secret'], arg_group='Azure Active Directory',
                   help='AAD application secret')
        c.argument('client_secret_setting_name', options_list=['--aad-client-secret-setting-name'], arg_group='Azure Active Directory',
                   help='The app setting name that contains the client secret of the relying party application.')
        c.argument('client_secret_certificate_thumbprint', options_list=['--aad-client-secret-certificate-thumbprint', '--thumbprint'], arg_group='Azure Active Directory',
                   help='Alternative to AAD Client Secret, thumbprint of a certificate used for signing purposes')
        c.argument('allowed_audiences', nargs='+', options_list=['--aad-allowed-token-audiences'],
                   arg_group='Azure Active Directory', help="One or more token audiences (space-delimited).")
        c.argument('issuer', options_list=['--aad-token-issuer-url'],
                   help='This url can be found in the JSON output returned from your active directory endpoint using your tenantID. The endpoint can be queried from `az cloud show` at \"endpoints.activeDirectory\". '
                        'The tenantID can be found using `az account show`. Get the \"issuer\" from the JSON at <active directory endpoint>/<tenantId>/.well-known/openid-configuration.',
                   arg_group='Azure Active Directory')
        c.argument('facebook_app_id', arg_group='Facebook',
                   help="Application ID to integrate Facebook Sign-in into your web app")
        c.argument('facebook_app_secret', arg_group='Facebook', help='Facebook Application client secret')
        c.argument('facebook_app_secret_setting_name', arg_group='Facebook', help='The app setting name that contains the app secret used for Facebook Login.')
        c.argument('facebook_oauth_scopes', nargs='+',
                   help="One or more facebook authentication scopes (space-delimited).", arg_group='Facebook')
        c.argument('twitter_consumer_key', arg_group='Twitter',
                   help='Application ID to integrate Twitter Sign-in into your web app')
        c.argument('twitter_consumer_secret', arg_group='Twitter', help='Twitter Application client secret')
        c.argument('twitter_consumer_secret_setting_name', arg_group='Twitter', help='The app setting name that contains the OAuth 1.0a consumer secret of the Twitter application used for sign-in.')
        c.argument('google_client_id', arg_group='Google',
                   help='Application ID to integrate Google Sign-in into your web app')
        c.argument('google_client_secret', arg_group='Google', help='Google Application client secret')
        c.argument('google_client_secret_setting_name', arg_group='Google', help='The app setting name that contains the client secret associated with the Google web application.')
        c.argument('google_oauth_scopes', nargs='+', help="One or more Google authentication scopes (space-delimited).",
                   arg_group='Google')
        c.argument('microsoft_account_client_id', arg_group='Microsoft',
                   help="AAD V2 Application ID to integrate Microsoft account Sign-in into your web app")
        c.argument('microsoft_account_client_secret', arg_group='Microsoft', help='AAD V2 Application client secret')
        c.argument('microsoft_account_client_secret_setting_name', arg_group='Microsoft', help='The app setting name containing the OAuth 2.0 client secret that was created for the app used for authentication.')
        c.argument('microsoft_account_oauth_scopes', nargs='+',
                   help="One or more Microsoft authentification scopes (space-delimited).", arg_group='Microsoft')
        c.argument('git_hub_client_id', arg_group='GitHub', help="The Client Id of the GitHub app used for login.")
        c.argument('git_hub_client_secret', arg_group='GitHub', help="The Client Secret of the GitHub app used for login.")
        c.argument('git_hub_client_secret_setting_name', arg_group='GitHub', help="The app setting name that contains the client secret of the Github app used for GitHub Login.")
        c.argument('git_hub_o_auth_scopes', arg_group='GitHub', help="The OAuth 2.0 scopes that will be requested as part of GitHub Login authentication.")
