# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

MAXIMUM_SECRET_LENGTH = 20
MAXIMUM_CONTAINER_APP_NAME_LENGTH = 40

SHORT_POLLING_INTERVAL_SECS = 3
LONG_POLLING_INTERVAL_SECS = 10

LOG_ANALYTICS_RP = "Microsoft.OperationalInsights"
CONTAINER_APPS_RP = "Microsoft.App"

MAX_ENV_PER_LOCATION = 2

MICROSOFT_SECRET_SETTING_NAME = "microsoft-provider-authentication-secret"
FACEBOOK_SECRET_SETTING_NAME = "facebook-provider-authentication-secret"
GITHUB_SECRET_SETTING_NAME = "github-provider-authentication-secret"
GOOGLE_SECRET_SETTING_NAME = "google-provider-authentication-secret"
MSA_SECRET_SETTING_NAME = "msa-provider-authentication-secret"
TWITTER_SECRET_SETTING_NAME = "twitter-provider-authentication-secret"
APPLE_SECRET_SETTING_NAME = "apple-provider-authentication-secret"
UNAUTHENTICATED_CLIENT_ACTION = ['RedirectToLoginPage', 'AllowAnonymous', 'RejectWith401', 'RejectWith404']
FORWARD_PROXY_CONVENTION = ['NoProxy', 'Standard', 'Custom']
CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE = "Microsoft.App/managedEnvironments/certificates"
