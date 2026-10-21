# Azure CLI ServiceGroup Extension #
This is an extension to Azure CLI to manage Service Group resources.

Service Groups provide a construct to group multiple resources, resource groups,
subscriptions and other service groups into an organizational hierarchy and
centrally manage access control, policies, alerting and reporting.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name servicegroup
```

### Included Features

#### Create a service group under the tenant root
```
az service-group create --name MyServiceGroup --display-name "My Service Group" \
    --parent resource-id="/providers/Microsoft.Management/serviceGroups/<tenantId>"
```

#### Create a child service group under an existing parent
```
az service-group create --name ChildGroup --display-name "Child Group" \
    --parent resource-id="/providers/Microsoft.Management/serviceGroups/ParentGroup"
```

#### Create a service group with a criticality attribute
```
az service-group create --name CriticalGroup --display-name "Critical Group" \
    --attributes criticality=1 \
    --parent resource-id="/providers/Microsoft.Management/serviceGroups/<tenantId>"
```

#### Show a service group
```
az service-group show --name MyServiceGroup
```

#### Update a service group
```
az service-group update --name MyServiceGroup --display-name "Updated Name" \
    --attributes criticality=2
```

`kind` is create-time only and cannot be changed with `service-group update`.
Update does not support clearing display name, parent, or tags by passing an explicit null.
Omit an argument to retain its current value, or provide a replacement value.

#### Delete a service group
```
az service-group delete --name MyServiceGroup --yes
```
