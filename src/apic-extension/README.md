# Azure CLI APICenter Extension

This extension can help create and manage APICenter Resources

### How to use
Install this extension using the below CLI command
```
az extension add --name apic-extension
```

### API Center Extension Info
APICenter documentation: https://learn.microsoft.com/en-us/azure/api-center/

List Service Examples
```
az apic service show --resource-group api-center-test
```
```
az apic service show -g api-center-test
```

Show service Examples
```
az apic service show --resource-group api-center-test --service-name contosoeuap
```
```
az apic service show -g api-center-test -s contosoeuap
```

Delete Service Examples
```
az apic service delete --resource-group api-center-test --service-name contosoeuap
```
```
az apic service delete --resource-group arpi-test-rg1 -s apictestcli3
```

Show Workspace Example
```
Az apic workspace show -g api-center-test -s contosoeuap --name devdiv
```

Create API Examples
```
az apic api create -g api-center-test -s contosoeuap --name echo-api --title "Echo API" --kind "rest"
```
```
az apic api create --resource-group api-center-test --service-name contosoeuap --api-name echo-api2 --description "CLI Test" --kind rest --title "Echo API"
```

Update API Examples
```
az apic api update -g api-center-test -s contosoeuap --name echo-api --summary "Basic REST API service" -w default
```
```
az apic api update --resource-group api-center-test -s contosoeuap --name echo-api --summary "Basic REST API service" --workspace-name default
```

LIST Api Example
```
az apic api list --resource-group api-center-test --service-name contosoeuap
```
```
az apic api list -g api-center-test -s contosoeuap
```

SHOW Api Examples
```
az apic api show -g api-center-test -s contosoeuap --name echo-api
```
```
az apic api show --resource-group api-center-test --service-name contosoeuap -w default --api echo-api
```

Delete API Examples
```
az apic api delete -g api-center-test -s contosoeuap --name echo-api 
```
```
az apic api delete --resource-group contoso-resources --service-name contosoeuap --name echo-api
```

CREATE Api Version Examples
```
az apic api version create -g api-center-test -s contosoeuap --api-name echo-api --name 2023-01-01 --title "2023-01-01"
```
```
az apic api version create --resource-group api-center-test --service-name contosoeuap --api-name echo-api --name 2023-01-01 --title "2023-01-01"
```

UPDATE Api Version Examples
```
Az apic api version update -g api-center-test -s contosoeuap --api-name echo-api --name 2023-01-01 --title "2023-01-01" -w default
```
```
az apic api version update --resource-group api-center-test --service-name contosoeuap --api-name echo-api --name 2023-01-01 --title "2023-01-01" --workspace-name default
```

LIST Api Version Examples
```
az apic api version list -g api-center-test -s contosoeuap --api-name echo-api
```
```
az apic api version list --resource-group api-center-test --service-name contosoeuap --api-name echo-api
```

SHOW Api Version Example
```
az apic api version show -g api-center-test -s contosoeuap --api-name echo-api --name 2023-01-01
```
```
az apic api version show --resource-group api-center-test --service-name contosoeuap --api-name echo-api --name 2023-01-01
```

DELETE Api Version Example
```
az apic api version delete -g api-center-test -s contosoeuap --api-name echo-api --name 2023-01-01 
```
```
az apic api version delete --resource-group api-center-test --service-name contosoeuap --api-name echo-api --name 2023-01-01
```

CREATE API Definition Example
```
az apic api definition create -g api-center-test -s contosoeuap --api-name echo-api --version 2023-01-01 --name "openapi" --title "OpenAPI"
```

UPDATE API Definition Example
```
az apic api definition update -g api-center-test -s contosoeuap --api-name echo-api --version 2023-01-01 --name "openapi" --title "OpenAPI" -w default
```

SHOW API Definition Example
```
az apic api definition show -g api-center-test -s contosoeuap --api-name echo-api --version 2023-01-01 --name "openapi"
```

LIST API Definition Example
```
az apic api definition list -g api-center-test -s contosoeuap --api-name echo-api --version 2023-01-01 
```

DELETE API Definition Example
```
az apic api definition delete -g api-center-test -s contosoeuap --api-name echo-api --version 2023-01-01 --name "openapi" 
```

IMPORT Specification Examples
Import Specification inline option
```
az apic api definition import-specification -g api-center-test -s contosoeuap --api-name echo-api --version-name 2023-01-01 --definition-name openapi--format "inline" --value '{"openapi":"3.0.1","info":{"title":"httpbin.org","description":"API Management facade for a very handy and free online HTTP tool.","version":"1.0"}}' --specification '{"name":"openapi","version":"3.0.0"}' 
```

Import Specification Inline option where spec is provided by sending a file
```
az apic api definition import-specification -g api-center-test -s contosoeuap --api-name echo-api --version-name 2023-01-01 --definition-name openapi --format inline --specification '{"name":"openapi","version":"3.0.0"}' --file-name C:\Users\arpishah\examples\cli-examples\spec-examples\cat-facts-api.json 
```

