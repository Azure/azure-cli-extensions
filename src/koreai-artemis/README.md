# Azure CLI Kore.ai Artemis extension

This extension manages Kore.ai Artemis organizations, workspaces, and linked
Microsoft SaaS marketplace resources.

## Install

```bash
az extension add --name koreai-artemis
```

## Examples

```bash
az koreai artemis organization list
az koreai artemis organization show \
  --resource-group contoso-rg \
  --organization-name contoso-org
az koreai artemis organization workspace list \
  --resource-group contoso-rg \
  --organization-name contoso-org
```

Run `az koreai artemis --help` to see the complete preview command surface.