# Azure CLI Durabletask Extension #
This is an extension to Azure CLI to manage Durabletask resources.

## How to use ##
Install this extension using the following CLI command `az extension add --name durabletask`.

Remove this extension using the following CLI command `az extension remove --name durabletask`.

For more information on how to use this service, run the following CLI commands: 

` az durabletask namespace -h `
` az durabletask taskhub -h `

You can create a namespace with the following command:
` az durabletask namespace create -g "<resource-group-name>" -n "<namespace-name>"`

List all the namespaces in your resource group:
` az durabletask namespace list -g <resource-group-name> `

Show the information for a particular namespace within a resource group:
` az durabletask namespace show -g <resource-group-name> -n <namespace-name> `

Delete a namespace:
` az durabletask namespace delete -g <resource-group-name> -n <namespace-name> `

You can create a taskhub with the following command:
` az durabletask taskhub create -g <resource-group-name> -s <namespace-name> -n <taskhub-name> `

List all taskhubs within a particular namespace:
` az durabletask taskhub list -g <resource-group-name> -n <namespace-name> `

Show information on a single taskhub:
` az durabletask taskhub show -g <resource-group-name> -s <namespace-name> -n <task-hub-name> `

Delete a taskhub:
` az durabletask taskhub delete -g <resource-group-name> -s <namespace-name> -n <task-hub-name> `