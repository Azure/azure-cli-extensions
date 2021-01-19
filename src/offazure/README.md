# Azure CLI offazure Extension #
This is the extension for offazure

### How to use ###
Install this extension using the below CLI command
```
az extension add --name offazure
```

### Included Features ###
#### offazure hyper-v-cluster ####
##### Put-cluster #####
```
az offazure hyper-v-cluster put-cluster --fqdn "10.10.10.30" \
    --run-as-account-id "/subscriptions/4bd2aa0f-2bd2-4d67-91a8-5a4533d58600/resourceGroups/pajindTest/providers/Microsoft.OffAzure/HyperVSites/appliance1e39site/runasaccounts/Account1" \
    --cluster-name "cluster1" --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Show-all-cluster-in-site #####
```
az offazure hyper-v-cluster show-all-cluster-in-site --resource-group "ipsahoo-RI-121119" \
    --site-name "hyperv121319c813site" --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Show-cluster #####
```
az offazure hyper-v-cluster show-cluster \
    --cluster-name "hypgqlclusrs1-ntdev-corp-micros-11e77b27-67cc-5e46-a5d8-0ff3dc2ef179" \
    --resource-group "ipsahoo-RI-121119" --site-name "hyperv121319c813site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
#### offazure hyper-v-host ####
##### Put-host #####
```
az offazure hyper-v-host put-host --fqdn "10.10.10.20" --run-as-account-id "Account1" --host-name "Host1" \
    --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Show-all-host-in-site #####
```
az offazure hyper-v-host show-all-host-in-site --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Show-host #####
```
az offazure hyper-v-host show-host --host-name "bcdr-ewlab-46-ntdev-corp-micros-e4638031-3b19-5642-926d-385da60cfb8a" \
    --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
#### offazure hyper-v-job ####
#### offazure hyper-v-machine ####
##### Show-all-machine-in-site #####
```
az offazure hyper-v-machine show-all-machine-in-site --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Show-machine #####
```
az offazure hyper-v-machine show-machine --machine-name "96d27052-052b-48db-aa84-b9978eddbf5d" \
    --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
#### offazure hyper-v-operation-status ####
##### Show-operation-status #####
```
az offazure hyper-v-operation-status show-operation-status \
    --operation-status-name "996212ae-5c5f-419f-bb11-6f5c9b1ad90d" --resource-group "myResourceGroup" \
    --site-name "pajind_site1" --subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b" 
```
#### offazure hyper-v-run-as-account ####
##### Show-all-run-as-account-in-site #####
```
az offazure hyper-v-run-as-account show-all-run-as-account-in-site --resource-group "pajindTest" \
    --site-name "appliance1e39site" --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Show-run-as-account #####
```
az offazure hyper-v-run-as-account show-run-as-account --account-name "account1" --resource-group "pajindTest" \
    --site-name "appliance1e39site" --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
