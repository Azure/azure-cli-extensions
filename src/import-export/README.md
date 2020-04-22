# Azure CLI import-export Extension #
This package is for the 'import-export' extension, i.e. 'az import-export'.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name import-export
```

### Included Features
#### Import Export Management:
Manage Import Export: [more info](https://docs.microsoft.com/en-us/azure/storage/common/storage-import-export-service)\
*Examples:*

##### List locations to which you can ship the disks

```
az import-export location list
```

##### Show locations to which you can ship the disks

```
az import-export location show --location "West US"
```

##### Create an Import Job

```
az import-export create \
    --resource-group groupName \
    --name jobName \
    --location localtionName \
    --type Import \
    --log-level Verbose \
    --storage-account storageAccountID \
    --backup-drive-manifest true \
    --diagnostics-path waimportexport \
    --drive-list \
    drive-id=00000001 \
    bit-locker-key=000000-000000-000000-000000-000000-000000-000000-000000 \
    drive-header-hash="" \
    manifest-file=\\DriveManifest.xml \
    manifest-hash=109B21108597EF36D5785F08303F3638 \
    --return-address \
    city=Redmond \
    country-or-region=USA \
    email=Test@contoso.com \
    phone=4250000000 \
    postal-code=98007 \
    recipient-name=Tests \
    state-or-province=wa \
    street-address1=Street1 \
    street-address2=street2
```

##### Update an Import Job

```
az import-export update \
    --resource-group groupName \
    --name jobName \
    --cancel-requested true
```

##### List Import Export Jobs

```
az import-export list \
    --resource-group groupName
```

##### Delete a Job

```
az import-export delete \
    --resource-group groupName \
    --name jobName
```

##### List bit locker keys of a Job

```
az import-export bit-locker-key list \
    --resource-group groupName \
    --job-name jobName
```


If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.

