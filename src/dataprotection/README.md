# Azure CLI dataprotection Extension #
This is the extension for dataprotection

### How to use ###
Install this extension using the below CLI command
```
az extension add --name dataprotection
```

### Included Features ###
#### Configure backup ####
##### Initialize configure backup request #####
```
az dataprotection backup-instance initialize --datasource-type AzureDisk -l southeastasia \
    --policy-id {disk_policy_id} --datasource-id {disk_id}
```

Please copy paste the output of the above command and save it in a json file. e.g. backup_instance.json.
Based on datasource type, you might have to edit the json file and add some parameters.

##### Validate configure backup request #####
```
az dataprotection backup-instance validate-for-backup -g sarath-rg --vault-name sarath-vault --backup-instance backup_instance.json
```

If validation fails then please fix the error by following the recommendations.
##### Configure backup #####
```
az dataprotection backup-instance create -g MyResourceGroup --vault-name MyVault --backup-instance backup_instance.json
```
#### Create Policy ####
##### Get default policy template #####
```
az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk
```
Save the output of above command in a json file. e.g. defaultpolicy.json
##### Add retention rule to default policy #####
```
az dataprotection backup-policy retention-rule create-lifecycle --retention-duration-count 12 \
    --retention-duration-type Days --source-datastore OperationalStore
```
Save the output of above command in a json file e.g. lifecycle.json
```
az dataprotection backup-policy retention-rule set --lifecycles lifecycle.json --name Daily --policy defaultpolicy.json
```
Save the output of above command in a json file e.g. editedpolicy.json
##### Add tag rule to policy #####
```
az dataprotection backup-policy tag create-absolute-criteria --absolute-criteria FirstOfDay
```
Save the output of above command in a json file e.g. criteria.json
```
az dataprotection backup-policy tag set --criteria criteria.json --name Daily --policy editedpolicy.json
```
##### Create backup policy #####
```
az dataprotection backup-policy create -g sarath-rg --vault-name sarath-vault -n mypolicy --policy policy.json
```
#### Restore a backup instance ####
##### Initialize restore request for item recovery #####
```
az dataprotection backup-instance restore initialize-for-data-recovery --datasource-type AzureBlob \
    --restore-location centraluseuap --source-datastore OperationalStore --backup-instance-id {backup_instance_id} \
    --point-in-time 2021-05-26T15:00:00 --container-list container1 container2
```
##### Initialize restore request for data recovery #####
```
az dataprotection backup-instance restore initialize-for-data-recovery --datasource-type AzureDisk \
    --restore-location centraluseuap --source-datastore OperationalStore --target-resource-id {restore_disk_id} \
    --recovery-point-id b7e6f082-b310-11eb-8f55-9cfce85d4fae
```
##### Validate restore request #####
```
az dataprotection backup-instance validate-for-restore --name "testInstance1" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" --restore-request-object restore_request.json
```
##### Trigger restore #####
```
az dataprotection backup-instance restore trigger -g sarath-rg --vault-name sarath-vault \
    --backup-instance-name {backup_instance_name} --restore=request-object restore_request.json
```

#### Azure Cosmos DB for NoSQL database/container recovery ####

Item-level recovery selects databases and containers from a completed, committed
`VaultStore` recovery point; it does not select individual documents or perform
Cosmos-native point-in-time recovery. The target must be a pre-existing,
compatible, **completely empty NoSQL account**, distinct from the source, in the
same region for this workflow. Use its account ARM ID, not a database/container
ID, endpoint or backup instance ID. `FailIfExists` does not authorize overwrite
or deletion. CRR/CSR, original-location restore, rename and restore-as-files are
not part of this workflow.

Prerequisites: an already protected source account, its backup instance and a
completed VaultStore recovery point, an empty target account, and a usable vault
managed identity. The protected source requires continuous backup; that setting
is separate from vault retention. This guide creates no accounts, policies or
backup instances and changes no retention settings. All placeholders below are
synthetic; replace them with approved resources. These examples are usage
instructions, not a claim of live CLI acceptance or completed restore testing.

**Selection contract:** supply 1–50 quoted, literal `database` or
`database/container` names. A database selects its backed-up containers at the
chosen recovery point, not today's source inventory. Mixed selections retain
their exact order, spelling, case, spaces and Unicode. `DB1` and `db1` are
different. No trimming, case folding, URL decoding, sorting, comma/brace splitting
or wildcard expansion occurs; `*`, commas and braces are literal name characters.
Exact duplicates and a database selected together with its containers are
rejected. Empty/blank segments, more than one `/`, backslashes, `?`, `#` and
control characters are invalid. No rename, AKS filters/staging or Blob
container-list/prefix/range options are supported. Local syntax acceptance does
not establish that a name exists in the recovery point.

