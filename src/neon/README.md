
# Azure CLI Neon Extension #
This is an extension to Azure CLI to manage Neon Postgres resources.

## How to use ##
#### Install the extension ####
Install this extension using the below CLI command:
```
az extension add --name neon
```

#### Check the version ####
```
az extension show --name neon --query version
```

#### Connect to Azure subscription ####
```
az login
az account set -s {subs_id}
```

#### Create a resource group (or use an existing one) ####
```
az group create -n demoResourceGroup -l eastus
```

## Available Commands ##

### Create a Neon Postgres Instance ###
```
az neon postgres create --resource-group {resource_group} --name {resource_name} --user-details '{"first-name": "{user_first_name}", "last-name": "{user_last_name}", "email-address": "{user_email}", "upn": "{user_upn}", "phone-number": "{user_phone}"}' --company-details '{"company-name": "{company_name}", "office-address": "{office_address}", "country": "{country}", "domain": "{domain}", "number-of-employees": {number_of_employee}}' --partner-organization-properties '{"organization-id": "{org_id}", "org-name": "{partner_org_name}", "single-sign-on-properties": {"single-sign-on-state": "{sso_state}", "enterprise-app-id": "{app_id}", "single-sign-on-url": "{sso_url}", "aad-domains": ["{domain}"]}}' --tags "{key:value}" --location {location}
```

### Show a Neon Postgres Organization ###
```
az neon postgres organization show --resource-group {resource_group} --name {resource_name}
```

### Delete a Neon Postgres Organization ###
```
az neon postgres organization delete --resource-group {resource_group} --name {resource_name}
```

### List Neon resources by subscription ID ###
```
az neon postgres organization list --subscription {subscription_id} --resource-group {resource_group}
```

### Update a Neon Postgres Organization (without location and marketplace details) ###
```
az neon postgres organization update --resource-group {resource_group} --name {resource_name} --user-details '{"first-name": "{user_first_name}", "last-name": "{user_last_name}", "email-address": "{user_email}", "upn": "{user_upn}", "phone-number": "{user_phone}"}' --company-details '{"company-name": "{company_name}", "office-address": "{office_address}", "country": "{country}", "domain": "{domain}", "number-of-employees": {number_of_employee}}' --partner-organization-properties '{"organization-id": "{org_id}", "org-name": "{partner_org_name}", "single-sign-on-properties": {"single-sign-on-state": "{sso_state}", "enterprise-app-id": "{app_id}", "single-sign-on-url": "{sso_url}", "aad-domains": ["{domain}"]}}' --tags "{key:value}"
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
