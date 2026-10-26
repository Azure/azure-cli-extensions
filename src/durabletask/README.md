# Azure CLI Durabletask Extension #
This is an extension to Azure CLI to manage Durabletask resources.

## How to use ##
Install this extension using the following CLI command `az extension add --name durabletask`.

Remove this extension using the following CLI command `az extension remove --name durabletask`.

For more information on how to use this service, run the following CLI commands: 

` az durabletask scheduler -h `
` az durabletask taskhub -h `
` az durabletask taskqueue -h `
` az durabletask scheduler failover-instance -h `
` az durabletask retention-policy -h `

You can create a scheduler with the following command:
` az durabletask scheduler create -g "<resource-group-name>" -n "<scheduler-name>" --sku-name Consumption `

List all the schedulers in your resource group:
` az durabletask scheduler list -g <resource-group-name> `

Show the information for a particular scheduler within a resource group:
` az durabletask scheduler show -g <resource-group-name> -n <scheduler-name> `

Delete a scheduler:
` az durabletask scheduler delete -g <resource-group-name> -n <scheduler-name> `

You can create a taskhub with the following command:
` az durabletask taskhub create -g <resource-group-name> -s <scheduler-name> -n <taskhub-name> `

List all taskhubs within a particular scheduler:
` az durabletask taskhub list -g <resource-group-name> -s <scheduler-name> `

Show information on a single taskhub:
` az durabletask taskhub show -g <resource-group-name> -s <scheduler-name> -n <task-hub-name> `

Delete a taskhub:
` az durabletask taskhub delete -g <resource-group-name> -s <scheduler-name> -n <task-hub-name> `

Create a retention policy for a particular scheduler:
` az durabletask retention-policy create -g <resource-group-name> --scheduler-name <scheduler-name> --default-days 30 `

Show a retention policy for a particular scheduler:
` az durabletask retention-policy show -g <resource-group-name> --scheduler-name <scheduler-name> `

Delete a retention policy for a particular scheduler:
` az durabletask retention-policy delete -g <resource-group-name> --scheduler-name <scheduler-name> `

## Task queues ##

These examples assume the scheduler and task hub already exist. Replace the sample names with your resource names.
Taskqueue commands use `-t` or `--taskhub-name` to select the task hub.

Create a task queue with a throughput of 100 actions per second:
` az durabletask taskqueue create -g myResourceGroup -s myScheduler -t myTaskHub -n myTaskQueue --actions-per-second 100 `

Update the task queue throughput to 200 actions per second:
` az durabletask taskqueue update -g myResourceGroup -s myScheduler -t myTaskHub -n myTaskQueue --actions-per-second 200 `

List task queues in a task hub:
` az durabletask taskqueue list -g myResourceGroup -s myScheduler -t myTaskHub `

Show a task queue:
` az durabletask taskqueue show -g myResourceGroup -s myScheduler -t myTaskHub -n myTaskQueue `

Delete a task queue:
` az durabletask taskqueue delete -g myResourceGroup -s myScheduler -t myTaskHub -n myTaskQueue `

## Scheduler failover instances ##

These examples assume the schedulers already exist. Replace the sample resource ID with the resource ID of your partner scheduler.

Create a failover instance with a partner scheduler:
` az durabletask scheduler failover-instance create -g myResourceGroup -s myScheduler --partner-scheduler-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myPartnerResourceGroup/providers/Microsoft.DurableTask/schedulers/myPartnerScheduler `

Update the partner scheduler for a failover instance:
` az durabletask scheduler failover-instance update -g myResourceGroup -s myScheduler --partner-scheduler-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myPartnerResourceGroup/providers/Microsoft.DurableTask/schedulers/myNewPartnerScheduler `

Show the failover configuration:
` az durabletask scheduler failover-instance show -g myResourceGroup -s myScheduler `

Trigger a graceful failover for a scheduler:
` az durabletask scheduler failover-instance failover -g myResourceGroup -s myScheduler `

**Warning:** Forced failover can cause data loss. Use the following command only when you accept that risk:
` az durabletask scheduler failover-instance force-failover-allow-data-loss -g myResourceGroup -s myScheduler `

## Scheduler restart and encryption ##

Restart a scheduler:
` az durabletask scheduler restart -g myResourceGroup -n myScheduler `

Enable automatic rotation of customer-managed encryption keys on an existing encryption configuration:
` az durabletask scheduler transparent-data-encryption update -g myResourceGroup --scheduler-name myScheduler --auto-rotation-enabled true `

## Development and tests ##

Use an Azure CLI development environment with `azdev` and `azure-cli-testsdk` installed, following the
[Azure CLI test authoring guide](https://github.com/Azure/azure-cli/blob/dev/doc/authoring_tests.md).
Activate that environment and run these commands from the repository root:

```text
azdev extension add durabletask
azdev test --discover --series --no-exitfirst azext_durabletask
azdev style durabletask --pep8
azdev cmdcov durabletask
```

The tests run offline without an Azure login, subscription, or provisioned resources. They follow the
repository's `ScenarioTest` help-test and `unittest` patterns. Lifecycle tests invoke the CLI with mocked
HTTP responses while exercising its actual argument parsing, AAZ request serialization, response
deserialization, pagination, long-running-operation polling, and error handling. They cover schedulers,
identities, task hubs, task queues, retention policies, encryption, failover instances, and restart.
Additional unit tests cover scheduler attachment, identity and settings preservation, validation,
retention-policy construction, and table output.

No service recordings are required or fabricated. These are client-side regression tests, not a
substitute for live service validation of regional availability, SKU restrictions, customer-managed key
access, or failover behavior. Do not use `--live` to turn the mocked tests into service tests; their
HTTP responses remain mocked.