##### 1. Construct configuration and request locally (no authentication) #####

The following Bash examples use explicit system-assigned identity (SAMI)
throughout. Both initialization commands only construct and validate local JSON;
they do not log in, enumerate inventory, check target emptiness in Azure, grant
roles or submit a restore. Use `--output json` and save files as UTF-8. On Windows
PowerShell 5.1, use `| Set-Content -Encoding utf8 cosmos-config.json` (and likewise
for the request) instead of `>`, which writes UTF-16; adapt line continuations
to the shell.

```bash
az dataprotection backup-instance initialize-restoreconfig \
    --datasource-type AzureCosmosDB \
    --resource-identifiers 'db1/col1' 'db1/col2' 'db2' \
    --output json > cosmos-config.json

az dataprotection backup-instance restore initialize-for-item-recovery \
    --datasource-type AzureCosmosDB \
    --source-datastore VaultStore \
    --restore-location '<target-region>' \
    --recovery-point-id '<recovery-point-name>' \
    --target-resource-id '/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/restore-rg/providers/Microsoft.DocumentDB/databaseAccounts/empty-target' \
    --restore-configuration @cosmos-config.json \
    --mi-system-assigned true \
    --output json > cosmos-request.json
```

The configuration is one `GenericRestoreDatasourceCriteria` object with one
`ResourceListSelectionCriteria` containing the whole ordered list. Initialization
revalidates edited configuration and places it in the request's criteria array.
Keep the resulting **raw request** as input to both native validation and
trigger commands; do not add a `restoreRequestObject` wrapper yourself.

**UAMI alternative:** instead of the SAMI initialization above, use the same
command with `--uami '<attached-uami-arm-id>'` in place of
`--mi-system-assigned true`. A UAMI alone implies system-assigned `false`; explicit
`--mi-system-assigned false --uami '<attached-uami-arm-id>'` is also valid. Cosmos
rejects explicit `false` without a UAMI, `true` with a UAMI, and invalid UAMI ARM
IDs. Omitting both identity arguments leaves identity details unset; no service
default is implied. Use an identity already attached to the vault, not a source
account identity or an arbitrary unattached UAMI.

##### 2. Prepare permissions (authenticated cloud access and possible RBAC writes) #####

Authenticate to the intended tenant/subscription before continuing. The caller
needs permission to read the vault, inspect role assignments and grant the
required target role. Review the target ID and selected identity before accepting
the prompt. This command can grant `Cosmos DB Operator` to the selected vault
identity on the target account; `Resource` keeps the assignment scope narrow.
Declining confirmation makes no writes. `--yes` skips confirmation and is
intentionally omitted here; this is not a dry-run command.

```bash
az dataprotection backup-instance update-msi-permissions \
    --subscription '<vault-subscription-id>' \
    --resource-group '<vault-resource-group>' \
    --vault-name '<vault-name>' \
    --datasource-type AzureCosmosDB \
    --operation Restore \
    --permissions-scope Resource \
    --restore-request-object @cosmos-request.json
```

For Cosmos Restore, permission preparation accepts CLI client `snake_case` and
wire `camelCase` schema aliases, but rejects conflicting aliases for the same
field. It automatically selects the UAMI specified in the request, so the command
above also applies to the UAMI alternative. If you additionally pass `--uami`, it
must match the request-selected identity case-insensitively. Vault attachment ARM
IDs are also matched case-insensitively; missing/ambiguous attachments or missing
principal IDs are rejected, with no fallback to SAMI or the first attached UAMI.
These compatibility rules are Cosmos-scoped. Executing-user Cosmos SQL data-plane
permissions for verification are separate from vault management-plane roles;
do not grant Owner or weaken keys/firewalls to work around failures.

When request identity details are omitted, the helper retains legacy permission-side
selection (`--uami`, or SAMI when omitted), but does not insert that selection into the
restore request or establish the service's identity default. Use an explicit request
identity for a verified match between permission preparation and restore. An edited
request identity must explicitly contain a valid Boolean `useSystemAssignedIdentity`;
request member nulls are not equivalent to omitting initializer flags.

##### 3. Validate in Azure (does not restore data) #####

