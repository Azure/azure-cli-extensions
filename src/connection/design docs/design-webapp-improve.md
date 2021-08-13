# Service Connector Command Interface

## az {source} connection
```
Group
    az webapp connection: Manage webapp connections.

Subgroups:
    create             : Create a webapp connection.

Commands:
    delete             : Delete a webapp connection.
    list               : List connections which connects to a webapp.
    list-configuration : List source configurations of a webapp connection.
    show               : Get the details of a webapp connection.
    update             : Update a webapp connection.
    validate           : Validate a webapp connection.
```

## az {source} connection list-support-type
```
Command
    az webapp connection list-support-type : List webapp supported connection types.

Arguments
    --target

Examples:
    az webapp connection list-support-type --target keyvault -o table

    ====================sample output===================
        Target              AuthType
        --------------------------------------------
        keyvault            service-principal
        keyvault            system-managed-identity
        keyvault            user-managed-identity
    ====================sample output===================
```


## az {source} connection list
```
Command
    az webapp connection list  :   List webapp connections.
 
Arguments
    --source-id                     : The resource id of a webapp. "--source-resource-group" and "--
                                      webapp-name" are required if "--source-id" is not specified.
    --source-resource-group -sg     : The resource group which contains the webapp.
    --webapp-name                   : The name of the webapp.

Examples:
    az webapp connection list --source-id <XX>
    az webapp connection list --source-resource-group <XX> --webapp-name <XX> 
```


## az {source} connection delete

```
Command
    az webapp connection delete  : Delete a webapp connection.

Arguments
    --connection-name --name -n : The name of the webapp connection.
    --id                        : The resource id of the connection. "--source-resource-group", "--
                                  webapp-name" and "--connection-name" are required if "--id" is not
                                  specified.
    --source-resource-group -sg : The resource group which contains the webapp.
    --webapp-name               : The name of the webapp.

Examples:
    az webapp connection delete --id <XX>
    az webapp connection delete --webapp-name <XX> --source-resource-group <XX> --connection-name <XX>
```


## az {source} connection show

```
Command
    az webapp connection show  : Get the details of a webapp connection.

Arguments
    --connection-name --name -n : The name of the webapp connection.
    --id                        : The resource id of the connection. "--source-resource-group", "--
                                  webapp-name" and "--connection-name" are required if "--id" is not
                                  specified.
    --source-resource-group -sg : The resource group which contains the webapp.
    --webapp-name               : The name of the webapp.

Examples:
    az webapp connection show --id <XX>
    az webapp connection show --webapp-name <XX> --source-resource-group <XX> --connection-name <XX>
```


## az {source} connection list-configuration

```
Command
    az webapp connection list-configuration  : List the source configurations of a webapp connection.

Arguments
    --connection-name --name -n : The name of the webapp connection.
    --id                        : The resource id of the connection. "--source-resource-group", "--
                                  webapp-name" and "--connection-name" are required if "--id" is not
                                  specified.
    --source-resource-group -sg : The resource group which contains the webapp.
    --webapp-name               : The name of the webapp.

Examples:
    az webapp connection list-configuration --id <XX>
    az webapp connection list-configuration \
        --webapp-name <XX> --source-resource-group <XX> --connection-name <XX>
```


## az {source} connection validate

```
Command
    az webapp connection list-configuration  : List the source configurations of a webapp connection.

Arguments
    --connection-name --name -n : The name of the webapp connection.
    --id                        : The resource id of the connection. "--source-resource-group", "--
                                  webapp-name" and "--connection-name" are required if "--id" is not
                                  specified.
    --source-resource-group -sg : The resource group which contains the webapp.
    --webapp-name               : The name of the webapp.

Examples:
    az webapp connection validate --id <XX>
    az webapp connection validate --webapp-name <XX> --source-resource-group <XX> --connection-name <XX>
```


## az {source} connection update
```
Command
    az webapp connection update : Update a webapp connection.

Arguments
    --client-type               : The client type of the webapp.  Allowed values: Nodejs, django,
                                  dotnet, dotnetCore, go, java, none, php, python, springCloudBinding.
    --connection-name --name -n : The name of the webapp connection.
    --id                        : The resource id of the connection. "--source-resource-group", "--
                                  webapp-name" and "--connection-name" are required if "--id" is not
                                  specified.
    --no-wait                   : Do not wait for the long-running operation to finish.
    --source-resource-group -sg : The resource group which contains the webapp.
    --webapp-name               : The name of the webapp.

AuthType Arguments
    --secret                    : The secret auth info.
        Usage: --secret name=XX secret=XX

        name    : Username or account name for secret auth.
        secret  : Password or account key for secret auth.
    --service-principal         : The service principal auth info.
        Usage: --service-principal id=XX name=XX

        id      : Required. Client Id fo the service principal.
        name    : Required. Name of the service principal.
    --system-assigned-identity  : The system assigned identity auth info.
        Usage: --system-assigned-identity.
    --user-assigned-identity    : The user assigned identity auth info.
        Usage: --user-assigned-identity id=XX

        id      : Required. Client Id of the user assigned managed identity.
```

## az {source} connection create
```
Group
    az webapp connection create : Create a webapp connection.

Commands:
    keyvault      : Create a webapp connection with keyvault.
    storage-blob  : Create a webapp connection with storage-blob.
    storage-file  : Create a webapp connection with storage-file.
    storage-queue : Create a webapp connection with storage-queue.
    storage-table : Create a webapp connection with storage-table.
    ...           : ...
```

## az {source} connection {target} create
```
Command
    az webapp connection create keyvault  : Create a webapp and keyvault connection.

Arguments
    --client-type               : The client type of the webapp.  Allowed values: Nodejs, django,
                                  dotnet, dotnetCore, go, java, none, php, python, springCloudBinding.
    --connection-name --name -n : The name of the webapp connection.
    --keyvault-name             : The name of the keyvault.
    --no-wait                   : Do not wait for the long-running operation to finish.
    --source-id                 : The resource id of a webapp. "--source-resource-group" and "--
                                  webapp-name" are required if "--source-id" is not specified.
    --source-resource-group -sg : The resource group which contains the webapp.
    --target-id                 : The resource id of the keyvault. "--target-resource-group" and "--
                                  keyvault-name" are required if "--target-id" is not specified.
    --target-resource-group -tg : The resource group name of the target resource.
    --webapp-name               : The name of the webapp.

AuthType Arguments
    --secret                    : The secret auth info.
        Usage: --secret name=XX secret=XX

        name    : Username or account name for secret auth.
        secret  : Password or account key for secret auth.
    --service-principal         : The service principal auth info.
        Usage: --service-principal id=XX name=XX

        id      : Required. Client Id fo the service principal.
        name    : Required. Name of the service principal.
    --system-assigned-identity  : The system assigned identity auth info.
        Usage: --system-assigned-identity.
    --user-assigned-identity    : The user assigned identity auth info.
        Usage: --user-assigned-identity id=XX

        id      : Required. Client Id of the user assigned managed identity.


Examples:
    Create a webapp and keyvault connection with default auth type.
        az webapp connection create keyvault --connection-name <XX> --source-id <XX> --target-id <XX>
        
    Create a webapp and keyvault connection with service principal.
        az webapp connection create keyvault \
            --source-resource-group <XX> --connection-name <XX> --client-type <XX> \
            --target-resource-group=<XX> --keyvault-name=<XX> \
            --service-principal id=<XX> secret=<XX>
```