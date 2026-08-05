# Azure CLI Computelimit Extension #
This is an extension to Azure CLI to manage Computelimit resources.

## How to use ##
Install the Computelimit extension using the CLI command below

```
az extension add --name computelimit
```

### Included features ###
There are 2 groups of compute limit operations that customers can perform on their host subscription

**Guest Subscription Operations:** These type of operations are to add/remove/get guest subscriptions that are added to the host subscription to shared compute limits.

**Shared Limit Operations:** These type of operations are to enable/disable/get compute limits that are enabled for sharing with the guest subscriptions.

#### Add a subscription as a guest to the host subscription. ####

```bash
az computelimit guest-subscription add --location eastus --guest-subscription-id 11111111-1111-1111-1111-111111111111
```

#### Remove a subscription as a guest to the host subscription. ####

```bash
az computelimit guest-subscription remove --location eastus --guest-subscription-id 11111111-1111-1111-1111-111111111111
```

#### Get a guest subscription added to the host subscription. ####

```bash
az computelimit guest-subscription show --location eastus --guest-subscription-id 11111111-1111-1111-1111-111111111111
```

#### List all guest subscriptions added to the host subscription. ####

```bash
az computelimit guest-subscription list --location eastus
```

#### Enable a compute limit to be shared by the host subscription with its guest subscriptions. ####

```bash
az computelimit shared-limit add --location eastus --name StandardDSv3Family
```

#### Disable sharing of a compute limit by the host subscription with its guest subscriptions. ####

```bash
az computelimit shared-limit remove --location eastus --name StandardDSv3Family
```

#### Get a compute limit shared by the host subscription with its guest subscriptions. ####

```bash
az computelimit shared-limit show --location eastus --name StandardDSv3Family
```

#### List all compute limits shared by the host subscription with its guest subscriptions. ####

```bash
az computelimit shared-limit list --location eastus
```