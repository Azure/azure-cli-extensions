# Service Connector Command Interface

## az webapp connection list-support-type

```
Arguments
    --target
    --auth-type

Global Arguments
    --...

Examples:
    az webapp connection list-support-type -o table

    ===============sample output==============
        Target              AuthType
        --------------------------------------
        postgres            secret
        storage-blob        secret
        storage-blob        service-principal
        ...                 ...
    ===============sample output==============
```


## az webapp connection create/update

```
Arguments
    --connection-name   [Required]:
    --resource-group    [Required]:
    --webapp-name       [Required]:
    --source-id

Target Services
    --target-id

    --postgres
        Usage: --postgres resource-group=XX server-name=XX database-name=XX

        resource-group:
        server-name:
        database-name:

    --storage-blob
        Usage: --storage-blob --storage-blob target-resource-group=XX account-name=XX

        resource-group:
        account-name:
    
    --...

AuthType
    --secret
        Usage: --secret name=XX secret=XX

        name:
        secret:
    
    --service-principal
        Usage: --service-principal id=XX secret=XX

        id: Service principal name, or object id. (refer `az ad sp show`)
        secret:
        certificate

    --user-assigned-identity
        Usage: --user-assigned-identity id=XX

        id:

    --system-assigned-identity

Global Arguments
    --...

Examples:
    az connection create \
        --webapp-name <XX> --resource-group <XX> --connection-name <XX> \
        --postgres resource-group=<XX> server-name=<XX> database-name=<XX> \
        --secret name=<XX> secret=<XX>

    az connection create \
        --connection-name <XX> \
        --source-id <XX> \
        --target-id <XX> \
        --secret name=<XX> secret=<XX>
```


## az webapp connection delete

```
Arguments
    --connection-name   [Required]:
    --resource-group    [Required]:
    --webapp-name       [Required]:
    --source-id

Global Arguments
    --...

Examples:
    az connection delete \
        --webapp-name <XX> --resource-group <XX> --connection-name <XX>
    
    az connection delete \
        --connection-name <XX> \
        --source-id <XX>
```


## az webapp connection show

```
Arguments
    --connection-name   [Required]:
    --resource-group    [Required]:
    --webapp-name       [Required]:
    --source-id

Global Arguments
    --...

Examples:
    az connection show \
        --webapp-name <XX> --resource-group <XX> --connection-name <XX>
    
    az connection show \
        --connection-name <XX> \
        --source-id <XX>
```


## az webapp connection list

```
Arguments
    --resource-group    [Required]:
    --webapp-name       [Required]:
    --source-id

Global Arguments
    --...

Examples:
    az connection list \
        --webapp-name <XX> --resource-group <XX> \
    
    az connection list \
        --source-id <XX>
```


## az webapp connection list-configuration

```
Arguments
    --connection-name   [Required]:
    --resource-group    [Required]:
    --webapp-name       [Required]:
    --source-id

Global Arguments
    --...

Examples:
    az connection list-configuration \
        --webapp-name <XX> --resource-group <XX> --connection-name <XX>
    
    az connection list-configuration \
        --connection-name <XX> \
        --source-id <XX>
```


## az webapp connection validate

```
Arguments
    --connection-name   [Required]:
    --resource-group    [Required]:
    --webapp-name       [Required]:
    --source-id

Global Arguments
    --...

Examples:
    az connection validate \
        --webapp-name <XX> --resource-group <XX> --connection-name <XX>
    
    az connection validate \
        --connection-name <XX> \
        --source-id <XX>
```