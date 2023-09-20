# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (resource_group_name_type, get_resource_name_completion_list,
                                                get_three_state_flag, get_enum_type)
from azure.cli.command_modules.appservice._params import AUTH_TYPES
from azure.cli.core.local_context import LocalContextAttribute, LocalContextAction
from azure.cli.core.cloud import AZURE_PUBLIC_CLOUD, AZURE_CHINA_CLOUD, AZURE_US_GOV_CLOUD, AZURE_GERMAN_CLOUD

UNAUTHENTICATED_CLIENT_ACTION = ['RedirectToLoginPage', 'AllowAnonymous', 'Return401', 'Return404', 'Return403']
FORWARD_PROXY_CONVENTION = ['NoProxy', 'Standard', 'Custom']
CLOUD_NAMES = [AZURE_PUBLIC_CLOUD.name, AZURE_CHINA_CLOUD.name, AZURE_US_GOV_CLOUD.name, AZURE_GERMAN_CLOUD.name]


def load_arguments(self, _):
    webapp_name_arg_type = CLIArgumentType(configured_default='web', options_list=['--name', '-n'], metavar='NAME',
                                           completer=get_resource_name_completion_list('Microsoft.Web/sites'),
                                           id_part='name',
                                           help="name of the web app.",
                                           local_context_attribute=LocalContextAttribute(name='web_name', actions=[
                                               LocalContextAction.GET]))

    with self.argument_context('webapp auth') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('slot', options_list=['--slot', '-s'],
                   help="the name of the slot. Default to the productions slot if not specified")
        c.argument('name', arg_type=webapp_name_arg_type)

    with self.argument_context('webapp auth-classic') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('slot', options_list=['--slot', '-s'],
                   help="the name of the slot. Default to the productions slot if not specified")
        c.argument('name', arg_type=webapp_name_arg_type)

    with self.argument_context('webapp auth set') as c:
        c.argument('body', options_list=['--body', '-b'],
                   help='JSON representation of the configuration settings for the Azure App Service Authentication / Authorization V2 feature.')

    with self.argument_context('webapp auth update') as c:
        c.argument('set_string', options_list=['--set'],
                   help='Value of a specific field within the configuration settings for the Azure App Service Authentication / Authorization V2 feature.')
        c.argument('enabled', options_list=['--enabled'], arg_type=get_three_state_flag(return_label=True),
                   help='true if the Authentication / Authorization feature is enabled for the current app; otherwise, false.')
        c.argument('runtime_version', options_list=['--runtime-version'],
                   help='The RuntimeVersion of the Authentication / Authorization feature in use for the current app.')
        c.argument('config_file_path', options_list=['--config-file-path'],
                   help='The path of the config file containing auth settings if they come from a file.')
        c.argument('unauthenticated_client_action', options_list=['--unauthenticated-client-action', '--action'],
                   arg_type=get_enum_type(UNAUTHENTICATED_CLIENT_ACTION),
                   help='The action to take when an unauthenticated client attempts to access the app.')
        c.argument('redirect_provider', options_list=['--redirect-provider'],
                   help='The default authentication provider to use when multiple providers are configured.')
        c.argument('enable_token_store', options_list=['--enable-token-store'], arg_type=get_three_state_flag(return_label=True),
                   help='true to durably store platform-specific security tokens that are obtained during login flows; otherwise, false.')
        c.argument('require_https', options_list=['--require-https'], arg_type=get_three_state_flag(return_label=True),
                   help='false if the authentication/authorization responses not having the HTTPS scheme are permissible; otherwise, true.')
        c.argument('proxy_convention', options_list=['--proxy-convention'], arg_type=get_enum_type(FORWARD_PROXY_CONVENTION),
                   help='The convention used to determine the url of the request made.')
        c.argument('proxy_custom_host_header', options_list=['--proxy-custom-host-header', '--custom-host-header'],
                   help='The name of the header containing the host of the request.')
        c.argument('proxy_custom_proto_header', options_list=['--proxy-custom-proto-header', '--custom-proto-header'],
                   help='The name of the header containing the scheme of the request.')
        c.argument('excluded_paths', options_list=['--excluded-paths'],
                   help='The list of paths that should be excluded from authentication rules.')

    with self.argument_context('webapp auth microsoft update') as c:
        c.argument('client_id', options_list=['--client-id'],
                   help='The Client ID of this relying party application, known as the client_id.')
        c.argument('client_secret', options_list=['--client-secret'],
                   help='AAD application secret')
        c.argument('client_secret_setting_name', options_list=['--client-secret-setting-name', '--secret-setting'],
                   help='The app setting name that contains the client secret of the relying party application.')
        c.argument('issuer', options_list=['--issuer'],
                   help='The OpenID Connect Issuer URI that represents the entity which issues access tokens for this application.')
        c.argument('allowed_token_audiences', options_list=['--allowed-token-audiences', '--allowed-audiences'],
                   help='The configuration settings of the allowed list of audiences from which to validate the JWT token.')
        c.argument('client_secret_certificate_thumbprint', options_list=['--thumbprint', '--client-secret-certificate-thumbprint'],
                   help='Alternative to AAD Client Secret, thumbprint of a certificate used for signing purposes')
        c.argument('client_secret_certificate_san', options_list=['--san', '--client-secret-certificate-san'],
                   help='Alternative to AAD Client Secret and thumbprint, subject alternative name of a certificate used for signing purposes')
        c.argument('client_secret_certificate_issuer', options_list=['--certificate-issuer', '--client-secret-certificate-issuer'],
                   help='Alternative to AAD Client Secret and thumbprint, issuer of a certificate used for signing purposes')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')
        c.argument('tenant_id', options_list=['--tenant-id'],
                   help='The tenant id of the application.')

    with self.argument_context('webapp auth facebook update') as c:
        c.argument('app_id', options_list=['--app-id'],
                   help='The App ID of the app used for login.')
        c.argument('app_secret', options_list=['--app-secret'],
                   help='The app secret.')
        c.argument('app_secret_setting_name', options_list=['--app-secret-setting-name', '--secret-setting'],
                   help='The app setting name that contains the app secret.')
        c.argument('graph_api_version', options_list=['--graph-api-version'],
                   help='The version of the Facebook api to be used while logging in.')
        c.argument('scopes', options_list=['--scopes'],
                   help='A list of the scopes that should be requested while authenticating.')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('webapp auth github update') as c:
        c.argument('client_id', options_list=['--client-id'],
                   help='The Client ID of the app used for login.')
        c.argument('client_secret_setting_name', options_list=['--client-secret-setting-name', '--secret-setting'],
                   help='The app setting name that contains the client secret.')
        c.argument('client_secret', options_list=['--client-secret'],
                   help='The client secret.')
        c.argument('scopes', options_list=['--scopes'],
                   help='A list of the scopes that should be requested while authenticating.')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('webapp auth google update') as c:
        c.argument('client_id', options_list=['--client-id'],
                   help='The Client ID of the app used for login.')
        c.argument('client_secret', options_list=['--client-secret'],
                   help='The client secret.')
        c.argument('client_secret_setting_name', options_list=['--client-secret-setting-name', '--secret-setting'],
                   help='The app setting name that contains the client secret.')
        c.argument('scopes', options_list=['--scopes'],
                   help='A list of the scopes that should be requested while authenticating.')
        c.argument('allowed_token_audiences', options_list=['--allowed-token-audiences', '--allowed-audiences'],
                   help='The configuration settings of the allowed list of audiences from which to validate the JWT token.')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('webapp auth twitter update') as c:
        c.argument('consumer_key', options_list=['--consumer-key'],
                   help='The OAuth 1.0a consumer key of the Twitter application used for sign-in.')
        c.argument('consumer_secret', options_list=['--consumer-secret'],
                   help='The consumer secret.')
        c.argument('consumer_secret_setting_name', options_list=['--consumer-secret-setting-name', '--secret-setting'],
                   help='The app setting name that contains the OAuth 1.0a consumer secret of the Twitter.')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('webapp auth apple update') as c:
        c.argument('client_id', options_list=['--client-id'],
                   help='The Client ID of the app used for login.')
        c.argument('client_secret', options_list=['--client-secret'],
                   help='The client secret.')
        c.argument('client_secret_setting_name', options_list=['--client-secret-setting-name', '--secret-setting'],
                   help='The app setting name that contains the client secret.')
        c.argument('scopes', options_list=['--scopes'],
                   help='A list of the scopes that should be requested while authenticating.')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('webapp auth openid-connect show') as c:
        c.argument('provider_name', options_list=['--provider-name'], required=True,
                   help='The name of the custom OpenID Connect provider.')

    with self.argument_context('webapp auth openid-connect add') as c:
        c.argument('provider_name', options_list=['--provider-name'], required=True,
                   help='The name of the custom OpenID Connect provider.')
        c.argument('client_id', options_list=['--client-id'],
                   help='The Client ID of the app used for login.')
        c.argument('client_secret_setting_name', options_list=['--client-secret-setting-name', '--secret-setting'],
                   help='The app setting name that contains the client secret.')
        c.argument('openid_configuration', options_list=['--openid-configuration'],
                   help='The endpoint that contains all the configuration endpoints for the provider.')
        c.argument('scopes', options_list=['--scopes'],
                   help='A list of the scopes that should be requested while authenticating.')
        c.argument('client_secret', options_list=['--client-secret'],
                   help='The application secret of the app used for login.')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('webapp auth openid-connect update') as c:
        c.argument('provider_name', options_list=['--provider-name'], required=True,
                   help='The name of the custom OpenID Connect provider.')
        c.argument('client_id', options_list=['--client-id'],
                   help='The Client ID of the app used for login.')
        c.argument('client_secret_setting_name', options_list=['--client-secret-setting-name', '--secret-setting'],
                   help='The app setting name that contains the client secret.')
        c.argument('openid_configuration', options_list=['--openid-configuration'],
                   help='The endpoint that contains all the configuration endpoints for the provider.')
        c.argument('scopes', options_list=['--scopes'],
                   help='A list of the scopes that should be requested while authenticating.')
        c.argument('client_secret', options_list=['--client-secret'],
                   help='The application secret of the app used for login.')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('webapp auth openid-connect remove') as c:
        c.argument('provider_name', options_list=['--provider-name'], required=True,
                   help='The name of the custom OpenID Connect provider.')

    with self.argument_context('webapp auth-classic update') as c:
        c.argument('enabled', arg_type=get_three_state_flag(return_label=True),
                   help='true if the Authentication / Authorization feature is enabled for the current app; otherwise, false.')
        c.argument('token_store_enabled', options_list=['--token-store'],
                   arg_type=get_three_state_flag(return_label=True), help='use App Service Token Store')
        c.argument('action', arg_type=get_enum_type(AUTH_TYPES),
                   help='The action to take when an unauthenticated client attempts to access the app.')
        c.argument('runtime_version',
                   help='Runtime version of the Authentication/Authorization feature in use for the current app')
        c.argument('token_refresh_extension_hours', type=float, options_list=['--token-refresh-extension-hours', '--token-refresh-hours'],
                   help="Hours, must be formattable into a float")
        c.argument('allowed_external_redirect_urls', options_list=['--allowed-redirect-urls'], nargs='+',
                   help="One or more urls (space-delimited).")
        c.argument('client_id', options_list=['--aad-client-id'], arg_group='Azure Active Directory',
                   help='Application ID to integrate AAD organization account Sign-in into your web app')
        c.argument('client_secret', options_list=['--aad-client-secret'], arg_group='Azure Active Directory',
                   help='AAD application secret')
        c.argument('client_secret_setting_name', options_list=['--aad-client-secret-setting-name', '--aad-secret-setting'], arg_group='Azure Active Directory',
                   help='The app setting name that contains the client secret of the relying party application.')
        c.argument('client_secret_certificate_thumbprint', options_list=['--aad-client-secret-certificate-thumbprint', '--thumbprint'], arg_group='Azure Active Directory',
                   help='Alternative to AAD Client Secret, thumbprint of a certificate used for signing purposes')
        c.argument('allowed_audiences', nargs='+', options_list=['--aad-allowed-token-audiences', '--allowed-audiences'],
                   arg_group='Azure Active Directory', help="One or more token audiences (space-delimited).")
        c.argument('issuer', options_list=['--aad-token-issuer-url'],
                   help='This url can be found in the JSON output returned from your active directory endpoint using your tenantID. The endpoint can be queried from `az cloud show` at \"endpoints.activeDirectory\". '
                        'The tenantID can be found using `az account show`. Get the \"issuer\" from the JSON at <active directory endpoint>/<tenantId>/.well-known/openid-configuration.',
                   arg_group='Azure Active Directory')
        c.argument('facebook_app_id', arg_group='Facebook',
                   help="Application ID to integrate Facebook Sign-in into your web app")
        c.argument('facebook_app_secret', arg_group='Facebook', help='Facebook Application client secret')
        c.argument('facebook_app_secret_setting_name', arg_group='Facebook', options_list=['--facebook-app-secret-setting-name', '--fb-secret-setting'],
                   help='The app setting name that contains the app secret used for Facebook Login.')
        c.argument('facebook_oauth_scopes', nargs='+',
                   help="One or more facebook authentication scopes (space-delimited).", arg_group='Facebook')
        c.argument('twitter_consumer_key', arg_group='Twitter',
                   help='Application ID to integrate Twitter Sign-in into your web app')
        c.argument('twitter_consumer_secret', arg_group='Twitter', options_list=['--twitter-consumer-secret', '--twitter-secret'],
                   help='Twitter Application client secret')
        c.argument('twitter_consumer_secret_setting_name', arg_group='Twitter', options_list=['--twitter-consumer-secret-setting-name', '--twitter-secret-setting'],
                   help='The app setting name that contains the OAuth 1.0a consumer secret of the Twitter application used for sign-in.')
        c.argument('google_client_id', arg_group='Google',
                   help='Application ID to integrate Google Sign-in into your web app')
        c.argument('google_client_secret', arg_group='Google', help='Google Application client secret')
        c.argument('google_client_secret_setting_name', arg_group='Google', options_list=['--google-client-secret-setting-name', '--google-secret-setting'],
                   help='The app setting name that contains the client secret associated with the Google web application.')
        c.argument('google_oauth_scopes', nargs='+', help="One or more Google authentication scopes (space-delimited).",
                   arg_group='Google')
        c.argument('microsoft_account_client_id', arg_group='Microsoft', options_list=['--microsoft-account-client-id', '--msa-client'],
                   help="AAD V2 Application ID to integrate Microsoft account Sign-in into your web app")
        c.argument('microsoft_account_client_secret', arg_group='Microsoft', options_list=['--microsoft-account-client-secret', '--msa-secret'],
                   help='AAD V2 Application client secret')
        c.argument('microsoft_account_client_secret_setting_name', arg_group='Microsoft', options_list=['--microsoft-account-client-secret-setting-name', '--msa-secret-setting'],
                   help='The app setting name containing the OAuth 2.0 client secret that was created for the app used for authentication.')
        c.argument('microsoft_account_oauth_scopes', nargs='+', options_list=['--microsoft-account-oauth-scopes', '--msa-scopes'],
                   help="One or more Microsoft authentification scopes (space-delimited).", arg_group='Microsoft')
        c.argument('git_hub_client_id', options_list=['--github-client-id'], arg_group='GitHub',
                   help="The Client Id of the GitHub app used for login.")
        c.argument('git_hub_client_secret', options_list=['--github-client-secret'], arg_group='GitHub',
                   help="The Client Secret of the GitHub app used for login.")
        c.argument('git_hub_client_secret_setting_name', arg_group='GitHub', options_list=['--github-client-secret-setting-name', '--github-secret-setting'],
                   help="The app setting name that contains the client secret of the Github app used for GitHub Login.")
        c.argument('git_hub_o_auth_scopes', options_list=['--github-oauth-scopes', '--github-scopes'], arg_group='GitHub',
                   help="The OAuth 2.0 scopes that will be requested as part of GitHub Login authentication.")
