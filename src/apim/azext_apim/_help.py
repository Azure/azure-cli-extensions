# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['apim api'] = """
    type: group
    short-summary: Commands to manage Api.
"""

helps['apim api create'] = """
    type: command
    short-summary: create api.
    examples:
      - name: ApiManagementCreateApiUsingOai3Import
        text: |-
               az apim api create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "petstore" --path "petstore" --value "https://raw.githubusercontent.com/OAI/OpenAPI-Specif
               ication/master/examples/v3.0/petstore.yaml" --format "openapi-link"
      - name: ApiManagementCreateApiUsingSwaggerImport
        text: |-
               az apim api create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "petstore" --path "petstore" --value "http://petstore.swagger.io/v2/swagger.json" \\
               --format "swagger-link-json"
      - name: ApiManagementCreateApiUsingWadlImport
        text: |-
               az apim api create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "petstore" --path "collector" --value "https://developer.cisco.com/media/wae-release-6-2-a
               pi-reference/wae-collector-rest-api/application.wadl" --format "wadl-link-json"
      - name: ApiManagementCreateSoapToRestApiUsingWsdlImport
        text: |-
               az apim api create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "soapApi" --path "currency" --value \\
               "http://www.webservicex.net/CurrencyConvertor.asmx?WSDL" --format "wsdl-link"
      - name: ApiManagementCreateSoapPassThroughApiUsingWsdlImport
        text: |-
               az apim api create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "soapApi" --path "currency" --value \\
               "http://www.webservicex.net/CurrencyConvertor.asmx?WSDL" --format "wsdl-link" --api-type \\
               "soap"
      - name: ApiManagementCreateApi
        text: |-
               az apim api create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "tempgroup" --description "apidescription5200" --display-name "apiname1463" --service-url \\
               "http://newechoapi.cloudapp.net/api" --path "newapiPath"
      - name: ApiManagementCreateApiRevisionFromExistingApi
        text: |-
               az apim api create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "echo-api;rev=3" --api-revision-description "Creating a Revision of an existing API" \\
               --source-api-id "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/
               providers/Microsoft.ApiManagement/service/{{ service_name }}/apis/{{ api_name }}" \\
               --service-url "http://echoapi.cloudapp.net/apiv3" --path "echo"
      - name: ApiManagementCreateApiNewVersionUsingExistingApi
        text: |-
               az apim api create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "echoapiv3" --description \\
               "Create Echo API into a new Version using Existing Version Set and Copy all Operations." \\
               --api-version "v4" --is-current true --api-version-set-id "/subscriptions/{{ subscription_
               id }}/resourceGroups/{{ resource_group }}/providers/Microsoft.ApiManagement/service/{{ ser
               vice_name }}/apiVersionSets/{{ api_version_set_name }}" --subscription-required true \\
               --source-api-id "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/
               providers/Microsoft.ApiManagement/service/{{ service_name }}/apis/{{ api_name }}" \\
               --display-name "Echo API2" --service-url "http://echoapi.cloudapp.net/api" --path "echo2"
      - name: ApiManagementCreateApiClone
        text: |-
               az apim api create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "echo-api2" --description "Copy of Existing Echo Api including Operations." --is-current \\
               true --subscription-required true --source-api-id "/subscriptions/{{ subscription_id }}/re
               sourceGroups/{{ resource_group }}/providers/Microsoft.ApiManagement/service/{{ service_nam
               e }}/apis/{{ api_name }}" --display-name "Echo API2" --service-url \\
               "http://echoapi.cloudapp.net/api" --path "echo2"
      - name: ApiManagementCreateApiWithOpenIdConnect
        text: |-
               az apim api create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "tempgroup" --description "This is a sample server Petstore server.  You can find out more
                about Swagger at [http://swagger.io](http://swagger.io) or on [irc.freenode.net, #swagger
               ](http://swagger.io/irc/).  For this sample, you can use the api key `special-key` to test
                the authorization filters." --display-name "Swagger Petstore" --service-url \\
               "http://petstore.swagger.io/v2" --path "petstore"
"""

helps['apim api update'] = """
    type: command
    short-summary: update api.
    examples:
      - name: ApiManagementUpdateApi
        text: |-
               az apim api update --resource-group "rg1" --service-name "apimService1" --api-id \\
               "echo-api" --display-name "Echo API New" --service-url "http://echoapi.cloudapp.net/api2" \\
               --path "newecho"
"""

helps['apim api delete'] = """
    type: command
    short-summary: delete api.
    examples:
      - name: ApiManagementDeleteApi
        text: |-
               az apim api delete --resource-group "rg1" --service-name "apimService1" --api-id \\
               "echo-api"
"""

helps['apim api list'] = """
    type: command
    short-summary: list api.
"""

helps['apim api show'] = """
    type: command
    short-summary: show api.
"""

helps['apim api release'] = """
    type: group
    short-summary: Commands to manage ApiRelease.
"""

helps['apim api release create'] = """
    type: command
    short-summary: create api release.
    examples:
      - name: ApiManagementCreateApiRelease
        text: |-
               az apim api release create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "a1" --release-id "testrev" --notes "yahooagain"
"""

helps['apim api release update'] = """
    type: command
    short-summary: update api release.
    examples:
      - name: ApiManagementUpdateApiRelease
        text: |-
               az apim api release update --resource-group "rg1" --service-name "apimService1" --api-id \\
               "a1" --release-id "testrev" --notes "yahooagain"
"""

helps['apim api release delete'] = """
    type: command
    short-summary: delete api release.
    examples:
      - name: ApiManagementDeleteApiRelease
        text: |-
               az apim api release delete --resource-group "rg1" --service-name "apimService1" --api-id \\
               "5a5fcc09124a7fa9b89f2f1d" --release-id "testrev"
"""

helps['apim api release list'] = """
    type: command
    short-summary: list api release.
"""

helps['apim api release show'] = """
    type: command
    short-summary: show api release.
"""

helps['apim api operation'] = """
    type: group
    short-summary: Commands to manage ApiOperation.
"""

helps['apim api operation create'] = """
    type: command
    short-summary: create api operation.
    examples:
      - name: ApiManagementCreateApiOperation
        text: |-
               az apim api operation create --resource-group "rg1" --service-name "apimService1" \\
               --api-id "PetStoreTemplate2" --operation-id "newoperations" --description \\
               "This can only be done by the logged in user." --display-name "createUser2" --method \\
               "POST" --url-template "/user1"
"""

helps['apim api operation update'] = """
    type: command
    short-summary: update api operation.
    examples:
      - name: ApiManagementUpdateApiOperation
        text: |-
               az apim api operation update --resource-group "rg1" --service-name "apimService1" \\
               --api-id "echo-api" --operation-id "operationId" --display-name "Retrieve resource" \\
               --method "GET" --url-template "/resource"
"""

helps['apim api operation delete'] = """
    type: command
    short-summary: delete api operation.
    examples:
      - name: ApiManagementDeleteApiOperation
        text: |-
               az apim api operation delete --resource-group "rg1" --service-name "apimService1" \\
               --api-id "57d2ef278aa04f0888cba3f3" --operation-id "57d2ef278aa04f0ad01d6cdc"
"""

helps['apim api operation list'] = """
    type: command
    short-summary: list api operation.
"""

helps['apim api operation show'] = """
    type: command
    short-summary: show api operation.
"""

helps['apim api operation policy'] = """
    type: group
    short-summary: Commands to manage ApiOperationPolicy.
"""

helps['apim api operation policy create'] = """
    type: command
    short-summary: create api operation policy.
    examples:
      - name: ApiManagementCreateApiOperationPolicy
        text: |-
               az apim api operation policy create --resource-group "rg1" --service-name "apimService1" \\
               --api-id "5600b57e7e8880006a040001" --operation-id "5600b57e7e8880006a080001" --policy-id \\
               "policy" --value "<policies> <inbound /> <backend>    <forward-request />  </backend>  <ou
               tbound /></policies>" --format "xml"
"""

helps['apim api operation policy update'] = """
    type: command
    short-summary: update api operation policy.
"""

helps['apim api operation policy delete'] = """
    type: command
    short-summary: delete api operation policy.
    examples:
      - name: ApiManagementDeleteApiOperationPolicy
        text: |-
               az apim api operation policy delete --resource-group "rg1" --service-name "apimService1" \\
               --api-id "testapi" --operation-id "testoperation" --policy-id "policy"
"""

helps['apim api operation policy list'] = """
    type: command
    short-summary: list api operation policy.
"""

helps['apim api operation policy show'] = """
    type: command
    short-summary: show api operation policy.
"""

helps['apim tag'] = """
    type: group
    short-summary: Commands to manage Tag.
"""

helps['apim tag create'] = """
    type: command
    short-summary: create tag.
    examples:
      - name: ApiManagementCreateTag
        text: |-
               az apim tag create --resource-group "rg1" --service-name "apimService1" --tag-id "tagId1" \\
               --display-name "tag1"
"""

helps['apim tag update'] = """
    type: command
    short-summary: update tag.
    examples:
      - name: ApiManagementUpdateTag
        text: |-
               az apim tag update --resource-group "rg1" --service-name "apimService1" --tag-id \\
               "temptag" --display-name "temp tag"
"""

helps['apim tag delete'] = """
    type: command
    short-summary: delete tag.
    examples:
      - name: ApiManagementDeleteTag
        text: |-
               az apim tag delete --resource-group "rg1" --service-name "apimService1" --tag-id "tagId1"
"""

helps['apim tag list'] = """
    type: command
    short-summary: list tag.
"""

helps['apim tag show'] = """
    type: command
    short-summary: show tag.
"""

helps['apim api policy'] = """
    type: group
    short-summary: Commands to manage ApiPolicy.
"""

helps['apim api policy create'] = """
    type: command
    short-summary: create api policy.
    examples:
      - name: ApiManagementCreateApiPolicy
        text: |-
               az apim api policy create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "5600b57e7e8880006a040001" --policy-id "policy" --value "<policies> <inbound /> <backend> 
                  <forward-request />  </backend>  <outbound /></policies>" --format "xml"
      - name: ApiManagementCreateApiPolicyNonXmlEncoded
        text: |-
               az apim api policy create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "5600b57e7e8880006a040001" --policy-id "policy" --value "<policies>\\r\\n     <inbound>\\r\\n 
                   <base />\\r\\n  <set-header name=\\"newvalue\\" exists-action=\\"override\\">\\r\\n   <value>\\
               "@(context.Request.Headers.FirstOrDefault(h => h.Ke==\\"Via\\"))\\" </value>\\r\\n    </set-hea
               der>\\r\\n  </inbound>\\r\\n      </policies>" --format "rawxml"
"""

helps['apim api policy update'] = """
    type: command
    short-summary: update api policy.
"""

helps['apim api policy delete'] = """
    type: command
    short-summary: delete api policy.
    examples:
      - name: ApiManagementDeleteApiPolicy
        text: |-
               az apim api policy delete --resource-group "rg1" --service-name "apimService1" --api-id \\
               "loggerId" --policy-id "policy"
"""

helps['apim api policy list'] = """
    type: command
    short-summary: list api policy.
"""

helps['apim api policy show'] = """
    type: command
    short-summary: show api policy.
"""

helps['apim api schema'] = """
    type: group
    short-summary: Commands to manage ApiSchema.
"""

helps['apim api schema create'] = """
    type: command
    short-summary: create api schema.
    examples:
      - name: ApiManagementCreateApiSchema
        text: |-
               az apim api schema create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "59d6bb8f1f7fab13dc67ec9b" --schema-id "ec12520d-9d48-4e7b-8f39-698ca2ac63f1" \\
               --content-type "application/vnd.ms-azure-apim.xsd+xml"
"""

helps['apim api schema update'] = """
    type: command
    short-summary: update api schema.
"""

helps['apim api schema delete'] = """
    type: command
    short-summary: delete api schema.
    examples:
      - name: ApiManagementDeleteApiSchema
        text: |-
               az apim api schema delete --resource-group "rg1" --service-name "apimService1" --api-id \\
               "59d5b28d1f7fab116c282650" --schema-id "59d5b28e1f7fab116402044e"
"""

helps['apim api schema list'] = """
    type: command
    short-summary: list api schema.
"""

helps['apim api schema show'] = """
    type: command
    short-summary: show api schema.
"""

helps['apim api diagnostic'] = """
    type: group
    short-summary: Commands to manage ApiDiagnostic.
"""

helps['apim api diagnostic create'] = """
    type: command
    short-summary: create api diagnostic.
    examples:
      - name: ApiManagementCreateApiDiagnostic
        text: |-
               az apim api diagnostic create --resource-group "rg1" --service-name "apimService1" \\
               --api-id "57d1f7558aa04f15146d9d8a" --diagnostic-id "applicationinsights" --always-log \\
               "allErrors" --logger-id "/loggers/applicationinsights"
"""

helps['apim api diagnostic update'] = """
    type: command
    short-summary: update api diagnostic.
    examples:
      - name: ApiManagementUpdateApiDiagnostic
        text: |-
               az apim api diagnostic update --resource-group "rg1" --service-name "apimService1" \\
               --api-id "57d1f7558aa04f15146d9d8a" --diagnostic-id "applicationinsights" --always-log \\
               "allErrors" --logger-id "/loggers/applicationinsights"
"""

helps['apim api diagnostic delete'] = """
    type: command
    short-summary: delete api diagnostic.
    examples:
      - name: ApiManagementDeleteApiDiagnostic
        text: |-
               az apim api diagnostic delete --resource-group "rg1" --service-name "apimService1" \\
               --api-id "57d1f7558aa04f15146d9d8a" --diagnostic-id "applicationinsights"
"""

helps['apim api diagnostic list'] = """
    type: command
    short-summary: list api diagnostic.
"""

helps['apim api diagnostic show'] = """
    type: command
    short-summary: show api diagnostic.
"""

helps['apim api issue'] = """
    type: group
    short-summary: Commands to manage ApiIssue.
"""

helps['apim api issue create'] = """
    type: command
    short-summary: create api issue.
    examples:
      - name: ApiManagementCreateApiIssue
        text: |-
               az apim api issue create --resource-group "rg1" --service-name "apimService1" --api-id \\
               "57d1f7558aa04f15146d9d8a" --issue-id "57d2ef278aa04f0ad01d6cdc" --created-date \\
               "2018-02-01T22:21:20.467Z" --state "open" --title "New API issue" --description \\
               "New API issue description" --user-id "/subscriptions/{{ subscription_id }}/resourceGroups
               /{{ resource_group }}/providers/Microsoft.ApiManagement/service/{{ service_name }}/users/{
               { user_name }}"
"""

helps['apim api issue update'] = """
    type: command
    short-summary: update api issue.
    examples:
      - name: ApiManagementUpdateApiIssue
        text: |-
               az apim api issue update --resource-group "rg1" --service-name "apimService1" --api-id \\
               "57d1f7558aa04f15146d9d8a" --issue-id "57d2ef278aa04f0ad01d6cdc" --state "closed"
"""

helps['apim api issue delete'] = """
    type: command
    short-summary: delete api issue.
    examples:
      - name: ApiManagementDeleteApiIssue
        text: |-
               az apim api issue delete --resource-group "rg1" --service-name "apimService1" --api-id \\
               "57d1f7558aa04f15146d9d8a" --issue-id "57d2ef278aa04f0ad01d6cdc"
"""

helps['apim api issue list'] = """
    type: command
    short-summary: list api issue.
"""

helps['apim api issue show'] = """
    type: command
    short-summary: show api issue.
"""

helps['apim api issue comment'] = """
    type: group
    short-summary: Commands to manage ApiIssueComment.
"""

helps['apim api issue comment create'] = """
    type: command
    short-summary: create api issue comment.
    examples:
      - name: ApiManagementCreateApiIssueComment
        text: |-
               az apim api issue comment create --resource-group "rg1" --service-name "apimService1" \\
               --api-id "57d1f7558aa04f15146d9d8a" --issue-id "57d2ef278aa04f0ad01d6cdc" --comment-id \\
               "599e29ab193c3c0bd0b3e2fb" --text "Issue comment." --created-date \\
               "2018-02-01T22:21:20.467Z" --user-id "/subscriptions/{{ subscription_id }}/resourceGroups/
               {{ resource_group }}/providers/Microsoft.ApiManagement/service/{{ service_name }}/users/{{
                user_name }}"
"""

helps['apim api issue comment update'] = """
    type: command
    short-summary: update api issue comment.
"""

helps['apim api issue comment delete'] = """
    type: command
    short-summary: delete api issue comment.
    examples:
      - name: ApiManagementDeleteApiIssueComment
        text: |-
               az apim api issue comment delete --resource-group "rg1" --service-name "apimService1" \\
               --api-id "57d1f7558aa04f15146d9d8a" --issue-id "57d2ef278aa04f0ad01d6cdc" --comment-id \\
               "599e29ab193c3c0bd0b3e2fb"
"""

helps['apim api issue comment list'] = """
    type: command
    short-summary: list api issue comment.
"""

helps['apim api issue comment show'] = """
    type: command
    short-summary: show api issue comment.
"""

helps['apim api issue attachment'] = """
    type: group
    short-summary: Commands to manage ApiIssueAttachment.
"""

helps['apim api issue attachment create'] = """
    type: command
    short-summary: create api issue attachment.
    examples:
      - name: ApiManagementCreateApiIssueAttachment
        text: |-
               az apim api issue attachment create --resource-group "rg1" --service-name "apimService1" \\
               --api-id "57d1f7558aa04f15146d9d8a" --issue-id "57d2ef278aa04f0ad01d6cdc" --attachment-id \\
               "57d2ef278aa04f0888cba3f3" --title "Issue attachment." --content-format "image/jpeg" \\
               --content "IEJhc2U2NA=="
"""

helps['apim api issue attachment update'] = """
    type: command
    short-summary: update api issue attachment.
"""

helps['apim api issue attachment delete'] = """
    type: command
    short-summary: delete api issue attachment.
    examples:
      - name: ApiManagementDeleteApiIssueAttachment
        text: |-
               az apim api issue attachment delete --resource-group "rg1" --service-name "apimService1" \\
               --api-id "57d1f7558aa04f15146d9d8a" --issue-id "57d2ef278aa04f0ad01d6cdc" --attachment-id \\
               "57d2ef278aa04f0888cba3f3"
"""

helps['apim api issue attachment list'] = """
    type: command
    short-summary: list api issue attachment.
"""

helps['apim api issue attachment show'] = """
    type: command
    short-summary: show api issue attachment.
"""

helps['apim api tagdescription'] = """
    type: group
    short-summary: Commands to manage ApiTagDescription.
"""

helps['apim api tagdescription create'] = """
    type: command
    short-summary: create api tag description.
    examples:
      - name: ApiManagementCreateApiTagDescription
        text: |-
               az apim api tagdescription create --resource-group "rg1" --service-name "apimService1" \\
               --api-id "5931a75ae4bbd512a88c680b" --tag-id "tagId1" --description "Some description that
                will be displayed for operation's tag if the tag is assigned to operation of the API" \\
               --external-docs-url "http://some.url/additionaldoc" --external-docs-description \\
               "Description of the external docs resource"
"""

helps['apim api tagdescription update'] = """
    type: command
    short-summary: update api tag description.
"""

helps['apim api tagdescription delete'] = """
    type: command
    short-summary: delete api tag description.
    examples:
      - name: ApiManagementDeleteApiTagDescription
        text: |-
               az apim api tagdescription delete --resource-group "rg1" --service-name "apimService1" \\
               --api-id "59d5b28d1f7fab116c282650" --tag-id "59d5b28e1f7fab116402044e"
"""

helps['apim api tagdescription list'] = """
    type: command
    short-summary: list api tag description.
"""

helps['apim api tagdescription show'] = """
    type: command
    short-summary: show api tag description.
"""

helps['apim apiversionset'] = """
    type: group
    short-summary: Commands to manage ApiVersionSet.
"""

helps['apim apiversionset create'] = """
    type: command
    short-summary: create api version set.
    examples:
      - name: ApiManagementCreateApiVersionSet
        text: |-
               az apim apiversionset create --resource-group "rg1" --service-name "apimService1" \\
               --version-set-id "api1" --description "Version configuration" --display-name "api set 1" \\
               --versioning-scheme "Segment"
"""

helps['apim apiversionset update'] = """
    type: command
    short-summary: update api version set.
    examples:
      - name: ApiManagementUpdateApiVersionSet
        text: |-
               az apim apiversionset update --resource-group "rg1" --service-name "apimService1" \\
               --version-set-id "api1" --description "Version configuration" --display-name "api set 1" \\
               --versioning-scheme "Segment"
"""

helps['apim apiversionset delete'] = """
    type: command
    short-summary: delete api version set.
    examples:
      - name: ApiManagementDeleteApiVersionSet
        text: |-
               az apim apiversionset delete --resource-group "rg1" --service-name "apimService1" \\
               --version-set-id "a1"
"""

helps['apim apiversionset list'] = """
    type: command
    short-summary: list api version set.
"""

helps['apim apiversionset show'] = """
    type: command
    short-summary: show api version set.
"""

helps['apim authorizationserver'] = """
    type: group
    short-summary: Commands to manage AuthorizationServer.
"""

helps['apim authorizationserver create'] = """
    type: command
    short-summary: create authorization server.
    examples:
      - name: ApiManagementCreateAuthorizationServer
        text: |-
               az apim authorizationserver create --resource-group "rg1" --service-name "apimService1" \\
               --authsid "newauthServer" --description "test server" --token-endpoint \\
               "https://www.contoso.com/oauth2/token" --support-state true --default-scope "read write" \\
               --client-secret "2" --resource-owner-username "un" --resource-owner-password "pwd" \\
               --display-name "test2" --client-registration-endpoint "https://www.contoso.com/apps" \\
               --authorization-endpoint "https://www.contoso.com/oauth2/auth" --client-id "1"
"""

helps['apim authorizationserver update'] = """
    type: command
    short-summary: update authorization server.
    examples:
      - name: ApiManagementUpdateAuthorizationServer
        text: |-
               az apim authorizationserver update --resource-group "rg1" --service-name "apimService1" \\
               --authsid "newauthServer" --client-secret "updated" --client-id "update"
"""

helps['apim authorizationserver delete'] = """
    type: command
    short-summary: delete authorization server.
    examples:
      - name: ApiManagementDeleteAuthorizationServer
        text: |-
               az apim authorizationserver delete --resource-group "rg1" --service-name "apimService1" \\
               --authsid "newauthServer2"
"""

helps['apim authorizationserver list'] = """
    type: command
    short-summary: list authorization server.
"""

helps['apim authorizationserver show'] = """
    type: command
    short-summary: show authorization server.
"""

helps['apim backend'] = """
    type: group
    short-summary: Commands to manage Backend.
"""

helps['apim backend create'] = """
    type: command
    short-summary: create backend.
    examples:
      - name: ApiManagementCreateBackendServiceFabric
        text: |-
               az apim backend create --resource-group "rg1" --service-name "apimService1" --backend-id \\
               "sfbackend" --description "Service Fabric Test App 1" --url \\
               "fabric:/mytestapp/mytestservice" --protocol "http"
      - name: ApiManagementCreateBackendProxyBackend
        text: |-
               az apim backend create --resource-group "rg1" --service-name "apimService1" --backend-id \\
               "proxybackend" --description "description5308" --url "https://backendname2644/" \\
               --protocol "http"
"""

helps['apim backend update'] = """
    type: command
    short-summary: update backend.
    examples:
      - name: ApiManagementUpdateBackend
        text: |-
               az apim backend update --resource-group "rg1" --service-name "apimService1" --backend-id \\
               "proxybackend" --description "description5308"
"""

helps['apim backend delete'] = """
    type: command
    short-summary: delete backend.
    examples:
      - name: ApiManagementDeleteBackend
        text: |-
               az apim backend delete --resource-group "rg1" --service-name "apimService1" --backend-id \\
               "sfbackend"
"""

helps['apim backend list'] = """
    type: command
    short-summary: list backend.
"""

helps['apim backend show'] = """
    type: command
    short-summary: show backend.
"""

helps['apim cache'] = """
    type: group
    short-summary: Commands to manage Cache.
"""

helps['apim cache create'] = """
    type: command
    short-summary: create cache.
    examples:
      - name: ApiManagementCreateCache
        text: |-
               az apim cache create --resource-group "rg1" --service-name "apimService1" --cache-id \\
               "westindia" --description "Redis cache instances in West India" --connection-string \\
               "contoso5.redis.cache.windows.net,ssl=true,password=..." --resource-id "/subscriptions/{{ 
               subscription_id }}/resourceGroups/{{ resource_group }}/providers/Microsoft.Cache/Redis/{{ 
               redis_name }}"
