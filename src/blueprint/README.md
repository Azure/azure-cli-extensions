# Azure CLI blueprint Extension #
This package is for the 'blueprint' extension, i.e. 'az blueprint'. More info on what is [Blueprint](https://docs.microsoft.com/azure/governance/blueprints/overview).

### How to use ###
Install this extension using the below CLI command
```
az extension add --name blueprint
```

### Included Features
#### Blueprint Definition Management:
*Examples:*

##### Create an Empty Blueprint

```
az blueprint create \
    --scope "/subscriptions/{subscriptionId}" \
    --name blueprintName \
    --description "An example blueprint." \
    --target-scope "subscription"
```

##### Add a Resource Group in the Blueprint
```
az blueprint resource-group create \
    --scope "/subscriptions/{subscriptionId}" \
    --blueprint-name blueprintName \
    --artifact-name my-rg-art
```

##### Add a Role Assignment Artifact
```
az blueprint artifact role create \
    --scope "/subscriptions/{subscriptionId}" \
    --blueprint-name blueprintName \
    --artifact-name my-role-art \
    --display-name "My Role Name" \
    --resource-group-art my-rg-art \
    --role-definition-id "/providers/Microsoft.Authorization/roleDefinitions/00000000-0000-0000-0000-000000000000" \
    --principal-ids "[parameters('MyRoleName_RoleAssignmentName')]"
```

##### Add a Policy Assignment Artifact
```
az blueprint artifact policy create \
    --scope "/subscriptions/{subscriptionId}" \
    --blueprint-name blueprintName \
    --artifact-name my-policy-art \
    --display-name "My Policy Name" \
    --policy-definition-id "/providers/Microsoft.Authorization/policySetDefinitions/00000000-0000-0000-0000-000000000000" \
    --parameters @/path/to/policy_params.json
```
An example policy_params.json may look like this:
```json
{
    "Members":{
        "value":"[parameters('MyPolicyName_Members')]"
    }
}
```

##### Update Parameter in Blueprint
```
az blueprint update \
    --scope "/subscriptions/{subscriptionId}" \
    --name blueprintName \
    --parameters @/path/to/blueprint_params.json
```
An example blueprint_params.json may look like this:
```json
{
    "MyRoleName_RoleAssignmentName": {
        "type": "array",
        "displayName": "[User group or application name] ([User group or application name] : Reader)",
        "strongType": "PrincipalId"
    },
    "MyPolicyName_Members": {
      "type": "string",
      "displayName": "Members",
      "allowedValues": []
    }
}
```

##### Publish a Blueprint
```
az blueprint published create \
    --scope "/subscriptions/{subscriptionId}" \
    --blueprint-name blueprintName \
    --version "1.0" \
    --change-notes "First release"
```

##### Assign a Blueprint to a subscription
```
az blueprint assignment create \
    --scope "/subscriptions/{subscriptionId}" \
    --assignment-name assignmentName \
    --location "westus2" \
    --identity-type "SystemAssigned" \
    --blueprint-id "/subscriptions/{subscriptionId}/providers/Microsoft.Blueprint/blueprints/blueprintName/versions/1.0" \
    --locks-mode "None" \
    --resource-groups @/path/to/resource_group_params.json \
    --parameters @/path/to/assignment_params.json
```
An example resource_group_params.json may look like this:
```json
{
    "my-rg-art":{
        "name":"blueprint-rg",
        "location":"eastasia"
    }
}
```

An example assignment_params.json may look like this:
```json
{
    "MyRoleName_RoleAssignmentName":{
        "value":["31e600e0-d7ce-4e98-a927-19bb30042e44"]
    },
    "MyPolicyName_Members":{
        "value":"jack"
    }
}
```
##### Wait for assignment to finish
```
az blueprint assignment wait '
    --scope "/subscriptions/{subscriptionId}" \
    --assignment-name assignmentName \
    --custom "provisioningState=='succeeded'" \
    --created
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.