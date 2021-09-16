from enum import Enum
from .action import (
    AddSecretAuthInfo,
    AddUserAssignedIdentityAuthInfo,
    AddSystemAssignedIdentityAuthInfo,
    AddServicePrincipalAuthInfo
)


# The dict defines the resource types, including both source resources and target resources.
# The enum value will be used in command name
class RESOURCE(Enum):
    WebApp = 'webapp'
    SpringCloud = 'spring-cloud'
    CosmosCassandra = 'cosmos-cassandra'
    CosmosGremlin = 'cosmos-gremlin'
    CosmosMongo = 'cosmos-mongo'
    CosmosSql = 'cosmos-sql'
    CosmosTable = 'cosmos-table'
    StorageBlob = 'storage-blob'
    StorageQueue = 'storage-queue'
    StorageFile = 'storage-file'
    StorageTable = 'storage-table'
    Postgres = 'postgres'
    FlexiblePostgres = 'flexible-postgres'
    Mysql = 'mysql'
    MysqlFlexible = 'mysql-flexible'
    Sql = 'sql'
    KeyVault = 'keyvault'
    EventHub = 'event-hub'
    AppConfig = 'app-config'
    


# The dict defines the auth types
# The enum values will be used as parameter names
class AUTH_TYPE(Enum):
    Secret = 'secret'
    SystemIdentity = 'system-managed-identity'
    UserIdentity = 'user-managed-identity'
    ServicePrincipal = 'service-principal'


# The source resources released as CLI extensions
SOURCE_RESOURCES_IN_EXTENSION = [RESOURCE.SpringCloud]


# The dict defines the resource id pattern of source resources.
SOURCE_RESOURCES = {
    RESOURCE.WebApp: '/subscriptions/{subscription}/resourceGroups/{source_resource_group}/providers/Microsoft.Web/sites/{webapp}',
    RESOURCE.SpringCloud: '/subscriptions/{subscription}/resourceGroups/{source_resource_group}/providers/Microsoft.AppPlatform/Spring/{spring_service}/apps/{app_name}/deployments/{deployment_name}'
}


# The dict defines the resource id pattern of target resources.
TARGET_RESOURCES = {
    RESOURCE.Postgres: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.DBforPostgreSQL/servers/{postgres}/databases/{database}',
    RESOURCE.FlexiblePostgres: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.DBforPostgreSQL/flexibleServers/{postgres}/databases/{database}',
    RESOURCE.MysqlFlexible: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.DBforMySQL/flexibleServers/{server_name}/databases/{db_name}',
    RESOURCE.Mysql: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.DBForMySQL/servers/{server_name}/databases/{db_name}',
    RESOURCE.Sql: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.Sql/servers/{server_name}/databases/{db_name}',
    
    RESOURCE.CosmosCassandra: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.DocumentDB/databaseAccounts/{cosmos_account_name}/cassandraKeyspaces/{key_space}',
    RESOURCE.CosmosGremlin: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.DocumentDB/databaseAccounts/{cosmos_account_name}/gremlinDatabases/{db_name}/graphs/{graph_name}',
    RESOURCE.CosmosMongo: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.DocumentDB/databaseAccounts/{cosmos_account_name}/mongodbDatabases/{db_name}',
    RESOURCE.CosmosSql: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.DocumentDB/databaseAccounts/{cosmos_account_name}/sqlDatabases/{db_name}',
    RESOURCE.CosmosTable: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.DocumentDB/databaseAccounts/{cosmos_account_name}/tables/{table_name}',
    
    RESOURCE.StorageBlob: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}/blobServices/default',
    RESOURCE.StorageQueue: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}/fileServices/default',
    RESOURCE.StorageFile: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}/queueServices/default',
    RESOURCE.StorageTable: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}/tableServices/default',

    RESOURCE.KeyVault: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.KeyVault/vaults/{vault_name}',
    RESOURCE.AppConfig: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.AppConfiguration/configurationStores/{app_config}',
    RESOURCE.EventHub: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.EventHub/namespaces/{namespace}'
}


