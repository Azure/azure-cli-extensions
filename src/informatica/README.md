# Azure CLI Informatica Extension #
This is an extension to Azure CLI to manage Informatica resources.

## How to use ##
#### Install the extension ####
Install this extension using the below CLI command
```
az extension add --name informatica
```
#### Check the version ####
```
az extension show --name informatica --query version
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
# Create Informatica Organization
```
az informatica data-management organization create --resource-group {resource_group} --organization-name {name} --subscription {subscription} --location {location} --company-details '{"company-name": "{company_name}", "office-address": "{office_address}", "country": "{country}", "domain": "{domain}", "number-of-employees": {number_of_employee}}' --marketplace-details '{"marketplace-subscription-id": "{marketplace_subscription_id}", "offer-details": {"offer-id": "{offer_id}", "plan-id": "{plan_id}", "plan-name": "{plan_name}", "publisher-id": "{publisher_id}", "term-unit": "{term_unit}", "term-id": "{term_id}"}}' --user-details '{"first-name": "{user_first_name}", "last-name": "{user_last_name}", "email-address": "{user_email}", "upn": "{user_upn}", "phone-number": "{user_phone}"}' --informatica-properties '{"organization-id": "{org_id}", "organization-name": "{org_name}", "informatica-region": "{informatica_region}"}' --link-organization '{"token": "{link_token}"}'
```
# Show an Informatica Organization Resource
```
az informatica data-management organization show -g {resource_group} -n {org_name} --subscription {subscription}
```
# List Informatica Organization Resourcs by subscription ID
```
az informatica data-management organization list --subscription {subscription} --resource-group {resource_group}
```
# Delete Informatica Organization
```
az informatica data-management organization delete -n {org_name} -g {resource_group} --subscription {subscription} --yes
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
