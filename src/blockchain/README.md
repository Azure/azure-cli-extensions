Microsoft Azure CLI 'blockchain' Extension
==========================================

This package is for the 'blockchain' extension.
i.e. 'az blockchain'
#### Install:
Install CLI first: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

#### Install blockchain extension. (Pre-request)

`az extension add -n blockchain`

#### Preparation:
Create the resource group if it doesn't exist:

`az group create -n MyResourceGroup -l westus`

#### Usage Examples:
List consortiums for a specif location

`az blockchain consortium list --location southeastasia`

Create a blockchain memeber

`az blockchain member create --location southeastasia --consortium "ContoseConsortium" --consortium-management-account-password "1234abcdEFG1"  --password "1234abcdEFG1" --validator-nodes-sku capacity=2 --protocol "Quorum"  --name "contosemember1" --resource-group "MyResourceGroup" --firewall-rules rule-name=mytest start-ip-address=10.0.0.0 end-ip-address=10.0.1.0`

Show a blockchain memeber

`az blockchain member show --name "contosemember1" --resource-group "MyResourceGroup"`

List all blockchain memebers in a resource group

`az blockchain member list --resource-group "MyResourceGroup"`


List all blockchain memebers in a sub

`az blockchain member list`


List all consortium members in a blockchain memeber

`az blockchain member list-consortium-member --name "contosemember1" --resource-group "MyResourceGroup"`


List api keys of a blockchain memeber

`az blockchain member list-api-keys --name "contosemember1" --resource-group "MyResourceGroup"`


Regen key 1 for a blockchain memeber

`az blockchain member regenerate-api-key --key-name "key1" --name "contosemember1" --resource-group "MyResourceGroup"`


Update a blockchain memeber

`az blockchain member update --consortium-management-account-password "1234abcdEFG12"  --password "1234abcdEFG12" --name "contosemember1" --resource-group "MyResourceGroup" --firewall-rules rule-name=mytest start-ip-address=10.0.0.0 end-ip-address=10.0.1.0`

Create a blockchain transaction node

`az blockchain transaction-node create --member-name "contosemember1" -g MyResourceGroup -l southeastasia --password "1234abcdEFG1" --name txnode2`

Show a blockchain transaction node

`az blockchain transaction-node show --member-name "contosemember1" -g MyResourceGroup  --name txnode2`

List all blockchain transaction node

`az blockchain transaction-node list --member-name "contosemember1" -g MyResourceGroup`

List api keys for a blockchain transaction node

`az blockchain transaction-node list-api-key --member-name "contosemember1" -g MyResourceGroup --name txnode2`

Regen api key 1 for a blockchain transaction node

`az blockchain transaction-node regenerate-api-key --member-name "contosemember1" -g MyResourceGroup --name txnode2 --key-name "key1"`

Update a blockchain transaction node

`az blockchain transaction-node update --member-name "contosemember1" -g MyResourceGroup --password "1234abcdEFG2" --name txnode2`

Delete a blockchain transaction node

`az blockchain transaction-node delete --member-name "contosemember1" -g MyResourceGroup  --name txnode2`

Delete a blockchain memeber

`az blockchain member delete --name "contosemember1" --resource-group "MyResourceGroup"`



