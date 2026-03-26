# Azure CLI StorageMover Extension #
This is an extension to Azure CLI to manage StorageMover resources.

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