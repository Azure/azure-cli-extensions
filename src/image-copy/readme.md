# Azure CLI Image Copy Extension #
This is an extension to azure cli that allows copying virtual machine images between regions with just one command.

The extension simplifies the process and also enables you to save time by copying to multiple regions in parallel.

## How to use ##
First, install the extension:
```
az extension add --name image-copy-extension
```

Then, call it as you would any other az command:
```
az image copy --source-resource-group mySources-rg --source-object-name myImage --target-location uksouth northeurope --target-resource-group "images-repo-rg" --cleanup
```

One thing you should keep in mind is that we are relying on the source os disk as the actual source for the copy. So, when you "capture" a new image off a vm in Azure, don't delete the os disk if your intention is to copy it to other regions.

Other options and examples of using the extensions can be viewed with the help command:
```
az image copy --help
```