"""

helps['apim cache update'] = """
    type: command
    short-summary: update cache.
    examples:
      - name: ApiManagementUpdateCache
        text: |-
               az apim cache update --resource-group "rg1" --service-name "apimService1" --cache-id \\
               "westindia" --description "Update Cache in west India"
"""

helps['apim cache delete'] = """
    type: command
    short-summary: delete cache.
    examples:
      - name: ApiManagementDeleteCache
        text: |-
               az apim cache delete --resource-group "rg1" --service-name "apimService1" --cache-id \\
               "southindia"
"""

helps['apim cache list'] = """
    type: command
    short-summary: list cache.
"""

helps['apim cache show'] = """
    type: command
    short-summary: show cache.
"""

helps['apim certificate'] = """
    type: group
    short-summary: Commands to manage Certificate.
"""

helps['apim certificate create'] = """
    type: command
    short-summary: create certificate.
    examples:
      - name: ApiManagementCreateCertificate
        text: |-
               az apim certificate create --resource-group "rg1" --service-name "apimService1" \\
               --certificate-id "tempcert" --data \\
               "****************Base 64 Encoded Certificate *******************************" --password \\
               "****Certificate Password******"
"""

helps['apim certificate update'] = """
    type: command
    short-summary: update certificate.
"""

helps['apim certificate delete'] = """
    type: command
    short-summary: delete certificate.
    examples:
      - name: ApiManagementDeleteCertificate
        text: |-
               az apim certificate delete --resource-group "rg1" --service-name "apimService1" \\
               --certificate-id "tempcert"