Import Specification Link option where spec is provided via a link
```
az apic api definition import-specification -g api-center-test -s contosoeuap - --api-name echo-api --version-name 2023-01-01 --definition-name openapi --format "link" --value https://alzaslonaztest.blob.core.windows.net/arpitestblobs/cat-facts-api.json --specification '{"name":"openapi","version":"3.0.0"}'
```

Export Specification Examples
Export Spec to a file
```
az apic api definition export-specification -g api-center-test -s contosoeuap --api-name echo-api-10 --version-name 2023-11-08 --definition-name arpitest4 --file-name C:\Users\arpishah\examples\cli-examples\exported-results\exported-spec-inline.json
```

CREATE Api Deployment

```
az apic api deployment create -g api-center-test -s contosoeuap --name production --title "Production deployment" --description "Public cloud production deployment." --api echo-api --server C:/Users/arpishah/examples/cli-examples/payload-examples/deplcreate.json --environment-id "/workspaces/default/environments/production" --definition-id "/workspaces/default/apis/echo-api/versions/2023-01-01/definitions/openapi"
where examples/deplcreate.json contains  
{"runtime-uri": ["https://api.contoso.com"]} 
```

UPDATE Api Deployment
```
az apic api deployment update -g api-center-test -s contosoeuap --name production --title "Production deployment 10" --api echo-api –w default
```

LIST Api Deployment
```
az apic api deployment list -g api-center-test -s contosoeuap --api-name echo-api
```

SHOW Api Deployment
```
az apic api deployment show -g api-center-test -s contosoeuap --name production --api-name echo-api
```

DELETE Api Deployment
```
Az apic api deployment delete -g api-center-test -s contosoeuap --name production --api-name echo-api
```

CREATE Environment
```
az apic environment create -g api-center-test -s contosoeuap --name public-3 --title "Public cloud" --kind "development" --server "C:\Users\arpishah\examples\cli-examples\payload-examples\envcreate1.json"
Where envcreate1.json contains 
{ 
    "type": "Azure API Management", 
    "managementPortalUri": [ 
        "management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-resource-group/providers/Microsoft.ApiManagement/service/my-api-management-service" 
    ] 
} 
```

UPDATE Environment
```
az apic environment update -g api-center-test -s contosoeuap --name public --title "Public cloud" -w default
```

LIST Environment
```
az apic environment list -g api-center-test -s contosoeuap 
```

SHOW Environment
```
az apic environment show -g api-center-test -s contosoeuap --name public 
```

DELETE Environment
```
az apic environment delete -g api-center-test -s contosoeuap --name public 
```

CREATE Metadata Schema
```
az apic metadata-schema create --resource-group api-center-test --service-name contosoeuap --name "test1" --file-name "C:\Users\arpishah\examples\cli-examples\payload-examples\schemacreate.json" 
Where schemacreate.json contains metadata schema 
{ 
    "type": "string", 
    "title": "First name", 
    "pattern": "^[a-zA-Z0-9 ]+$" 
} 
```

UPDATE Metadata Schema
```
az apic metadata-schema update --resource-group api-center-test --service-name contosoeuap --name "test1" --file-name "C:\Users\arpishah\examples\cli-examples\payload-examples\schemaupdate.json" 
Where schemaupdate.json contains metadata schema 
{ 
    "type": "string", 
    "title": "Last name", 
    "pattern": "^[a-zA-Z0-9 ]+$" 
}
```

LIST Metadata Schema
```
az apic metadata-schema list -g api-center-test -s contosoeuap
```

SHOW Metadata Schema
```
az apic metadata-schema show --resource-group api-center-test --service-name contosoeuap --name "test1"
```

DELETE Metadata Schema 
```
az apic metadata-schema delete --resource-group api-center-test --service-name contosoeuap --name "test1"
```

EXPORT Metadata Schema
EXPORT Metadata Schema assigned to an API
```
az apic metadata-schema export-metadata-schema -g api-center-test -s contosoeuap --assigned-to api --file-name C:\Users\arpishah\examples\cli-examples\exported-results\exported-schema-3.json
```

EXPORT Metadata Schema assigned to a Deployment
```
az apic metadata-schema export-metadata-schema -g api-center-test -s contosoeuap --assigned-to deployment --file-name C:\Users\arpishah\examples\cli-examples\exported-results\exported-schema-5.json
```

EXPORT Metadata Schema assigned to an Environment
```
az apic metadata-schema export-metadata-schema -g api-center-test -s contosoeuap --assigned-to environment --file-name C:\Users\arpishah\examples\cli-examples\exported-results\exported-schema-6.json
```

Register API or Quick Add
```
az apic api register -g api-center-test -s contosoeuap --api-location "C:/Users/arpishah/examples/cli-examples/spec-examples/openai.json" --environment-name public
```