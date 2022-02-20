# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['fidalgo admin'] = """
    type: group
    short-summary: "Manage sadmin Fidalgo resources"
"""

helps['fidalgo dev'] = """
    type: group
    short-summary: "Manage developer Fidalgo resources"
"""

helps['fidalgo dev project'] = """
    type: group
    short-summary: "Manage developer Fidalgo projects"
"""

helps['fidalgo dev project list'] = """
    type: command
    short-summary: "Lists all projects in a devcenter"
    examples:
      - name: Project_ListByDevCenter
        text: |-
               az fidalgo dev project list --dev-center "{devCenter}"
"""

helps['fidalgo dev pool'] = """
    type: group
    short-summary: "Manage developer Fidalgo pools"
"""

helps['fidalgo dev pool list'] = """
    type: command
    short-summary: "Lists available pools."
    examples:
      - name: Pool_List
        text: |-
               az fidalgo dev pool list --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo dev pool show'] = """
    type: command
    short-summary: "Gets a machine pool."
    examples:
      - name: Pool_Get
        text: |-
               az fidalgo dev pool show --name "{poolName}" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo dev virtual-machine'] = """
    type: group
    short-summary: Manage Fidalgo virtual machines
"""

helps['fidalgo dev virtual-machine assign'] = """
    type: command
    short-summary: Assigns a Virtual Machine to a different user."
    examples:
      - name: VirtualMachine_Assign
        text: |-
               az fidalgo dev virtual-machine assign --name "MyDevBox" --new-owner "5862847c-3bba-4720-bd44-982b1da21586" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo dev virtual-machine create'] = """
    type: command
    short-summary: "Creates or updates a virtual machine."
    examples:
      - name: VirtualMachine_Create
        text: |-
               az fidalgo dev virtual-machine create --name "MyDevBox" --pool-name "LargeDevWorkStationPool" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo dev virtual-machine delete'] = """
    type: command
    short-summary: "Deletes a virtual machine."
    examples:
      - name: VirtualMachine_Delete
        text: |-
               az fidalgo dev virtual-machine delete --name "MyDevBox" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo dev virtual-machine get-rdp-file-content'] = """
    type: command
    short-summary: "Gets a string that represents the contents of the RDP file for the virtual machine."
    examples:
      - name: VirtualMachine_GetRdpFileContents
        text: |-
               az fidalgo dev virtual-machine get-rdp-file-content --name "MyDevBox" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo dev virtual-machine list'] = """
    type: command
    short-summary: "Lists Virtual Machines that the caller has access to in the DevCenter."
    examples:
      - name: VirtualMachine_List
        text: |-
               az fidalgo dev virtual-machine list --dev-center "{devCenter}"    
      - name: VirtualMachine_ListByUser
        text: |-
               az fidalgo dev virtual-machine list --dev-center "{devCenter}" --project-name "{projectName}" --user-id "me"       
"""

helps['fidalgo dev virtual-machine show'] = """
    type: command
    short-summary: "Gets a virtual machine."
    examples:
      - name: VirtualMachine_Get
        text: |-
               az fidalgo dev virtual-machine show --name "MyDevBox" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo dev virtual-machine start'] = """
    type: command
    short-summary: "Starts a Virtual Machine."
    examples:
      - name: VirtualMachine_Start
        text: |-
               az fidalgo dev virtual-machine start --name "MyDevBox" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo dev virtual-machine stop'] = """
    type: command
    short-summary: "Stops a Virtual machine."
    examples:
      - name: VirtualMachine_Stop
        text: |-
               az fidalgo dev virtual-machine stop --name "MyDevBox" --project-name "{projectName}" \
 --dev-center "{devCenter}"
"""

helps['fidalgo dev catalog-item'] = """
    type: group
    short-summary: "Manage developer Fidalgo catalog items"
"""

helps['fidalgo dev catalog-item list'] = """
    type: command
    short-summary: "Lists all catalog items available for a project."
    examples:
      - name: CatalogItem_ListByProject
        text: |-
               az fidalgo dev catalog-item list --fidalgo-dns-suffix "fidalgo.azure.net" --project-name "{projectName}" --dev-center "{devCenter}" \
--resource-group "rg1"
"""

helps['fidalgo dev deployment'] = """
    type: group
    short-summary: "Manage developer Fidalgo deployments"
"""

helps['fidalgo dev deployment list'] = """
    type: command
    short-summary: "Gets an environment's deployment history."
    examples:
      - name: Actions_Get
        text: |-
               az fidalgo dev deployment list --environment-name "{environmentName}" --project-name "{projectName}" \
--dev-center "{devCenter}" --fidalgo-dns-suffix "fidalgo.azure.net"
"""

helps['fidalgo dev environment-type'] = """
    type: group
    short-summary: "Manage developer Fidalgo environment types"