"""

helps['apim certificate list'] = """
    type: command
    short-summary: list certificate.
"""

helps['apim certificate show'] = """
    type: command
    short-summary: show certificate.
"""

helps['apim'] = """
    type: group
    short-summary: Commands to manage ApiManagementService.
"""

helps['apim create'] = """
    type: command
    short-summary: create api management service.
    examples:
      - name: ApiManagementCreateService
        text: |-
               az apim create --resource-group "rg1" --name "apimService1" --publisher-email \\
               "apim@autorestsdk.com" --publisher-name "autorestsdk" --sku-name "Developer" \\
               --sku-capacity "1" --location "Central US"
      - name: ApiManagementCreateMultiRegionServiceWithCustomHostname
        text: |-
               az apim create --resource-group "rg1" --name "apimService1" --virtual-network-type \\
               "External" --publisher-email "admin@live.com" --publisher-name "contoso" --sku-name \\
               "Premium" --sku-capacity "1" --location "Central US"
      - name: ApiManagementCreateServiceHavingMsi
        text: |-
               az apim create --resource-group "rg1" --name "apimService1" --publisher-email \\
               "apim@autorestsdk.com" --publisher-name "autorestsdk" --sku-name "Consumption" --location \\
               "West US"
      - name: ApiManagementCreateServiceWithSystemCertificates
        text: |-
               az apim create --resource-group "rg1" --name "apimService1" --publisher-email \\
               "apim@autorestsdk.com" --publisher-name "autorestsdk" --sku-name "Basic" --sku-capacity \\
               "1" --location "Central US"
