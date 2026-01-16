# Azure CLI Site Extension #
This is an extension to Azure CLI to manage Site resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name site
```
## What is Azure Arc site manager?
Azure Arc site manager allows you to manage and monitor your on-premises environments as Azure Arc sites. Arc sites are scoped to an Azure resource group, subscription or service group and enable you to track connectivity, alerts, and updates across your environment. The experience is tailored for on-premises scenarios where infrastructure is often managed within a common physical boundary, such as a store, restaurant, or factory.

### Included Features ###
##### Create a Site at service group scope #####
    ```
        az site create --site-name TestSiteName --service-group TestSGName --display-name 'Test Site Display' --description "Test Site" --labels key1="value1" key2="value2" --street-address1="16 TOWNSEND ST" --street-address2="UNIT 1" --city="newyork" --state-or-province="CA" --country="US" --postal-code="94107"
    ```

##### Create a Site at resource group scope #####
    ```
        az site create --site-name TestSiteName --resource-group TestRGName --subscription 000000000-0000-0000-0000-000000000000 --display-name 'Test Site Display' --description "Test Site" --street-address1="16 TOWNSEND ST" --street-address2="UNIT 1" --city="newyork" --state-or-province="CA" --country="US" --postal-code="94107"
    ```

##### Create a Site at subscription scope #####
    ```
        az site create --site-name TestSiteName --subscription 000000000-0000-0000-0000-000000000000 --display-name 'Test Site Display' --description "Test Site" --labels key1="value1" --street-address1="16 TOWNSEND ST" --street-address2="UNIT 1" --city="newyork" --state-or-province="CA" --country="US" --postal-code="94107"
    ```

##### Delete a Site at service group scope #####
    ```
        az site delete --site-name TestSiteName --service-group TestSGName
    ```

##### Delete a Site at resource group scope #####
    ```
        az site delete --site-name TestSiteName --resource-group TestRGName --subscription 00000000-0000-0000-0000-000000000000
    ```

##### Delete a Site at subscription scope #####
    ```
        az site delete --site-name TestSiteName --subscription 00000000-0000-0000-0000-000000000000
    ```

##### List Sites at service group scope #####
    ```
        az site list --service-group TestSGName
    ```

##### List Sites at resource group scope #####
    ```
        az site list --resource-group TestRGName --subscription 00000000000-0000-0000-0000-000000000000
    ```

##### List Sites at subscription scope #####
    ```
        az site list --subscription 00000000000-0000-0000-0000-000000000000
    ```

##### Show a Site at service group scope #####
    ```
        az site show --site-name TestSiteName --service-group TestSGName
    ```

##### Show a Site at resource group scope #####
    ```
        az site show --site-name TestSiteName --resource-group TestRGName --subscription 00000000-0000-0000-0000-000000000000
    ```

##### Show a Site at subscription scope #####
    ```
        az site show --site-name TestSiteName --subscription 00000000-0000-0000-0000-000000000000
    ```

##### Update a Site at service group scope #####
    ```
        az site update --site-name TestSiteName --service-group TestSGName --description "Test Site" --labels key1="value1" key2="value2" --street-address1="17 TOWNSEND ST" --street-address2="UNIT 2" --city="newyork" --state-or-province="CA" --country="US" --postal-code="94107"
    ```

##### Update a Site at resource group scope #####
    ```
        az site update --site-name TestSiteName --resource-group TestMSRG --subscription 00000000-0000-0000-0000-000000000000 --description "Test Site" --labels key1="value1" key2="value2" --street-address1="17 TOWNSEND ST" --street-address2="UNIT 2" --city="newyork" --state-or-province="CA" --country="US" --postal-code="94107"
    ```

##### Update a Site at subscription scope #####
    ```
        az site update --site-name TestSiteName  --subscription 00000000-0000-0000-0000-000000000000 --description "Test Site" --labels key1="value1" key2="value2" --street-address1="17 TOWNSEND ST" --street-address2="UNIT 2" --city="newyork" --state-or-province="CA" --country="US" --postal-code="94107"
    ```