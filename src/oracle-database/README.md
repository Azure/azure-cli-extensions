# Azure CLI OracleDatabase Extension #
This is an extension to Azure CLI to manage OracleDatabase resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name oracle-database
```
## Included Features ##
Provision and Manage Oracle Databases, Exadata, Resource Anchors, Network Anchors, and Autonomous Databases
Create a Resource Anchor

#### Create an Autonomous Database ####
az oracle-database autonomous-database create --resource-group MyResourceGroup --location eastus --autonomousdatabasename MyAutoDB --db-version 19c --admin-password <password> --compute-model ECPU --compute-count 2 --data-storage-size-in-gbs 1024 --license-model LicenseIncluded

#### Show an Autonomous Database ####
az oracle-database autonomous-database show --name MyAutoDB --resource-group MyResourceGroup

#### List Autonomous Databases ####
az oracle-database autonomous-database list --resource-group MyResourceGroup

#### Delete an Autonomous Database ####
az oracle-database autonomous-database delete --name MyAutoDB --resource-group MyResourceGroup --yes --no-wait

#### Create an Exadb VM Cluster ####
az oracle-database exadb-vm-cluster create --name MyVmCluster --resource-group MyResourceGroup --location eastus --zone 1 --exascale-db-storage-vault-id <vault_id> --display-name MyVmCluster --enabled-ecpu-count 16 --grid-image-ocid <ocid> --hostname myexahost --node-count 2 --shape Exadata.X9M --ssh-public-keys '<ssh_key>' --vnet-id <vnet_id> --subnet-id <subnet_id> --total-ecpu-count 32 --vm-file-system-storage total-size-in-gbs=1024

#### Show a VM Cluster ####
az oracle-database exadb-vm-cluster show --name MyVmCluster --resource-group MyResourceGroup

#### List VM Clusters ####
az oracle-database exadb-vm-cluster list --resource-group MyResourceGroup

#### Delete a VM Cluster ####
az oracle-database exadb-vm-cluster delete --name MyVmCluster --resource-group MyResourceGroup --yes --no-wait

#### Create an Exascale DB Storage Vault ####
az oracle-database exascale-db-storage-vault create --name MyVault --resource-group MyResourceGroup --location eastus --zone 1 --display-name MyVault --high-capacity-database-storage-input total-size-in-gbs=300

#### Show a Storage Vault ####
az oracle-database exascale-db-storage-vault show --name MyVault --resource-group MyResourceGroup

#### List Storage Vaults ####
az oracle-database exascale-db-storage-vault list --resource-group MyResourceGroup

#### Delete a Storage Vault ####
az oracle-database exascale-db-storage-vault delete --name MyVault --resource-group MyResourceGroup --yes --no-wait

#### Create a Resource Anchor ####
az oracle-database resource-anchor create --name MyResourceAnchor --resource-group MyResourceGroup --location global

#### Show a Resource Anchor ####
az oracle-database resource-anchor show --name MyResourceAnchor --resource-group MyResourceGroup

#### List Resource Anchors ####
az oracle-database resource-anchor list --resource-group MyResourceGroup

#### Delete a Resource Anchor ####
az oracle-database resource-anchor delete --name MyResourceAnchor --resource-group MyResourceGroup --yes --no-wait

#### Create a Network Anchor ####
az oracle-database network-anchor create --name MyNetworkAnchor --resource-group MyResourceGroup --location eastus --resource-anchor-id <resource_anchor_id> --subnet-id <subnet_id> --zone 1

#### Show a Network Anchor ####
az oracle-database network-anchor show --name MyNetworkAnchor --resource-group MyResourceGroup

#### List Network Anchors ####
az oracle-database network-anchor list --resource-group MyResourceGroup

#### Delete a Network Anchor ####
az oracle-database network-anchor delete --name MyNetworkAnchor --resource-group MyResourceGroup --yes --no-wait

#### Create a DB System ####
az oracle-database db-system create --name MyDbSystem --resource-group MyResourceGroup --location eastus --zones 1 --database-edition EnterpriseEdition --admin-password <password> --resource-anchor-id <resource_anchor_id> --network-anchor-id <network_anchor_id> --hostname mydbhost --shape VM.Standard.E5.Flex --display-name MyDbSystem --node-count 1 --initial-data-storage-size-in-gb 256 --compute-model OCPU --compute-count 4 --db-version 19.27.0.0 --pdb-name mypdb --db-system-options storage-management=LVM --ssh-public-keys '<ssh_key>'

#### Show a DB System ####
az oracle-database db-system show --name MyDbSystem --resource-group MyResourceGroup

#### List DB Systems ####
az oracle-database db-system list --resource-group MyResourceGroup

#### Delete a DB System ####
az oracle-database db-system delete --name MyDbSystem --resource-group MyResourceGroup --yes --no-wait

### More Information ###
az oracle-database --help
az oracle-database <subgroup> --help
az oracle-database <subgroup> <command> --help