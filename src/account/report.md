# Azure CLI Module Creation Report

### account operations list

list a account operations.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### account subscription_factory create_csp_subscription

create_csp_subscription a account subscription_factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--body**|object|The subscription creation parameters.|/something/my_option|/something/myOption|
|**--display_name**|string|The friendly name of the subscription.|/something/my_option|/something/myOption|
|**--sku_id**|string|The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.|/something/my_option|/something/myOption|
|--reseller_id**|string|Reseller ID, basically MPN Id.|/something/my_option|/something/myOption|
|--service_provider_id**|string|Service provider ID, basically MPN Id.|/something/my_option|/something/myOption|
### account subscription_factory create_subscription

create_subscription a account subscription_factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--body**|object|The subscription creation parameters.|/something/my_option|/something/myOption|
### account subscription_factory create_subscription_in_enrollment_account

create_subscription_in_enrollment_account a account subscription_factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--body**|object|The subscription creation parameters.|/something/my_option|/something/myOption|
|--display_name**|string|The display name of the subscription.|/something/my_option|/something/myOption|
|--owners**|array|The list of principals that should be granted Owner access on the subscription. Principals should be of type User, Service Principal or Security Group.|/something/my_option|/something/myOption|
|--offer_type**|choice|The offer type of the subscription. For example, MS-AZR-0017P (EnterpriseAgreement) and MS-AZR-0148P (EnterpriseAgreement devTest) are available. Only valid when creating a subscription in a enrollment account scope.|/something/my_option|/something/myOption|
|--additional_parameters**|dictionary|Additional, untyped parameters to support custom subscription creation scenarios.|/something/my_option|/something/myOption|
### account subscription_operation show

show a account subscription_operation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### account subscription_operations list

list a account subscription_operations.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### account subscriptions cancel

cancel a account subscriptions.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### account subscriptions enable

enable a account subscriptions.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### account subscriptions list

list a account subscriptions.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### account subscriptions rename

rename a account subscriptions.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--body**|object|Subscription Name|/something/my_option|/something/myOption|
|--subscription_name**|string|New subscription name|/something/my_option|/something/myOption|
### account subscriptions show

show a account subscriptions.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### account tenants list

list a account tenants.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|