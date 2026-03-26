# Azure CLI Trustedsigning Extension #
This is an extension to Azure CLI to manage Trustedsigning resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name trustedsigning
```

#### Connect to Azure subscription ####
```
az login
az account set -s {subs_id}
```

#### Create a resource group (or use an existing one) ####
```
az group create -n testrg -l eastus
```

### Included Features ###
#### Create a trusted signing account ####
```
az trustedsigning create -n MyAccount -l westus -g MyResourceGroup  -sku Basic
```

#### List accounts under a resource group ####
```
az trustedsigning list -g MyResourceGroup
```

#### Get an account ####
```
az trustedsigning show -n MyAccount  -g MyResourceGroup
```

#### Update an account ####
```
az trustedsigning update -n MyAccount -g MyResourceGroup --sku Premium --tags "key1=value1 key2=value2"
```

#### Delete an account ####
```
az trustedsigning delete -n MyAccount -g MyResourceGroup
```

#### trustedsigning certificate-profile ####

#### Create a certificate profile under an account ####
```
az trustedsigning certificate-profile create -g MyResourceGroup --account-name MyAccount -n MyProfile --profile-type PublicTrust --identity-validation-id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 
```

#### List certificate profiles under an account ####
```
az trustedsigning certificate-profile list -g MyResourceGroup --account-name
```

#### Get a certificate profile  ####
```
az trustedsigning certificate-profile show -n MyAccount -g MyResourceGroup
```

#### Delete a certificate profile ####
```
az trustedsigning certificate-profile delete -g MyResourceGroup --account-name MyAccount -n MyProfile
```

#### Check if account name is available ####
```
az trustedsigning check-name-availability --name MyAccount --type Microsoft.CodeSigning/codeSigningAccounts
```

#### Check if certificate profile name is available ####
```
az trustedsigning check-name-availability --name MyAccount/MyProfile --type Microsoft.CodeSigning/codeSigningAccounts/certificateProfiles
```