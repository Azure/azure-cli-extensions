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


**Command examples**

Fetch a single manifest
```bash
az acr query -n MyRegistry -q "Manifests | limit 1"
```
\
List all manifests within a repository in order of creation date
```bash
az acr query -n MyRegistry --repository MyRepository -q "Manifests | order by createdAt desc"
```
\
Query for images that have a specific OS and architecture
```bash
az acr query -n MyRegistry -q "Manifests | where mediaType == 'application/vnd.docker.distribution.manifest.v2+json' and os == 'linux' and architecture == 'amd64'"
```
\
Query for images that are larger than 1 GB and order response based on image size

```bash
az acr query -n MyRegistry -q "Manifests | where mediaType == 'application/vnd.docker.distribution.manifest.v2+json' | where imageSize > 1000000000 | project imageSize, digest, repository | order by imageSize desc"
```
\
Query for all digests in 'MyRegistry' signed by 'wabbit-networks.io' in the repository 'MyRepository'

```bash
az acr query -n MyRegistry --repository MyRepository -q "Manifests | where annotations['org.cncf.notary.signature.subject'] == 'wabbit-networks.io' | project createdAt, digest, subject, repository"
```