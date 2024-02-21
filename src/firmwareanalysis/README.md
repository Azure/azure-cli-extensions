# Azure CLI Firmwareanalysis Extension #
This is an extension to Azure CLI to manage Firmwareanalysis resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name firmwareanalysis
```

### Included Features
##### Create a workspace.
```
az firmwareanalysis workspace create \
    --resource-group my-rg \
    --name my-workspace \
    --location westus \
    --tags {key:value}
```

##### Show a workspace.
```
az firmwareanalysis workspace show \
    --resource-group my-rg \
    --workspace-name my-workspace
```

##### List all workspaces.
```
az firmwareanalysis workspace list \
    --resource-group my-rg
```

##### Delete a workspace.
```
az firmwareanalysis workspace delete \
    --resource-group my-rg \
    --workspace-name my-workspace
```

##### Generate an url for file upload.
```
az firmwareanalysis workspace generate-upload-url \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id
```

##### Create a firmware.
```
az firmwareanalysis firmware create \
    --resource-group my-rg \
    --name my-workspace \
    --file-name file-name \
    --file-size file-size \
    --vendor vendor \
    --version version \
    --description description \
    --model model
```

##### Show a firmware.
```
az firmwareanalysis firmware show \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id
```

##### List all firmwares.
```
az firmwareanalysis firmware list \
    --resource-group my-rg \
    --workspace-name my-workspace
```

##### Delete a firmware.
```
az firmwareanalysis firmware delete \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id
```

##### List cryptographic certificate analysis results found in a firmware.
```
az firmwareanalysis firmware crypto-certificate \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id
```

##### List cryptographic key analysis results found in a firmware.
```
az firmwareanalysis firmware crypto-key \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id
```

##### List cve analysis results found in a firmware.
```
az firmwareanalysis firmware cve \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id
```

##### List password hash analysis results found in a firmware.
```
az firmwareanalysis firmware password-hash \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id
```

##### List binaryhardening analysis results found in a firmware.
```
az firmwareanalysis firmware binary-hardening \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id
```

##### List sbom component analysis results found in a firmware.
```
az firmwareanalysis firmware sbom-component \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id
```

##### Get a url for tar file download.
```
az firmwareanalysis firmware generate-filesystem-download-url \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id
```

##### Get an analysis result summary of a firmware by name.
```
az firmwareanalysis firmware summary \
    --resource-group my-rg \
    --workspace-name my-workspace \
    --firmware-id firmware-id \
    --n type
```