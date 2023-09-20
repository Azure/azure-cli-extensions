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
    --sources [{fullyQualifiedReservationId1},{fullyQualifiedReservationId2}] \
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

##### Calculates price for exchanging Reservations if there are no policy errors.
```
az reservations calculate-exchange --ris-to-exchange "[{reservation-id:/providers/microsoft.capacity/reservationOrders/40000000-aaaa-bbbb-cccc-200000000012/reservations/51000000-aaaa-bbbb-cccc-200000000012,quantity:1},{reservation-id:/providers/microsoft.capacity/reservationOrders/90000000-aaaa-bbbb-cccc-200000000012/reservations/36000000-aaaa-bbbb-cccc-200000000012,quantity:1}]" --ris-to-purchase "[{reserved-resource-type:VirtualMachines,applied-scope-type:Shared,billing-scope:12350000-aaaa-bbbb-cccc-200000000012,display-name:exchangeTest1,quantity:1,sku:Standard_B1s,term:P1Y,billing-plan:Monthly,location:eastus},{reserved-resource-type:VirtualMachines,applied-scope-type:Shared,billing-scope:12350000-aaaa-bbbb-cccc-200000000012,display-name:exchangeTest2,quantity:1,sku:Standard_B1s,term:P1Y,billing-plan:Monthly,location:eastus}]"
```

##### Returns one or more Reservations in exchange for one or more Reservation purchases.
```
az reservations exchange --session-id 40000000-aaaa-bbbb-cccc-200000000012
```

##### Archiving a reservation.
```
az reservations reservation archive --reservation-order-id 40000000-aaaa-bbbb-cccc-20000000000 --reservation-id 50000000-aaaa-bbbb-cccc-200000000000
```

##### Unarchiving a reservation.
```
az reservations reservation unarchive --reservation-order-id 40000000-aaaa-bbbb-cccc-20000000000 --reservation-id 50000000-aaaa-bbbb-cccc-200000000000
```

##### List reservation available scopes.
```
az reservations reservation list-available-scope --reservation-order-id 40000000-aaaa-bbbb-cccc-20000000000 --reservation-id 30000000-aaaa-bbbb-cccc-20000000000 --scopes ['/subscriptions/60000000-aaaa-bbbb-cccc-20000000000']
```

##### Change a reservation order to another tenant.
```
az reservations reservation-order change-directory --reservation-order-id 50000000-aaaa-bbbb-cccc-200000000000 --destination-tenant-id 10000000-aaaa-bbbb-cccc-200000000011
```

##### Calculates price for Reservations refund if there are no policy errors.
```
az reservations reservation-order calculate-refund --reservation-order-id 0000000-aaaa-bbbb-cccc-20000000001 --id /providers/microsoft.capacity/reservationOrders/0000000-aaaa-bbbb-cccc-20000000001 --scope Reservation --quantity 1 --reservation-id /providers/microsoft.capacity/reservationOrders/0000000-aaaa-bbbb-cccc-20000000001/reservations/50000000-aaaa-bbbb-cccc-200000000000
```

##### Return a reservation.
```
az reservations reservation-order return --reservation-order-id 50000000-aaaa-bbbb-cccc-200000000000 --return-reason mockReason --scope Reservation --quantity 1 --reservation-id /providers/microsoft.capacity/reservationOrders/50000000-aaaa-bbbb-cccc-200000000000/reservations/30000000-aaaa-bbbb-cccc-200000000011 --session-id 40000000-aaaa-bbbb-cccc-200000000012
```

##### Listing reservations under the tenant
```
az reservations list
    [--selected-state {state}] \
    [--filter {filter}] \
    [--orderby {orderby}]
```