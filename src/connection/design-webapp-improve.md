# Service Connector Command Interface

## az {source} connect
```
Group
    az webapp connect: Manage webapp connections.

Subgroups:
    keyvault      : Manage webapp connections with keyvault.
    storage-blob  : Manage webapp connections with storage-blob.
    storage-file  : Manage webapp connections with storage-file.
    storage-queue : Manage webapp connections with storage-queue.
    storage-table : Manage webapp connections with storage-table.
    ...           : ...

Commands:
    list-support-type  : List webapp supported connection types.
    list               : List connections which connects to a webapp.
    list-configuration : List source configurations for a webapp connection.
    delete             : Delete a webapp connection.
    show               : Get the details of a webapp connection.
    validate           : Validate a connection.
```

## az {source} connect list-support-type
```
Command
    az webapp connect list-support-type : List webapp supported connection types.

Arguments
    --target

Examples:
    az webapp connect list-support-type --target keyvault -o table

    ====================sample output===================
        Target              AuthType
        --------------------------------------------
        keyvault            service-principal
        keyvault            system-managed-identity
        keyvault            user-managed-identity
    ====================sample output===================
```


## az {source} connect list
```
Command
    az webapp connect list  :   List webapp connections.
 
Arguments
    --source-resource-group :   The resource group which contains the webapp.
    --webapp-name           :   The name of the webapp.
    --source-id             :   The resource id of the webapp.

Examples:
    az webapp connect list --source-id <XX>
    az webapp connect list --source-resource-group <XX> --webapp-name <XX> 
```


## az {source} connect delete

```
Command
    az webapp connect delete  : Delete a webapp connection.

Arguments
    --source-resource-group         :   The resource group which contains the webapp.
    --webapp-name                   :   The name of the webapp.
    --source-id                     :   The resource id of the webapp.
    --connection-name   [Required]  :   The connection name.

Examples:
    az webapp connect delete --source-id <XX> --connection-name <XX>
    az webapp connect delete --webapp-name <XX> --source-resource-group <XX> --connection-name <XX>
```


## az {source} connect show

```
Command
    az webapp connect show  : Get the details of a webapp connection.

Arguments
    --source-resource-group         :   The resource group which contains the webapp.
    --webapp-name                   :   The name of the webapp.
    --source-id                     :   The resource id of the webapp.
    --connection-name   [Required]  :   The connection name.

Examples:
    az webapp connect show --source-id <XX> --connection-name <XX>
    az webapp connect show --webapp-name <XX> --source-resource-group <XX> --connection-name <XX>
```


## az {source} connect list-configuration

```
Command
    az webapp connect list-configuration  : List the source configurations of a webapp connection.

Arguments
    --source-resource-group         :   The resource group which contains the webapp.
    --webapp-name                   :   The name of the webapp.
    --source-id                     :   The resource id of the webapp.
    --connection-name   [Required]  :   The connection name.

Examples:
    az webapp connect list-configuration \
        --source-id <XX> --connection-name <XX>
    az webapp connect list-configuration \
        --webapp-name <XX> --source-resource-group <XX> --connection-name <XX>
```


## az {source} connect validate

```
Command
    az webapp connect list-configuration  : List the source configurations of a webapp connection.

Arguments
    --source-resource-group         :   The resource group which contains the webapp.
    --webapp-name                   :   The name of the webapp.
    --source-id                     :   The resource id of the webapp.
    --connection-name   [Required]  :   The connection name.

Examples:
    az webapp connect validate --source-id <XX> --connection-name <XX>
    az webapp connect validate --webapp-name <XX> --source-resource-group <XX> --connection-name <XX>
```

## az {source} connect {target}
```
Group
    az webapp connect keyvault : Manage webapp connections with keyvault.

Commands:
    create  : Create a webapp connection with keyvault.
    update  : Update an existing connection.
```

## az {source} connect {target} create/update
```
Command
    az webapp connect keyvault create  : Create a webapp and keyvault connection.


Arguments
    --source-resource-group         :   The resource group which contains the webapp.
    --webapp-name                   :   The name of the webapp.
    --source-id                     :   The resource id of the webapp.
    --connection-name   [Required]  :   The connection name.
    --client-type                   :   The client type of the webapp.


Target Resource Arguments
    --target-resource-group     :   The resource group which contains the target resource.
    --keyvault-name:            :   The name of the keyvault.
    --target-id                 :   The resource id of the keyvault.


Auth Type Arguments
    --secret
        Usage: --secret name=XX secret=XX

        name        :   The user name of an account.
        secret      :   The secret of the account.
    
    --service-principal
        Usage: --service-principal id=XX secret=XX

        id          :   Service principal name, or object id. (refer `az ad sp show`)
        secret      :   The service principal secret.
        certificate :   The service principal certificate.

    --user-assigned-identity
        Usage: --user-assigned-identity id=XX

        id          :   The client id of a user assigned managed identity.

    --system-assigned-identity


Examples:
    Create a webapp and keyvault connection with default auth type.
        az webapp connect keyvault create --connection-name <XX> --source-id <XX> --target-id <XX>
        
    Create a webapp and keyvault connection with service principal.
        az webapp connect keyvault create \
            --source-resource-group <XX> --connection-name <XX> --client-type <XX> \
            --target-resource-group=<XX> --keyvault-name=<XX> \
            --service-principal id=<XX> secret=<XX>
```