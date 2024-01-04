# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az ad|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az ad` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az ad ds|DomainServices|[commands](#CommandsInDomainServices)|

## COMMANDS
### <a name="CommandsInDomainServices">Commands in `az ad ds` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az ad ds list](#DomainServicesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDomainServicesListByResourceGroup)|[Example](#ExamplesDomainServicesListByResourceGroup)|
|[az ad ds list](#DomainServicesList)|List|[Parameters](#ParametersDomainServicesList)|[Example](#ExamplesDomainServicesList)|
|[az ad ds show](#DomainServicesGet)|Get|[Parameters](#ParametersDomainServicesGet)|[Example](#ExamplesDomainServicesGet)|
|[az ad ds create](#DomainServicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDomainServicesCreateOrUpdate#Create)|[Example](#ExamplesDomainServicesCreateOrUpdate#Create)|
|[az ad ds update](#DomainServicesUpdate)|Update|[Parameters](#ParametersDomainServicesUpdate)|[Example](#ExamplesDomainServicesUpdate)|
|[az ad ds delete](#DomainServicesDelete)|Delete|[Parameters](#ParametersDomainServicesDelete)|[Example](#ExamplesDomainServicesDelete)|


## COMMAND DETAILS

### group `az ad ds`
#### <a name="DomainServicesListByResourceGroup">Command `az ad ds list`</a>

##### <a name="ExamplesDomainServicesListByResourceGroup">Example</a>
```
az ad ds list --resource-group "TestResourceGroup"
```
##### <a name="ParametersDomainServicesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DomainServicesList">Command `az ad ds list`</a>

##### <a name="ExamplesDomainServicesList">Example</a>
```
az ad ds list
```
##### <a name="ParametersDomainServicesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="DomainServicesGet">Command `az ad ds show`</a>

##### <a name="ExamplesDomainServicesGet">Example</a>
```
az ad ds show --name "TestDomainService.com" --resource-group "TestResourceGroup"
```
##### <a name="ParametersDomainServicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--domain-service-name**|string|The name of the domain service.|domain_service_name|domainServiceName|

#### <a name="DomainServicesCreateOrUpdate#Create">Command `az ad ds create`</a>

##### <a name="ExamplesDomainServicesCreateOrUpdate#Create">Example</a>
```
az ad ds create --domain "TestDomainService.com" --ntlm-v1 "Enabled" --sync-ntlm-pwd "Enabled" --tls-v1 "Disabled" \
--filtered-sync "Enabled" --external-access "Enabled" --ldaps "Enabled" --pfx-cert "MIIDPDCCAiSgAwIBAgIQQUI9P6tq2p9OFIJ\
a7DLNvTANBgkqhkiG9w0BAQsFADAgMR4w..." --pfx-cert-pwd "<pfxCertificatePassword>" --notify-others "jicha@microsoft.com" \
"caalmont@microsoft.com" --notify-dc-admins "Enabled" --notify-global-admins "Enabled" --replica-sets location="West \
US" subnet-id="/subscriptions/1639790a-76a2-4ac4-98d9-8562f5dfcb4d/resourceGroups/TestNetworkResourceGroup/providers/Mi\
crosoft.Network/virtualNetworks/TestVnetWUS/subnets/TestSubnetWUS" --name "TestDomainService.com" --resource-group \
"TestResourceGroup"
```
##### <a name="ParametersDomainServicesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--domain-service-name**|string|The name of the domain service.|domain_service_name|domainServiceName|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--domain-name**|string|The name of the Azure domain that the user would like to deploy Domain Services to.|domain_name|domainName|
|**--replica-sets**|array|List of ReplicaSets|replica_sets|replicaSets|
|**--domain-configuration-type**|choice|Domain Configuration Type|domain_configuration_type|domainConfigurationType|
|**--sku**|choice|Sku Type|sku|sku|
|**--filtered-sync**|choice|Enabled or Disabled flag to turn on Group-based filtered sync|filtered_sync|filteredSync|
|**--notify-global-admins**|choice|Should global admins be notified|notify_global_admins|notifyGlobalAdmins|
|**--notify-dc-admins**|choice|Should domain controller admins be notified|notify_dc_admins|notifyDcAdmins|
|**--additional-recipients**|array|The list of additional recipients|additional_recipients|additionalRecipients|
|**--ntlm-v1**|choice|A flag to determine whether or not NtlmV1 is enabled or disabled.|ntlm_v1|ntlmV1|
|**--tls-v1**|choice|A flag to determine whether or not TlsV1 is enabled or disabled.|tls_v1|tlsV1|
|**--sync-ntlm-passwords**|choice|A flag to determine whether or not SyncNtlmPasswords is enabled or disabled.|sync_ntlm_passwords|syncNtlmPasswords|
|**--sync-kerberos-passwords**|choice|A flag to determine whether or not SyncKerberosPasswords is enabled or disabled.|sync_kerberos_passwords|syncKerberosPasswords|
|**--sync-on-prem-passwords**|choice|A flag to determine whether or not SyncOnPremPasswords is enabled or disabled.|sync_on_prem_passwords|syncOnPremPasswords|
|**--settings**|array|List of settings for Resource Forest|settings|settings|
|**--resource-forest**|choice|Resource Forest|resource_forest|resourceForest|
|**--ldaps**|choice|A flag to determine whether or not Secure LDAP is enabled or disabled.|ldaps|ldaps|
|**--pfx-certificate**|string|The certificate required to configure Secure LDAP. The parameter passed here should be a base64encoded representation of the certificate pfx file.|pfx_certificate|pfxCertificate|
|**--pfx-certificate-password**|string|The password to decrypt the provided Secure LDAP certificate pfx file.|pfx_certificate_password|pfxCertificatePassword|
|**--external-access**|choice|A flag to determine whether or not Secure LDAP access over the internet is enabled or disabled.|external_access|externalAccess|

#### <a name="DomainServicesUpdate">Command `az ad ds update`</a>

##### <a name="ExamplesDomainServicesUpdate">Example</a>
```
az ad ds update --ntlm-v1 "Enabled" --sync-ntlm-pwd "Enabled" --tls-v1 "Disabled" --filtered-sync "Enabled" \
--external-access "Enabled" --ldaps "Enabled" --pfx-cert "MIIDPDCCAiSgAwIBAgIQQUI9P6tq2p9OFIJa7DLNvTANBgkqhkiG9w0BAQsFA\
DAgMR4w..." --pfx-cert-pwd "<pfxCertificatePassword>" --notify-others "jicha@microsoft.com" "caalmont@microsoft.com" \
--notify-dc-admins "Enabled" --notify-global-admins "Enabled" --replica-sets location="West US" \
subnet-id="/subscriptions/1639790a-76a2-4ac4-98d9-8562f5dfcb4d/resourceGroups/TestNetworkResourceGroup/providers/Micros\
oft.Network/virtualNetworks/TestVnetWUS/subnets/TestSubnetWUS" --replica-sets location="East US" \
subnet-id="/subscriptions/1639790a-76a2-4ac4-98d9-8562f5dfcb4d/resourceGroups/TestNetworkResourceGroup/providers/Micros\
oft.Network/virtualNetworks/TestVnetEUS/subnets/TestSubnetEUS" --name "TestDomainService.com" --resource-group \
"TestResourceGroup"
```
##### <a name="ParametersDomainServicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--domain-service-name**|string|The name of the domain service.|domain_service_name|domainServiceName|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--replica-sets**|array|List of ReplicaSets|replica_sets|replicaSets|
|**--domain-configuration-type**|choice|Domain Configuration Type|domain_configuration_type|domainConfigurationType|
|**--sku**|choice|Sku Type|sku|sku|
|**--filtered-sync**|choice|Enabled or Disabled flag to turn on Group-based filtered sync|filtered_sync|filteredSync|
|**--notify-global-admins**|choice|Should global admins be notified|notify_global_admins|notifyGlobalAdmins|
|**--notify-dc-admins**|choice|Should domain controller admins be notified|notify_dc_admins|notifyDcAdmins|
|**--additional-recipients**|array|The list of additional recipients|additional_recipients|additionalRecipients|
|**--ntlm-v1**|choice|A flag to determine whether or not NtlmV1 is enabled or disabled.|ntlm_v1|ntlmV1|
|**--tls-v1**|choice|A flag to determine whether or not TlsV1 is enabled or disabled.|tls_v1|tlsV1|
|**--sync-ntlm-passwords**|choice|A flag to determine whether or not SyncNtlmPasswords is enabled or disabled.|sync_ntlm_passwords|syncNtlmPasswords|
|**--sync-kerberos-passwords**|choice|A flag to determine whether or not SyncKerberosPasswords is enabled or disabled.|sync_kerberos_passwords|syncKerberosPasswords|
|**--sync-on-prem-passwords**|choice|A flag to determine whether or not SyncOnPremPasswords is enabled or disabled.|sync_on_prem_passwords|syncOnPremPasswords|
|**--settings**|array|List of settings for Resource Forest|settings|settings|
|**--resource-forest**|choice|Resource Forest|resource_forest|resourceForest|
|**--ldaps**|choice|A flag to determine whether or not Secure LDAP is enabled or disabled.|ldaps|ldaps|
|**--pfx-certificate**|string|The certificate required to configure Secure LDAP. The parameter passed here should be a base64encoded representation of the certificate pfx file.|pfx_certificate|pfxCertificate|
|**--pfx-certificate-password**|string|The password to decrypt the provided Secure LDAP certificate pfx file.|pfx_certificate_password|pfxCertificatePassword|
|**--external-access**|choice|A flag to determine whether or not Secure LDAP access over the internet is enabled or disabled.|external_access|externalAccess|

#### <a name="DomainServicesDelete">Command `az ad ds delete`</a>

##### <a name="ExamplesDomainServicesDelete">Example</a>
```
az ad ds delete --name "TestDomainService.com" --resource-group "TestResourceGroup"
```
##### <a name="ParametersDomainServicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--domain-service-name**|string|The name of the domain service.|domain_service_name|domainServiceName|