"""

helps['apim update'] = """
    type: command
    short-summary: update api management service.
    examples:
      - name: ApiManagementUpdateServiceDisableTls10
        text: |-
               az apim update --resource-group "rg1" --name "apimService1"
      - name: ApiManagementUpdateServicePublisherDetails
        text: |-
               az apim update --resource-group "rg1" --name "apimService1" --publisher-email \\
               "foobar@live.com" --publisher-name "Contoso Vnext"
"""

helps['apim delete'] = """
    type: command
    short-summary: delete api management service.
    examples:
      - name: ApiManagementServiceDeleteService
        text: |-
               az apim delete --resource-group "rg1" --name "apimService1"
"""

helps['apim list'] = """
    type: command
    short-summary: list api management service.
"""

helps['apim show'] = """
    type: command
    short-summary: show api management service.
"""

helps['apim diagnostic'] = """
    type: group
    short-summary: Commands to manage Diagnostic.
"""

helps['apim diagnostic create'] = """
    type: command
    short-summary: create diagnostic.
    examples:
      - name: ApiManagementCreateDiagnostic
        text: |-
               az apim diagnostic create --resource-group "rg1" --service-name "apimService1" \\
               --diagnostic-id "applicationinsights" --always-log "allErrors" --logger-id \\
               "/loggers/azuremonitor"
