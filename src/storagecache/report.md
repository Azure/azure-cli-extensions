# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az storagecache|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az storagecache` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az storagecache sku|Skus|[commands](#CommandsInSkus)|
|az storagecache usage-model|UsageModels|[commands](#CommandsInUsageModels)|
|az storagecache asc-operation|AscOperations|[commands](#CommandsInAscOperations)|
|az storagecache|Caches|[commands](#CommandsInCaches)|
|az storagecache storage-target|StorageTargets|[commands](#CommandsInStorageTargets)|

## COMMANDS
### <a name="CommandsInCaches">Commands in `az storagecache` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagecache list](#CachesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersCachesListByResourceGroup)|[Example](#ExamplesCachesListByResourceGroup)|
|[az storagecache list](#CachesList)|List|[Parameters](#ParametersCachesList)|[Example](#ExamplesCachesList)|
|[az storagecache show](#CachesGet)|Get|[Parameters](#ParametersCachesGet)|[Example](#ExamplesCachesGet)|
|[az storagecache create](#CachesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersCachesCreateOrUpdate#Create)|[Example](#ExamplesCachesCreateOrUpdate#Create)|
|[az storagecache update](#CachesUpdate)|Update|[Parameters](#ParametersCachesUpdate)|[Example](#ExamplesCachesUpdate)|
|[az storagecache delete](#CachesDelete)|Delete|[Parameters](#ParametersCachesDelete)|[Example](#ExamplesCachesDelete)|
|[az storagecache debug-info](#CachesDebugInfo)|DebugInfo|[Parameters](#ParametersCachesDebugInfo)|[Example](#ExamplesCachesDebugInfo)|
|[az storagecache flush](#CachesFlush)|Flush|[Parameters](#ParametersCachesFlush)|[Example](#ExamplesCachesFlush)|
|[az storagecache start](#CachesStart)|Start|[Parameters](#ParametersCachesStart)|[Example](#ExamplesCachesStart)|
|[az storagecache stop](#CachesStop)|Stop|[Parameters](#ParametersCachesStop)|[Example](#ExamplesCachesStop)|
|[az storagecache upgrade-firmware](#CachesUpgradeFirmware)|UpgradeFirmware|[Parameters](#ParametersCachesUpgradeFirmware)|[Example](#ExamplesCachesUpgradeFirmware)|

### <a name="CommandsInAscOperations">Commands in `az storagecache asc-operation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagecache asc-operation show](#AscOperationsGet)|Get|[Parameters](#ParametersAscOperationsGet)|[Example](#ExamplesAscOperationsGet)|

### <a name="CommandsInSkus">Commands in `az storagecache sku` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagecache sku list](#SkusList)|List|[Parameters](#ParametersSkusList)|[Example](#ExamplesSkusList)|

### <a name="CommandsInStorageTargets">Commands in `az storagecache storage-target` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagecache storage-target list](#StorageTargetsListByCache)|ListByCache|[Parameters](#ParametersStorageTargetsListByCache)|[Example](#ExamplesStorageTargetsListByCache)|
|[az storagecache storage-target show](#StorageTargetsGet)|Get|[Parameters](#ParametersStorageTargetsGet)|[Example](#ExamplesStorageTargetsGet)|
|[az storagecache storage-target create](#StorageTargetsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersStorageTargetsCreateOrUpdate#Create)|[Example](#ExamplesStorageTargetsCreateOrUpdate#Create)|
|[az storagecache storage-target update](#StorageTargetsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersStorageTargetsCreateOrUpdate#Update)|Not Found|
|[az storagecache storage-target delete](#StorageTargetsDelete)|Delete|[Parameters](#ParametersStorageTargetsDelete)|[Example](#ExamplesStorageTargetsDelete)|
|[az storagecache storage-target dns-refresh](#StorageTargetsDnsRefresh)|DnsRefresh|[Parameters](#ParametersStorageTargetsDnsRefresh)|[Example](#ExamplesStorageTargetsDnsRefresh)|

### <a name="CommandsInUsageModels">Commands in `az storagecache usage-model` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagecache usage-model list](#UsageModelsList)|List|[Parameters](#ParametersUsageModelsList)|[Example](#ExamplesUsageModelsList)|


## COMMAND DETAILS

### group `az storagecache`
#### <a name="CachesListByResourceGroup">Command `az storagecache list`</a>

##### <a name="ExamplesCachesListByResourceGroup">Example</a>
```
az storagecache list --resource-group "scgroup"
```
##### <a name="ParametersCachesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|

#### <a name="CachesList">Command `az storagecache list`</a>

##### <a name="ExamplesCachesList">Example</a>
```
az storagecache list
```
##### <a name="ParametersCachesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="CachesGet">Command `az storagecache show`</a>

##### <a name="ExamplesCachesGet">Example</a>
```
az storagecache show --cache-name "sc1" --resource-group "scgroup"
```
##### <a name="ParametersCachesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|

#### <a name="CachesCreateOrUpdate#Create">Command `az storagecache create`</a>

##### <a name="ExamplesCachesCreateOrUpdate#Create">Example</a>
```
az storagecache create --location "westus" --cache-size-gb 3072 --cache-net-bios-name "contosoSmb" \
--cache-active-directory-settings-credentials password="<password>" username="consotoAdmin" --domain-name \
"contosoAd.contoso.local" --domain-net-bios-name "contosoAd" --primary-dns-ip-address "192.0.2.10" \
--secondary-dns-ip-address "192.0.2.11" --credentials bind-dn="cn=ldapadmin,dc=contosoad,dc=contoso,dc=local" \
bind-password="<bindPassword>" --extended-groups true --ldap-base-dn "dc=contosoad,dc=contoso,dc=local" --ldap-server \
"192.0.2.12" --username-source "LDAP" --key-url "https://keyvault-cmk.vault.azure.net/keys/key2047/test" --id \
"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.KeyVault/vaults/keyvaul\
t-cmk" --access-policies name="default" access-rules={"access":"rw","rootSquash":false,"scope":"default","submountAcces\
s":true,"suid":false} --subnet "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Mi\
crosoft.Network/virtualNetworks/scvnet/subnets/sub1" --name "Standard_2G" --tags Dept="Contoso" --cache-name "sc1" \
--resource-group "scgroup"
```
##### <a name="ExamplesCachesCreateOrUpdate#Create">Example</a>
```
az storagecache create --location "westus" --cache-size-gb 3072 --credentials bind-dn="cn=ldapadmin,dc=contosoad,dc=con\
toso,dc=local" bind-password="<bindPassword>" --extended-groups true --ldap-base-dn "dc=contosoad,dc=contoso,dc=local" \
--ldap-server "192.0.2.12" --username-source "LDAP" --key-url "https://keyvault-cmk.vault.azure.net/keys/key2048/test" \
--id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.KeyVault/vaults/ke\
yvault-cmk" --access-policies name="default" access-rules={"access":"rw","rootSquash":false,"scope":"default","submount\
Access":true,"suid":false} --subnet "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/provide\
rs/Microsoft.Network/virtualNetworks/scvnet/subnets/sub1" --name "Standard_2G" --tags Dept="Contoso" --cache-name \
"sc1" --resource-group "scgroup"
```
##### <a name="ParametersCachesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|Region name string.|location|location|
|**--cache-size-gb**|integer|The size of this Cache, in GB.|cache_size_gb|cacheSizeGB|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|provisioningState|
|**--subnet**|string|Subnet used for the Cache.|subnet|subnet|
|**--network-settings**|object|Specifies network settings of the cache.|network_settings|networkSettings|
|**--extended-groups**|boolean|Whether or not Extended Groups is enabled.|extended_groups|extendedGroups|
|**--username-source**|choice|This setting determines how the cache gets username and group names for clients.|username_source|usernameSource|
|**--group-file-uri**|string|The URI of the file containing group information (in /etc/group file format). This field must be populated when 'usernameSource' is set to 'File'.|group_file_uri|groupFileURI|
|**--user-file-uri**|string|The URI of the file containing user information (in /etc/passwd file format). This field must be populated when 'usernameSource' is set to 'File'.|user_file_uri|userFileURI|
|**--ldap-server**|string|The fully qualified domain name or IP address of the LDAP server to use.|ldap_server|ldapServer|
|**--ldap-base-dn**|string|The base distinguished name for the LDAP domain.|ldap_base_dn|ldapBaseDN|
|**--encrypt-ldap-connection**|boolean|Whether or not the LDAP connection should be encrypted.|encrypt_ldap_connection|encryptLdapConnection|
|**--require-valid-certificate**|boolean|Determines if the certificates must be validated by a certificate authority. When true, caCertificateURI must be provided.|require_valid_certificate|requireValidCertificate|
|**--auto-download-certificate**|boolean|Determines if the certificate should be automatically downloaded. This applies to 'caCertificateURI' only if 'requireValidCertificate' is true.|auto_download_certificate|autoDownloadCertificate|
|**--ca-certificate-uri**|string|The URI of the CA certificate to validate the LDAP secure connection. This field must be populated when 'requireValidCertificate' is set to true.|ca_certificate_uri|caCertificateURI|
|**--credentials**|object|When present, these are the credentials for the secure LDAP connection.|credentials|credentials|
|**--primary-dns-ip-address**|string|Primary DNS IP address used to resolve the Active Directory domain controller's fully qualified domain name.|primary_dns_ip_address|primaryDnsIpAddress|
|**--secondary-dns-ip-address**|string|Secondary DNS IP address used to resolve the Active Directory domain controller's fully qualified domain name.|secondary_dns_ip_address|secondaryDnsIpAddress|
|**--domain-name**|string|The fully qualified domain name of the Active Directory domain controller.|domain_name|domainName|
|**--domain-net-bios-name**|string|The Active Directory domain's NetBIOS name.|domain_net_bios_name|domainNetBiosName|
|**--cache-net-bios-name**|string|The NetBIOS name to assign to the HPC Cache when it joins the Active Directory domain as a server. Length must 1-15 characters from the class [-0-9a-zA-Z].|cache_net_bios_name|cacheNetBiosName|
|**--cache-active-directory-settings-credentials**|object|Active Directory admin credentials used to join the HPC Cache to a domain.|cache_active_directory_settings_credentials|credentials|
|**--access-policies**|array|NFS access policies defined for this cache.|access_policies|accessPolicies|
|**--key-url**|string|The URL referencing a key encryption key in Key Vault.|key_url|keyUrl|
|**--id**|string|Resource Id.|id|id|
|**--name**|string|SKU name for this Cache.|name|name|
|**--type**|sealed-choice|The type of identity used for the cache|type|type|

#### <a name="CachesUpdate">Command `az storagecache update`</a>

##### <a name="ExamplesCachesUpdate">Example</a>
```
az storagecache update --location "westus" --cache-size-gb 3072 --cache-net-bios-name "contosoSmb" --domain-name \
"contosoAd.contoso.local" --domain-net-bios-name "contosoAd" --primary-dns-ip-address "192.0.2.10" \
--secondary-dns-ip-address "192.0.2.11" --extended-groups true --username-source "AD" --network-settings \
dns-search-domain="contoso.com" dns-servers="10.1.22.33" dns-servers="10.1.12.33" mtu=1500 \
ntp-server="time.contoso.com" --access-policies name="default" access-rules={"access":"rw","rootSquash":false,"scope":"\
default","submountAccess":true,"suid":false} --access-policies name="restrictive" access-rules={"access":"rw","filter":\
"10.99.3.145","rootSquash":false,"scope":"host","submountAccess":true,"suid":true} access-rules={"access":"rw","filter"\
:"10.99.1.0/24","rootSquash":false,"scope":"network","submountAccess":true,"suid":true} access-rules={"access":"no","an\
onymousGID":"65534","anonymousUID":"65534","rootSquash":true,"scope":"default","submountAccess":true,"suid":false} \
--subnet "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.Network/virtua\
lNetworks/scvnet/subnets/sub1" --name "Standard_2G" --tags Dept="Contoso" --cache-name "sc1" --resource-group \
"scgroup"
```
##### <a name="ExamplesCachesUpdate">Example</a>
```
az storagecache update --location "westus" --cache-size-gb 3072 --credentials bind-dn="cn=ldapadmin,dc=contosoad,dc=con\
toso,dc=local" bind-password="<bindPassword>" --extended-groups true --ldap-base-dn "dc=contosoad,dc=contoso,dc=local" \
--ldap-server "192.0.2.12" --username-source "LDAP" --network-settings dns-search-domain="contoso.com" \
dns-servers="10.1.22.33" dns-servers="10.1.12.33" mtu=1500 ntp-server="time.contoso.com" --access-policies \
name="default" access-rules={"access":"rw","rootSquash":false,"scope":"default","submountAccess":true,"suid":false} \
--access-policies name="restrictive" access-rules={"access":"rw","filter":"10.99.3.145","rootSquash":false,"scope":"hos\
t","submountAccess":true,"suid":true} access-rules={"access":"rw","filter":"10.99.1.0/24","rootSquash":false,"scope":"n\
etwork","submountAccess":true,"suid":true} access-rules={"access":"no","anonymousGID":"65534","anonymousUID":"65534","r\
ootSquash":true,"scope":"default","submountAccess":true,"suid":false} --subnet "/subscriptions/00000000-0000-0000-0000-\
000000000000/resourceGroups/scgroup/providers/Microsoft.Network/virtualNetworks/scvnet/subnets/sub1" --name \
"Standard_2G" --tags Dept="Contoso" --cache-name "sc1" --resource-group "scgroup"
```
##### <a name="ParametersCachesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|Region name string.|location|location|
|**--cache-size-gb**|integer|The size of this Cache, in GB.|cache_size_gb|cacheSizeGB|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|provisioningState|
|**--subnet**|string|Subnet used for the Cache.|subnet|subnet|
|**--network-settings**|object|Specifies network settings of the cache.|network_settings|networkSettings|
|**--extended-groups**|boolean|Whether or not Extended Groups is enabled.|extended_groups|extendedGroups|
|**--username-source**|choice|This setting determines how the cache gets username and group names for clients.|username_source|usernameSource|
|**--group-file-uri**|string|The URI of the file containing group information (in /etc/group file format). This field must be populated when 'usernameSource' is set to 'File'.|group_file_uri|groupFileURI|
|**--user-file-uri**|string|The URI of the file containing user information (in /etc/passwd file format). This field must be populated when 'usernameSource' is set to 'File'.|user_file_uri|userFileURI|
|**--ldap-server**|string|The fully qualified domain name or IP address of the LDAP server to use.|ldap_server|ldapServer|
|**--ldap-base-dn**|string|The base distinguished name for the LDAP domain.|ldap_base_dn|ldapBaseDN|
|**--encrypt-ldap-connection**|boolean|Whether or not the LDAP connection should be encrypted.|encrypt_ldap_connection|encryptLdapConnection|
|**--require-valid-certificate**|boolean|Determines if the certificates must be validated by a certificate authority. When true, caCertificateURI must be provided.|require_valid_certificate|requireValidCertificate|
|**--auto-download-certificate**|boolean|Determines if the certificate should be automatically downloaded. This applies to 'caCertificateURI' only if 'requireValidCertificate' is true.|auto_download_certificate|autoDownloadCertificate|
|**--ca-certificate-uri**|string|The URI of the CA certificate to validate the LDAP secure connection. This field must be populated when 'requireValidCertificate' is set to true.|ca_certificate_uri|caCertificateURI|
|**--credentials**|object|When present, these are the credentials for the secure LDAP connection.|credentials|credentials|
|**--primary-dns-ip-address**|string|Primary DNS IP address used to resolve the Active Directory domain controller's fully qualified domain name.|primary_dns_ip_address|primaryDnsIpAddress|
|**--secondary-dns-ip-address**|string|Secondary DNS IP address used to resolve the Active Directory domain controller's fully qualified domain name.|secondary_dns_ip_address|secondaryDnsIpAddress|
|**--domain-name**|string|The fully qualified domain name of the Active Directory domain controller.|domain_name|domainName|
|**--domain-net-bios-name**|string|The Active Directory domain's NetBIOS name.|domain_net_bios_name|domainNetBiosName|
|**--cache-net-bios-name**|string|The NetBIOS name to assign to the HPC Cache when it joins the Active Directory domain as a server. Length must 1-15 characters from the class [-0-9a-zA-Z].|cache_net_bios_name|cacheNetBiosName|
|**--cache-active-directory-settings-credentials**|object|Active Directory admin credentials used to join the HPC Cache to a domain.|cache_active_directory_settings_credentials|credentials|
|**--access-policies**|array|NFS access policies defined for this cache.|access_policies|accessPolicies|
|**--key-url**|string|The URL referencing a key encryption key in Key Vault.|key_url|keyUrl|
|**--id**|string|Resource Id.|id|id|
|**--name**|string|SKU name for this Cache.|name|name|
|**--type**|sealed-choice|The type of identity used for the cache|type|type|

#### <a name="CachesDelete">Command `az storagecache delete`</a>

##### <a name="ExamplesCachesDelete">Example</a>
```
az storagecache delete --cache-name "sc" --resource-group "scgroup"
```
##### <a name="ParametersCachesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|

#### <a name="CachesDebugInfo">Command `az storagecache debug-info`</a>

##### <a name="ExamplesCachesDebugInfo">Example</a>
```
az storagecache debug-info --cache-name "sc" --resource-group "scgroup"
```
##### <a name="ParametersCachesDebugInfo">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|

#### <a name="CachesFlush">Command `az storagecache flush`</a>

##### <a name="ExamplesCachesFlush">Example</a>
```
az storagecache flush --cache-name "sc" --resource-group "scgroup"
```
##### <a name="ParametersCachesFlush">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|

#### <a name="CachesStart">Command `az storagecache start`</a>

##### <a name="ExamplesCachesStart">Example</a>
```
az storagecache start --cache-name "sc" --resource-group "scgroup"
```
##### <a name="ParametersCachesStart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|

#### <a name="CachesStop">Command `az storagecache stop`</a>

##### <a name="ExamplesCachesStop">Example</a>
```
az storagecache stop --cache-name "sc" --resource-group "scgroup"
```
##### <a name="ParametersCachesStop">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|

#### <a name="CachesUpgradeFirmware">Command `az storagecache upgrade-firmware`</a>

##### <a name="ExamplesCachesUpgradeFirmware">Example</a>
```
az storagecache upgrade-firmware --cache-name "sc1" --resource-group "scgroup"
```
##### <a name="ParametersCachesUpgradeFirmware">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|

### group `az storagecache asc-operation`
#### <a name="AscOperationsGet">Command `az storagecache asc-operation show`</a>

##### <a name="ExamplesAscOperationsGet">Example</a>
```
az storagecache asc-operation show --operation-id "testoperationid" --location "westus"
```
##### <a name="ParametersAscOperationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The name of the region used to look up the operation.|location|location|
|**--operation-id**|string|The operation id which uniquely identifies the asynchronous operation.|operation_id|operationId|

### group `az storagecache sku`
#### <a name="SkusList">Command `az storagecache sku list`</a>

##### <a name="ExamplesSkusList">Example</a>
```
az storagecache sku list
```
##### <a name="ParametersSkusList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
### group `az storagecache storage-target`
#### <a name="StorageTargetsListByCache">Command `az storagecache storage-target list`</a>

##### <a name="ExamplesStorageTargetsListByCache">Example</a>
```
az storagecache storage-target list --cache-name "sc1" --resource-group "scgroup"
```
##### <a name="ParametersStorageTargetsListByCache">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|

#### <a name="StorageTargetsGet">Command `az storagecache storage-target show`</a>

##### <a name="ExamplesStorageTargetsGet">Example</a>
```
az storagecache storage-target show --cache-name "sc1" --resource-group "scgroup" --name "st1"
```
##### <a name="ParametersStorageTargetsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--storage-target-name**|string|Name of Storage Target.|storage_target_name|storageTargetName|

#### <a name="StorageTargetsCreateOrUpdate#Create">Command `az storagecache storage-target create`</a>

##### <a name="ExamplesStorageTargetsCreateOrUpdate#Create">Example</a>
```
az storagecache storage-target create --cache-name "sc1" --resource-group "scgroup" --name "st1" --junctions \
namespace-path="/path/on/cache" nfs-access-policy="default" nfs-export="exp1" target-path="/path/on/exp1" --junctions \
namespace-path="/path2/on/cache" nfs-access-policy="rootSquash" nfs-export="exp2" target-path="/path2/on/exp2" --nfs3 \
target="10.0.44.44" usage-model="READ_HEAVY_INFREQ" --target-type "nfs3"
```
##### <a name="ExamplesStorageTargetsCreateOrUpdate#Create">Example</a>
```
az storagecache storage-target create --cache-name "sc1" --resource-group "scgroup" --name "st1" --blob-nfs \
target="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/scgroup/providers/Microsoft.Storage/storageA\
ccounts/blofnfs/blobServices/default/containers/blobnfs" usage-model="WRITE_WORKLOAD_15" --junctions \
namespace-path="/blobnfs" --target-type "blobNfs"
```
##### <a name="ExamplesStorageTargetsCreateOrUpdate#Create">Example</a>
```
az storagecache storage-target create --cache-name "sc1" --resource-group "scgroup" --name "st1" --nfs3 \
target="10.0.44.44" usage-model="READ_HEAVY_INFREQ" --target-type "nfs3"
```
##### <a name="ParametersStorageTargetsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--storage-target-name**|string|Name of Storage Target.|storage_target_name|storageTargetName|
|**--junctions**|array|List of Cache namespace junctions to target for namespace associations.|junctions|junctions|
|**--target-type**|choice|Type of the Storage Target.|target_type|targetType|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|provisioningState|
|**--nfs3**|object|Properties when targetType is nfs3.|nfs3|nfs3|
|**--blob-nfs**|object|Properties when targetType is blobNfs.|blob_nfs|blobNfs|
|**--attributes**|dictionary|Dictionary of string->string pairs containing information about the Storage Target.|attributes|attributes|
|**--target**|string|Resource ID of storage container.|target|target|

#### <a name="StorageTargetsCreateOrUpdate#Update">Command `az storagecache storage-target update`</a>

##### <a name="ParametersStorageTargetsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--storage-target-name**|string|Name of Storage Target.|storage_target_name|storageTargetName|
|**--junctions**|array|List of Cache namespace junctions to target for namespace associations.|junctions|junctions|
|**--target-type**|choice|Type of the Storage Target.|target_type|targetType|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|provisioningState|
|**--nfs3**|object|Properties when targetType is nfs3.|nfs3|nfs3|
|**--blob-nfs**|object|Properties when targetType is blobNfs.|blob_nfs|blobNfs|
|**--attributes**|dictionary|Dictionary of string->string pairs containing information about the Storage Target.|attributes|attributes|
|**--target**|string|Resource ID of storage container.|target|target|

#### <a name="StorageTargetsDelete">Command `az storagecache storage-target delete`</a>

##### <a name="ExamplesStorageTargetsDelete">Example</a>
```
az storagecache storage-target delete --cache-name "sc1" --resource-group "scgroup" --name "st1"
```
##### <a name="ParametersStorageTargetsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--storage-target-name**|string|Name of Storage Target.|storage_target_name|storageTargetName|

#### <a name="StorageTargetsDnsRefresh">Command `az storagecache storage-target dns-refresh`</a>

##### <a name="ExamplesStorageTargetsDnsRefresh">Example</a>
```
az storagecache storage-target dns-refresh --cache-name "sc" --resource-group "scgroup" --name "st1"
```
##### <a name="ParametersStorageTargetsDnsRefresh">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must not be greater than 80 and chars must be from the [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--storage-target-name**|string|Name of Storage Target.|storage_target_name|storageTargetName|

### group `az storagecache usage-model`
#### <a name="UsageModelsList">Command `az storagecache usage-model list`</a>

##### <a name="ExamplesUsageModelsList">Example</a>
```
az storagecache usage-model list
```
##### <a name="ParametersUsageModelsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|