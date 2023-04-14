Microsoft Azure CLI 'acrquery' Extension
==========================================

This package is for the 'acrquery' extension to support the Azure Container Registry metadata querying feature.

Install via: 
`az extension add --name acrquery`

## Background
The az acr query extension provides support to KQL (Kusto Querying Language) queries against manifests within Azure Container Registries. In the future, ACR may support additional tables, such as Tags or Layers.

**Command arguments**

| Command argument | Definition | Required | Type |
|--|--|--|--|
| `--name`/`-n` | The name of the container registry that the query is run against. | Yes | String |
| `--repository` | The repository that the query is run against. If no repository is provided, the query is run at the registry level.  | No | String |
| `--kql-query`/`-q` | The KQL query to execute. | Yes | String |
| `--skip-token` | Skip token to get the next page of the query if applicable. | No | String |


**Command example**

Query for all digests in 'MyRegistry' signed by 'wabbit-networks.io' in the repository 'MyRepository'

```bash
az acr query -n MyRegistry --repository MyRepository -q "Manifests | where annotations['org.cncf.notary.signature.subject'] == 'wabbit-networks.io' | project createdAt, digest, subject"
```