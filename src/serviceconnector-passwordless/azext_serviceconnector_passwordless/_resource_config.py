# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.serviceconnector._resource_config import (
    RESOURCE,
    AUTH_TYPE,
    SUPPORTED_AUTH_TYPE
)
from azure.cli.command_modules.serviceconnector.action import (
    AddSecretAuthInfo,
    AddSecretAuthInfoAuto,
)
from .action import (
    AddSystemAssignedIdentityAuthInfo,
    AddUserAssignedIdentityAuthInfo,
    AddServicePrincipalAuthInfo,
    AddUserAccountAuthInfo,
)

EX_SUPPORTED_AUTH_TYPE = SUPPORTED_AUTH_TYPE.copy()
PASSWORDLESS_SOURCE_RESOURCES = [
    RESOURCE.WebApp,
    RESOURCE.ContainerApp,
    RESOURCE.SpringCloud,
    RESOURCE.SpringCloudDeprecated
]

PASSWORDLESS_TARGET_RESOURCES = [
    RESOURCE.Postgres,
    RESOURCE.PostgresFlexible,
    RESOURCE.MysqlFlexible,
    RESOURCE.Sql
]

# pylint: disable=line-too-long
EX_SUPPORTED_AUTH_TYPE[RESOURCE.Local] = {
    RESOURCE.Postgres: [AUTH_TYPE.Secret, AUTH_TYPE.UserAccount, AUTH_TYPE.ServicePrincipalSecret],
    RESOURCE.PostgresFlexible: [AUTH_TYPE.Secret, AUTH_TYPE.UserAccount, AUTH_TYPE.ServicePrincipalSecret],
    RESOURCE.MysqlFlexible: [AUTH_TYPE.Secret, AUTH_TYPE.UserAccount, AUTH_TYPE.ServicePrincipalSecret],
    RESOURCE.Sql: [AUTH_TYPE.Secret, AUTH_TYPE.UserAccount, AUTH_TYPE.ServicePrincipalSecret],
}

for resourceType in PASSWORDLESS_SOURCE_RESOURCES:
    EX_SUPPORTED_AUTH_TYPE[resourceType] = {
        RESOURCE.Postgres: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipalSecret],
        RESOURCE.PostgresFlexible: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipalSecret],
        RESOURCE.MysqlFlexible: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipalSecret],
        RESOURCE.Sql: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipalSecret],
    }

TARGET_RESOURCES_PARAMS = {
    RESOURCE.Postgres: {
        'target_resource_group': {
            'options': ['--target-resource-group', '--tg'],
            'help': 'The resource group which contains the postgres service',
            'placeholder': 'PostgresRG'
        },
        'server': {
            'options': ['--server'],
            'help': 'Name of postgres server',
            'placeholder': 'MyServer'
        },
        'database': {
            'options': ['--database'],
            'help': 'Name of postgres database',
            'placeholder': 'MyDB'
        }
    },
    RESOURCE.PostgresFlexible: {
        'target_resource_group': {
            'options': ['--target-resource-group', '--tg'],
            'help': 'The resource group which contains the flexible postgres service',
            'placeholder': 'PostgresRG'
        },
        'server': {
            'options': ['--server'],
            'help': 'Name of postgres flexible server',
            'placeholder': 'MyServer'
        },
        'database': {
            'options': ['--database'],
            'help': 'Name of postgres flexible database',
            'placeholder': 'MyDB'
        }
    },
    RESOURCE.MysqlFlexible: {
        'target_resource_group': {
            'options': ['--target-resource-group', '--tg'],
            'help': 'The resource group which contains the mysql flexible server',
            'placeholder': 'MysqlRG'
        },
        'server': {
            'options': ['--server'],
            'help': 'Name of the mysql flexible server',
            'placeholder': 'MyServer'
        },
        'database': {
            'options': ['--database'],
            'help': 'Name of the mysql flexible database',
            'placeholder': 'MyDB'
        }
    },
    RESOURCE.Sql: {
        'target_resource_group': {
            'options': ['--target-resource-group', '--tg'],
            'help': 'The resource group which contains the sql server',
            'placeholder': 'SqlRG'
        },
        'server': {
            'configured_default': 'sql-server',
            'options': ['--server'],
            'help': 'Name of the sql server',
            'placeholder': 'MyServer'
        },
        'database': {
            'options': ['--database'],
            'help': 'Name of the sql database',
            'placeholder': 'MyDB'
        }
    },
}

AUTH_TYPE_PARAMS = {
    AUTH_TYPE.Secret: {
        'secret_auth_info': {
            'options': ['--secret'],
            'help': 'The secret auth info',
            'action': AddSecretAuthInfo
        }
    },
    AUTH_TYPE.SecretAuto: {
        'secret_auth_info_auto': {
            'options': ['--secret'],
            'help': 'The secret auth info',
            'action': AddSecretAuthInfoAuto
        }
    },
    AUTH_TYPE.SystemIdentity: {
        'system_identity_auth_info': {
            'options': ['--system-identity'],
            'help': 'The system assigned identity auth info',
            'action': AddSystemAssignedIdentityAuthInfo
        }
    },
    AUTH_TYPE.UserIdentity: {
        'user_identity_auth_info': {
            'options': ['--user-identity'],
            'help': 'The user assigned identity auth info',
            'action': AddUserAssignedIdentityAuthInfo
        }
    },
    AUTH_TYPE.ServicePrincipalSecret: {
        'service_principal_auth_info_secret': {
            'options': ['--service-principal'],
            'help': 'The service principal auth info',
            'action': AddServicePrincipalAuthInfo
        }
    },
    AUTH_TYPE.UserAccount: {
        'user_account_auth_info': {
            'options': ['--user-account'],
            'help': 'The local user account auth info',
            'action': AddUserAccountAuthInfo
        }
    }
}