"""

helps['apim diagnostic update'] = """
    type: command
    short-summary: update diagnostic.
    examples:
      - name: ApiManagementUpdateDiagnostic
        text: |-
               az apim diagnostic update --resource-group "rg1" --service-name "apimService1" \\
               --diagnostic-id "applicationinsights" --always-log "allErrors" --logger-id \\
               "/loggers/applicationinsights"
"""

helps['apim diagnostic delete'] = """
    type: command
    short-summary: delete diagnostic.
    examples:
      - name: ApiManagementDeleteDiagnostic
        text: |-
               az apim diagnostic delete --resource-group "rg1" --service-name "apimService1" \\
               --diagnostic-id "applicationinsights"
"""

helps['apim diagnostic list'] = """
    type: command
    short-summary: list diagnostic.
"""

helps['apim diagnostic show'] = """
    type: command
    short-summary: show diagnostic.
"""

helps['apim template'] = """
    type: group
    short-summary: Commands to manage EmailTemplate.
"""

helps['apim template create'] = """
    type: command
    short-summary: create email template.
    examples:
      - name: ApiManagementCreateEmailTemplate
        text: |-
               az apim template create --resource-group "rg1" --service-name "apimService1" --name \\
               "newIssueNotificationMessage" --subject \\
               "Your request for $IssueName was successfully received."
"""

helps['apim template update'] = """
    type: command
    short-summary: update email template.
    examples:
      - name: ApiManagementUpdateEmailTemplate
        text: |-
               az apim template update --resource-group "rg1" --service-name "apimService1" --name \\
               "applicationApprovedNotificationMessage" --subject \\
               "Your application $AppName is published in the gallery" --body "<!DOCTYPE html >\\r\\n<html>
               \\r\\n  <head />\\r\\n  <body>\\r\\n    <p style=\\"font-size:12pt;font-family:'Segoe UI'\\">Dear 
               $DevFirstName $DevLastName,</p>\\r\\n    <p style=\\"font-size:12pt;font-family:'Segoe UI'\\">
               \\r\\n          We are happy to let you know that your request to publish the $AppName appli
               cation in the gallery has been approved. Your application has been published and can be vi
               ewed <a href=\\"http://$DevPortalUrl/Applications/Details/$AppId\\">here</a>.\\r\\n        </p
               >\\r\\n    <p style=\\"font-size:12pt;font-family:'Segoe UI'\\">Best,</p>\\r\\n    <p style=\\"fo
               nt-size:12pt;font-family:'Segoe UI'\\">The $OrganizationName API Team</p>\\r\\n  </body>\\r\\n<
               /html>"
"""

helps['apim template delete'] = """
    type: command
    short-summary: delete email template.
    examples:
      - name: ApiManagementDeleteEmailTemplate
        text: |-
               az apim template delete --resource-group "rg1" --service-name "apimService1" --name \\
               "newIssueNotificationMessage"
"""

helps['apim template list'] = """
    type: command
    short-summary: list email template.
"""

helps['apim template show'] = """
    type: command
    short-summary: show email template.
"""

helps['apim group'] = """
    type: group
    short-summary: Commands to manage Group.
"""

helps['apim group create'] = """
    type: command
    short-summary: create group.
    examples:
      - name: ApiManagementCreateGroup
        text: |-
               az apim group create --resource-group "rg1" --service-name "apimService1" --group-id \\
               "tempgroup" --display-name "temp group"
      - name: ApiManagementCreateGroupExternal
        text: |-
               az apim group create --resource-group "rg1" --service-name "apimService1" --group-id \\
               "aadGroup" --display-name "NewGroup (samiraad.onmicrosoft.com)" --description \\
               "new group to test" --type "external" --external-id \\
               "aad://samiraad.onmicrosoft.com/groups/83cf2753-5831-4675-bc0e-2f8dc067c58d"
"""

helps['apim group update'] = """
    type: command
    short-summary: update group.
    examples:
      - name: ApiManagementUpdateGroup
        text: |-
               az apim group update --resource-group "rg1" --service-name "apimService1" --group-id \\
               "tempgroup" --display-name "temp group"
"""

helps['apim group delete'] = """
    type: command
    short-summary: delete group.
    examples:
      - name: ApiManagementDeleteGroup
        text: |-
               az apim group delete --resource-group "rg1" --service-name "apimService1" --group-id \\
               "aadGroup"
