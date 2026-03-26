# Azure CLI NetworkAnalytics Extension #
This is an extension to Azure CLI to manage NetworkAnalytics resources.

## How to use ##
az network-analytics data-product create --name clitest --resource-group test-RG --location southcentralus --publisher Microsoft --product MCC --major-version  2.0.0 --owners xyz@email

az network-analytics data-product list --resource-group test-RG

az network-analytics data-product show --name clitest --resource-group test-RG

az network-analytics data-product add-user-role --data-product-name clitest --resource-group test-RG --data-type-scope " " --principal-id test@microsoft.com --principal-type user --role reader --role-id " " --user-name " "

az network-analytics data-product list-roles-assignment --data-product-name clitest --resource-group test-RG

az network-analytics data-product remove-user-role --data-product-name clitest --resource-group test-RG --data-type-scope " " --principal-id test@microsoft.com --principal-type user --role reader --role-id " " --user-name " " --role-assignment-id " "

az network-analytics data-product delete --name clitest --resource-group test-RG