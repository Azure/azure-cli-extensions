# Azure CLI StorageMover Extension #
This is an extension to Azure CLI to manage StorageMover resources.
It uses the stable management API version `2026-05-01`.

## How to use ##
### Create a top-level Storage Mover resource.
`az storage-mover create -g "rg" -n "mover_name" -l eastus2 --tags {{key1:value1}} --description ExampleDesc`

### Deploy and register an Agent resource, which references a hybrid compute machine that can run jobs.
#### Deploy Agent
https://learn.microsoft.com/en-us/azure/storage-mover/agent-deploy?tabs=xdmshell
#### Register Agent
https://learn.microsoft.com/en-us/azure/storage-mover/agent-register

### Create a Project resource, which is a logical grouping of related jobs.
`az storage-mover project create -g "rg" --storage-mover-name "mover_name" -n "project_name" --description ProjectDesc`

### Create an Endpoint resource for nfs, which represents the data transfer source.
`az storage-mover endpoint create-for-nfs -g "rg" --storage-mover-name "mover_name" -n "source_endpoint" --description srcendpointDesc --export exportfolder --nfs-version NFSv4 --host "vm_ip"`

### Create an Endpoint resource for storage container, which represents the data transfer destination.
`az storage-mover endpoint create-for-storage-container -g "rg" --storage-mover-name "mover_name" -n "target_endpoint" --container-name "target_container" --storage-account-id "account_id" --description tgtendpointDesc`

### Create a Job Definition resource, which contains configuration for a single unit of managed data transfer.
`az storage-mover job-definition create -g "rg" -n "job_definition" --project-name "project_name" --storage-mover-name "mover_name" --copy-mode Additive --source-name "source_endpoint" --target-name "target_endpoint" --agent-name "agent_name" --description JobDefinitionDescription --source-subpath path1 --target-subpath path2`

### Request an Agent to start a new instance of this Job Definition, generating a new Job Run resource.
`az storage-mover job-definition start-job -g "rg" --job-definition-name "job_definition" --project-name "project_name" --storage-mover-name "mover_name"`

### List all Job Runs in a Job Definition.
`az storage-mover job-run list -g "rg" --job-definition-name "job_definition" --project-name "project_name" --storage-mover-name "mover_name"`

### Request the Agent of any active instance of this Job Definition to stop.
`az storage-mover job-definition stop-job -g "rg" --job-definition-name "job_definition" --project-name "project_name" --storage-mover-name "mover_name"`

### Delete a Job Definition resource.
`az storage-mover job-definition delete -g "rg" -n "job_definition" --project-name "project_name" --storage-mover-name "mover_name"`

## API 2026-05-01 features ##

### Cross-tenant endpoints and job definitions
The storage container and storage SMB file share endpoint commands accept
`--enable-cross-tenant-transfer` and `--allowed-storage-accounts`. The allow list
contains full ARM resource IDs of storage accounts in the partner tenant.

`az storage-mover endpoint create-for-storage-container -g "rg" --storage-mover-name "mover_name" -n "source_endpoint" --container-name "source_container" --storage-account-id "source_account_id" --endpoint-kind Source --enable-cross-tenant-transfer true --allowed-storage-accounts "partner_account_id"`

Updating the allow list replaces the entire list. Omit the option to preserve it,
or specify it without values to clear it:

`az storage-mover endpoint update-for-storage-container -g "rg" --storage-mover-name "mover_name" -n "source_endpoint" --allowed-storage-accounts`

Use the following create-only parameters for a cross-tenant job definition. Both
endpoints must allow the other tenant's storage account:

`az storage-mover job-definition create -g "rg" -n "job_definition" --project-name "project_name" --storage-mover-name "mover_name" --copy-mode Additive --job-type CloudToCloud --source-name "source_endpoint" --target-name "partner_target_endpoint" --is-cross-tenant-job true --cross-tenant-endpoint-tenant-id "partner_tenant_id" --cross-tenant-endpoint-resource-id "partner_endpoint_resource_id"`

### Hourly schedules and synchronization
Job definition create and update commands accept `Hourly` schedules with a
`repeat-interval`, as well as `--sync-mode` and `--mover-synced-until`.

`az storage-mover job-definition update -g "rg" -n "job_definition" --project-name "project_name" --storage-mover-name "mover_name" --schedule "{frequency:Hourly,repeat-interval:1h,is-active:true}"`

Reconcile a running job without creating a new job definition:

`az storage-mover job-definition reconcile-job -g "rg" --job-definition-name "job_definition" --project-name "project_name" --storage-mover-name "mover_name"`

This action sends a bodyless POST and returns the job run resource ID.

### Agentless and FSX sources
Job definitions support `--job-type OnPremToCloudAgentLess` with `--connections`.
NFS endpoints support `--nfs-version NFSv4_1` and `--source-type FSX-EFS`. SMB mount
endpoints support `--source-type FSX-SMB`.

`az storage-mover endpoint create-for-nfs -g "rg" --storage-mover-name "mover_name" -n "source_endpoint" --export "/export" --host "nfs.example.com" --nfs-version NFSv4_1 --source-type FSX-EFS`

## Development ##
Run recorded scenarios and offline contract tests with `azdev test storage-mover --series`.
The self-contained scenarios use disposable resource groups and keyless StorageV2
accounts, provisioning containers and file shares through ARM. Tenant identifiers
are sanitized in recordings.
Prerequisite Storage requests use an explicit stable API version so playback does
not depend on the Azure CLI Storage SDK version.

New feature scenarios stay in `test_storage_mover.py`, with the same split between
recorded service scenarios and offline request checks as Az.StorageMover:

| Coverage | Scenario |
| --- | --- |
| Recorded | Blob cross-tenant enablement, allow-list replacement, omission/preservation, disablement, and clearing |
| Recorded | NFS `FSX-EFS` and SMB `FSX-SMB` endpoint create, update, and show |
| Recorded | Cross-tenant CloudToCloud job create, show, update, and delete against a real partner endpoint |
| Recorded | Azure SMB file share with `--endpoint-kind Source` in the existing endpoint scenario |
| Offline CLI request checks | Azure SMB cross-tenant settings; FSX source values and `NFSv4_1`; hourly schedules; synchronization fields; agentless jobs with connections; bodyless reconciliation |

The offline scenarios execute real CLI argument parsing and serialization with
mocked HTTP responses; they are not live recordings. The service currently
rejects Azure SMB cross-tenant settings and `NFSv4_1`, does not echo mount
`sourceType`, and has not confirmed the remaining synchronization/reconcile
flows. These checks do not claim successful data transfers.

To re-record the cross-tenant job scenario, provision a source storage account
and container, and a partner-tenant Storage Mover Target endpoint. Enable
cross-tenant transfer on the partner endpoint and allow the source storage
account. Set `SM_XT_SOURCE_STORAGE_ACCOUNT_ID`, `SM_XT_SOURCE_CONTAINER_NAME`,
`SM_XT_PARTNER_TENANT`, `SM_XT_PARTNER_STORAGE_ACCOUNT_ID`, and
`SM_XT_PARTNER_ENDPOINT_ID`. Recording skips this scenario if any variable is
missing; playback uses sanitized placeholders and needs no partner login.
The test creates only its disposable host mover and children; it does not
modify or delete these pre-provisioned prerequisites.

Partner allow-list and endpoint IDs are metadata resolved by Storage Mover,
not resources that require the caller to obtain auxiliary partner-tenant tokens.

Registered-agent scenarios are skipped until a disposable registered agent is
available. Scenarios that depend on shared multi-cloud or private-link
infrastructure retain their existing live-only restrictions.