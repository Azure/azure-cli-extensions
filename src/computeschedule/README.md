# Azure CLI Computeschedule Extension #
This is an extension to Azure CLI to manage Computeschedule resources.

### How to use ###
Install the Computeschedule extension using the CLI command below

```
az extension add --name az computeschedule
```

### Included features ###
The Computeschedule extension allows clients schedule Start/Hibernate/Deallocate operations on their batch of virtual machines.

The ComputeSchedule allows customers to schedule one off operations on their virtual machines. These operations include:

- Start
- Deallocate
- Hibernate

There are 2 groups of schedule type operations that customers can perform on their virtual machines

**Submit Type Operations:** These type of operations can be scheduled at a later date in the future, up to 14 days ahead.
**Execute Type Operations:** These type of operations allow clients to perform operations on their virtual machines immediately.

Other operations include endpoints to *get operation status* on virtual machines, *cancel operations* scheduled on virtual machines and get errors that might have occured during operations.

#### Operations List ####
#### VirtualMachinesExecuteStart: Execute start operation for a batch of virtual machines ####
This operation is triggered as soon as Computeschedule receives it.

```
az computeschedule vm-execute-start \
    --location eastus2euap \
    --execution-parameters "{retry-policy:{retry-count:2,retry-window-in-minutes:27}}" \
    --resources "{ids:[/subscriptions/fe541807-8c68-475d-976d-f453f9db4d81/resourceGroups/test-rg/providers/Microsoft.Compute/virtualMachines/testResource3]}" \
    --correlationid 23480d2f-1dca-4610-afb4-dd25eec1f34r
```

#### VirtualMachinesExecuteHibernate: Execute hibernate operation for a batch of virtual machines ####
This operation is triggered as soon as Computeschedule receives it.

```
az computeschedule vm-execute-hibernate \
    --location eastus2euap \
    --execution-parameters "{retry-policy:{retry-count:5,retry-window-in-minutes:27}}" \
    --resources "{ids:[/subscriptions/fe541807-8c68-475d-976d-f453f9db4d81/resourceGroups/test-rg/providers/Microsoft.Compute/virtualMachines/testResource3]}" \
    --correlationid 23480d2f-1dca-4610-afb4-dd25eec1f34r
```

#### VirtualMachinesExecuteDeallocate: Execute deallocate operation for a batch of virtual machines ####
This operation is triggered as soon as Computeschedule receives it.

```
az computeschedule vm-execute-deallocate \
    --location eastus2euap \
    --execution-parameters "{retry-policy:{retry-count:4,retry-window-in-minutes:27}}" \
    --resources "{ids:[/subscriptions/fe541807-8c68-475d-976d-f453f9db4d81/resourceGroups/test-rg/providers/Microsoft.Compute/virtualMachines/testResource3]}" \
    --correlationid 23480d2f-1dca-4610-afb4-dd25eec1f34r
```

#### VirtualMachinesSubmitStart: Schedule start operation for a batch of virtual machines at datetime in future ####
The below command is scheduling a start operation on a batch of virtual machines by the given deadline. The list below describes guidance on `Deadline` and `Timezone`:

- Computeschedule supports **"UTC"** timezone currently
- Deadline for a submit type operation can not be more than 5 minutes in the past or greater than 14 days in the future

```
az computeschedule vm-submit-start \
    --location eastus2euap \
    --schedule "{deadline:'2024-11-01T17:52:54.215Z',timezone:UTC,deadline-type:InitiateAt}" \
    --execution-parameters "{retry-policy:{retry-count:5,retry-window-in-minutes:27}}" \
    --resources "{ids:[/subscriptions/fe541807-8c68-475d-976d-f453f9db4d81/resourceGroups/test-rg/providers/Microsoft.Compute/virtualMachines/testResource3]}" \
    --correlationid 23480d2f-1dca-4610-afb4-dd25eec1f34r
```

#### VirtualMachinesSubmitDeallocate: Submit deallocate operation for a batch of virtual machines ####
The below command is scheduling a deallocate operation on a batch of virtual machines by the given deadline. The list below describes guidance on `Deadline` and `Timezone`:

- Computeschedule supports **"UTC"** timezone currently
- Deadline for a submit type operation can not be more than 5 minutes in the past or greater than 14 days in the future

```
az computeschedule vm-submit-deallocate \
    --location eastus2euap \
    --schedule "{deadline:'2024-11-01T17:52:54.215Z',timezone:UTC,deadline-type:InitiateAt}" \
    --execution-parameters "{retry-policy:{retry-count:5,retry-window-in-minutes:27}}" \
    --resources "{ids:[/subscriptions/fe541807-8c68-475d-976d-f453f9db4d81/resourceGroups/test-rg/providers/Microsoft.Compute/virtualMachines/testResource3]}" \
    --correlationid 23480d2f-1dca-4610-afb4-dd25eec1f34r
```

#### VirtualMachinesSubmitHibernate: Submit hibernate operation for a batch of virtual machines ####
The below command is scheduling a hibernate operation on a batch of virtual machines by the given deadline. The list below describes guidance on `Deadline` and `Timezone`:

- Computeschedule supports **"UTC"** timezone currently
- Deadline for a submit type operation can not be more than 5 minutes in the past or greater than 14 days in the future

```
az computeschedule vm-submit-hibernate \
    --location eastus2euap \
    --schedule "{deadline:'2024-11-01T17:52:54.215Z',timezone:UTC,deadline-type:InitiateAt}" \
    --execution-parameters "{retry-policy:{retry-count:5,retry-window-in-minutes:27}}" \
    --resources "{ids:[/subscriptions/fe541807-8c68-475d-976d-f453f9db4d81/resourceGroups/test-rg/providers/Microsoft.Compute/virtualMachines/testResource3]}" \
    --correlationid 23480d2f-1dca-4610-afb4-dd25eec1f34r
```

#### VirtualMachinesCancelOperations: Cancel a previously submitted (start/deallocate/hibernate) request on a batch of virtual machines ####
The below command cancels scheduled operations (Start/Deallocate/Hibernate) on virtual machines using the operationids gotten from previous Execute/Submit type operations.
```
az computeschedule vm-cancel-operations \
    --location eastus2euap \
    --operation-ids "[23480d2f-1dca-4610-afb4-dd25eec1f34r]" \
    --correlationid 23480d2f-1dca-4610-afb4-gg25eec1f34r
```

#### VirtualMachinesGetOperationStatus: Polling endpoint to read status of operations performed on virtual machines ####
The below command cancels scheduled operations (Start/Deallocate/Hibernate) on virtual machines using the operationids gotten from previous Execute/Submit type API calls

```
az computeschedule vm-get-operation-status \
    --location eastus2euap \
    --operation-ids "[23480d2f-1dca-4610-afb4-dd25eec1f34r]" \
    --correlationid 35780d2f-1dca-4610-afb4-dd25eec1f34r
```

#### VirtualMachinesGetOperationErrors: Get error details on operation errors (like transient errors encountered, additional logs) if they exist ####
The below command gets the details on the retriable errors that may have occured during the lifetime of an operation requested on a virtual machine

```
az computeschedule vm-get-operation-errors \
    --location eastus2euap \
    --operation-ids "[23480d2f-1dca-4610-afb4-dd25eec1f34r]"
```
