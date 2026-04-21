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

#### Show a service group
```
az service-group show --name MyServiceGroup
```

#### Update a service group
```
az service-group update --name MyServiceGroup --display-name "Updated Name"
```

#### List ancestors of a service group
```
az service-group list-ancestors --name MyServiceGroup
```

#### Delete a service group
```
az service-group delete --name MyServiceGroup --yes
```
