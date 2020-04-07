# Azure CLI blueprint Extension #
This package is for the 'blueprint' extension, i.e. 'az blueprint'. More info on what is [Blueprint](https://docs.microsoft.com/azure/governance/blueprints/overview).

### How to use ###
Install this extension using the below CLI command
```
az extension add --name blueprint
```

Blueprint can be scoped in a subscription or management group, which is a group of subscriptions. You can use management group by specify `--management-group`, or use subscription by specify `--subscription.` If both parameters are omitted, the command will use your default subscription. You can set it by running:
```
az account set --subscription subscription_id
```

Register Blueprint Resource Provider for your susbcription.
```
az provider register -n "Microsoft.Blueprint"
```

### Included Features
#### Blueprint Definition Management:
*Examples:*

##### Import Blueprint Definition and Artifacts Settings

```
az blueprint import \
--name blueprintName \
--input-path "path/to/blueprint/directory"

```

In the input directory, there should be a file named "blueprint.json" with a blueprint definition and parameters for artifacts. There should be a subdirectory named "artifacts" and it should contain files for artifact definitions. Examples can be found [here](https://github.com/Azure/azure-cli-extensions/tree/master/src/blueprint/azext_blueprint/tests/latest/input/import_with_artifacts).

The import command will overwrite defnitions for the blueprint and its artifacts if a blueprint with the same name already exists.

##### Create a Blueprint with Parameters

```
az blueprint create \
    --name blueprintName \
    --description "An example blueprint." \
    --target-scope "subscription" \
    --parameters path/to/blueprint_params.json
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
The paramters are for artifacts which will be added in below commands.

##### Add a Resource Group in the Blueprint
```
az blueprint resource-group add \
    --blueprint-name blueprintName \
    --artifact-name myRgArt
```

##### Add a Role Assignment Artifact
```
az blueprint artifact role create \
    --blueprint-name blueprintName \
    --artifact-name my-role-art \
    --display-name "My Role Name" \
    --resource-group-art myRgArt \
    --role-definition-id "/providers/Microsoft.Authorization/roleDefinitions/00000000-0000-0000-0000-000000000000" \
    --principal-ids "[parameters('MyRoleName_RoleAssignmentName')]"
```
You can use the following command to get the role definition id based on role name:
```
az role definition list --name "Owner" --scope "/" --resource-group "" --query "[0].id"
```

##### Add a Policy Assignment Artifact
```
az blueprint artifact policy create \
    --blueprint-name blueprintName \
    --artifact-name my-policy-art \
    --display-name "My Policy Name" \
    --policy-definition-id "/providers/Microsoft.Authorization/policyDefinitions/00000000-0000-0000-0000-000000000000" \
    --parameters path/to/policy_params.json
```
An example policy_params.json may look like this:
```json
{
    "Members":{
        "value":"[parameters('MyPolicyName_Members')]"
    }
}
```
You can use the following command to get the policy definition id based on policy name:
```
az policy definition show -n policy-name --query "id"
```

##### Add an ARM Template Artifact
```
az blueprint artifact template add \
    --blueprint-name blueprintName \
    --artifact-name my-template-art \
    --display-name "My Template Name" \
    --parameters path/to/params.json \
    --template path/to/template.json
```

##### Publish a Blueprint
```
az blueprint publish \
    --blueprint-name blueprintName \
    --version "1.0" \
    --change-notes "First release"
```

##### Assign a Blueprint to a subscription
```
az blueprint assignment create \
    --name assignmentName \
    --location "westus2" \
    --identity-type "SystemAssigned" \
    --blueprint-version "/subscriptions/{subscriptionId}/providers/Microsoft.Blueprint/blueprints/blueprintName/versions/1.0" \
    --locks-mode "None" \
    --resource-group-value artifact_name=myRgArt name=blueprint-rg location=westus \
    --parameters path/to/assignment_params.json
```
Values need to be assigned for the parameters when assigning a blueprint.

An example assignment_params.json may look like this:
```json
{
    "MyRoleName_RoleAssignmentName":{
        "value":["00000000-0000-0000-0000-000000000000"]
    },
    "MyPolicyName_Members":{
        "value":"jack"
    }
}
```

##### Wait for assignment to finish
```
az blueprint assignment wait \
    --name assignmentName \
    --created
```

##### Delete Blueprint Assignment
```
az blueprint assignment delete \
    --name assignmentName
```
Deleting a blueprint assignment does not delete the resources created in the target subscription.

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.