```bash
az dataprotection backup-instance validate-for-restore \
    --subscription '<vault-subscription-id>' \
    --resource-group '<vault-resource-group>' \
    --vault-name '<vault-name>' \
    --backup-instance-name '<source-backup-instance-name>' \
    --restore-request-object @cosmos-request.json
```

This submits a cloud validation operation, not a restore or a completion check.
Resolve any reported errors before triggering; a successful validation is not
proof that restored data exists or that a future restore will complete.

##### 4. Submit once, then inspect the specific returned job #####

Triggering writes to Azure and starts a restore that can incur charges. Confirm
the approved scope and that the target is still completely empty, then submit
**once** and retain the entire response:

```bash
az dataprotection backup-instance restore trigger \
    --subscription '<vault-subscription-id>' \
    --resource-group '<vault-resource-group>' \
    --vault-name '<vault-name>' \
    --backup-instance-name '<source-backup-instance-name>' \
    --restore-request-object @cosmos-request.json \
    --output json > cosmos-trigger-response.json

az dataprotection job show \
    --subscription '<vault-subscription-id>' \
    --resource-group '<vault-resource-group>' \
    --vault-name '<vault-name>' \
    --job-id '<job-id-returned-by-trigger>'
```

Use the trigger response's returned **job ID**, not an ActivityID, correlation ID
or validation operation ID. If a job ARM ID is returned, use its final job-name
segment for `--job-id`. Inspect that specific job until terminal, matching vault,
backup instance, restore operation and recovery point where exposed. Submission
or `InProgress` is not completion. If the trigger response is lost or times out,
**do not blindly retry**: first reconcile the submission using native
`az dataprotection job list` in that vault and the backup instance, operation,
submission time and recovery point where exposed. Identify the specific job or
resolve the uncertain submission before considering another trigger.

After successful job completion, independently verify the exact restored
database/container inventory against the selected recovery point, document IDs,
partition keys, full document content and counts for selected containers, and
absence of every excluded database/container (including unselected siblings).
For a database selector, verify all of that database's containers backed up at
the recovery point, not just those currently present on the source. Counts alone
are insufficient: use expected content captured for that recovery point, not
post-backup source churn. Validation success and job success do not replace these
data and exclusion checks.

**Full-account request shape is preserved:** use
`az dataprotection backup-instance restore initialize-for-data-recovery` with
`--datasource-type AzureCosmosDB`, the VaultStore recovery point, target account
and intended identity, and **omit `--restore-configuration`**. A Cosmos selection
configuration is rejected by that full initializer rather than silently ignored.
No new public arguments or API version change are needed for item-level recovery.

#### Azure Elastic SAN (preview) configure and restore scripts ####
##### Configure backup for Elastic SAN volumes #####
```
# 1) Create backup configuration for selected source volumes in the chosen volume group
az dataprotection backup-instance initialize-backupconfig \
    --datasource-type AzureElasticSAN \
    --resource-selectors volume001 > esan_backup_config.json

# 2) Initialize backup instance payload (datasource-id is the source volume group ARM ID)
az dataprotection backup-instance initialize \
    --datasource-type AzureElasticSAN \
    --datasource-location {location} \
    --datasource-id {source_volume_group_id} \
    --policy-id {esan_policy_id} \
    --friendly-name esan-bi \
    --backup-configuration @esan_backup_config.json > esan_backup_instance.json

# 3) Grant missing backup permissions to vault MSI (Elastic SAN Snapshot Exporter + Disk Snapshot Contributor)
az dataprotection backup-instance update-msi-permissions \
    --datasource-type AzureElasticSAN \
    --operation Backup \
    --permissions-scope Resource \
    --resource-group {vault_rg} \
    --vault-name {vault_name} \
    --backup-instance @esan_backup_instance.json

# 4) Validate and configure backup
az dataprotection backup-instance validate-for-backup \
    --resource-group {vault_rg} \
    --vault-name {vault_name} \
    --backup-instance @esan_backup_instance.json

az dataprotection backup-instance create \
    --resource-group {vault_rg} \
    --vault-name {vault_name} \
    --backup-instance @esan_backup_instance.json
```

