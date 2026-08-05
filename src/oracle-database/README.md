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
az oracle-database autonomous-database create --resource-group MyResourceGroup --location eastus --autonomousdatabasename MyAutoDB --display-name MyAutoDB --db-version 19c --admin-password <password> --compute-model ECPU --compute-count 2 --data-storage-size-in-gbs 1024 --license-model LicenseIncluded --db-workload OLTP --character-set AL32UTF8 --ncharacter-set AL16UTF16 --vnet-id <vnet_id> --subnet-id <subnet_id> --regular

Use one create mode option per request. The database type is inferred from `--regular`, `--clone`, `--clone-from-backup-timestamp`, or `--cross-region-disaster-recovery`.

Do not pass `dataBaseType` directly. Clone and disaster recovery fields must be nested inside the matching create mode option, for example `--clone clone-type=Full source=Database source-id=<source_autonomous_database_id>`.

#### Clone an Autonomous Database ####
az oracle-database autonomous-database create --resource-group MyResourceGroup --location eastus --autonomousdatabasename MyCloneDB --display-name MyCloneDB --db-version 19c --admin-password <password> --compute-model ECPU --compute-count 2 --data-storage-size-in-gbs 1024 --license-model LicenseIncluded --db-workload OLTP --character-set AL32UTF8 --ncharacter-set AL16UTF16 --vnet-id <vnet_id> --subnet-id <subnet_id> --clone clone-type=Full source=Database source-id=<source_autonomous_database_id>

Use `source=Database` when cloning directly from an existing Autonomous Database. Put clone fields such as `clone-type`, `source`, and `source-id` inside `--clone`. If you pass `--store-auto-scaling`, use the same storage auto-scaling value as the source database. The clone requires a valid networking configuration, such as `--vnet-id` and `--subnet-id`.

#### Clone an Autonomous Database from a backup timestamp ####
az oracle-database autonomous-database create --resource-group MyResourceGroup --location eastus --autonomousdatabasename MyBackupCloneDB --display-name MyBackupCloneDB --db-version 19c --admin-password <password> --compute-model ECPU --compute-count 2 --data-storage-size-in-gbs 32 --license-model BringYourOwnLicense --db-workload OLTP --character-set AL32UTF8 --ncharacter-set AL16UTF16 --vnet-id <vnet_id> --subnet-id <subnet_id> --clone-from-backup-timestamp clone-type=Full source=BackupFromTimestamp source-id=<source_autonomous_database_id> timestamp=2026-06-03T15:45:11.000Z use-latest-available-backup-time-stamp=false

Use `source=BackupFromTimestamp` when cloning from a point-in-time backup. The timestamp uses RFC3339 UTC format. If the backup list only shows seconds, use `.000Z` for the millisecond value. Use `--database-edition` only with `--license-model BringYourOwnLicense`.

#### Create an Autonomous Database cross-region disaster recovery peer ####
az oracle-database autonomous-database create --resource-group MyResourceGroup --location germanywestcentral --autonomousdatabasename MyCrossRegionPeerDB --display-name MyCrossRegionPeerDB --db-version 19c --compute-model ECPU --compute-count 2 --data-storage-size-in-gbs 1024 --license-model LicenseIncluded --character-set AL32UTF8 --ncharacter-set AL16UTF16 --vnet-id <destination_vnet_id> --subnet-id <destination_subnet_id> --cross-region-disaster-recovery remote-disaster-recovery-type=Adg source=CrossRegionDisasterRecovery source-id=<source_autonomous_database_id> source-location=eastus is-replicate-automatic-backups=true

Use top-level `--location` for the destination region where the cross-region DR peer will be created. Use `source-location` for the existing source Autonomous Database region. The destination VNet and subnet must be in the destination region and must be supported for the mapped OCI region.

#### Show an Autonomous Database ####
az oracle-database autonomous-database show --name MyAutoDB --resource-group MyResourceGroup

#### Show Autonomous Database connection strings ####
az oracle-database autonomous-database show --name MyAutoDB --resource-group MyResourceGroup --query "properties.connectionStrings"

Connection strings are available after the Autonomous Database finishes provisioning.

#### List Autonomous Databases ####
az oracle-database autonomous-database list --resource-group MyResourceGroup

#### Delete an Autonomous Database ####
az oracle-database autonomous-database delete --name MyAutoDB --resource-group MyResourceGroup --yes --no-wait

