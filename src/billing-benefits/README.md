# Azure CLI BillingBenefits Extension #
This is an extension to Azure CLI to manage BillingBenefits resources.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name billing-benefits
```

### Included Features
#### Manage Azure Billing Benefits(savings plans).

##### Validate purchase of Azure billing benefits(savings plans).
```
az reservations billing-benefits validate-purchase \
    --benefits "[{applied-scope-type:Shared,billing-plan:P1M,billing-scope-id:50000000-aaaa-bbbb-cccc-200000000012,display-name:name1,sku:Compute_Savings_Plan,term:P1Y,commitment:{amount:10.0,currency-code:USD,grain:Hourly}}]"
```

##### Create a reservation order alias.
```
az billing-benefits reservation-order-aliases create \
    --order-alias-name TestRO \
    --location westus \
    --applied-scope-type Single \
    --applied-scope-prop "{subscription-id:/subscriptions/30000000-aaaa-bbbb-cccc-200000000004}" \
    --billing-plan P1M --billing-scope-id /subscriptions/30000000-aaaa-bbbb-cccc-200000000004 \
    --display-name TestRO \
    --quantity 1 \
    --renew false \
    --reserved-resource-type VirtualMachines \
    --sku Standard_B1ls \
    --term P1Y \
    --instance-flexibility On
```

##### Get a reservation order alias.
```
az billing-benefits order-aliases show \
    --reservation-order-alias-name TestRO
```

##### List savings plans.
```
az billing-benefits savings-plan list
```

##### Elevate as owner on savings plan order based on billing permissions.
```
az billing-benefits savings-plan-order elevate \
    --savings-plan-order-id 30000000-aaaa-bbbb-cccc-200000000017
```

##### List all Savings plan orders.
```
az billing-benefits savings-plan-order list
```

##### Get a savings plan order.
```
az billing-benefits savings-plan-order show \
    --savings-plan-order-id 30000000-aaaa-bbbb-cccc-200000000017
```

##### List savings plans in an order.
```
az billing-benefits savings-plan-order savings-plan list \
    --savings-plan-order-id 30000000-aaaa-bbbb-cccc-200000000017
```

##### Get savings plan.
```
az billing-benefits savings-plan-order savings-plan show \
    --savings-plan-order-id 30000000-aaaa-bbbb-cccc-200000000017 \
    --savings-plan-id 30000000-aaaa-bbbb-cccc-200000000019
```

##### Update savings plan.
```
az billing-benefits savings-plan-order savings-plan update \
    --savings-plan-order-id 30000000-aaaa-bbbb-cccc-200000000017 \
    --savings-plan-id 30000000-aaaa-bbbb-cccc-200000000019 \
    --display-name "cliTest"
```

##### Validate savings plan patch.
```
az billing-benefits savings-plan-order savings-plan validate-update \
    --savings-plan-order-id 30000000-aaaa-bbbb-cccc-200000000006 \
    --savings-plan-id 30000000-aaaa-bbbb-cccc-200000000004 \
    --benefits "[{applied-scope-type:Shared,display-name:name1}]"
```

##### Create a savings plan.
```
az billing-benefits savings-plan-order-aliases create \
    --order-alias-name "cliTest" \
    --applied-scope-type Shared \
    --billing-plan P1M \
    --billing-scope-id /subscriptions/30000000-aaaa-bbbb-cccc-200000000004 \
    --commitment "{amount:10.0,currency-code:USD,grain:Hourly}" \
    --display-name "cliTest" \
    --term P1Y \
    --sku Compute_Savings_Plan
```

##### Get a savings plan order alias.
```
az billing-benefits savings-plan-order-aliases show \
    --order-alias-name aliasName
```