"""

helps['fidalgo dev environment-type list'] = """
    type: command
    short-summary: "Lists all environment types configured for a project."
    examples:
      - name: EnvironmentType_List
        text: |-
               az fidalgo dev environment-type list --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo dev environment'] = """
    type: group
    short-summary: "Manage developer Fidalgo environments"
"""

helps['fidalgo dev environment list'] = """
    type: command
    short-summary: "Lists the environments for a project."
    examples:
      - name: Environments_ListByProject
        text: |-
               az fidalgo dev environment list --project-name "{projectName}" --dev-center "{devCenter}" --fidalgo-dns-suffix "fidalgo.azure.net"
"""

helps['fidalgo dev environment show'] = """
    type: command
    short-summary: "Gets an environment."
    examples:
      - name: Environments_Get
        text: |-
               az fidalgo dev environment show --name "{environmentName}" --project-name "{projectName}" \
--dev-center "{devCenter}" --fidalgo-dns-suffix "fidalgo.azure.net"
"""

helps['fidalgo dev environment create'] = """
    type: command
    short-summary: "Create an environment."
    examples:
      - name: Environments_CreateByCatalogItem
        text: |-
               az fidalgo dev environment create --dev-center "{devCenter}" --description "Personal Dev Environment" \
--catalog-item-name "helloworld" --deployment-parameters "{\\"app_name\\":\\"mydevApi\\"}" --environment-type \
"DevTest" --tags ProjectType="WebApi" Role="Development" Tech="NetCore" --name "{environmentName}" --project-name \
"{projectName}" --fidalgo-dns-suffix "fidalgo.azure.net"
"""

helps['fidalgo dev environment update'] = """
    type: command
    short-summary: "Partially updates an environment."
    examples:
      - name: Environments_Update
        text: |-
               az fidalgo dev environment update --description "Personal Dev Environment 2" --tags ProjectType="WebApi" \
Role="Development" Tech="NetCore" --name "{environmentName}" --project-name "{projectName}" --dev-center "{devCenter}" \
--fidalgo-dns-suffix "fidalgo.azure.net"    
"""

helps['fidalgo dev environment delete'] = """
    type: command
    short-summary: "Deletes an environment and all it's associated resources."
    examples:
      - name: Environments_Delete
        text: |-
               az fidalgo dev environment delete --name "{environmentName}" --project-name "{projectName}" \
--dev-center "{devCenter} --fidalgo-dns-suffix "fidalgo.azure.net"
"""

helps['fidalgo dev environment deploy'] = """
    type: command
    short-summary: "Deploys an environment's resources."
    examples:
      - name: Environments_Deploy
        text: |-
               az fidalgo dev environment deploy --name "{environmentName}" --project-name "{projectName}" \
--dev-center "{devCenter} --fidalgo-dns-suffix "fidalgo.azure.net"
"""

#control plane
helps['fidalgo'] = '''
    type: group
    short-summary: Manage Fidalgo
'''

helps['fidalgo admin dev-center'] = """
    type: group
    short-summary: Manage dev center with fidalgo
"""

helps['fidalgo admin dev-center list'] = """
    type: command
    short-summary: "Lists all devcenters in a resource group. And Lists all devcenters in a subscription."
    examples:
      - name: DevCenters_ListByResourceGroup
        text: |-
               az fidalgo admin dev-center list --resource-group "rg1"
      - name: DevCenters_ListBySubscription
        text: |-
               az fidalgo admin dev-center list
"""

helps['fidalgo admin dev-center show'] = """
    type: command
    short-summary: "Gets a devcenter."
    examples:
      - name: DevCenters_Get
        text: |-
               az fidalgo admin dev-center show --name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin dev-center create'] = """
    type: command
    short-summary: "Create a devcenter resource."
    examples:
      - name: DevCenters_Create
        text: |-
               az fidalgo admin dev-center create --location "centralus" --tags CostCode="12345" --name "Contoso" \
--resource-group "rg1"
      - name: DevCenters_CreateWithUserIdentity
        text: |-
               az fidalgo admin dev-center create --identity-type "UserAssigned" --user-assigned-identities \
"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/identityGroup/providers/Microsoft.ManagedIdenti\
ty/userAssignedIdentities/testidentity1" --location "centralus" --tags CostCode="12345" --name "Contoso" \
--resource-group "rg1"
"""

helps['fidalgo admin dev-center update'] = """
    type: command
    short-summary: "Partially updates a devcenter."
    examples:
      - name: DevCenters_Update
        text: |-
               az fidalgo admin dev-center update --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin dev-center delete'] = """
    type: command
    short-summary: "Deletes a devcenter."
    examples:
      - name: DevCenters_Delete
        text: |-
               az fidalgo admin dev-center delete --name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin dev-center wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the fidalgo dev-center is met.
    examples:
      - name: Pause executing next line of CLI script until the fidalgo dev-center is successfully created.
        text: |-
               az fidalgo admin dev-center wait --name "Contoso" --resource-group "rg1" --created
      - name: Pause executing next line of CLI script until the fidalgo dev-center is successfully updated.
        text: |-
               az fidalgo admin dev-center wait --name "Contoso" --resource-group "rg1" --updated
      - name: Pause executing next line of CLI script until the fidalgo dev-center is successfully deleted.
        text: |-
               az fidalgo admin dev-center wait --name "Contoso" --resource-group "rg1" --deleted
