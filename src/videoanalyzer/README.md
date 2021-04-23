# Azure CLI videoanalyzer Extension #
This is the extension for videoanalyzer

### How to use ###
Install this extension using the below CLI command
```
az extension add --name videoanalyzer
```

### Included Features ###
#### videoanalyzer video-analyzer ####
##### Create #####
```
az videoanalyzer video-analyzer create --account-name "contosotv" --video-analyzer-identity-type "UserAssigned" \
    --user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id1\\":{},\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id2\\":{},\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id3\\":{}}" \
    --location "South Central US" --type "SystemKey" \
    --storage-accounts id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/storage1" user-assigned-identity="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id2" \
    --tags tag1="value1" tag2="value2" --resource-group "contoso" 
```
##### Show #####
```
az videoanalyzer video-analyzer show --account-name "contosotv" --resource-group "contoso"
```
##### List #####
```
az videoanalyzer video-analyzer list --resource-group "contoso"
```
##### Update #####
```
az videoanalyzer video-analyzer update --account-name "contosotv" --tags key1="value3" --resource-group "contoso"
```
##### Sync-storage-key #####
```
az videoanalyzer video-analyzer sync-storage-key --account-name "contosotv" \
    --id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/contoso/providers/Microsoft.Storage/storageAccounts/contosotvstore" \
    --resource-group "contoso" 
```
##### Delete #####
```
az videoanalyzer video-analyzer delete --account-name "contosotv" --resource-group "contoso"
```
#### videoanalyzer edge-module ####
##### Create #####
```
az videoanalyzer edge-module create --account-name "testaccount2" --name "edgeModule1" --resource-group "testrg"
```
##### Show #####
```
az videoanalyzer edge-module show --account-name "testaccount2" --name "edgeModule1" --resource-group "testrg"
```
##### List #####
```
az videoanalyzer edge-module list --account-name "testaccount2" --resource-group "testrg"
```
##### List-provisioning-token #####
```
az videoanalyzer edge-module list-provisioning-token --account-name "testaccount2" --name "edgeModule1" \
    --expiration-date "3021-01-23T11:04:49.0526841-08:00" --resource-group "testrg" 
```
##### Delete #####
```
az videoanalyzer edge-module delete --account-name "testaccount2" --name "edgeModule1" --resource-group "testrg"
```
#### videoanalyzer video ####
##### Create #####
```
az videoanalyzer video create --account-name "testaccount2" --description "Sample Description 1" \
    --title "Sample Title 1" --resource-group "testrg" --name "video1" 
```
##### Show #####
```
az videoanalyzer video show --account-name "testaccount2" --resource-group "testrg" --name "video1"
```
##### List #####
```
az videoanalyzer video list --top "2" --account-name "testaccount2" --resource-group "testrg"
```
##### Update #####
```
az videoanalyzer video update --account-name "testaccount2" --description "Parking Lot East Entrance" \
    --resource-group "testrg" --name "video1" 
```
##### List-streaming-token #####
```
az videoanalyzer video list-streaming-token --account-name "testaccount2" --resource-group "testrg" --name "video3"
```
##### Delete #####
```
az videoanalyzer video delete --account-name "testaccount2" --resource-group "testrg" --name "video1"
```
#### videoanalyzer access-policy ####
##### Create #####
```
az videoanalyzer access-policy create --name "accessPolicyName1" --account-name "testaccount2" \
    --authentication "{\\"@type\\":\\"#Microsoft.VideoAnalyzer.JwtAuthentication\\",\\"audiences\\":[\\"audience1\\"],\\"claims\\":[{\\"name\\":\\"claimname1\\",\\"value\\":\\"claimvalue1\\"},{\\"name\\":\\"claimname2\\",\\"value\\":\\"claimvalue2\\"}],\\"issuers\\":[\\"issuer1\\",\\"issuer2\\"],\\"keys\\":[{\\"@type\\":\\"#Microsoft.VideoAnalyzer.RsaTokenKey\\",\\"alg\\":\\"RS256\\",\\"e\\":\\"ZLFzZTY0IQ==\\",\\"kid\\":\\"123\\",\\"n\\":\\"YmFzZTY0IQ==\\"},{\\"@type\\":\\"#Microsoft.VideoAnalyzer.EccTokenKey\\",\\"alg\\":\\"ES256\\",\\"kid\\":\\"124\\",\\"x\\":\\"XX==\\",\\"y\\":\\"YY==\\"}]}" \
    --resource-group "testrg" 
```
##### Show #####
```
az videoanalyzer access-policy show --name "accessPolicyName1" --account-name "testaccount2" --resource-group "testrg"
```
##### List #####
```
az videoanalyzer access-policy list --top "2" --account-name "testaccount2" --resource-group "testrg"
```
##### Update #####
```
az videoanalyzer access-policy update --name "accessPolicyName1" --account-name "testaccount2" \
    --authentication "{\\"@type\\":\\"#Microsoft.VideoAnalyzer.JwtAuthentication\\",\\"keys\\":[{\\"@type\\":\\"#Microsoft.VideoAnalyzer.RsaTokenKey\\",\\"alg\\":\\"RS256\\",\\"e\\":\\"ZLFzZTY0IQ==\\",\\"kid\\":\\"123\\",\\"n\\":\\"YmFzZTY0IQ==\\"},{\\"@type\\":\\"#Microsoft.VideoAnalyzer.EccTokenKey\\",\\"alg\\":\\"Updated\\",\\"kid\\":\\"124\\",\\"x\\":\\"XX==\\",\\"y\\":\\"YY==\\"}]}" \
    --resource-group "testrg" 
```
##### Delete #####
```
az videoanalyzer access-policy delete --name "accessPolicyName1" --account-name "testaccount2" \
    --resource-group "testrg" 
```