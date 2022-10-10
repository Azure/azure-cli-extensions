# Azure CLI Reservation Extension #
This is the extension for reservation feature

### How to use ###
Install this extension using the below CLI command
```
az extension add --name reservation
```

### Included Features
#### Manage Azure Reservations.

##### Get catalog of available reservation.
```
az reservations catalog show --subscription-id {subId} \
    [--location {location}] \
    [--offer-id {offerId}] \
    [--plan-id {planId}] \
    [--publisher-id {publisherId}] \
    [--reserved-resource-type {AVS, AppService, AzureDataExplorer, AzureFiles, BlockBlob, CosmosDb, DataFactory, Databricks, DedicatedHost, ManagedDisk, MariaDb, MySql, NetAppStorage, PostgreSql, RedHat, RedHatOsa, RedisCache, SapHana, SqlAzureHybridBenefit, SqlDataWarehouse, SqlDatabases, SqlEdge, SuseLinux, VMwareCloudSimple, VirtualMachineSoftware, VirtualMachines}]
```

##### List all reservations within a reservation order.
```
az reservations reservation list \
    --reservation-order-id {orderId}
```

##### Get history of a reservation.
```
az reservations reservation list-history \
    --reservation-id {reservationId} \
    --reservation-order-id {orderId}
```

##### Merge two reservations.
```
az reservations reservation merge \
    --reservation-id-1 {reservationId1} \
    --reservation-id-2 {reservationId2} \
    --reservation-order-id {orderId}
```

##### Get details of a reservation.
```
az reservations reservation show \
    --reservation-id {reservationId} \
    --reservation-order-id {orderId}
```

##### Split a reservation.
```
az reservations reservation split \
    --quantity-1 {quantity1} \
    --quantity-2 {quantity2} \
    --reservation-id {reservationId} \
    --reservation-order-id {orderId}
```

##### Updates the applied scopes of the reservation.
```
az reservations reservation update --applied-scope-type {Shared, Single} \
    --reservation-id {reservationId} \
    --reservation-order-id {orderId} \
    [--applied-scopes] \
    [--instance-flexibility {Off, On}] \
```

##### Calculate price for placing a reservation order.
```
az reservations reservation-order calculate 
    --applied-scope-type {Shared, Single} \
    --billing-scope {billingScope} \
    --display-name {name} \
    --quantity {quantity} \
    --reserved-resource-type {AVS, AppService, AzureDataExplorer, AzureFiles, BlockBlob, CosmosDb, DataFactory, Databricks, DedicatedHost, ManagedDisk, MariaDb, MySql, NetAppStorage, PostgreSql, RedHat, RedHatOsa, RedisCache, SapHana, SqlAzureHybridBenefit, SqlDataWarehouse, SqlDatabases, SqlEdge, SuseLinux, VMwareCloudSimple, VirtualMachineSoftware, VirtualMachines} \
    --sku {skuName} \
    --term {P1Y, P3Y, P5Y} \
    [--applied-scope {scopeId}] \
    [--billing-plan {Monthly, Upfront}] \
    [--instance-flexibility {On, Off}] \
    [--location {location}] \
    [--renew {false, true}]
```

##### List of all the reservation orders that the user has access to in the current tenant.
```
az reservations reservation list
```

##### Purchase reservation order and create resource under the specified URI.
```
az reservations reservation-order purchase
    --reservation-order-id {orderId} \
    --applied-scope-type {Shared, Single} \
    --billing-scope {billingScope} \
    --display-name {name} \
    --quantity {quantity} \
    --reserved-resource-type {AVS, AppService, AzureDataExplorer, AzureFiles, BlockBlob, CosmosDb, DataFactory, Databricks, DedicatedHost, ManagedDisk, MariaDb, MySql, NetAppStorage, PostgreSql, RedHat, RedHatOsa, RedisCache, SapHana, SqlAzureHybridBenefit, SqlDataWarehouse, SqlDatabases, SqlEdge, SuseLinux, VMwareCloudSimple, VirtualMachineSoftware, VirtualMachines} \
    --sku {skuName} \
    --term {P1Y, P3Y, P5Y} \
    [--applied-scope {scopeId}] \
    [--billing-plan {Monthly, Upfront}] \
    [--instance-flexibility {On, Off}] \
    [--location {location}] \
    [--renew {false, true}]
```

##### Get the details of the reservation order.
```
az reservations reservation-order show --reservation-order-id {orderId}
```

##### Get applicable reservations that are applied to this subscription.
```
az reservations reservation-order-id list --subscription-id {subId}
```