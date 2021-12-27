# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az confidentialledger|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az confidentialledger` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az confidentialledger|Ledger|[commands](#CommandsInLedger)|

## COMMANDS
### <a name="CommandsInLedger">Commands in `az confidentialledger` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az confidentialledger list](#LedgerListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersLedgerListByResourceGroup)|[Example](#ExamplesLedgerListByResourceGroup)|
|[az confidentialledger list](#LedgerListBySubscription)|ListBySubscription|[Parameters](#ParametersLedgerListBySubscription)|[Example](#ExamplesLedgerListBySubscription)|
|[az confidentialledger show](#LedgerGet)|Get|[Parameters](#ParametersLedgerGet)|[Example](#ExamplesLedgerGet)|
|[az confidentialledger create](#LedgerCreate)|Create|[Parameters](#ParametersLedgerCreate)|[Example](#ExamplesLedgerCreate)|
|[az confidentialledger update](#LedgerUpdate)|Update|[Parameters](#ParametersLedgerUpdate)|[Example](#ExamplesLedgerUpdate)|
|[az confidentialledger delete](#LedgerDelete)|Delete|[Parameters](#ParametersLedgerDelete)|[Example](#ExamplesLedgerDelete)|


## COMMAND DETAILS
### group `az confidentialledger`
#### <a name="LedgerListByResourceGroup">Command `az confidentialledger list`</a>

##### <a name="ExamplesLedgerListByResourceGroup">Example</a>
```
az confidentialledger list --resource-group "DummyResourceGroupName"
```
##### <a name="ParametersLedgerListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--filter**|string|The filter to apply on the list operation. eg. $filter=ledgerType eq 'Public'|filter|$filter|

#### <a name="LedgerListBySubscription">Command `az confidentialledger list`</a>

##### <a name="ExamplesLedgerListBySubscription">Example</a>
```
az confidentialledger list
```
##### <a name="ParametersLedgerListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|The filter to apply on the list operation. eg. $filter=ledgerType eq 'Public'|filter|$filter|

#### <a name="LedgerGet">Command `az confidentialledger show`</a>

##### <a name="ExamplesLedgerGet">Example</a>
```
az confidentialledger show --name "DummyLedgerName" --resource-group "DummyResourceGroupName"
```
##### <a name="ParametersLedgerGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--ledger-name**|string|Name of the Confidential Ledger|ledger_name|ledgerName|

#### <a name="LedgerCreate">Command `az confidentialledger create`</a>

##### <a name="ExamplesLedgerCreate">Example</a>
```
az confidentialledger create --location "EastUS" --aad-based-security-principals ledger-role-name="Administrator" \
principal-id="34621747-6fc8-4771-a2eb-72f31c461f2e" tenant-id="bce123b9-2b7b-4975-8360-5ca0b9b1cd08" \
--cert-based-security-principals cert="-----BEGIN CERTIFICATE-----MIIBsjCCATigAwIBAgIUZWIbyG79TniQLd2UxJuU74tqrKcwCgYIK\
oZIzj0EAwMwEDEOMAwGA1UEAwwFdXNlcjAwHhcNMjEwMzE2MTgwNjExWhcNMjIwMzE2MTgwNjExWjAQMQ4wDAYDVQQDDAV1c2VyMDB2MBAGByqGSM49AgEG\
BSuBBAAiA2IABBiWSo/j8EFit7aUMm5lF+lUmCu+IgfnpFD+7QMgLKtxRJ3aGSqgS/GpqcYVGddnODtSarNE/HyGKUFUolLPQ5ybHcouUk0kyfA7XMeSoUA\
4lBz63Wha8wmXo+NdBRo39qNTMFEwHQYDVR0OBBYEFPtuhrwgGjDFHeUUT4nGsXaZn69KMB8GA1UdIwQYMBaAFPtuhrwgGjDFHeUUT4nGsXaZn69KMA8GA1\
UdEwEB/wQFMAMBAf8wCgYIKoZIzj0EAwMDaAAwZQIxAOnozm2CyqRwSSQLls5r+mUHRGRyXHXwYtM4Dcst/VEZdmS9fqvHRCHbjUlO/+HNfgIwMWZ4FmsjD\
3wnPxONOm9YdVn/PRD7SsPRPbOjwBiE4EBGaHDsLjYAGDSGi7NJnSkA-----END CERTIFICATE-----" ledger-role-name="Reader" \
--ledger-type "Public" --tags additionalProps1="additional properties" --name "DummyLedgerName" --resource-group \
"DummyResourceGroupName"
```
##### <a name="ParametersLedgerCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--ledger-name**|string|Name of the Confidential Ledger|ledger_name|ledgerName|
|**--location**|string|The Azure location where the Confidential Ledger is running.|location|location|
|**--tags**|dictionary|Additional tags for Confidential Ledger|tags|tags|
|**--ledger-type**|choice|Type of Confidential Ledger|ledger_type|ledgerType|
|**--aad-based-security-principals**|array|Array of all AAD based Security Principals.|aad_based_security_principals|aadBasedSecurityPrincipals|
|**--cert-based-security-principals**|array|Array of all cert based Security Principals.|cert_based_security_principals|certBasedSecurityPrincipals|

#### <a name="LedgerUpdate">Command `az confidentialledger update`</a>

##### <a name="ExamplesLedgerUpdate">Example</a>
```
az confidentialledger update --location "EastUS" --tags additionProps2="additional property value" \
additionalProps1="additional properties" --name "DummyLedgerName" --resource-group "DummyResourceGroupName"
```
##### <a name="ParametersLedgerUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--ledger-name**|string|Name of the Confidential Ledger|ledger_name|ledgerName|
|**--location**|string|The Azure location where the Confidential Ledger is running.|location|location|
|**--tags**|dictionary|Additional tags for Confidential Ledger|tags|tags|
|**--ledger-type**|choice|Type of Confidential Ledger|ledger_type|ledgerType|
|**--aad-based-security-principals**|array|Array of all AAD based Security Principals.|aad_based_security_principals|aadBasedSecurityPrincipals|
|**--cert-based-security-principals**|array|Array of all cert based Security Principals.|cert_based_security_principals|certBasedSecurityPrincipals|

#### <a name="LedgerDelete">Command `az confidentialledger delete`</a>

##### <a name="ExamplesLedgerDelete">Example</a>
```
az confidentialledger delete --name "DummyLedgerName" --resource-group "DummyResourceGroupName"
```
##### <a name="ParametersLedgerDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--ledger-name**|string|Name of the Confidential Ledger|ledger_name|ledgerName|
