# Azure CLI Module Creation Report

### account subscription cancel

cancel a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--subscription-id**|string|Subscription Id.|subscription_id|
### account subscription create

create a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--alias-name**|string|Alias Name|alias_name|
|**--properties**|object|Put alias request properties.|properties|
### account subscription create-csp-subscription

create-csp-subscription a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--billing-account-name**|string|The name of the Microsoft Customer Agreement billing account for which you want to create the subscription.|billing_account_name|
|**--customer-name**|string|The name of the customer.|customer_name|
|**--display-name**|string|The friendly name of the subscription.|display_name|
|**--sku-id**|string|The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.|sku_id|
|**--reseller-id**|string|Reseller ID, basically MPN Id.|reseller_id|
### account subscription create-subscription

create-subscription a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--billing-account-name**|string|The name of the Microsoft Customer Agreement billing account for which you want to create the subscription.|billing_account_name|
|**--billing-profile-name**|string|The name of the billing profile in the billing account for which you want to create the subscription.|billing_profile_name|
|**--invoice-section-name**|string|The name of the invoice section in the billing account for which you want to create the subscription.|invoice_section_name|
|**--display-name**|string|The friendly name of the subscription.|display_name|
|**--sku-id**|string|The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.|sku_id|
|**--cost-center**|string|If set, the cost center will show up on the Azure usage and charges file.|cost_center|
|**--management-group-id**|string|The identifier of the management group to which this subscription will be associated.|management_group_id|
|**--additional-parameters**|dictionary|Additional, untyped parameters to support custom subscription creation scenarios.|additional_parameters|
|**--owner-object-id**|string|Object id of the Principal|object_id|
### account subscription create-subscription-in-enrollment-account

create-subscription-in-enrollment-account a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--enrollment-account-name**|string|The name of the enrollment account to which the subscription will be billed.|enrollment_account_name|
|**--display-name**|string|The display name of the subscription.|display_name|
|**--management-group-id**|string|The Management Group Id.|management_group_id|
|**--owners**|array|The list of principals that should be granted Owner access on the subscription. Principals should be of type User, Service Principal or Security Group.|owners|
|**--offer-type**|choice|The offer type of the subscription. For example, MS-AZR-0017P (EnterpriseAgreement) and MS-AZR-0148P (EnterpriseAgreement devTest) are available. Only valid when creating a subscription in a enrollment account scope.|offer_type|
|**--additional-parameters**|dictionary|Additional, untyped parameters to support custom subscription creation scenarios.|additional_parameters|
### account subscription delete

delete a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--alias-name**|string|Alias Name|alias_name|
### account subscription enable

enable a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--subscription-id**|string|Subscription Id.|subscription_id|
### account subscription get-alias

get-alias a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--alias-name**|string|Alias Name|alias_name|
### account subscription list

list a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### account subscription list-alias

list-alias a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### account subscription list-location

list-location a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|
### account subscription rename

rename a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--subscription-id**|string|Subscription Id.|subscription_id|
|**--subscription-name**|string|New subscription name|subscription_name|
### account subscription show

show a account subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|
### account subscription-operation show

show a account subscription-operation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--operation-id**|string|The operation ID, which can be found from the Location field in the generate recommendation response header.|operation_id|
### account tenant list

list a account tenant.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|