# The dict defines the parameters used to position the source resources.
# The parmaters should include all variables defined in source resource id expect
# for 'subscription', which will be dealt by CLI core as a default parameter.
SOURCE_RESOURCES_PARAMS = {
    RESOURCE.WebApp: {
        'source_resource_group': {
            'options': ['--source-resource-group', '-sg'],
            'help': 'The resource group which contains the webapp'
        },
        'webapp': {
            'options': ['--webapp'],
            'help': 'Name of the webapp'
        }
    },
    RESOURCE.SpringCloud: {
        'source_resource_group': {
            'options': ['--source-resource-group', '-sg'],
            'help': 'The resource group which contains the spring-cloud'
        },
        'spring_service': {
            'options': ['--service', '-s'],
            'help': 'Name of the spring-cloud service'
        },
        'app_name': {
            'options': ['--app'],
            'help': 'Name of the spring-cloud app'
        },
        'deployment_name': {
            'options': ['--deployment'],
            'help': 'The deployment name of the app'
        }
    }
}


# The dict defines the parameters used to position the target resources.
# The parmaters should include all variables defined in target resource id expect
# for 'subscription', which will be dealt by CLI core as a default parameter.
TARGET_RESOURCES_PARAMS = {
    RESOURCE.Postgres: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the postgres service'
        },
        'postgres': {
            'options': ['--postgres'],
            'help': 'Name of postgres server'
        },
        'database': {
            'options': ['--database'],
            'help': 'Name of database'
        }
    },
    RESOURCE.FlexiblePostgres: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the flexible postgres service'
        },
        'postgres': {
            'options': ['--postgres'],
            'help': 'Name of flexible postgres server'
        },
        'database': {
            'options': ['--database'],
            'help': 'Name of database'
        }
    },
    RESOURCE.MysqlFlexible: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the mysql flexible server'
        },
        'server_name': {
            'options': ['--server-name', '-s'],
            'help': 'Name of the server'
        },
        'db_name': {
            'options': ['--database-name', '-d'],
            'help': 'Name of the database'
        }
    },
    RESOURCE.Mysql: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the mysql server'
        },
        'server_name': {
            'options': ['--server-name', '-s'],
            'help': 'Name of the server'
        },
        'db_name': {
            'options': ['--database-name', '-d'],
            'help': 'Name of the database'
        }
    },
    RESOURCE.Sql: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the sql server'
        },
        'server_name': {
            'options': ['--server-name', '-s'],
            'help': 'Name of the server'
        },
        'db_name': {
            'options': ['--database-name', '-d'],
            'help': 'Name of the database'
        }
    },
    RESOURCE.CosmosCassandra: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the cosmos database account'
        },
        'cosmos_account_name': {
            'options': ['--account-name', '-a'],
            'help': 'Name of the cosmos database account'
        },
        'key_space': {
            'options': ['--key-space'],
            'help': 'Name of the keyspace'
        }
    },
    RESOURCE.CosmosGremlin: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the cosmos database account'
        },
        'cosmos_account_name': {
            'options': ['--account-name', '-a'],
            'help': 'Name of the cosmos database account'
        },
        'db_name': {
            'options': ['--database-name', '-d'],
            'help': 'Name of the database'
        },
        'graph_name': {
            'options': ['--graph-name'],
            'help': 'Name of the graph'
        }
    },
    RESOURCE.CosmosMongo: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the cosmos database account'
        },
        'cosmos_account_name': {
            'options': ['--account-name', '-a'],
            'help': 'Name of the cosmos database account'
        },
        'db_name': {
            'options': ['--database-name', '-d'],
            'help': 'Name of the database'
        }
    },
    RESOURCE.CosmosSql: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the cosmos database account'
        },
        'cosmos_account_name': {
            'options': ['--account-name', '-a'],
            'help': 'Name of the cosmos database account'
        },
        'db_name': {
            'options': ['--database-name', '-d'],
            'help': 'Name of the database'
        }
    },
    RESOURCE.CosmosTable: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the cosmos database account'
        },
        'cosmos_account_name': {
            'options': ['--account-name', '-a'],
            'help': 'Name of the cosmos database account'
        },
        'table_name': {
            'options': ['--table-name'],
            'help': 'Name of the table'
        }
    },
    RESOURCE.StorageBlob: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the storage account'
        },
        'storage_account_name': {
            'options': ['--account-name', '-a'],
            'help': 'Name of the storage account'
        },
    },
    RESOURCE.StorageQueue: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the storage account'
        },
        'storage_account_name': {
            'options': ['--account-name', '-a'],
            'help': 'Name of the storage account'
        },
    },
    RESOURCE.StorageFile: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the storage account'
        },
        'storage_account_name': {
            'options': ['--account-name', '-a'],
            'help': 'Name of the storage account'
        },
    },
    RESOURCE.StorageTable: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the storage account'
        },
        'storage_account_name': {
            'options': ['--account-name', '-a'],
            'help': 'Name of the storage account'
        },
    },
    RESOURCE.KeyVault: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the keyvault'
        },
        'vault_name': {
            'options': ['--vault-name'],
            'help': 'Name of the keyvault'
        }
    },
    RESOURCE.AppConfig: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the app configuration'
        },
        'app_config': {
            'options': ['--app-config'],
            'help': 'Name of the app configuration'
        }
    },
    RESOURCE.EventHub: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the eventhub'
        },
        'namespace': {
            'options': ['--namespace'],
            'help': 'Name of the eventhub namespace'
        }
    },
}