"""

helps['fidalgo admin project'] = """
    type: group
    short-summary: Manage project with fidalgo
"""

helps['fidalgo admin project list'] = """
    type: command
    short-summary: "Lists all projects in the resource group. And Lists all projects in the subscription."
    examples:
      - name: Projects_ListByResourceGroup
        text: |-
               az fidalgo admin project list --resource-group "rg1"
      - name: Projects_ListBySubscription
        text: |-
               az fidalgo admin project list
"""

helps['fidalgo admin project show'] = """
    type: command
    short-summary: "Gets a specific project."
    examples:
      - name: Projects_Get
        text: |-
               az fidalgo admin project show --name "{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin project create'] = """
    type: command
    short-summary: "Create a project."
    examples:
      - name: Projects_CreateOrUpdate
        text: |-
               az fidalgo admin project create --location "centralus" --description "This is my first project." \
--dev-center-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/devcenters/{devCenterNa\
me}" --tags CostCenter="R&D" --name "{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin project update'] = """
    type: command
    short-summary: "Partially updates a project."
    examples:
      - name: Projects_Update
        text: |-
               az fidalgo admin project update --description "This is my first project." --tags CostCenter="R&D" --name \
"{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin project delete'] = """
    type: command
    short-summary: "Deletes a project resource."
    examples:
      - name: Projects_Delete
        text: |-
               az fidalgo admin project delete --name "{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin project wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the fidalgo project is met.
    examples:
      - name: Pause executing next line of CLI script until the fidalgo project is successfully created.
        text: |-
               az fidalgo admin project wait --name "{projectName}" --resource-group "rg1" --created
      - name: Pause executing next line of CLI script until the fidalgo project is successfully updated.
        text: |-
               az fidalgo admin project wait --name "{projectName}" --resource-group "rg1" --updated
      - name: Pause executing next line of CLI script until the fidalgo project is successfully deleted.
        text: |-
               az fidalgo admin project wait --name "{projectName}" --resource-group "rg1" --deleted
"""

helps['fidalgo admin environment'] = """
    type: group
    short-summary: Manage environment with fidalgo
"""

helps['fidalgo admin environment list'] = """
    type: command
    short-summary: "Lists the environments for a project."
    examples:
      - name: Environments_ListByProject
        text: |-
               az fidalgo admin environment list --project-name "{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin environment show'] = """
    type: command
    short-summary: "Gets an environment."
    examples:
      - name: Environments_Get
        text: |-
               az fidalgo admin environment show --name "{environmentName}" --project-name "{projectName}" --resource-group \
"rg1"
"""

helps['fidalgo admin environment create'] = """
    type: command
    short-summary: "Create an environment."
    examples:
      - name: Environments_CreateByCatalogItem
        text: |-
               az fidalgo admin environment create --location "centralus" --description "Personal Dev Environment" \
--catalog-item-name "helloworld" --deployment-parameters "{\\"app_name\\":\\"mydevApi\\"}" --environment-type \
"DevTest" --tags ProjectType="WebApi" Role="Development" Tech="NetCore" --name "{environmentName}" --project-name \
"{projectName}" --resource-group "rg1"
      - name: Environments_CreateByTemplateUri
        text: |-
               az fidalgo admin environment create --location "centralus" --description "Personal Dev Environment" \
--deployment-parameters "{\\"app_name\\":\\"mydevApi\\"}" --environment-type "DevTest" --template-uri \
"https://raw.githubusercontent.com/contoso/webhelpcenter/master/environments/composition-template.json" --tags \
ProjectType="WebApi" Role="Development" Tech="NetCore" --name "{environmentName}" --project-name "{projectName}" \
--resource-group "rg1"
"""

helps['fidalgo admin environment update'] = """
    type: command
    short-summary: "Partially updates an environment."
    examples:
      - name: Environments_Update
        text: |-
               az fidalgo admin environment update --description "Personal Dev Environment 2" --tags ProjectType="WebApi" \
Role="Development" Tech="NetCore" --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin environment delete'] = """
    type: command
    short-summary: "Deletes an environment and all it's associated resources."
    examples:
      - name: Environments_Delete
        text: |-
               az fidalgo admin environment delete --name "{environmentName}" --project-name "{projectName}" \
--resource-group "rg1"
"""

helps['fidalgo admin environment deploy'] = """
    type: command
    short-summary: "Deploys an environment's resources."
    examples:
      - name: Environments_Deploy
        text: |-
               az fidalgo admin environment deploy --name "{environmentName}" --project-name "{projectName}" \
--resource-group "rg1"
"""

helps['fidalgo admin environment wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the fidalgo environment is met.
    examples:
      - name: Pause executing next line of CLI script until the fidalgo environment is successfully created.
        text: |-
               az fidalgo admin environment wait --name "{environmentName}" --project-name "{projectName}" --resource-group \
"rg1" --created
      - name: Pause executing next line of CLI script until the fidalgo environment is successfully updated.
        text: |-
               az fidalgo admin environment wait --name "{environmentName}" --project-name "{projectName}" --resource-group \
"rg1" --updated
      - name: Pause executing next line of CLI script until the fidalgo environment is successfully deleted.
        text: |-
               az fidalgo admin environment wait --name "{environmentName}" --project-name "{projectName}" --resource-group \
"rg1" --deleted
"""

helps['fidalgo admin deployment'] = """
    type: group
    short-summary: Manage deployment with fidalgo
"""

helps['fidalgo admin deployment list'] = """
    type: command
    short-summary: "Gets an environment's deployment history."
    examples:
      - name: Deployments_ListByEnvironment
        text: |-
               az fidalgo admin deployment list --environment-name "{environmentName}" --project-name "{projectName}" \
--resource-group "rg1"
"""

helps['fidalgo admin environment-type'] = """
    type: group
    short-summary: Manage environment type with fidalgo
"""

helps['fidalgo admin environment-type list'] = """
    type: command
    short-summary: "Lists all environment types configured for this project. And Lists environment types for the \
devcenter."
    examples:
      - name: EnvironmentTypes_ListByProject
        text: |-
               az fidalgo admin environment-type list --project-name "Contoso" --resource-group "rg1"
      - name: EnvironmentTypes_ListByDevCenter
        text: |-
               az fidalgo environment-type list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin environment-type show'] = """
    type: command
    short-summary: "Gets an environment type."
    examples:
      - name: EnvironmentTypes_Get
        text: |-
               az fidalgo admin environment-type show --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1"
"""

helps['fidalgo admine nvironment-type create'] = """
    type: command
    short-summary: "Create an environment type."
    examples:
      - name: EnvironmentTypes_CreateOrUpdate
        text: |-
               az fidalgo admin environment-type create --description "Developer/Testing environment" --dev-center-name \
"Contoso" --name "{environmentTypeName}" --resource-group "rg1"
"""

helps['fidalgo admin environment-type update'] = """
    type: command
    short-summary: "Partially updates an environment type."
    examples:
      - name: EnvironmentTypes_Update
        text: |-
               az fidalgo admin environment-type update --description "Updated description" --dev-center-name "Contoso" \
--name "{environmentTypeName}" --resource-group "rg1"
"""

helps['fidalgo admin environment-type delete'] = """
    type: command
    short-summary: "Deletes an environment type."
    examples:
      - name: EnvironmentTypes_Delete
        text: |-
               az fidalgo admin environment-type delete --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1"
"""

helps['fidalgo admin environment-type wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the fidalgo environment-type is met.
    examples:
      - name: Pause executing next line of CLI script until the fidalgo environment-type is successfully deleted.
        text: |-
               az fidalgo admin environment-type wait --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1" --deleted
"""

helps['fidalgo admin catalog-item'] = """
    type: group
    short-summary: Manage catalog item with fidalgo
"""

helps['fidalgo admin catalog-item list'] = """
    type: command
    short-summary: "Lists items by catalog And Lists all catalog items available for a project."
    examples:
      - name: CatalogItems_ListByCatalog
        text: |-
               az fidalgo admin catalog-item list --catalog-name "{catalogName}" --dev-center-name "Contoso" \
--resource-group "rg1"
      - name: CatalogItems_ListByProject
        text: |-
               az fidalgo admin catalog-item list --project-name "{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin catalog-item show'] = """
    type: command
    short-summary: "Gets a catalog item."
    examples:
      - name: CatalogItems_Get
        text: |-
               az fidalgo admin catalog-item show --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name \
"Contoso" --resource-group "rg1"
"""

helps['fidalgo admin catalog-item create'] = """
    type: command
    short-summary: "Creates a catalog item resource."
    parameters:
      - name: --parameters
        short-summary: "Parameters that can be provided to the catalog item."
        long-summary: |
            Usage: --parameters name=XX type=XX description=XX

            name: The name of the parameter.
            type: The type accepted for the parameter value.
            description: Description of the parameter.

            Multiple actions can be specified by using more than one --parameters argument.
    examples:
      - name: CatalogItems_CreateOrUpdate
        text: |-
               az fidalgo admin catalog-item create --description "Hello world template to deploy a basic API service" \
--parameters name="app_name" type="string" description="The name of the application. This must be provided when \
deploying an environment with this template." --template-path "azuredeploy.json" --name "{itemName}" --catalog-name \
"{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin catalog-item update'] = """
    type: command
    short-summary: "Partially updates a catalog item."
    examples:
      - name: CatalogItems_Update
        text: |-
               az fidalgo admin catalog-item update --description "Hello world template to deploy a basic API service" \
--name "{itemName}" --catalog-name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin catalog-item delete'] = """
    type: command
    short-summary: "Deletes a catalog item."
    examples:
      - name: CatalogItems_Delete
        text: |-
               az fidalgo admin catalog-item delete --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name \
"Contoso" --resource-group "rg1"
"""

helps['fidalgo admin catalog'] = """
    type: group
    short-summary: Manage catalog with fidalgo
"""

helps['fidalgo admin catalog list'] = """
    type: command
    short-summary: "Lists catalogs for a devcenter."
    examples:
      - name: Catalogs_ListByDevCenter
        text: |-
               az fidalgo admin catalog list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin catalog show'] = """
    type: command
    short-summary: "Gets a catalog."
    examples:
      - name: Catalogs_Get
        text: |-
               az fidalgo admin catalog show --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin catalog create'] = """
    type: command
    short-summary: "Create a catalog."
    parameters:
      - name: --git-hub
        short-summary: "Properties for a GitHub catalog type."
        long-summary: |
            Usage: --git-hub uri=XX branch=XX secret-identifier=XX path=XX

            uri: Git URI.
            branch: Git branch.
            secret-identifier: A reference to the Key Vault secret containing a security token to authenticate to a \
Git repository.
            path: The folder where the catalog items can be found inside the repository.
      - name: --ado-git
        short-summary: "Properties for an Azure DevOps catalog type."
        long-summary: |
            Usage: --ado-git uri=XX branch=XX secret-identifier=XX path=XX

            uri: Git URI.
            branch: Git branch.
            secret-identifier: A reference to the Key Vault secret containing a security token to authenticate to a \
Git repository.
            path: The folder where the catalog items can be found inside the repository.
    examples:
      - name: Catalogs_CreateOrUpdateAdo
        text: |-
               az fidalgo admin catalog create --ado-git path="/templates" branch="main" secret-identifier="https://contosokv\
.vault.azure.net/secrets/CentralRepoPat" uri="https://contoso@dev.azure.com/contoso/contosoOrg/_git/centralrepo-fakecon\
toso" --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
      - name: Catalogs_CreateOrUpdateGitHub
        text: |-
               az fidalgo admin catalog create --git-hub path="/templates" branch="main" secret-identifier="https://contosokv\
.vault.azure.net/secrets/CentralRepoPat" uri="https://github.com/Contoso/centralrepo-fake.git" --name "{catalogName}" \
--dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin catalog update'] = """
    type: command
    short-summary: "Partially updates a catalog."
    parameters:
      - name: --git-hub
        short-summary: "Properties for a GitHub catalog type."
        long-summary: |
            Usage: --git-hub uri=XX branch=XX secret-identifier=XX path=XX

            uri: Git URI.
            branch: Git branch.
            secret-identifier: A reference to the Key Vault secret containing a security token to authenticate to a \
Git repository.
            path: The folder where the catalog items can be found inside the repository.
      - name: --ado-git
        short-summary: "Properties for an Azure DevOps catalog type."
        long-summary: |
            Usage: --ado-git uri=XX branch=XX secret-identifier=XX path=XX

            uri: Git URI.
            branch: Git branch.
            secret-identifier: A reference to the Key Vault secret containing a security token to authenticate to a \
Git repository.
            path: The folder where the catalog items can be found inside the repository.
    examples:
      - name: Catalogs_Update
        text: |-
               az fidalgo admin catalog update --git-hub path="/environments" --name "{catalogName}" --dev-center-name \
"Contoso" --resource-group "rg1"
"""

helps['fidalgo admin catalog delete'] = """
    type: command
    short-summary: "Deletes a catalog resource."
    examples:
      - name: Catalogs_Delete
        text: |-
               az fidalgo admin catalog delete --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin catalog sync'] = """
    type: command
    short-summary: "Syncs templates for a template source."
    examples:
      - name: Catalogs_Sync
        text: |-
               az fidalgo admin catalog sync --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin catalog wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the fidalgo catalog is met.
    examples:
      - name: Pause executing next line of CLI script until the fidalgo catalog is successfully created.
        text: |-
               az fidalgo admin catalog wait --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" \
--created
      - name: Pause executing next line of CLI script until the fidalgo catalog is successfully updated.
        text: |-
               az fidalgo admin catalog wait --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" \
--updated
      - name: Pause executing next line of CLI script until the fidalgo catalog is successfully deleted.
        text: |-
               az fidalgo admin catalog wait --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" \
--deleted
"""

helps['fidalgo admin mapping'] = """
    type: group
    short-summary: Manage mapping with fidalgo
"""

helps['fidalgo admin mapping list'] = """
    type: command
    short-summary: "Lists mappings."
    examples:
      - name: Mappings_ListByDevCenter
        text: |-
               az fidalgo admin mapping list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin mapping show'] = """
    type: command
    short-summary: "Gets a mapping."
    examples:
      - name: Mappings_Get
        text: |-
               az fidalgo admin mapping show --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
"""

helps['fidalgo admin mapping create'] = """
    type: command
    short-summary: "Create a mapping."
    examples:
      - name: Mappings_CreateOrUpdate
        text: |-
               az fidalgo admin mapping create --environment-type "Sandbox" --mapped-subscription-id \
"/subscriptions/57a221ae-b5e9-4bea-be0a-e86e5f9317cc" --project-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/\
providers/Microsoft.Fidalgo/projects/{projectName}" --dev-center-name "Contoso" --name "{mappingName}" \
--resource-group "rg1"
"""

helps['fidalgo admin mapping update'] = """
    type: command
    short-summary: "Partially updates a mapping."
    examples:
      - name: Mappings_Update
        text: |-
               az fidalgo admin mapping update --mapped-subscription-id "/subscriptions/57a221ae-b5e9-4bea-be0a-e86e5f9317cc"\
 --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
"""

helps['fidalgo admin mapping delete'] = """
    type: command
    short-summary: "Deletes a mapping."
    examples:
      - name: Mappings_Delete
        text: |-
               az fidalgo admin mapping delete --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
"""

helps['fidalgo admin operation-statuses'] = """
    type: group
    short-summary: Manage operation statuses with fidalgo
"""

helps['fidalgo admin operation-statuses show'] = """
    type: command
    short-summary: "Gets the current status of an async operation."
    examples:
      - name: Get OperationStatus
        text: |-
               az fidalgo admin operation-statuses show --operation-id "{operationId}" --location "{location}"
"""

helps['fidalgo admin sku'] = """
    type: group
    short-summary: Manage sku with fidalgo
"""

helps['fidalgo admin sku list'] = """
    type: command
    short-summary: "Lists the Microsoft.Fidalgo SKUs available in a subscription."
    examples:
      - name: Skus_ListBySubscription
        text: |-
               az fidalgo admin sku list
"""

helps['fidalgo admin pool'] = """
    type: group
    short-summary: Manage pool with fidalgo
"""

helps['fidalgo admin pool list'] = """
    type: command
    short-summary: "Lists pools for a project."
    examples:
      - name: Pools_ListByProject
        text: |-
               az fidalgo admin pool list --project-name "{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin pool show'] = """
    type: command
    short-summary: "Gets a machine pool."
    examples:
      - name: Pools_Get
        text: |-
               az fidalgo admin pool show --name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin pool create'] = """
    type: command
    short-summary: "Create a machine pool."
    parameters:
      - name: --sku
        short-summary: "The SKU for the virtual machine. Defines the type of virtual machines used in the pool."
        long-summary: |
            Usage: --sku name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU.
            tier: This field is required to be implemented by the Resource Provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
    examples:
      - name: Pools_CreateOrUpdate
        text: |-
               az fidalgo admin pool create --location "centralus" --machine-definition-id "/subscriptions/{subscriptionId}/r\
esourceGroups/rg1/providers/Microsoft.Fidalgo/machinedefinitions/{machineDefinitionName}" --network-settings-id \
"/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/networksettings/{networkSettingName}" \
--sku name="medium" --name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin pool update'] = """
    type: command
    short-summary: "Partially updates a machine pool."
    parameters:
      - name: --sku
        short-summary: "The SKU for the virtual machine. Defines the type of virtual machines used in the pool."
        long-summary: |
            Usage: --sku name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU.
            tier: This field is required to be implemented by the Resource Provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
    examples:
      - name: Pools_Update
        text: |-
               az fidalgo admin pool update --machine-definition-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/provi\
ders/Microsoft.Fidalgo/machinedefinitions/{machineDefinitionName}" --name "{poolName}" --project-name "{projectName}" \
--resource-group "rg1"
"""

helps['fidalgo admin pool delete'] = """
    type: command
    short-summary: "Deletes a machine pool."
    examples:
      - name: Pools_Delete
        text: |-
               az fidalgo admin pool delete --name "poolName" --project-name "{projectName}" --resource-group "rg1"
"""

helps['fidalgo admin pool wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the fidalgo pool is met.
    examples:
      - name: Pause executing next line of CLI script until the fidalgo pool is successfully created.
        text: |-
               az fidalgo admin pool wait --name "{poolName}" --project-name "{projectName}" --resource-group "rg1" \
--created
      - name: Pause executing next line of CLI script until the fidalgo pool is successfully updated.
        text: |-
               az fidalgo admin pool wait --name "{poolName}" --project-name "{projectName}" --resource-group "rg1" \
--updated
      - name: Pause executing next line of CLI script until the fidalgo pool is successfully deleted.
        text: |-
               az fidalgo admin pool wait --name "{poolName}" --project-name "{projectName}" --resource-group "rg1" \
--deleted
"""

helps['fidalgo admin machine-definition'] = """
    type: group
    short-summary: Manage machine definition with fidalgo
"""

helps['fidalgo admin machine-definition list'] = """
    type: command
    short-summary: "List Machine Definitions in a resource group And Lists Machine Definitions in a subscription."
    examples:
      - name: MachineDefinitions_ListByResourceGroup
        text: |-
               az fidalgo admin machine-definition list --resource-group "rg1"
      - name: MachineDefinitions_ListBySubscription
        text: |-
               az fidalgo admin machine-definition list
"""

helps['fidalgo admin machine-definition show'] = """
    type: command
    short-summary: "Gets a Machine Definition."
    examples:
      - name: MachineDefinitions_Get
        text: |-
               az fidalgo admin machine-definition show --name "{machineDefinitionName}" --resource-group "rg1"
"""

helps['fidalgo admin machine-definition create'] = """
    type: command
    short-summary: "Create a Machine definition."
    parameters:
      - name: --image-reference
        short-summary: "Image reference information."
        long-summary: |
            Usage: --image-reference id=XX publisher=XX offer=XX sku=XX

            id: Image resource ID.
            publisher: The image publisher.
            offer: The image offer.
            sku: The image sku.
    examples:
      - name: MachineDefinitions_CreateWithCustomImage
        text: |-
               az fidalgo admin machine-definition create --location "centralus" --image-reference \
id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.Compute/images/exampl\
eImage" --name "{machineDefinitionName}" --resource-group "rg1"
"""

helps['fidalgo admin machine-definition update'] = """
    type: command
    short-summary: "Partially updates a Machine definition."
    parameters:
      - name: --image-reference
        short-summary: "Image reference information."
        long-summary: |
            Usage: --image-reference id=XX publisher=XX offer=XX sku=XX

            id: Image resource ID.
            publisher: The image publisher.
            offer: The image offer.
            sku: The image sku.
    examples:
      - name: MachineDefinitions_Patch
        text: |-
               az fidalgo admin machine-definition update --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c5\
8ffff/resourceGroups/Example/providers/Microsoft.Compute/images/image2" --name "{machineDefinitionName}" \
--resource-group "rg1"
"""

helps['fidalgo admin machine-definition delete'] = """
    type: command
    short-summary: "Deletes a Machine definition."
    examples:
      - name: MachineDefinitions_Delete
        text: |-
               az fidalgo admin machine-definition delete --name "{machineDefinitionName}" --resource-group "rg1"
"""

helps['fidalgo admin machine-definition wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the fidalgo machine-definition is met.
    examples:
      - name: Pause executing next line of CLI script until the fidalgo machine-definition is successfully created.
        text: |-
               az fidalgo admin machine-definition wait --name "{machineDefinitionName}" --resource-group "rg1" --created
      - name: Pause executing next line of CLI script until the fidalgo machine-definition is successfully updated.
        text: |-
               az fidalgo admin machine-definition wait --name "{machineDefinitionName}" --resource-group "rg1" --updated
      - name: Pause executing next line of CLI script until the fidalgo machine-definition is successfully deleted.
        text: |-
               az fidalgo admin machine-definition wait --name "{machineDefinitionName}" --resource-group "rg1" --deleted
"""

helps['fidalgo admin network-setting'] = """
    type: group
    short-summary: Manage network setting with fidalgo
"""

helps['fidalgo admin network-setting list'] = """
    type: command
    short-summary: "Lists network settings in a resource group And Lists network settings in a subscription."
    examples:
      - name: NetworkSettings_ListByResourceGroup
        text: |-
               az fidalgo admin network-setting list --resource-group "rg1"
      - name: NetworkSettings_ListBySubscription
        text: |-
               az fidalgo admin network-setting list
"""

helps['fidalgo admin network-setting show'] = """
    type: command
    short-summary: "Gets a network settings resource."
    examples:
      - name: NetworkSettings_Get
        text: |- 
               az fidalgo admin network-setting show --name "{networkSettingName}" --resource-group "rg1"
"""

helps['fidalgo admin network-setting create'] = """
    type: command
    short-summary: "Create a Network Settings resource."
    examples:
      - name: NetworkSettings_CreateOrUpdate
        text: |-
               az fidalgo admin network-setting create --location "centralus" --domain-name "mydomaincontroller.local" \
--domain-password "Password value for user" --domain-username "testuser@mydomaincontroller.local" \
--networking-resource-group-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG" \
--subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG/providers/Microsoft.Network/v\
irtualNetworks/ExampleVNet/subnets/default" --name "{networkSettingName}" --resource-group "rg1"
"""

helps['fidalgo admin network-setting update'] = """
    type: command
    short-summary: "Partially updates Network Settings."
    examples:
      - name: NetworkSettings_Update
        text: |-
               az fidalgo admin network-setting update --domain-password "New Password value for user" --name \
"{networkSettingName}" --resource-group "rg1"
"""

helps['fidalgo admin network-setting delete'] = """
    type: command
    short-summary: "Deletes a Network Settings resource."
    examples:
      - name: NetworkSettings_Delete
        text: |-
               az fidalgo admin network-setting delete --name "{networkSettingName}" --resource-group "rg1"
"""

helps['fidalgo admin network-setting show-health-detail'] = """
    type: command
    short-summary: "Gets health check status details."
    examples:
      - name: NetworkSettings_GetHealthDetails
        text: |-
               az fidalgo admin network-setting show-health-detail --name "{networkSettingName}" --resource-group "rg1"
"""

helps['fidalgo admin network-setting wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the fidalgo network-setting is met.
    examples:
      - name: Pause executing next line of CLI script until the fidalgo network-setting is successfully created.
        text: |-
               az fidalgo admin network-setting wait --name "{networkSettingName}" --resource-group "rg1" --created
      - name: Pause executing next line of CLI script until the fidalgo network-setting is successfully updated.
        text: |-
               az fidalgo admin network-setting wait --name "{networkSettingName}" --resource-group "rg1" --updated
      - name: Pause executing next line of CLI script until the fidalgo network-setting is successfully deleted.
        text: |-
               az fidalgo admin network-setting wait --name "{networkSettingName}" --resource-group "rg1" --deleted
"""

helps['fidalgo admin gallery'] = """
    type: group
    short-summary: Manage gallery with fidalgo
"""

helps['fidalgo admin gallery list'] = """
    type: command
    short-summary: "Lists galleries for a devcenter."
    examples:
      - name: Galleries_ListByDevCenter
        text: |-
               az fidalgo gallery list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin gallery show'] = """
    type: command
    short-summary: "Gets a gallery."
    examples:
      - name: Galleries_Get
        text: |-
               az fidalgo gallery show --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
"""

helps['fidalgo admin gallery create'] = """
    type: command
    short-summary: "Create a gallery."
    examples:
      - name: Galleries_CreateOrUpdate
        text: |-
               az fidalgo gallery create --gallery-resource-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/prov\
iders/Microsoft.Compute/galleries/{galleryName}" --dev-center-name "Contoso" --name "{galleryName}" --resource-group \
"rg1"
"""

helps['fidalgo admin gallery update'] = """
    type: command
    short-summary: "Update a gallery."
"""

helps['fidalgo admin gallery delete'] = """
    type: command
    short-summary: "Deletes a gallery resource."
    examples:
      - name: Galleries_Delete
        text: |-
               az fidalgo gallery delete --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
"""

helps['fidalgo admin gallery wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the fidalgo gallery is met.
    examples:
      - name: Pause executing next line of CLI script until the fidalgo gallery is successfully created.
        text: |-
               az fidalgo gallery wait --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1" \
--created
      - name: Pause executing next line of CLI script until the fidalgo gallery is successfully updated.
        text: |-
               az fidalgo gallery wait --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1" \
--updated
      - name: Pause executing next line of CLI script until the fidalgo gallery is successfully deleted.
        text: |-
               az fidalgo gallery wait --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1" \
--deleted
"""

helps['fidalgo admin image'] = """
    type: group
    short-summary: Manage image with fidalgo
"""

helps['fidalgo admin image list'] = """
    type: command
    short-summary: "Lists images for a gallery. And Lists images for a devcenter."
    examples:
      - name: Images_ListByGallery
        text: |-
               az fidalgo image list --dev-center-name "Contoso" --gallery-name "DevGallery" --resource-group "rg1"
      - name: Images_ListByDevCenter
        text: |-
               az fidalgo image list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['fidalgo admin image show'] = """
    type: command
    short-summary: "Gets a gallery image."
    examples:
      - name: Images_Get
        text: |-
               az fidalgo image show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --name \
"{imageName}" --resource-group "rg1"
"""

helps['fidalgo admin image-version'] = """
    type: group
    short-summary: Manage image version with fidalgo
"""

helps['fidalgo admin image-version list'] = """
    type: command
    short-summary: "Lists versions for an image."
    examples:
      - name: ImageVersions_ListByImage
        text: |-
               az fidalgo image-version list --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" \
--image-name "Win11" --resource-group "rg1"
"""

helps['fidalgo admin image-version show'] = """
    type: command
    short-summary: "Gets an image version."
    examples:
      - name: Versions_Get
        text: |-
               az fidalgo image-version show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" \
--image-name "Win11" --resource-group "rg1" --version-name "{versionName}"
"""