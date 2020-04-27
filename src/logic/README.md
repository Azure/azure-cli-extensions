# Azure CLI Logic Apps Extension #
This package is for the 'logic app' extension, i.e. 'az logic'. 
More info on what is [Logic](https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-overview).

### How to use ###
Install this extension using the below CLI command
```
az extension add --name logic
```

### Getting Help

To see examples of commands and parameters details got commands or command groups, one should run the command of interest with a -h

Examples:
```
az logic workflow create -h

az logic integration-account -h

az logic worflow update -h
```


##### Creating a Logic App

For creating a logic app, one must provide a logic app definition.
A definition is a JSON description of a logic app workflow. It is recommended that the logic app designer be used to create this definition, as these definitions can be very complex depending on a workflow. The designed tool works with VS Code, Visual Studio, and Azure Portal: https://docs.microsoft.com/en-us/azure/logic-apps/. 

Access Controls: For a great reference on this see: (https://msftplayground.com/2020/02/managing-access-control-for-logic-apps/)
An example of how an access control would look is:

```json
"accessControl": { "triggers": 
	{ "allowedCallerIpAddresses": 
		[{ "addressRange": "10.0.0.0/24" }]}, 
			"actions": { "allowedCallerIpAddresses": 
			[{ "addressRange": "10.0.0.0/24" }]}
	}
```
##### Creating an Integration Account

Integration accounts are a way for Azure Logic Apps to utilize services outside of Azure to integrate into your logic app workflows. See (https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-enterprise-integration-create-integration-account) for more information. 

Integration Service enviroments go hand in hand with a integration account. It is enviroment that connects to your azure vnet for seamless flow of data and logic apps services to on premise enviroments and services. See (https://azure.microsoft.com/en-us/blog/announcing-azure-integration-service-environment-for-logic-apps/) for more information


#### Import an Integration Account

You can import an integration account from a JSON file. Run az workflow integration-account import -h to see the parameters. 

An example JSON for import could look like:

```json
{"properties": {
	   "state": "Enabled"
       },
    "sku": {
    "name": "Standard"
    },
    "location": "centralus"
}
'''