"""

helps['apim group list'] = """
    type: command
    short-summary: list group.
"""

helps['apim group show'] = """
    type: command
    short-summary: show group.
"""

helps['apim group user'] = """
    type: group
    short-summary: Commands to manage GroupUser.
"""

helps['apim group user create'] = """
    type: command
    short-summary: create group user.
    examples:
      - name: ApiManagementCreateGroupUser
        text: |-
               az apim group user create --resource-group "rg1" --service-name "apimService1" --group-id \\
               "tempgroup" --user-id "59307d350af58404d8a26300"
"""

helps['apim group user delete'] = """
    type: command
    short-summary: delete group user.
    examples:
      - name: ApiManagementDeleteGroupUser
        text: |-
               az apim group user delete --resource-group "rg1" --service-name "apimService1" --group-id \\
               "templategroup" --user-id "59307d350af58404d8a26300"
"""

helps['apim group user list'] = """
    type: command
    short-summary: list group user.
"""

helps['apim identityprovider'] = """
    type: group
    short-summary: Commands to manage IdentityProvider.
"""

helps['apim identityprovider create'] = """
    type: command
    short-summary: create identity provider.
    examples:
      - name: ApiManagementCreateIdentityProvider
        text: |-
               az apim identityprovider create --resource-group "rg1" --service-name "apimService1" \\
               --name "facebook" --client-id "facebookid" --client-secret "facebookapplicationsecret"
"""

helps['apim identityprovider update'] = """
    type: command
    short-summary: update identity provider.
    examples:
      - name: ApiManagementUpdateIdentityProvider
        text: |-
               az apim identityprovider update --resource-group "rg1" --service-name "apimService1" \\
               --name "facebook" --client-id "updatedfacebookid" --client-secret "updatedfacebooksecret"
"""

helps['apim identityprovider delete'] = """
    type: command
    short-summary: delete identity provider.
    examples:
      - name: ApiManagementDeleteIdentityProvider
        text: |-
               az apim identityprovider delete --resource-group "rg1" --service-name "apimService1" \\
               --name "aad"
"""

helps['apim identityprovider list'] = """
    type: command
    short-summary: list identity provider.
"""

helps['apim identityprovider show'] = """
    type: command
    short-summary: show identity provider.
"""

helps['apim logger'] = """
    type: group
    short-summary: Commands to manage Logger.
"""

helps['apim logger create'] = """
    type: command
    short-summary: create logger.
    examples:
      - name: ApiManagementCreateEHLogger
        text: |-
               az apim logger create --resource-group "rg1" --service-name "apimService1" --logger-id \\
               "loggerId" --logger-type "azureEventHub" --description "adding a new logger"
      - name: ApiManagementCreateAILogger
        text: |-
               az apim logger create --resource-group "rg1" --service-name "apimService1" --logger-id \\
               "loggerId" --logger-type "applicationInsights" --description "adding a new logger"
"""

helps['apim logger update'] = """
    type: command
    short-summary: update logger.
    examples:
      - name: ApiManagementUpdateLogger
        text: |-
               az apim logger update --resource-group "rg1" --service-name "apimService1" --logger-id \\
               "loggerId"
"""

helps['apim logger delete'] = """
    type: command
    short-summary: delete logger.
    examples:
      - name: ApiManagementDeleteLogger
        text: |-
               az apim logger delete --resource-group "rg1" --service-name "apimService1" --logger-id \\
               "loggerId"
"""

helps['apim logger list'] = """
    type: command
    short-summary: list logger.
"""

helps['apim logger show'] = """
    type: command
    short-summary: show logger.
"""

helps['apim notification'] = """
    type: group
    short-summary: Commands to manage Notification.
"""

helps['apim notification create'] = """
    type: command
    short-summary: create notification.
    examples:
      - name: ApiManagementCreateNotification
        text: |-
               az apim notification create --resource-group "rg1" --service-name "apimService1" --name \\
               "RequestPublisherNotificationMessage"
"""

helps['apim notification update'] = """
    type: command
    short-summary: update notification.
"""

helps['apim notification list'] = """
    type: command
    short-summary: list notification.
"""

helps['apim notification show'] = """
    type: command
    short-summary: show notification.
"""

helps['apim notification recipientuser'] = """
    type: group
    short-summary: Commands to manage NotificationRecipientUser.
"""

helps['apim notification recipientuser create'] = """
    type: command
    short-summary: create notification recipient user.
    examples:
      - name: ApiManagementCreateNotificationRecipientUser
        text: |-
               az apim notification recipientuser create --resource-group "rg1" --service-name \\
               "apimService1" --notification-name "RequestPublisherNotificationMessage" --user-id \\
               "576823d0a40f7e74ec07d642"
"""

helps['apim notification recipientuser update'] = """
    type: command
    short-summary: update notification recipient user.
"""

helps['apim notification recipientuser delete'] = """
    type: command
    short-summary: delete notification recipient user.
    examples:
      - name: ApiManagementDeleteNotificationRecipientUser
        text: |-
               az apim notification recipientuser delete --resource-group "rg1" --service-name \\
               "apimService1" --notification-name "RequestPublisherNotificationMessage" --user-id \\
               "576823d0a40f7e74ec07d642"
"""

helps['apim notification recipientuser list'] = """
    type: command
    short-summary: list notification recipient user.
"""

helps['apim notification recipientemail'] = """
    type: group
    short-summary: Commands to manage NotificationRecipientEmail.
"""

helps['apim notification recipientemail create'] = """
    type: command
    short-summary: create notification recipient email.
    examples:
      - name: ApiManagementCreateNotificationRecipientEmail
        text: |-
               az apim notification recipientemail create --resource-group "rg1" --service-name \\
               "apimService1" --notification-name "RequestPublisherNotificationMessage" --email \\
               "foobar@live.com"
"""

helps['apim notification recipientemail update'] = """
    type: command
    short-summary: update notification recipient email.
"""

helps['apim notification recipientemail delete'] = """
    type: command
    short-summary: delete notification recipient email.
    examples:
      - name: ApiManagementDeleteNotificationRecipientEmail
        text: |-
               az apim notification recipientemail delete --resource-group "rg1" --service-name \\
               "apimService1" --notification-name "RequestPublisherNotificationMessage" --email \\
               "contoso@live.com"
"""

helps['apim notification recipientemail list'] = """
    type: command
    short-summary: list notification recipient email.
"""

helps['apim openidconnectprovider'] = """
    type: group
    short-summary: Commands to manage OpenIdConnectProvider.
