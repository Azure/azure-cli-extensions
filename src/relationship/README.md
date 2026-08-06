# Azure CLI Relationship Extension #
This is an extension to Azure CLI to manage Relationship resources.

Relationships are ARM extension resources that create semantic associations
between a source resource and a target resource. Two relationship types are supported:

- **dependencyOf** — creates dependency links between ARM resources
- **serviceGroupMember** — associates resources with Service Groups

## How to use ##
Install this extension using the below CLI command
```
az extension add --name relationship
```

### Included Features

#### Create a dependencyOf relationship from a resource group to a service group
```
az relationship dependency-of create \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myDependency \
    --target-id "/providers/Microsoft.Management/serviceGroups/mySG"
```

#### Create a dependencyOf relationship from a subscription to a service group
```
az relationship dependency-of create \
    --resource-uri "/subscriptions/{sub}" \
    --name subDep \
    --target-id "/providers/Microsoft.Management/serviceGroups/mySG"
```

#### Show a dependencyOf relationship
```
az relationship dependency-of show \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myDependency
```

#### Delete a dependencyOf relationship
```
az relationship dependency-of delete \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myDependency --yes
```

#### Create a serviceGroupMember relationship
```
az relationship service-group-member create \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myMembership \
    --target-id "/providers/Microsoft.Management/serviceGroups/mySG"
```

#### Show a serviceGroupMember relationship
```
az relationship service-group-member show \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myMembership
```

#### Delete a serviceGroupMember relationship
```
az relationship service-group-member delete \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myMembership --yes
```
