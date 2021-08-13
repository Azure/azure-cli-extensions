from enum import Enum

class RESOURCE(Enum):
    WebApp = 'webapp'
    SpringCloud = 'spring-cloud'
    Postgres = 'postgres'
    KeyVault = 'keyvault'
    CosmosCassandra = 'cosmos-cassandra'
    CosmosGremlin = 'cosmos-gremlin'
    CosmosMongo = 'cosmos-mongo'
    CosmosSql = 'cosmos-sql'
    CosmosTable = 'cosmos-table'
    FlexibleCosmosSql = 'flexible-cosmos-sql'
    MysqlFlexible = 'mysql-flexible'
    Mysql = 'mysql'
    StorageBlob = 'storage-blob'
    StorageQueue = 'storage-queue'
    StorageFile = 'storage-file'
    StorageTable = 'storage-table'


SOURCE_RESOURCES = {
    RESOURCE.WebApp: '/subscriptions/{subscription}/resourceGroups/{source_resource_group}/providers/Microsoft.Web/sites/{webapp}', 
    RESOURCE.SpringCloud: '/subscriptions/{subscription}/resourceGroups/{source_resource_group}/providers/Microsoft.AppPlatform/Spring/{spring_cloud}'
}


TARGET_RESOURCES = {
    RESOURCE.Postgres: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.DBforPostgreSQL/servers/{postgres}/databases/{database}',
    RESOURCE.KeyVault: '/subscriptions/{subscription}/resourceGroups/{target_resource_group}/providers/Microsoft.KeyVault/vaults/{vault_name}',
    RESOURCE.CosmosCassandra: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DocumentDB/databaseAccounts/{}/cassandraKeyspaces/{}',
    RESOURCE.CosmosGremlin: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DocumentDB/databaseAccounts/{}/gremlinDatabases/{}/graphs/{}',
    RESOURCE.CosmosMongo: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DocumentDB/databaseAccounts/{}/mongodbDatabases/{}',
    RESOURCE.CosmosSql: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DocumentDB/databaseAccounts/{}/sqlDatabases/{}',
    RESOURCE.CosmosTable: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DocumentDB/databaseAccounts/{}/tables/{}',
    RESOURCE.FlexibleCosmosSql: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DBforPostgreSQL/flexibleServers/{}/databases/{}',
    RESOURCE.MysqlFlexible: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DBforMySQL/flexibleServers/{}/databases/{}',
    RESOURCE.Mysql: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DBForMySQL/servers/{}/databases/{}',
    RESOURCE.StorageBlob: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}/blobServices',
    RESOURCE.StorageQueue: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}/fileServices',
    RESOURCE.StorageFile: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}/queueServices',
    RESOURCE.StorageTable: '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}/tableServices'
}


SOURCE_RESOURCES_PARAMS = {
    RESOURCE.WebApp: {
        'source_resource_group': {
            'options': ['--source-resource-group', '-sg'],
            'help': 'The resource group which contains the webapp'
        },
        'webapp': {
            'options': ['--webapp'],
            'help': 'The name of the webapp'
        }
    }, 
    RESOURCE.SpringCloud: {
        'source_resource_group': {
            'options': ['--source-resource-group', '-sg'],
            'help': 'The resource group which contains the spring-cloud'
        },
        'spring_cloud': {
            'options': ['--spring-cloud'],
            'help': 'The name of the spring-cloud'
        }
    }
}

TARGET_RESOURCES_PARAMS = {
    RESOURCE.Postgres: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the postgres service'
        },
        'postgres': {
            'options': ['--postgres'],
            'help': 'The name of postgres service'
        },
        'database': {
            'options': ['--database'],
            'help': 'The name of database'
        }
    },
    RESOURCE.KeyVault: {
        'target_resource_group': {
            'options': ['--target-resource-group', '-tg'],
            'help': 'The resource group which contains the keyvault'
        },
        'keyvault': {
            'options': ['--vault-name'],
            'help': 'The name of the keyvault'
        }
    }
}

DEFAULT_AUTH_TYPE = {
    RESOURCE.WebApp: {
        RESOURCE.Postgres: {
            'secret_auth_info': {
                'options': ['--secret-auth-info'],
                'help': 'The secret auth info'
            }
        },
        RESOURCE.StorageBlob: {
            'system_assigned_identity_auth_info': {
                'options': ['--system-identity-auth-info'],
                'help': 'The system assigned identity auth info'
            }
        }
    }
}