"""

helps['apim openidconnectprovider create'] = """
    type: command
    short-summary: create open id connect provider.
    examples:
      - name: ApiManagementCreateOpenIdConnectProvider
        text: |-
               az apim openidconnectprovider create --resource-group "rg1" --service-name "apimService1" \\
               --opid "templateOpenIdConnect3" --display-name "templateoidprovider3" --metadata-endpoint \\
               "https://oidprovider-template3.net" --client-id "oidprovidertemplate3"
"""

helps['apim openidconnectprovider update'] = """
    type: command
    short-summary: update open id connect provider.
    examples:
      - name: ApiManagementUpdateOpenIdConnectProvider
        text: |-
               az apim openidconnectprovider update --resource-group "rg1" --service-name "apimService1" \\
               --opid "templateOpenIdConnect2" --client-secret "updatedsecret"
"""

helps['apim openidconnectprovider delete'] = """
    type: command
    short-summary: delete open id connect provider.
    examples:
      - name: ApiManagementDeleteOpenIdConnectProvider
        text: |-
               az apim openidconnectprovider delete --resource-group "rg1" --service-name "apimService1" \\
               --opid "templateOpenIdConnect3"
"""

helps['apim openidconnectprovider list'] = """
    type: command
    short-summary: list open id connect provider.
"""

helps['apim openidconnectprovider show'] = """
    type: command
    short-summary: show open id connect provider.
"""

helps['apim policy'] = """
    type: group
    short-summary: Commands to manage Policy.
"""

helps['apim policy create'] = """
    type: command
    short-summary: create policy.
    examples:
      - name: ApiManagementCreatePolicy
        text: |-
               az apim policy create --resource-group "rg1" --service-name "apimService1" --policy-id \\
               "policy" --value "<policies>\\r\\n  <inbound />\\r\\n  <backend>\\r\\n    <forward-request />\\r\\
               n  </backend>\\r\\n  <outbound />\\r\\n</policies>" --format "xml"
"""

helps['apim policy update'] = """
    type: command
    short-summary: update policy.
"""

helps['apim policy delete'] = """
    type: command
    short-summary: delete policy.
    examples:
      - name: ApiManagementDeletePolicy
        text: |-
               az apim policy delete --resource-group "rg1" --service-name "apimService1" --policy-id \\
               "policy"
"""

helps['apim policy list'] = """
    type: command
    short-summary: list policy.
"""

helps['apim policy show'] = """
    type: command
    short-summary: show policy.
"""

helps['apim portalsetting signin'] = """
    type: group
    short-summary: Commands to manage SignInSetting.
"""

helps['apim portalsetting signin create'] = """
    type: command
    short-summary: create sign in setting.
    examples:
      - name: ApiManagementPortalSettingsUpdateSignIn
        text: |-
               az apim portalsetting signin create --resource-group "rg1" --name "apimService1" \\
               --enabled true
"""

helps['apim portalsetting signin update'] = """
    type: command
    short-summary: update sign in setting.
    examples:
      - name: ApiManagementPortalSettingsUpdateSignIn
        text: |-
               az apim portalsetting signin update --resource-group "rg1" --name "apimService1" \\
               --enabled true
"""

helps['apim portalsetting signin show'] = """
    type: command
    short-summary: show sign in setting.
"""

helps['apim portalsetting signup'] = """
    type: group
    short-summary: Commands to manage SignUpSetting.
"""

helps['apim portalsetting signup create'] = """
    type: command
    short-summary: create sign up setting.
    examples:
      - name: ApiManagementPortalSettingsUpdateSignUp
        text: |-
               az apim portalsetting signup create --resource-group "rg1" --name "apimService1" \\
               --enabled true
"""

helps['apim portalsetting signup update'] = """
    type: command
    short-summary: update sign up setting.
    examples:
      - name: ApiManagementPortalSettingsUpdateSignUp
        text: |-
               az apim portalsetting signup update --resource-group "rg1" --name "apimService1" \\
               --enabled true
"""

helps['apim portalsetting signup show'] = """
    type: command
    short-summary: show sign up setting.
"""

helps['apim portalsetting delegation'] = """
    type: group
    short-summary: Commands to manage DelegationSetting.
"""

helps['apim portalsetting delegation create'] = """
    type: command
    short-summary: create delegation setting.
    examples:
      - name: ApiManagementPortalSettingsUpdateDelegation
        text: |-
               az apim portalsetting delegation create --resource-group "rg1" --name "apimService1" \\
               --url "http://contoso.com/delegation" --validation-key "nVF7aKIvr9mV/RM5lOD0sYoi8ThXTRHQP7
               o66hvUmjCDkPKR3qxPu/otJcNciz2aQdqPuzJH3ECG4TU2yZjQ7Q=="
"""

helps['apim portalsetting delegation update'] = """
    type: command
    short-summary: update delegation setting.
    examples:
      - name: ApiManagementPortalSettingsUpdateDelegation
        text: |-
               az apim portalsetting delegation update --resource-group "rg1" --name "apimService1" \\
               --url "http://contoso.com/delegation" --validation-key "nVF7aKIvr9mV/RM5lOD0sYoi8ThXTRHQP7
               o66hvUmjCDkPKR3qxPu/otJcNciz2aQdqPuzJH3ECG4TU2yZjQ7Q=="
"""

helps['apim portalsetting delegation show'] = """
    type: command
    short-summary: show delegation setting.
"""

helps['apim product'] = """
    type: group
    short-summary: Commands to manage Product.
"""

helps['apim product create'] = """
    type: command
    short-summary: create product.
    examples:
      - name: ApiManagementCreateProduct
        text: |-
               az apim product create --resource-group "rg1" --service-name "apimService1" --product-id \\
               "testproduct" --display-name "Test Template ProductName 4"
"""

helps['apim product update'] = """
    type: command
    short-summary: update product.
    examples:
      - name: ApiManagementUpdateProduct
        text: |-
               az apim product update --resource-group "rg1" --service-name "apimService1" --product-id \\
               "testproduct" --display-name "Test Template ProductName 4"
"""

helps['apim product delete'] = """
    type: command
    short-summary: delete product.
    examples:
      - name: ApiManagementDeleteProduct
        text: |-
               az apim product delete --resource-group "rg1" --service-name "apimService1" --product-id \\
               "testproduct"
"""

helps['apim product list'] = """
    type: command
    short-summary: list product.
"""

helps['apim product show'] = """
    type: command
    short-summary: show product.
"""

helps['apim product api'] = """
    type: group
    short-summary: Commands to manage ProductApi.
"""

helps['apim product api create'] = """
    type: command
    short-summary: create product api.
    examples:
      - name: ApiManagementCreateProductApi
        text: |-
               az apim product api create --resource-group "rg1" --service-name "apimService1" \\
               --product-id "testproduct" --api-id "echo-api"
"""

helps['apim product api update'] = """
    type: command
    short-summary: update product api.
