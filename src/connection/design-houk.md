# Service Connector Command Interface

## az connection list-support-type

```
Arguments
    --source
    --target
    --auth-type

Global Arguments
    --...

Examples:
    az connection list-available --source webapp -o table

    =======================sample output======================
        Source          Target              AuthType
        ------------------------------------------------------
        webapp          postgres            secret
        webapp          storage-blob        secret
        webapp          storage-blob        service-principal
        webapp          ...                 ...
    =======================sample output======================
```


## az connection create/update

```
Arguments
    --connection-name   [Required]:

Source Services
    --source-id

    --webapp
        Usage: --webapp resource-group=XX name=XX

        resource-group:
        name: 

    --spring-cloud
        Usage: --spring-cloud resource-group=XX name=XX

        resource-group:
        name:
    
    --...

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
        --connection-name <XX> \
        --webapp resource-group=<XX> name=<XX> \
        --postgres resource-group=<XX> server-name=<XX> database-name=<XX> \
        --secret name=<XX> secret=<XX>

    az connection create \
        --connection-name <XX> \
        --source-id <XX> \
        --target-id <XX> \
        --secret name=<XX> secret=<XX>
```


## az connection delete

```
Arguments
    --connection-name   [Required]:

Source Services
    --source-id

    --webapp
        Usage: --webapp resource-group=XX name=XX

        resource-group:
        name: 

    --spring-cloud
        Usage: --spring-cloud resource-group=XX name=XX

        resource-group:
        name:

    --...

Global Arguments
    --...

Examples:
    az connection delete \
        --connection-name <XX> \
        --webapp resource-group=<XX> name=<XX>
    
    az connection delete \
        --connection-name <XX> \
        --source-id <XX>
```


## az connection show

```
Arguments
    --connection-name   [Required]:

Source Services
    --source-id

    --webapp
        Usage: --webapp resource-group=XX name=XX

        resource-group:
        name: 

    --spring-cloud
        Usage: --spring-cloud resource-group=XX name=XX

        resource-group:
        name:

    --...

Global Arguments
    --...

Examples:
    az connection show \
        --connection-name <XX> \
        --webapp resource-group=<XX> name=<XX>
    
    az connection show \
        --connection-name <XX> \
        --source-id <XX>
```


## az connection list

```
Source Services
    --source-id

    --webapp
        Usage: --webapp resource-group=XX name=XX

        resource-group:
        name: 

    --spring-cloud
        Usage: --spring-cloud resource-group=XX name=XX

        resource-group:
        name:

    --...

Global Arguments
    --...

Examples:
    az connection list \
        --webapp resource-group=<XX> name=<XX>
    
    az connection list \
        --source-id <XX>
```


## az connection list-configuration

```
Arguments
    --connection-name   [Required]:

Source Services
    --source-id

    --webapp
        Usage: --webapp resource-group=XX name=XX

        resource-group:
        name: 

    --spring-cloud
        Usage: --spring-cloud resource-group=XX name=XX

        resource-group:
        name:

    --...

Global Arguments
    --...

Examples:
    az connection list-configuration \
        --connection-name <XX> \
        --webapp resource-group=<XX> name=<XX>
    
    az connection list-configuration \
        --connection-name <XX> \
        --source-id <XX>
```


## az connection validate

```
Arguments
    --connection-name   [Required]:

Source Services
    --source-id

    --webapp
        Usage: --webapp resource-group=XX name=XX

        resource-group:
        name: 

    --spring-cloud
        Usage: --spring-cloud resource-group=XX name=XX

        resource-group:
        name:

    --...

Global Arguments
    --...

Examples:
    az connection validate \
        --connection-name <XX> \
        --webapp resource-group=<XX> name=<XX>
    
    az connection validate \
        --connection-name <XX> \
        --source-id <XX>
```