#### Start, stop, or restart an Autonomous Database ####
az oracle-database autonomous-database action --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --action Start

Use `--action Start`, `--action Stop`, or `--action Restart` to run a lifecycle action on an Autonomous Database.

#### Restore an Autonomous Database to a point in time ####
az oracle-database autonomous-database restore --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --timestamp 2026-06-03T15:45:11.000Z

Use an RFC3339 UTC timestamp for `--timestamp`.

#### Shrink an Autonomous Database ####
az oracle-database autonomous-database shrink --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB

Use this command to shrink the current allocated storage down to the current actual used data storage.

#### Enable local Autonomous Data Guard for an Autonomous Database ####
az oracle-database autonomous-database update --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --local-data-guard true --local-adg-auto-failover-max-data-loss-limit 0

Use `--local-data-guard true` to enable local, in-region Autonomous Data Guard for an existing Autonomous Database. Use `--local-adg-auto-failover-max-data-loss-limit` to set the maximum data loss limit, in seconds, for local Autonomous Data Guard automatic failover when supported.

#### Switchover an Autonomous Database disaster recovery peer ####
az oracle-database autonomous-database switchover --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --peer-db-id <peer_database_id> --peer-db-location <peer_region>

#### Failover an Autonomous Database disaster recovery peer ####
az oracle-database autonomous-database failover --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --peer-db-id <peer_database_id> --peer-db-location <peer_region>

#### Wait for an Autonomous Database condition ####
az oracle-database autonomous-database wait --resource-group MyResourceGroup --name MyAutoDB --created

Use `wait` with Azure CLI wait conditions such as `--created`, `--updated`, `--deleted`, or `--exists`.

#### Create an Autonomous Database backup ####
az oracle-database autonomous-database backup create --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --adbbackupid MyBackup01 --display-name "My backup" --retention-period-in-days 30

Use the Azure backup resource name (the final segment of `id` returned by `backup create` or `backup list`) as `--adbbackupid` for all backup operations. Do not pass the full Azure resource ID.

#### List Autonomous Database backups ####
az oracle-database autonomous-database backup list --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB

#### Show an Autonomous Database backup ####
az oracle-database autonomous-database backup show --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --adbbackupid MyBackup01

#### Update an Autonomous Database backup ####
az oracle-database autonomous-database backup update --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --adbbackupid MyBackup01 --retention-period-in-days 60

#### Delete an Autonomous Database backup ####
az oracle-database autonomous-database backup delete --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --adbbackupid MyBackup01 --yes --no-wait

#### Wait for an Autonomous Database backup condition ####
az oracle-database autonomous-database backup wait --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --adbbackupid MyBackup01 --created

For all backup operations, pass the backup resource name rather than its full Azure resource ID.

#### Change Autonomous Database disaster recovery configuration ####
az oracle-database autonomous-database change-disaster-recovery-configuration --resource-group MyResourceGroup --autonomousdatabasename MyCrossRegionPeerDB --disaster-recovery-type Adg --is-replicate-automatic-backups false

Use this command on an Autonomous Database that already has cross-region disaster recovery enabled. Pass the peer Autonomous Database name as `--autonomousdatabasename`.

#### Generate an Autonomous Database Wallet ####
az oracle-database autonomous-database generate-wallet --resource-group MyResourceGroup --autonomousdatabasename MyAutoDB --password <wallet-password> --generate-type All --is-regional true --file wallet-MyAutoDB.zip

Use the wallet when your client connection requires wallet-based authentication, including mTLS connections. The command saves a wallet zip file that includes the database network configuration files such as `tnsnames.ora`, `sqlnet.ora`, and `cwallet.sso`.

#### List Autonomous Database versions ####
az oracle-database autonomous-database version list --location eastus

#### Show an Autonomous Database version ####
az oracle-database autonomous-database version show --location eastus --name 19c

#### List Autonomous Database character sets ####
az oracle-database autonomous-database character-set list --location eastus

#### Show an Autonomous Database character set ####
az oracle-database autonomous-database character-set show --location eastus --name AL32UTF8

#### List Autonomous Database national character sets ####
az oracle-database autonomous-database national-character-set list --location eastus

#### Show an Autonomous Database national character set ####
az oracle-database autonomous-database national-character-set show --location eastus --name AL16UTF16

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
