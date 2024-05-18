# Azure CLI StorageActions Extension #
This is an extension to Azure CLI to manage StorageActions resources.

## How to use ##
### az storage-actions task create ###
```commandline
az storage-actions task create -g rgteststorageactions -n testtask1 --identity "{type:SystemAssigned}" 
--tags "{key1:value1}" --action "{if:{condition:'[[equals(AccessTier,'/Cool'/)]]',
operations:[{name:'SetBlobTier',parameters:{tier:'Hot'},onSuccess:'continue',onFailure:'break'}]},
else:{operations:[{name:'DeleteBlob',onSuccess:'continue',onFailure:'break'}]}}" 
--description StorageTask1 --enabled true
```

### az storage-actions task show ###
```commandline
az storage-actions task show -g rgteststorageactions -n testtask1
```

### az storage-actions task update ###
```commandline
az storage-actions task update -g rgteststorageactions -n testtask1 --identity "{type:SystemAssigned}" 
--tags "{key2:value2}" --action "{if:{condition:'[[equals(BlobType,'/BlockBlob'/)]]',
operations:[{name:'SetBlobTags',parameters:{Archive-Status:'Archived'},onSuccess:'continue',onFailure:'break'}]},
else:{operations:[{name:'UndeleteBlob',onSuccess:'continue',onFailure:'break'}]}}" 
--description StorageTask1Update --enabled true
```

### az storage-actions task list ###
```commandline
az storage-actions task list -g rgteststorageactions
```

### az storage-actions task delete ###
```commandline
az storage-actions task delete -g rgteststorageactions -n testtask1
```

### az storage-actions task list-assignment ###
```commandline
az storage-actions task list-assignment -g rgteststorageactions -n testtask1
```

### az storage-actions task list-report ###
```commandline
az storage-actions task list-report -g rgteststorageactions -n testtask1
```

### az storage-actions task preview-action ###
```commandline
az storage-actions task preview-action -l eastus2euap --action "{if:{condition:'[[equals(AccessTier,'/Cool'/)]]'},
else-block-exists:True}" --blobs "[{name:'folder2/file1.txt',
properties:[{key:'Creation-Time',value:'Wed, 06 Jun 2023 05:23:29 GMT'},
{key:'Last-Modified',value:'Wed, 06 Jun 2023 05:23:29 GMT'},
{key:'Etag',value:'0x6FB67175454D36D'}],metadata:[{key:'mKey2',value:'mValue2'}],
tags:[{key:'tKey2',value:'tValue2'}]}]" --container "{name:'firstContainer',
metadata:[{key:'mContainerKey1',value:'mContainerValue1'}]}"
```