# The dict defines the parameters used to provide auth info
AUTH_TYPE_PARAMS = {
    AUTH_TYPE.Secret: {
        'secret_auth_info': {
            'options': ['--secret'],
            'help': 'The secret auth info',
            'action': AddSecretAuthInfo
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
    AUTH_TYPE.ServicePrincipal: {
        'service_principal_auth_info': {
            'options': ['--service-principal'],
            'help': 'The service principal auth info',
            'action': AddServicePrincipalAuthInfo
        }
    }
}


# The dict defines the supported auth type of each source-target resource pair
# The first one will be used as the default auth type
SUPPORTED_AUTH_TYPE = {
    RESOURCE.WebApp: {
        RESOURCE.Postgres: [AUTH_TYPE.Secret],
        RESOURCE.FlexiblePostgres: [AUTH_TYPE.Secret],
        RESOURCE.Mysql: [AUTH_TYPE.Secret],
        RESOURCE.MysqlFlexible: [AUTH_TYPE.Secret],
        RESOURCE.Sql: [AUTH_TYPE.Secret],
        
        RESOURCE.CosmosCassandra: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
        RESOURCE.CosmosGremlin: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
        RESOURCE.CosmosMongo: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
        RESOURCE.CosmosTable: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
        RESOURCE.CosmosSql: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
        
        RESOURCE.StorageBlob: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
        RESOURCE.StorageQueue: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
        RESOURCE.StorageFile: [AUTH_TYPE.Secret],
        RESOURCE.StorageTable: [AUTH_TYPE.Secret],

        RESOURCE.KeyVault: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
        RESOURCE.AppConfig: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
        RESOURCE.EventHub: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
    },
    RESOURCE.SpringCloud: {
        RESOURCE.Postgres: [AUTH_TYPE.Secret],
        RESOURCE.FlexiblePostgres: [AUTH_TYPE.Secret],
        RESOURCE.Mysql: [AUTH_TYPE.Secret],
        RESOURCE.MysqlFlexible: [AUTH_TYPE.Secret],
        RESOURCE.Sql: [AUTH_TYPE.Secret],

        RESOURCE.CosmosCassandra: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.ServicePrincipal],
        RESOURCE.CosmosGremlin: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.ServicePrincipal],
        RESOURCE.CosmosMongo: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.ServicePrincipal],
        RESOURCE.CosmosTable: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.ServicePrincipal],
        RESOURCE.CosmosSql: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.ServicePrincipal],
        
        RESOURCE.StorageBlob: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.ServicePrincipal],
        RESOURCE.StorageQueue: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.ServicePrincipal],
        RESOURCE.StorageFile: [AUTH_TYPE.Secret],
        RESOURCE.StorageTable: [AUTH_TYPE.Secret],

        RESOURCE.KeyVault: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.ServicePrincipal],
        RESOURCE.AppConfig: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
        RESOURCE.EventHub: [AUTH_TYPE.SystemIdentity, AUTH_TYPE.Secret, AUTH_TYPE.UserIdentity, AUTH_TYPE.ServicePrincipal],
    }
}
