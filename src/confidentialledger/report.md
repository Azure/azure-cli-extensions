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
az confidentialledger update --location "EastUS" --aad-based-security-principals ledger-role-name="Administrator" \
principal-id="34621747-6fc8-4771-a2eb-72f31c461f2e" tenant-id="bce123b9-2b7b-4975-8360-5ca0b9b1cd08" \
--cert-based-security-principals cert="-----BEGIN CERTIFICATE-----\\nMIIDUjCCAjqgAwIBAgIQJ2IrDBawSkiAbkBYmiAopDANBgkqhk\
iG9w0BAQsFADAmMSQwIgYDVQQDExtTeW50aGV0aWNzIExlZGdlciBVc2VyIENlcnQwHhcNMjAwOTIzMjIxODQ2WhcNMjEwOTIzMjIyODQ2WjAmMSQwIgYDV\
QQDExtTeW50aGV0aWNzIExlZGdlciBVc2VyIENlcnQwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCX2s/Eu4q/eQ63N+Ugeg5oAciZua/YCJr4\
1c/696szvSY7Zg1SNJlW88/nbz70+QpO55OmqlEE3QCU+T0Vl/h0Gf//n1PYcoBbTGUnYEmV+fTTHict6rFiEwrGJ62tvcpYgwapInSLyEeUzjki0zhOLJ1\
OfRnYd1eGnFVMpE5aVjiS8Q5dmTEUyd51EIprGE8RYAW9aeWSwTH7gjHUsRlJnHKcdhaK/v5QKJnNu5bzPFUcpC0ZBcizoMPAtroLAD4B68Jl0z3op18MgZ\
e6lRrVoWuxfqnk5GojuB/Vu8ohAZKoFhQ6NB6r+LL2AUs+Zr7Bt26IkEdR178n9JMEA4gHAgMBAAGjfDB6MA4GA1UdDwEB/wQEAwIFoDAJBgNVHRMEAjAAM\
B0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAfBgNVHSMEGDAWgBS/a7PU9iOfOKEyZCp11Oen5VSuuDAdBgNVHQ4EFgQUv2uz1PYjnzihMmQqddTn\
p+VUrrgwDQYJKoZIhvcNAQELBQADggEBAF5q2fDwnse8egXhfaJCqqM969E9gSacqFmASpoDJPRPEX7gqoO7v1ww7nqRtRDoRiBvo/yNk7jlSAkRN3nRRnZ\
LZZ3MYQdmCr4FGyIqRg4Y94+nja+Du9pDD761rxRktMVPSOaAVM/E5DQvscDlPvlPYe9mkcrLCE4DXYpiMmLT8Tm55LJJq5m07dVDgzAIR1L/hmEcbK0pnL\
gzciMtMLxGO2udnyyW/UW9WxnjvrrD2JluTHH9mVbb+XQP1oFtlRBfH7aui1ZgWfKvxrdP4zdK9QoWSUvRux3TLsGmHRBjBMtqYDY3y5mB+aNjLelvWpeVb\
0m2aOSVXynrLwNCAVA=\\n-----END CERTIFICATE-----" ledger-role-name="Reader" --ledger-type "Public" --tags \
additionProps2="additional property value" additionalProps1="additional properties" --name "DummyLedgerName" \
--resource-group "DummyResourceGroupName"
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