"""

helps['apim product api delete'] = """
    type: command
    short-summary: delete product api.
    examples:
      - name: ApiManagementDeleteProductApi
        text: |-
               az apim product api delete --resource-group "rg1" --service-name "apimService1" \\
               --product-id "testproduct" --api-id "echo-api"
"""

helps['apim product api list'] = """
    type: command
    short-summary: list product api.
"""

helps['apim product group'] = """
    type: group
    short-summary: Commands to manage ProductGroup.
"""

helps['apim product group create'] = """
    type: command
    short-summary: create product group.
    examples:
      - name: ApiManagementCreateProductGroup
        text: |-
               az apim product group create --resource-group "rg1" --service-name "apimService1" \\
               --product-id "testproduct" --group-id "templateGroup"
"""

helps['apim product group update'] = """
    type: command
    short-summary: update product group.
"""

helps['apim product group delete'] = """
    type: command
    short-summary: delete product group.
    examples:
      - name: ApiManagementDeleteProductGroup
        text: |-
               az apim product group delete --resource-group "rg1" --service-name "apimService1" \\
               --product-id "testproduct" --group-id "templateGroup"
"""

helps['apim product group list'] = """
    type: command
    short-summary: list product group.
"""

helps['apim product policy'] = """
    type: group
    short-summary: Commands to manage ProductPolicy.
"""

helps['apim product policy create'] = """
    type: command
    short-summary: create product policy.
    examples:
      - name: ApiManagementCreateProductPolicy
        text: |-
               az apim product policy create --resource-group "rg1" --service-name "apimService1" \\
               --product-id "5702e97e5157a50f48dce801" --policy-id "policy" --value "<policies>\\r\\n  <inb
               ound>\\r\\n    <rate-limit calls=\\"{{call-count}}\\" renewal-period=\\"15\\"></rate-limit>\\r\\n 
                  <log-to-eventhub logger-id=\\"16\\">\\r\\n                      @( string.Join(\\",\\", DateT
               ime.UtcNow, context.Deployment.ServiceName, context.RequestId, context.Request.IpAddress, 
               context.Operation.Name) ) \\r\\n                  </log-to-eventhub>\\r\\n    <quota-by-key ca
               lls=\\"40\\" counter-key=\\"cc\\" renewal-period=\\"3600\\" increment-count=\\"@(context.Request.
               Method == &quot;POST&quot; ? 1:2)\\" />\\r\\n    <base />\\r\\n  </inbound>\\r\\n  <backend>\\r\\n 
                  <base />\\r\\n  </backend>\\r\\n  <outbound>\\r\\n    <base />\\r\\n  </outbound>\\r\\n</policies
               >" --format "xml"
"""

helps['apim product policy update'] = """
    type: command
    short-summary: update product policy.
"""

helps['apim product policy delete'] = """
    type: command
    short-summary: delete product policy.
    examples:
      - name: ApiManagementDeleteProductPolicy
        text: |-
               az apim product policy delete --resource-group "rg1" --service-name "apimService1" \\
               --product-id "testproduct" --policy-id "policy"
"""

helps['apim product policy list'] = """
    type: command
    short-summary: list product policy.
"""

helps['apim product policy show'] = """
    type: command
    short-summary: show product policy.
"""

helps['apim property'] = """
    type: group
    short-summary: Commands to manage Property.
"""

helps['apim property create'] = """
    type: command
    short-summary: create property.
    examples:
      - name: ApiManagementCreateProperty
        text: |-
               az apim property create --resource-group "rg1" --service-name "apimService1" --prop-id \\
               "testprop2" --secret true --display-name "prop3name" --value "propValue"
"""

helps['apim property update'] = """
    type: command
    short-summary: update property.
    examples:
      - name: ApiManagementUpdateProperty
        text: |-
               az apim property update --resource-group "rg1" --service-name "apimService1" --prop-id \\
               "testprop2" --secret true
"""

helps['apim property delete'] = """
    type: command
    short-summary: delete property.
    examples:
      - name: ApiManagementDeleteProperty
        text: |-
               az apim property delete --resource-group "rg1" --service-name "apimService1" --prop-id \\
               "testprop2"
"""

helps['apim property list'] = """
    type: command
    short-summary: list property.
"""

helps['apim property show'] = """
    type: command
    short-summary: show property.
"""

helps['apim subscription'] = """
    type: group
    short-summary: Commands to manage Subscription.
"""

helps['apim subscription create'] = """
    type: command
    short-summary: create subscription.
    examples:
      - name: ApiManagementCreateSubscription
        text: |-
               az apim subscription create --resource-group "rg1" --service-name "apimService1" --sid \\
               "testsub" --owner-id "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_grou
               p }}/providers/Microsoft.ApiManagement/service/{{ service_name }}/users/{{ user_name }}" \\
               --scope "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/provider
               s/Microsoft.ApiManagement/service/{{ service_name }}/products/{{ product_name }}" \\
               --display-name "testsub"
"""

helps['apim subscription update'] = """
    type: command
    short-summary: update subscription.
    examples:
      - name: ApiManagementUpdateSubscription
        text: |-
               az apim subscription update --resource-group "rg1" --service-name "apimService1" --sid \\
               "testsub" --display-name "testsub"
"""

helps['apim subscription delete'] = """
    type: command
    short-summary: delete subscription.
    examples:
      - name: ApiManagementDeleteSubscription
        text: |-
               az apim subscription delete --resource-group "rg1" --service-name "apimService1" --sid \\
               "testsub"
"""

helps['apim subscription list'] = """
    type: command
    short-summary: list subscription.
"""

helps['apim subscription show'] = """
    type: command
    short-summary: show subscription.
"""

helps['apim user'] = """
    type: group
    short-summary: Commands to manage User.
"""

helps['apim user create'] = """
    type: command
    short-summary: create user.
    examples:
      - name: ApiManagementCreateUser
        text: |-
               az apim user create --resource-group "rg1" --service-name "apimService1" --user-id \\
               "5931a75ae4bbd512288c680b" --email "foobar@outlook.com" --first-name "foo" --last-name \\
               "bar" --confirmation "signup"
"""

helps['apim user update'] = """
    type: command
    short-summary: update user.
    examples:
      - name: ApiManagementUpdateUser
        text: |-
               az apim user update --resource-group "rg1" --service-name "apimService1" --user-id \\
               "5931a75ae4bbd512288c680b" --email "foobar@outlook.com" --first-name "foo" --last-name \\
               "bar"
"""

helps['apim user delete'] = """
    type: command
    short-summary: delete user.
    examples:
      - name: ApiManagementDeleteUser
        text: |-
               az apim user delete --resource-group "rg1" --service-name "apimService1" --user-id \\
               "5931a75ae4bbd512288c680b"
"""

helps['apim user list'] = """
    type: command
    short-summary: list user.
"""

helps['apim user show'] = """
    type: command
    short-summary: show user.
"""
