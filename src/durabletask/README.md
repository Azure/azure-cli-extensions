# Azure CLI Durabletask Extension #
This is an extension to Azure CLI to manage Durabletask resources.

## How to use ##
Install this extension using the following CLI command `az extension add --name durabletask`.

Remove this extension using the following CLI command `az extension remove --name durabletask`.

For more information on how to use this service, run the following CLI commands: 

` az durabletask scheduler -h `
` az durabletask taskhub -h `

You can create a scheduler with the following command:
` az durabletask scheduler create -g "<resource-group-name>" -n "<scheduler-name>"`

List all the schedulers in your resource group:
` az durabletask scheduler list -g <resource-group-name> `

Show the information for a particular scheduler within a resource group:
` az durabletask scheduler show -g <resource-group-name> -n <scheduler-name> `

Delete a scheduler:
` az durabletask scheduler delete -g <resource-group-name> -n <scheduler-name> `

You can create a taskhub with the following command:
` az durabletask taskhub create -g <resource-group-name> -s <scheduler-name> -n <taskhub-name> `

List all taskhubs within a particular scheduler:
` az durabletask taskhub list -g <resource-group-name> -n <scheduler-name> `

Show information on a single taskhub:
` az durabletask taskhub show -g <resource-group-name> -s <scheduler-name> -n <task-hub-name> `

Delete a taskhub:
` az durabletask taskhub delete -g <resource-group-name> -s <scheduler-name> -n <task-hub-name> `