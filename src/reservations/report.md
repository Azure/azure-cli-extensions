# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az quota|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az quota` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az quota reservation|Reservation|[commands](#CommandsInReservation)|
|az quota||[commands](#CommandsIn)|
|az quota reservation-order|ReservationOrder|[commands](#CommandsInReservationOrder)|
|az quota operation|Operation|[commands](#CommandsInOperation)|
|az quota calculate-exchange|CalculateExchange|[commands](#CommandsInCalculateExchange)|
|az quota exchange|Exchange|[commands](#CommandsInExchange)|
|az quota|Quota|[commands](#CommandsInQuota)|
|az quota quota-request-status|QuotaRequestStatus|[commands](#CommandsInQuotaRequestStatus)|

## COMMANDS
### <a name="CommandsIn">Commands in `az quota` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota show-applied-reservation-list](#GetAppliedReservationList)|GetAppliedReservationList|[Parameters](#ParametersGetAppliedReservationList)|[Example](#ExamplesGetAppliedReservationList)|
|[az quota show-catalog](#GetCatalog)|GetCatalog|[Parameters](#ParametersGetCatalog)|[Example](#ExamplesGetCatalog)|

### <a name="CommandsInQuota">Commands in `az quota` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota list](#QuotaList)|List|[Parameters](#ParametersQuotaList)|[Example](#ExamplesQuotaList)|
|[az quota show](#QuotaGet)|Get|[Parameters](#ParametersQuotaGet)|[Example](#ExamplesQuotaGet)|
|[az quota create](#QuotaCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersQuotaCreateOrUpdate#Create)|[Example](#ExamplesQuotaCreateOrUpdate#Create)|
|[az quota update](#QuotaUpdate)|Update|[Parameters](#ParametersQuotaUpdate)|[Example](#ExamplesQuotaUpdate)|

### <a name="CommandsInCalculateExchange">Commands in `az quota calculate-exchange` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota calculate-exchange post](#CalculateExchangePost)|Post|[Parameters](#ParametersCalculateExchangePost)|[Example](#ExamplesCalculateExchangePost)|

### <a name="CommandsInExchange">Commands in `az quota exchange` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota exchange post](#ExchangePost)|Post|[Parameters](#ParametersExchangePost)|[Example](#ExamplesExchangePost)|

### <a name="CommandsInOperation">Commands in `az quota operation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota operation list](#OperationList)|List|[Parameters](#ParametersOperationList)|[Example](#ExamplesOperationList)|

### <a name="CommandsInQuotaRequestStatus">Commands in `az quota quota-request-status` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota quota-request-status list](#QuotaRequestStatusList)|List|[Parameters](#ParametersQuotaRequestStatusList)|[Example](#ExamplesQuotaRequestStatusList)|
|[az quota quota-request-status show](#QuotaRequestStatusGet)|Get|[Parameters](#ParametersQuotaRequestStatusGet)|[Example](#ExamplesQuotaRequestStatusGet)|

### <a name="CommandsInReservation">Commands in `az quota reservation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota reservation list](#ReservationList)|List|[Parameters](#ParametersReservationList)|[Example](#ExamplesReservationList)|
|[az quota reservation show](#ReservationGet)|Get|[Parameters](#ParametersReservationGet)|[Example](#ExamplesReservationGet)|
|[az quota reservation update](#ReservationUpdate)|Update|[Parameters](#ParametersReservationUpdate)|[Example](#ExamplesReservationUpdate)|
|[az quota reservation available-scope](#ReservationAvailableScopes)|AvailableScopes|[Parameters](#ParametersReservationAvailableScopes)|[Example](#ExamplesReservationAvailableScopes)|
|[az quota reservation list-revision](#ReservationListRevisions)|ListRevisions|[Parameters](#ParametersReservationListRevisions)|[Example](#ExamplesReservationListRevisions)|
|[az quota reservation merge](#ReservationMerge)|Merge|[Parameters](#ParametersReservationMerge)|[Example](#ExamplesReservationMerge)|
|[az quota reservation split](#ReservationSplit)|Split|[Parameters](#ParametersReservationSplit)|[Example](#ExamplesReservationSplit)|

### <a name="CommandsInReservationOrder">Commands in `az quota reservation-order` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota reservation-order list](#ReservationOrderList)|List|[Parameters](#ParametersReservationOrderList)|[Example](#ExamplesReservationOrderList)|
|[az quota reservation-order show](#ReservationOrderGet)|Get|[Parameters](#ParametersReservationOrderGet)|[Example](#ExamplesReservationOrderGet)|
|[az quota reservation-order calculate](#ReservationOrderCalculate)|Calculate|[Parameters](#ParametersReservationOrderCalculate)|[Example](#ExamplesReservationOrderCalculate)|
|[az quota reservation-order purchase](#ReservationOrderPurchase)|Purchase|[Parameters](#ParametersReservationOrderPurchase)|[Example](#ExamplesReservationOrderPurchase)|


## COMMAND DETAILS

### group `az quota`
#### <a name="GetAppliedReservationList">Command `az quota show-applied-reservation-list`</a>

##### <a name="ExamplesGetAppliedReservationList">Example</a>
```
az quota show-applied-reservation-list --subscription-id "23bc208b-083f-4901-ae85-4f98c0c3b4b6"
```
##### <a name="ParametersGetAppliedReservationList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Id of the subscription|subscription_id|subscriptionId|

#### <a name="GetCatalog">Command `az quota show-catalog`</a>

##### <a name="ExamplesGetCatalog">Example</a>
```
az quota show-catalog --location "eastus" --reserved-resource-type "VirtualMachines" --subscription-id \
"23bc208b-083f-4901-ae85-4f98c0c3b4b6"
```
##### <a name="ParametersGetCatalog">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Id of the subscription|subscription_id|subscriptionId|
|**--reserved-resource-type**|string|The type of the resource for which the skus should be provided.|reserved_resource_type|reservedResourceType|
|**--location**|string|Filters the skus based on the location specified in this parameter. This can be an azure region or global|location|location|

### group `az quota`
#### <a name="QuotaList">Command `az quota list`</a>

##### <a name="ExamplesQuotaList">Example</a>
```
az quota list --location "eastus" --provider-id "Microsoft.Compute" --subscription-id "00000000-0000-0000-0000-00000000\
0000"
```
##### <a name="ExamplesQuotaList">Example</a>
```
az quota list --location "eastus" --provider-id "Microsoft.MachineLearningServices" --subscription-id \
"00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersQuotaList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Azure subscription ID.|subscription_id|subscriptionId|
|**--provider-id**|string|Azure resource provider ID.|provider_id|providerId|
|**--location**|string|Azure region.|location|location|

#### <a name="QuotaGet">Command `az quota show`</a>

##### <a name="ExamplesQuotaGet">Example</a>
```
az quota show --location "eastus" --provider-id "Microsoft.Compute" --resource-name "standardNDSFamily" \
--subscription-id "00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersQuotaGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Azure subscription ID.|subscription_id|subscriptionId|
|**--provider-id**|string|Azure resource provider ID.|provider_id|providerId|
|**--location**|string|Azure region.|location|location|
|**--resource-name**|string|The resource name for a resource provider, such as SKU name for Microsoft.Compute, Sku or TotalLowPriorityCores for Microsoft.MachineLearningServices|resource_name|resourceName|

#### <a name="QuotaCreateOrUpdate#Create">Command `az quota create`</a>

##### <a name="ExamplesQuotaCreateOrUpdate#Create">Example</a>
```
az quota create --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":200,\\"unit\\":\\"Count\\"\
}" --location "eastus" --provider-id "Microsoft.Compute" --resource-name "standardFSv2Family" --subscription-id \
"D7EC67B3-7657-4966-BFFC-41EFD36BAAB3"
```
##### <a name="ExamplesQuotaCreateOrUpdate#Create">Example</a>
```
az quota create --properties "{\\"name\\":{\\"value\\":\\"StandardDv2Family\\"},\\"limit\\":200,\\"resourceType\\":\\"d\
edicated\\",\\"unit\\":\\"Count\\"}" --location "eastus" --provider-id "Microsoft.MachineLearningServices" \
--resource-name "StandardDv2Family" --subscription-id "D7EC67B3-7657-4966-BFFC-41EFD36BAAB3"
```
##### <a name="ExamplesQuotaCreateOrUpdate#Create">Example</a>
```
az quota create --properties "{\\"name\\":{\\"value\\":\\"TotalLowPriorityCores\\"},\\"limit\\":200,\\"resourceType\\":\
\\"lowPriority\\",\\"unit\\":\\"Count\\"}" --location "eastus" --provider-id "Microsoft.MachineLearningServices" \
--resource-name "TotalLowPriorityCores" --subscription-id "D7EC67B3-7657-4966-BFFC-41EFD36BAAB3"
```
##### <a name="ParametersQuotaCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Azure subscription ID.|subscription_id|subscriptionId|
|**--provider-id**|string|Azure resource provider ID.|provider_id|providerId|
|**--location**|string|Azure region.|location|location|
|**--resource-name**|string|The resource name for a resource provider, such as SKU name for Microsoft.Compute, Sku or TotalLowPriorityCores for Microsoft.MachineLearningServices|resource_name|resourceName|
|**--limit**|integer|Quota properties.|limit|limit|
|**--unit**|string| The limit units, such as **count** and **bytes**. Use the unit field provided in the response of the GET quota operation.|unit|unit|
|**--resource-type**|choice|The name of the resource type.|resource_type|resourceType|
|**--properties**|any|Additional properties for the specified resource provider.|properties|properties|
|**--value**|string|Resource name.|value|value|

#### <a name="QuotaUpdate">Command `az quota update`</a>

##### <a name="ExamplesQuotaUpdate">Example</a>
```
az quota update --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":200,\\"unit\\":\\"Count\\"\
}" --location "eastus" --provider-id "Microsoft.Compute" --resource-name "standardFSv2Family" --subscription-id \
"D7EC67B3-7657-4966-BFFC-41EFD36BAAB3"
```
##### <a name="ParametersQuotaUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Azure subscription ID.|subscription_id|subscriptionId|
|**--provider-id**|string|Azure resource provider ID.|provider_id|providerId|
|**--location**|string|Azure region.|location|location|
|**--resource-name**|string|The resource name for a resource provider, such as SKU name for Microsoft.Compute, Sku or TotalLowPriorityCores for Microsoft.MachineLearningServices|resource_name|resourceName|
|**--limit**|integer|Quota properties.|limit|limit|
|**--unit**|string| The limit units, such as **count** and **bytes**. Use the unit field provided in the response of the GET quota operation.|unit|unit|
|**--resource-type**|choice|The name of the resource type.|resource_type|resourceType|
|**--properties**|any|Additional properties for the specified resource provider.|properties|properties|
|**--value**|string|Resource name.|value|value|

### group `az quota calculate-exchange`
#### <a name="CalculateExchangePost">Command `az quota calculate-exchange post`</a>

##### <a name="ExamplesCalculateExchangePost">Example</a>
```
az quota calculate-exchange post --reservations-to-exchange quantity=1 reservation-id="/providers/microsoft.capacity/re\
servationOrders/1f14354c-dc12-4c8d-8090-6f295a3a34aa/reservations/c8c926bd-fc5d-4e29-9d43-b68340ac23a6" \
--reservations-to-purchase location="westus" reserved-resource-type="VirtualMachines" billing-scope-id="/subscriptions/\
ed3a1871-612d-abcd-a849-c2542a68be83" term="P1Y" billing-plan="Upfront" quantity=1 display-name="testDisplayName" \
applied-scope-type="Shared" applied-scopes=null renew=false instance-flexibility="On" name="Standard_B1ls"
```
##### <a name="ParametersCalculateExchangePost">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--reservations-to-purchase**|array|List of reservations that are being purchased in this exchange.|reservations_to_purchase|reservationsToPurchase|
|**--reservations-to-exchange**|array|List of reservations that are being returned in this exchange.|reservations_to_exchange|reservationsToExchange|

### group `az quota exchange`
#### <a name="ExchangePost">Command `az quota exchange post`</a>

##### <a name="ExamplesExchangePost">Example</a>
```
az quota exchange post --session-id "66e2ac8f-439e-4345-8235-6fef07608081"
```
##### <a name="ParametersExchangePost">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--session-id**|string|SessionId that was returned by CalculateExchange API.|session_id|sessionId|

### group `az quota operation`
#### <a name="OperationList">Command `az quota operation list`</a>

##### <a name="ExamplesOperationList">Example</a>
```
az quota operation list
```
##### <a name="ParametersOperationList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
### group `az quota quota-request-status`
#### <a name="QuotaRequestStatusList">Command `az quota quota-request-status list`</a>

##### <a name="ExamplesQuotaRequestStatusList">Example</a>
```
az quota quota-request-status list --location "eastus" --provider-id "Microsoft.Compute" --subscription-id \
"3f75fdf7-977e-44ad-990d-99f14f0f299f"
```
##### <a name="ParametersQuotaRequestStatusList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Azure subscription ID.|subscription_id|subscriptionId|
|**--provider-id**|string|Azure resource provider ID.|provider_id|providerId|
|**--location**|string|Azure region.|location|location|
|**--filter**|string|| Field                    | Supported operators   |---------------------|------------------------  |requestSubmitTime | ge, le, eq, gt, lt |filter|$filter|
|**--top**|integer|Number of records to return.|top|$top|
|**--skiptoken**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element includes a skiptoken parameter that specifies a starting point to use for subsequent calls.|skiptoken|$skiptoken|

#### <a name="QuotaRequestStatusGet">Command `az quota quota-request-status show`</a>

##### <a name="ExamplesQuotaRequestStatusGet">Example</a>
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --location "eastus" --provider-id \
"Microsoft.Compute" --subscription-id "00000000-0000-0000-0000-000000000000"
```
##### <a name="ExamplesQuotaRequestStatusGet">Example</a>
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --location "eastus" --provider-id \
"Microsoft.Compute" --subscription-id "00000000-0000-0000-0000-000000000000"
```
##### <a name="ExamplesQuotaRequestStatusGet">Example</a>
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --location "eastus" --provider-id \
"Microsoft.Compute" --subscription-id "00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersQuotaRequestStatusGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Azure subscription ID.|subscription_id|subscriptionId|
|**--provider-id**|string|Azure resource provider ID.|provider_id|providerId|
|**--location**|string|Azure region.|location|location|
|**--id**|string|Quota Request ID.|id|id|

### group `az quota reservation`
#### <a name="ReservationList">Command `az quota reservation list`</a>

##### <a name="ExamplesReservationList">Example</a>
```
az quota reservation list --reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da"
```
##### <a name="ParametersReservationList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--reservation-order-id**|string|Order Id of the reservation|reservation_order_id|reservationOrderId|

#### <a name="ReservationGet">Command `az quota reservation show`</a>

##### <a name="ExamplesReservationGet">Example</a>
```
az quota reservation show --expand "renewProperties" --reservation-id "6ef59113-3482-40da-8d79-787f823e34bc" \
--reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da"
```
##### <a name="ParametersReservationGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--reservation-id**|string|Id of the Reservation Item|reservation_id|reservationId|
|**--reservation-order-id**|string|Order Id of the reservation|reservation_order_id|reservationOrderId|
|**--expand**|string|Supported value of this query is renewProperties|expand|expand|

#### <a name="ReservationUpdate">Command `az quota reservation update`</a>

##### <a name="ExamplesReservationUpdate">Example</a>
```
az quota reservation update --applied-scope-type "Shared" --instance-flexibility "Off" --reservation-id \
"6ef59113-3482-40da-8d79-787f823e34bc" --reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da"
```
##### <a name="ParametersReservationUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--reservation-order-id**|string|Order Id of the reservation|reservation_order_id|reservationOrderId|
|**--reservation-id**|string|Id of the Reservation Item|reservation_id|reservationId|
|**--applied-scope-type**|choice|Type of the Applied Scope.|applied_scope_type|appliedScopeType|
|**--applied-scopes**|array|List of the subscriptions that the benefit will be applied. Do not specify if AppliedScopeType is Shared.|applied_scopes|appliedScopes|
|**--instance-flexibility**|choice|Turning this on will apply the reservation discount to other VMs in the same VM size group. Only specify for VirtualMachines reserved resource type.|instance_flexibility|instanceFlexibility|
|**--name**|string|Name of the Reservation|name|name|
|**--renew**|boolean|Setting this to true will automatically purchase a new reservation on the expiration date time.|renew|renew|
|**--location**|string|The Azure Region where the reserved resource lives.|location|location|
|**--reserved-resource-type**|choice|The type of the resource that is being reserved.|reserved_resource_type|reservedResourceType|
|**--billing-scope-id**|string|Subscription that will be charged for purchasing Reservation|billing_scope_id|billingScopeId|
|**--term**|choice|Represent the term of Reservation.|term|term|
|**--billing-plan**|choice|Represent the billing plans.|billing_plan|billingPlan|
|**--quantity**|integer|Quantity of the SKUs that are part of the Reservation. Must be greater than zero.|quantity|quantity|
|**--display-name**|string|Friendly name of the Reservation|display_name|displayName|
|**--applied-scope-type-applied-scope-type**|choice|Type of the Applied Scope.|applied_scope_type_applied_scope_type|appliedScopeType|
|**--applied-scopes1**|array|List of the subscriptions that the benefit will be applied. Do not specify if AppliedScopeType is Shared.|applied_scopes1|appliedScopes|
|**--renew1**|boolean|Setting this to true will automatically purchase a new reservation on the expiration date time.|renew1|renew|
|**--instance-flexibility1**|choice|Turning this on will apply the reservation discount to other VMs in the same VM size group. Only specify for VirtualMachines reserved resource type.|instance_flexibility1|instanceFlexibility|
|**--sku-name**|string||sku_name|name|

#### <a name="ReservationAvailableScopes">Command `az quota reservation available-scope`</a>

##### <a name="ExamplesReservationAvailableScopes">Example</a>
```
az quota reservation available-scope --properties scopes="/subscriptions/efc7c997-7700-4a74-b731-55aec16c15e9" \
--reservation-id "356e7ae4-84d0-4da6-ab4b-d6b94f3557da" --reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da"
```
##### <a name="ParametersReservationAvailableScopes">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--reservation-order-id**|string|Order Id of the reservation|reservation_order_id|reservationOrderId|
|**--reservation-id**|string|Id of the Reservation Item|reservation_id|reservationId|
|**--properties**|object|Available scope request properties|properties|properties|

#### <a name="ReservationListRevisions">Command `az quota reservation list-revision`</a>

##### <a name="ExamplesReservationListRevisions">Example</a>
```
az quota reservation list-revision --reservation-id "6ef59113-3482-40da-8d79-787f823e34bc" --reservation-order-id \
"276e7ae4-84d0-4da6-ab4b-d6b94f3557da"
```
##### <a name="ParametersReservationListRevisions">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--reservation-id**|string|Id of the Reservation Item|reservation_id|reservationId|
|**--reservation-order-id**|string|Order Id of the reservation|reservation_order_id|reservationOrderId|

#### <a name="ReservationMerge">Command `az quota reservation merge`</a>

##### <a name="ExamplesReservationMerge">Example</a>
```
az quota reservation merge --sources "/providers/Microsoft.Capacity/reservationOrders/c0565a8a-4491-4e77-b07b-5e6d66718\
e1c/reservations/cea04232-932e-47db-acb5-e29a945ecc73" "/providers/Microsoft.Capacity/reservationOrders/c0565a8a-4491-4\
e77-b07b-5e6d66718e1c/reservations/5bf54dc7-dacd-4f46-a16b-7b78f4a59799" --reservation-order-id \
"276e7ae4-84d0-4da6-ab4b-d6b94f3557da"
```
##### <a name="ParametersReservationMerge">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--reservation-order-id**|string|Order Id of the reservation|reservation_order_id|reservationOrderId|
|**--sources**|array|Format of the resource id should be /providers/Microsoft.Capacity/reservationOrders/{reservationOrderId}/reservations/{reservationId}|sources|sources|

#### <a name="ReservationSplit">Command `az quota reservation split`</a>

##### <a name="ExamplesReservationSplit">Example</a>
```
az quota reservation split --quantities 1 2 --reservation-id "/providers/Microsoft.Capacity/reservationOrders/276e7ae4-\
84d0-4da6-ab4b-d6b94f3557da/reservations/bcae77cd-3119-4766-919f-b50d36c75c7a" --reservation-order-id \
"276e7ae4-84d0-4da6-ab4b-d6b94f3557da"
```
##### <a name="ParametersReservationSplit">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--reservation-order-id**|string|Order Id of the reservation|reservation_order_id|reservationOrderId|
|**--quantities**|array|List of the quantities in the new reservations to create.|quantities|quantities|
|**--reservation-id**|string|Resource id of the reservation to be split. Format of the resource id should be /providers/Microsoft.Capacity/reservationOrders/{reservationOrderId}/reservations/{reservationId}|reservation_id|reservationId|

### group `az quota reservation-order`
#### <a name="ReservationOrderList">Command `az quota reservation-order list`</a>

##### <a name="ExamplesReservationOrderList">Example</a>
```
az quota reservation-order list
```
##### <a name="ParametersReservationOrderList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ReservationOrderGet">Command `az quota reservation-order show`</a>

##### <a name="ExamplesReservationOrderGet">Example</a>
```
az quota reservation-order show --reservation-order-id "a075419f-44cc-497f-b68a-14ee811d48b9"
```
##### <a name="ExamplesReservationOrderGet">Example</a>
```
az quota reservation-order show --expand "schedule" --reservation-order-id "a075419f-44cc-497f-b68a-14ee811d48b9"
```
##### <a name="ParametersReservationOrderGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--reservation-order-id**|string|Order Id of the reservation|reservation_order_id|reservationOrderId|
|**--expand**|string|May be used to expand the planInformation.|expand|$expand|

#### <a name="ReservationOrderCalculate">Command `az quota reservation-order calculate`</a>

##### <a name="ExamplesReservationOrderCalculate">Example</a>
```
az quota reservation-order calculate --location "westus" --applied-scope-type "Shared" --billing-plan "Monthly" \
--billing-scope-id "/subscriptions/ed3a1871-612d-abcd-a849-c2542a68be83" --display-name "TestReservationOrder" \
--quantity 1 --instance-flexibility "On" --reserved-resource-type "VirtualMachines" --term "P1Y" --name "standard_D1"
```
##### <a name="ParametersReservationOrderCalculate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The Azure Region where the reserved resource lives.|location|location|
|**--reserved-resource-type**|choice|The type of the resource that is being reserved.|reserved_resource_type|reservedResourceType|
|**--billing-scope-id**|string|Subscription that will be charged for purchasing Reservation|billing_scope_id|billingScopeId|
|**--term**|choice|Represent the term of Reservation.|term|term|
|**--billing-plan**|choice|Represent the billing plans.|billing_plan|billingPlan|
|**--quantity**|integer|Quantity of the SKUs that are part of the Reservation. Must be greater than zero.|quantity|quantity|
|**--display-name**|string|Friendly name of the Reservation|display_name|displayName|
|**--applied-scope-type**|choice|Type of the Applied Scope.|applied_scope_type|appliedScopeType|
|**--applied-scopes**|array|List of the subscriptions that the benefit will be applied. Do not specify if AppliedScopeType is Shared.|applied_scopes|appliedScopes|
|**--renew**|boolean|Setting this to true will automatically purchase a new reservation on the expiration date time.|renew|renew|
|**--instance-flexibility**|choice|Turning this on will apply the reservation discount to other VMs in the same VM size group. Only specify for VirtualMachines reserved resource type.|instance_flexibility|instanceFlexibility|
|**--name**|string||name|name|

#### <a name="ReservationOrderPurchase">Command `az quota reservation-order purchase`</a>

##### <a name="ExamplesReservationOrderPurchase">Example</a>
```
az quota reservation-order purchase --location "westus" --applied-scope-type "Shared" --billing-plan "Monthly" \
--billing-scope-id "/subscriptions/ed3a1871-612d-abcd-a849-c2542a68be83" --display-name "TestReservationOrder" \
--quantity 1 --renew false --instance-flexibility "On" --reserved-resource-type "VirtualMachines" --term "P1Y" --name \
"standard_D1" --reservation-order-id "a075419f-44cc-497f-b68a-14ee811d48b9"
```
##### <a name="ParametersReservationOrderPurchase">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--reservation-order-id**|string|Order Id of the reservation|reservation_order_id|reservationOrderId|
|**--location**|string|The Azure Region where the reserved resource lives.|location|location|
|**--reserved-resource-type**|choice|The type of the resource that is being reserved.|reserved_resource_type|reservedResourceType|
|**--billing-scope-id**|string|Subscription that will be charged for purchasing Reservation|billing_scope_id|billingScopeId|
|**--term**|choice|Represent the term of Reservation.|term|term|
|**--billing-plan**|choice|Represent the billing plans.|billing_plan|billingPlan|
|**--quantity**|integer|Quantity of the SKUs that are part of the Reservation. Must be greater than zero.|quantity|quantity|
|**--display-name**|string|Friendly name of the Reservation|display_name|displayName|
|**--applied-scope-type**|choice|Type of the Applied Scope.|applied_scope_type|appliedScopeType|
|**--applied-scopes**|array|List of the subscriptions that the benefit will be applied. Do not specify if AppliedScopeType is Shared.|applied_scopes|appliedScopes|
|**--renew**|boolean|Setting this to true will automatically purchase a new reservation on the expiration date time.|renew|renew|
|**--instance-flexibility**|choice|Turning this on will apply the reservation discount to other VMs in the same VM size group. Only specify for VirtualMachines reserved resource type.|instance_flexibility|instanceFlexibility|
|**--name**|string||name|name|
