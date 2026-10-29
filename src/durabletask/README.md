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

The default test run replays checked-in ARM recordings without an Azure login or provisioned resources.
`test_durabletask_scenario.py` uses `ScenarioTest`, `ResourceGroupPreparer`, randomized resource names,
and real CLI commands without mocking ARM operations. Its recordings are stored in
`azext_durabletask/tests/latest/recordings/`.

The recorded scenarios cover scheduler and managed identity lifecycles, task hubs, retention policies,
task queue throughput changes, restart, and Function App attachment. Attachment checks the actual app
settings written to a disposable Function App; no running function host or storage keys are needed.
Task hubs, retention policies, and scheduler identities also have independent lifecycle scenarios:
task hubs exercise idempotent creation and deletion, retention policies exercise replacement of
state-specific periods, and identity coverage verifies that adding or removing one identity preserves
other assignments.
Customer-managed encryption uses a disposable Key Vault and RSA key, granting the existing Durable
Task Scheduler enterprise application crypto access scoped only to that vault. It exercises encryption
configuration and automatic key rotation without installing or modifying a tenant-wide application.

The failover scenario is explicitly `live_only`: attempts with a `northcentralus` primary and a
`westus2` partner reported a failed failover configuration while the ARM operation remained accepted.
`recordings/diagnostics/failover_westus2_failed.yaml` preserves a sanitized real failure trace, including
the successfully provisioned schedulers and primary task hub. This is diagnostic evidence, not a
passing playback fixture. The scenario remains available against a deployment with functioning
failover support, with bounded waits. No successful failover recording is claimed or fabricated.

To re-record, sign in and select a subscription in your local CLI configuration, then run only the
desired scenario with `--live`, for example:

```text
az login
az account set --subscription "<test-subscription>"
azdev test --series --live test_durabletask_scheduler_lifecycle_recorded
azdev test --series --live test_durabletask_taskhub_lifecycle_recorded
azdev test --series --live test_durabletask_retention_policy_lifecycle_recorded
azdev test --series --live test_durabletask_identity_lifecycle_recorded
azdev test --series --live test_durabletask_taskqueue_lifecycle_recorded
azdev test --series --live test_durabletask_attach_functionapp_recorded
azdev test --series --live test_durabletask_encryption_lifecycle_recorded
```

The failover scenario can be retried separately with
`azdev test --series --live test_durabletask_failover_lifecycle_live`.

Recording provisions billable resources in temporary resource groups, primarily in `northcentralus`.
The preparers request deletion of the groups after the test, including on failure; verify cleanup if
a service operation fails or remains in progress. The Key Vault has purge
protection and seven-day soft-delete retention, so its deleted name remains reserved until retention
expires. Failover additionally provisions a partner scheduler in `westus2`. Do not configure
the preparers to reuse a persistent resource group unless you intend to manage its cleanup yourself.

Review recordings before committing them. The test SDK removes authentication headers, subscription
IDs, and email addresses; the extension's recording processor additionally removes account/identity
metadata, tenant IDs in dashboard links, generated scheduler hostnames, and signed operation-link
parameters. Run the tests again without `--live` to verify playback, then run
`azdev scan --confidence-level MEDIUM -d src/durabletask -r` before submitting.

The `unittest` request/serialization regressions and custom-logic tests remain complementary coverage
for boundary values, error propagation, settings preservation, retention-policy construction, and table
output. Their HTTP responses remain mocked even when `--live` is specified.
