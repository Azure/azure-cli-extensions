# Azure CLI Module Creation Report

### account operations list

list a account operations.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### account subscription-factory create-csp-subscription

create-csp-subscription a account subscription-factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--body**|object|The subscription creation parameters.|/something/my_option|/something/myOption|
|**--display-name**|string|The friendly name of the subscription.|/something/my_option|/something/myOption|
|**--sku-id**|string|The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.|/something/my_option|/something/myOption|
|--reseller-id**|string|Reseller ID, basically MPN Id.|/something/my_option|/something/myOption|
|--service-provider-id**|string|Service provider ID, basically MPN Id.|/something/my_option|/something/myOption|
### account subscription-factory create-subscription

create-subscription a account subscription-factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--body**|object|The subscription creation parameters.|/something/my_option|/something/myOption|
### account subscription-factory create-subscription-in-enrollment-account

create-subscription-in-enrollment-account a account subscription-factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--body**|object|The subscription creation parameters.|/something/my_option|/something/myOption|
|--display-name**|string|The display name of the subscription.|/something/my_option|/something/myOption|
|--owners**|array|The list of principals that should be granted Owner access on the subscription. Principals should be of type User, Service Principal or Security Group.|/something/my_option|/something/myOption|
|--offer-type**|choice|The offer type of the subscription. For example, MS-AZR-0017P (EnterpriseAgreement) and MS-AZR-0148P (EnterpriseAgreement devTest) are available. Only valid when creating a subscription in a enrollment account scope.|/something/my_option|/something/myOption|
|--additional-parameters**|dictionary|Additional, untyped parameters to support custom subscription creation scenarios.|/something/my_option|/something/myOption|
### account subscription-operation show

show a account subscription-operation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### account subscription-operations list

list a account subscription-operations.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### account subscriptions cancel

cancel a account subscriptions.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### account subscriptions enable

enable a account subscriptions.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### account subscriptions list

list a account subscriptions.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### account subscriptions rename

rename a account subscriptions.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--body**|object|Subscription Name|/something/my_option|/something/myOption|
|--subscription-name**|string|New subscription name|/something/my_option|/something/myOption|
### account subscriptions show

show a account subscriptions.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### account tenants list

list a account tenants.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|