#### offazure hyper-v-site ####
##### Put-site #####
```
az offazure hyper-v-site put-site --location "eastus" \
    --service-principal-identity-details aad-authority="https://login.windows.net/72f988bf-86f1-41af-91ab-2d7cd011db47" application-id="e9f013df-2a2a-4871-b766-e79867f30348" audience="https://72f988bf-86f1-41af-91ab-2d7cd011db47/MaheshSite17ac9agentauthaadapp" object-id="2cd492bc-7ef3-4ee0-b301-59a88108b47b" tenant-id="72f988bf-86f1-41af-91ab-2d7cd011db47" \
    --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Get-site-usage #####
```
az offazure hyper-v-site get-site-usage --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Patch-site #####
```
az offazure hyper-v-site patch-site --location "westeurope" \
    --agent-details key-vault-id="/subscriptions/4bd2aa0f-2bd2-4d67-91a8-5a4533d58600/resourceGroups/pajindTest/providers/Microsoft.KeyVault/vaults/appliance1e39kv" key-vault-uri="https://appliance1e39kv.vault.azure.net" \
    --appliance-name "appliance" \
    --discovery-solution-id "/subscriptions/4bd2aa0f-2bd2-4d67-91a8-5a4533d58600/resourceGroups/pajindTest/providers/Microsoft.Migrate/MigrateProjects/WestEuropeTest/Solutions/Servers-Discovery-ServerDiscovery" \
    --service-principal-identity-details aad-authority="https://login.windows.net/72f988bf-86f1-41af-91ab-2d7cd011db47" application-id="61635e77-1e11-4c57-86d1-a8bf45d027fe" audience="https://72f988bf-86f1-41af-91ab-2d7cd011db47/appliance1e39agentauthaadapp" object-id="809f96f7-5c3b-45cf-a1ee-65b5d1689919" raw-cert-data="MIIDNDCCAhygAwIBAgIQcG1waNhSQHq+QWMteouKoDANBgkqhkiG9w0BAQsFADAXMRUwEwYDVQQDEwxBZ2VudFNwbkNlcnQwHhcNMTkwNTA5MDc0MDQ5WhcNMjIwNTA5MDc1MDQ5WjAXMRUwEwYDVQQDEwxBZ2VudFNwbkNlcnQwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCovoqe6ey6QROBYESERRC8ZECO0jqsSDUWYtoFpEsgmvPa5ht3nqQAx7ODGzbV3eIPGHF2dRz2E4quvmo9g7DK4n5mukloE7zIVeo9WCdxF6ru13X6Q8aKCz6BLl10L9DpmKTeQwrbohKV+9HSE4K8wXB0flezTrcUzRZGQRbB3CInpPhRJfWVLIQuZngSJ3qZ/Y6ejYLA4dUdKHMyvjDcmc//VGczZPhfLxZc9t8bhxiiYopWyAkF6ZWCeEUsMcFuiBOft5lNHEFNRkRVgADBekDSK5iJqcvBIzOezbagZewvum2GviQEbe3yxQF+TygjLB8xLL1XVYop4Y4xRu2bAgMBAAGjfDB6MA4GA1UdDwEB/wQEAwIFoDAJBgNVHRMEAjAAMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAfBgNVHSMEGDAWgBSFDL/nQvfZoLGuuw+fwSiFMi8CSTAdBgNVHQ4EFgQUhQy/50L32aCxrrsPn8EohTIvAkkwDQYJKoZIhvcNAQELBQADggEBADxJp9gLn7x6tp4fmApAoMBIghIJb36KJjT6sjGz9wsXNfH4S0kHQbgj8EAJpz8TlSBpjNmJ7DkwxorNn1BeG/DrnBvUJ9sNeI3rISCXrrw89CHy86uGXtn7BZ+2Co1UTHy98nkWK/1pPyMrSM8HxneWQGAa1bLKTclp+QRJNnQwJ9pEPuAr5BaWJkT737YkiE5NNcaaGDA5nLW91ARL5HNumtpwIDoN+l7OtAfRIgu83HFLeiqlVaR6x+7wtnA7n+fomIznBQ4vsoIclSPZ9vSaudT98TXN8m8CkQGEZi6w4gpmjQnXTehzvpdTbv1H+9iKsuPIDkjwiiLmr6mUbXs=" tenant-id="72f988bf-86f1-41af-91ab-2d7cd011db47" \
    --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Get-site-health-summary #####
```
az offazure hyper-v-site get-site-health-summary --resource-group "HMWalkthroughDay1-Scale" \
    --site-name "HyperV1acf8site" --subscription-id "8c3c936a-c09b-4de3-830b-3f5f244d72e9" 