##### Restore Elastic SAN backup #####
```
# 1) Build restore configuration: select source volumes and optional target names
az dataprotection backup-instance initialize-restoreconfig \
    --datasource-type AzureElasticSAN \
    --resource-identifiers source-vol1 \
    --resource-name-overrides '{"source-vol1":"restored-vol1"}' > esan_restore_config.json

# 2) Initialize restore request (target-resource-id is target volume group ARM ID).
#    Elastic SAN supports alternate-location restore only, so pass --target-resource-id
#    (do not pass --backup-instance-id; the two are mutually exclusive).
az dataprotection backup-instance restore initialize-for-item-recovery \
    --datasource-type AzureElasticSAN \
    --source-datastore OperationalStore \
    --restore-location {location} \
    --recovery-point-id {recovery_point_id} \
    --target-resource-id {target_volume_group_id} \
    --restore-configuration @esan_restore_config.json > esan_restore_request.json

# 3) Grant missing restore permissions to vault MSI
#    - Elastic SAN Volume Importer on target Elastic SAN
#    - Reader on snapshot resource group (pass --snapshot-resource-group-id)
az dataprotection backup-instance update-msi-permissions \
    --datasource-type AzureElasticSAN \
    --operation Restore \
    --permissions-scope Resource \
    --resource-group {vault_rg} \
    --vault-name {vault_name} \
    --restore-request-object @esan_restore_request.json \
    --snapshot-resource-group-id {snapshot_rg_id}

# 4) Validate and trigger restore
az dataprotection backup-instance validate-for-restore \
    --resource-group {vault_rg} \
    --vault-name {vault_name} \
    --backup-instance-name {backup_instance_name} \
    --restore-request-object @esan_restore_request.json

az dataprotection backup-instance restore trigger \
    --resource-group {vault_rg} \
    --vault-name {vault_name} \
    --backup-instance-name {backup_instance_name} \
    --restore-request-object @esan_restore_request.json
```

#### dataprotection backup-vault ####
##### Create #####
```
az dataprotection backup-vault create --type "None" --location "WestUS" \
    --storage-settings type="LocallyRedundant" datastore-type="VaultStore" --tags key1="val1" \
    --resource-group "SampleResourceGroup" --vault-name "swaggerExample" 
```
##### Show #####
```
az dataprotection backup-vault show --resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
##### Update #####
```
az dataprotection backup-vault update --tags newKey="newVal" --resource-group "SampleResourceGroup" \
    --vault-name "swaggerExample" 
```
##### Delete #####
```
az dataprotection backup-vault delete --resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
#### dataprotection backup-policy ####
##### Show #####
```
az dataprotection backup-policy show --name "OSSDBPolicy" --resource-group "000pikumar" \
    --vault-name "PrivatePreviewVault" 
```
##### List #####
```
az dataprotection backup-policy list --resource-group "000pikumar" --vault-name "PrivatePreviewVault"
```
##### Delete #####
```
az dataprotection backup-policy delete --name "OSSDBPolicy" --resource-group "000pikumar" \
    --vault-name "PrivatePreviewVault" 
```
#### dataprotection backup-instance ####
##### Show #####
```
az dataprotection backup-instance show --name "testInstance1" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" 
```
##### List #####
```
az dataprotection backup-instance list --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1"
```
##### Adhoc-backup #####
```
az dataprotection backup-instance adhoc-backup --name "testInstance1" --rule-name "BackupWeekly" \
    --retention-tag-override "yearly" --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1" 
```

##### Delete #####
```
az dataprotection backup-instance delete --name "testInstance1" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" 
```
#### dataprotection recovery-point ####
##### List #####
```
az dataprotection recovery-point list --backup-instance-name "testInstance1" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" 
```
##### Show #####
```
az dataprotection recovery-point show --backup-instance-name "testInstance1" \
    --recovery-point-id "7fb2cddd-c5b3-44f6-a0d9-db3c4f9d5f25" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" 
```
#### dataprotection job ####
##### List #####
```
az dataprotection job list --resource-group "BugBash1" --vault-name "BugBashVaultForCCYv11"
```
##### Show #####
```
az dataprotection job show --job-id "3c60cb49-63e8-4b21-b9bd-26277b3fdfae" --resource-group "BugBash1" \
    --vault-name "BugBashVaultForCCYv11" 
```
#### dataprotection restorable-time-range ####
##### Find #####
```
az dataprotection restorable-time-range find --backup-instance-name "zblobbackuptestsa58" \
    --end-time "2021-02-24T00:35:17.6829685Z" --source-data-store-type "OperationalStore" \
    --start-time "2020-10-17T23:28:17.6829685Z" --resource-group "Blob-Backup" --vault-name "ZBlobBackupVaultBVTD3" 
```