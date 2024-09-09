# Azure CLI AzureTerraform Extension #
This is an extension to Azure CLI for Terraform user experience on Azure.

## How to use ##

Install the latest version of the extension:

```
az extension add --name azure-terraform
```

Validate that the extension is installed correctly:

```
az azure-terraform --help
```

## Included Features ##

Below is a high-level overview of azure-terraform commands.

| Commands                                       | Description                                                                        |
|------------------------------------------------|------------------------------------------------------------------------------------|
| az azure-terraform export-terraform            | Exports the Terraform configuration of the specified scope                         |
