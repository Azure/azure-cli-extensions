# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.serviceconnector._resource_config import (
    RESOURCE,
    AUTH_TYPE
)
passwordless_target_resources = [
    RESOURCE.Postgres,
    RESOURCE.PostgresFlexible,
    RESOURCE.MysqlFlexible,
    RESOURCE.Sql
]

SUPPORTED_AUTH_TYPE = {
    RESOURCE.Local: {
        RESOURCE.Postgres: [AUTH_TYPE.Secret, AUTH_TYPE.UserAccount],
        RESOURCE.PostgresFlexible: [AUTH_TYPE.Secret, AUTH_TYPE.UserAccount],
        RESOURCE.MysqlFlexible: [AUTH_TYPE.Secret, AUTH_TYPE.UserAccount],
        RESOURCE.Sql: [AUTH_TYPE.Secret, AUTH_TYPE.UserAccount],
    },
    RESOURCE.WebApp: {
        RESOURCE.Postgres: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity],
        RESOURCE.PostgresFlexible: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity],
        RESOURCE.MysqlFlexible: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity],
        RESOURCE.Sql: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity],
    },
    RESOURCE.SpringCloud: {
        RESOURCE.Postgres: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity],
        RESOURCE.PostgresFlexible: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity],
        RESOURCE.MysqlFlexible: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity],
        RESOURCE.Sql: [AUTH_TYPE.Secret, AUTH_TYPE.SystemIdentity],
    },
    RESOURCE.KubernetesCluster: {
        RESOURCE.Postgres: [AUTH_TYPE.Secret],
        RESOURCE.PostgresFlexible: [AUTH_TYPE.Secret],
        RESOURCE.MysqlFlexible: [AUTH_TYPE.Secret],
        RESOURCE.Sql: [AUTH_TYPE.Secret],
    },
}
SUPPORTED_AUTH_TYPE[RESOURCE.ContainerApp] = SUPPORTED_AUTH_TYPE[RESOURCE.SpringCloud]

SUPPORTED_AUTH_TYPE[RESOURCE.SpringCloudDeprecated] = SUPPORTED_AUTH_TYPE[RESOURCE.SpringCloud]

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