```
##### Refresh-site #####
```
az offazure hyper-v-site refresh-site --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Show-site #####
```
az offazure hyper-v-site show-site --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Delete #####
```
az offazure hyper-v-site delete --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
#### offazure job ####
#### offazure machine ####
##### Show-all-machine-in-site #####
```
az offazure machine show-all-machine-in-site --resource-group "myResourceGroup" --site-name "pajind_site1" \
    --subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b" 
```
##### Show-machine #####
```
az offazure machine show-machine --name "machine1" --resource-group "myResourceGroup" --site-name "pajind_site1" \
    --subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b" 
```
#### offazure run-as-account ####
##### Show-all-run-as-account-in-site #####
```
az offazure run-as-account show-all-run-as-account-in-site --resource-group "myResourceGroup" \
    --site-name "pajind_site1" --subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b" 
```
##### Show-run-as-account #####
```
az offazure run-as-account show-run-as-account --account-name "account1" --resource-group "myResourceGroup" \
    --site-name "pajind_site1" --subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b" 
```
#### offazure site ####
##### Put-site #####
```
az offazure site put-site --location "eastus" \
    --service-principal-identity-details aad-authority="https://login.windows.net/72f988bf-86f1-41af-91ab-2d7cd011db47" application-id="e9f013df-2a2a-4871-b766-e79867f30348" audience="https://72f988bf-86f1-41af-91ab-2d7cd011db47/MaheshSite17ac9agentauthaadapp" object-id="2cd492bc-7ef3-4ee0-b301-59a88108b47b" tenant-id="72f988bf-86f1-41af-91ab-2d7cd011db47" \
    --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Get-site-usage #####
```
az offazure site get-site-usage --resource-group "rahasijaBugBash050919" --name "rahasapp122119d37csite" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Patch-site #####
```
az offazure site patch-site --name "pajind_site1" --location "" \
    --agent-details key-vault-id="string" key-vault-uri="https://keyVaultUri" --appliance-name "string" \
    --discovery-solution-id "string" \
    --service-principal-identity-details aad-authority="https://login.windows.net/72f988bf-86f1-41af-91ab-2d7cd011db47" application-id="e9f013df-2a2a-4871-b766-e79867f30348" audience="https://72f988bf-86f1-41af-91ab-2d7cd011db47/MaheshSite17ac9agentauthaadapp" object-id="2cd492bc-7ef3-4ee0-b301-59a88108b47b" raw-cert-data="string" tenant-id="72f988bf-86f1-41af-91ab-2d7cd011db47" \
    --resource-group "myResourceGroup" --site-name "pajind_site1" \
    --subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b" 
```
##### Get-site-health-summary #####
```
az offazure site get-site-health-summary --resource-group "rahasijaBugBash050919" --name "rahasapp122119d37csite" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Refresh-site #####
```
az offazure site refresh-site --resource-group "pajindTest" --name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Show-site #####
```
az offazure site show-site --resource-group "myResourceGroup" --name "pajind_site1" \
    --subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b" 
```
##### Delete #####
```
az offazure site delete --resource-group "myResourceGroup" --name "pajind_site1" \
    --subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b" 
```
#### offazure v-center ####
##### Put-v-center #####
```
az offazure v-center put-v-center --fqdn "idclab-a226vc6" \
    --run-as-account-id "/subscriptions/4bd2aa0f-2bd2-4d67-91a8-5a4533d58600/resourceGroups/pajindTest/providers/Microsoft.OffAzure/VMwareSites/appliance1e39site/runasaccounts/account1" \
    --resource-group "pajindTest" --site-name "appliance1e39site" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" --vcenter-name "vcenter1" 
```
##### Show-all-v-center-in-site #####
```
az offazure v-center show-all-v-center-in-site --resource-group "rahasijaBugBash050919" \
    --site-name "rahasapp122119d37csite" --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" 
```
##### Show-v-center #####
```
az offazure v-center show-v-center --resource-group "rahasijaBugBash050919" --site-name "rahasapp122119d37csite" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" --name "10-150-8-50-6af5f800-e9f6-56ff-9c3c-7be56d242c31" 
```
##### Delete #####
```
az offazure v-center delete --resource-group "rahasijaBugBash050919" --site-name "rahasapp122119d37csite" \
    --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" --name "10-150-8-50-6af5f800-e9f6-56ff-9c3c-7be56d242c31" 
```
#### offazure v-mware-operation-status ####
##### Show-operation-status #####
```
az offazure v-mware-operation-status show-operation-status \
    --operation-status-name "996212ae-5c5f-419f-bb11-6f5c9b1ad90d" --resource-group "myResourceGroup" \
    --site-name "pajind_site1" --subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b" 
```