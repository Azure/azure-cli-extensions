# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['fidalgo'] = '''
    type: group
    short-summary: Manage Fidalgo
'''

helps['fidalgo project'] = """
    type: group
    short-summary: Manage project with fidalgo
"""

helps['fidalgo project list'] = """
    type: command
    short-summary: "Lists all projects in a devcenter"
    examples:
      - name: Project_ListByDevCenter
        text: |-
               az fidalgo project list --dev-center "{devCenter}"
"""

helps['fidalgo pool'] = """
    type: group
    short-summary: Manage pool with fidalgo
"""

helps['fidalgo pool list'] = """
    type: command
    short-summary: "Lists available pools."
    examples:
      - name: Pool_List
        text: |-
               az fidalgo pool list --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo pool show'] = """
    type: command
    short-summary: "Gets a machine pool."
    examples:
      - name: Pool_Get
        text: |-
               az fidalgo pool show --name "{poolName}" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo virtual-machine'] = """
    type: group
    short-summary: Manage virtual machine with fidalgo
"""

helps['fidalgo virtual-machine assign'] = """
    type: command
    short-summary: Assigns a Virtual Machine to a different user."
    examples:
      - name: VirtualMachine_Assign
        text: |-
               az fidalgo virtual-machine assign --name "MyDevBox" --new-owner "5862847c-3bba-4720-bd44-982b1da21586" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo virtual-machine create'] = """
    type: command
    short-summary: "Creates or updates a virtual machine."
    examples:
      - name: VirtualMachine_Create
        text: |-
               az fidalgo virtual-machine create --name "MyDevBox" --pool-name "LargeDevWorkStationPool" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo virtual-machine delete'] = """
    type: command
    short-summary: "Deletes a virtual machine."
    examples:
      - name: VirtualMachine_Delete
        text: |-
               az fidalgo virtual-machine delete --name "MyDevBox" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo virtual-machine get-rdp-file-content'] = """
    type: command
    short-summary: "Gets a string that represents the contents of the RDP file for the virtual machine."
    examples:
      - name: VirtualMachine_GetRdpFileContents
        text: |-
               az fidalgo virtual-machine get-rdp-file-content --name "MyDevBox" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo virtual-machine list'] = """
    type: command
    short-summary: "Lists Virtual Machines that the caller has access to in the DevCenter."
    examples:
      - name: VirtualMachine_List
        text: |-
               az fidalgo virtual-machine list --dev-center "{devCenter}"    
      - name: VirtualMachine_ListByUser
        text: |-
               az fidalgo virtual-machine list --dev-center "{devCenter}" --project-name "{projectName}" --user-id "me"       
"""

helps['fidalgo virtual-machine show'] = """
    type: command
    short-summary: "Gets a virtual machine."
    examples:
      - name: VirtualMachine_Get
        text: |-
               az fidalgo virtual-machine show --name "MyDevBox" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo virtual-machine start'] = """
    type: command
    short-summary: "Starts a Virtual Machine."
    examples:
      - name: VirtualMachine_Start
        text: |-
               az fidalgo virtual-machine start --name "MyDevBox" --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo virtual-machine stop'] = """
    type: command
    short-summary: "Stops a Virtual machine."
    examples:
      - name: VirtualMachine_Stop
        text: |-
               az fidalgo virtual-machine stop --name "MyDevBox" --project-name "{projectName}" \
 --dev-center "{devCenter}"
"""

helps['fidalgo catalog-item'] = """
    type: group
    short-summary: Manage catalog item with fidalgo
"""

helps['fidalgo catalog-item list'] = """
    type: command
    short-summary: "Lists all catalog items available for a project."
    examples:
      - name: CatalogItem_ListByProject
        text: |-
               az fidalgo catalog-item list --fidalgo-dns-suffix "fidalgo.azure.net" --project-name "{projectName}" --dev-center "{devCenter}" \
--resource-group "rg1"
"""

helps['fidalgo deployment'] = """
    type: group
    short-summary: Manage deployment with fidalgo
"""

helps['fidalgo deployment list'] = """
    type: command
    short-summary: "Gets an environment's deployment history."
    examples:
      - name: Actions_Get
        text: |-
               az fidalgo deployment list --environment-name "{environmentName}" --project-name "{projectName}" \
--dev-center "{devCenter}" --fidalgo-dns-suffix "fidalgo.azure.net"
"""

helps['fidalgo environment-type'] = """
    type: group
    short-summary: Manage environment type with fidalgo
"""

helps['fidalgo environment-type list'] = """
    type: command
    short-summary: "Lists all environment types configured for a project."
    examples:
      - name: EnvironmentType_ListByProject
        text: |-
               az fidalgo environment-type list --project-name "{projectName}" --dev-center "{devCenter}"
      - name: EnvironmentTypes_ListByDevCenter
        text: |-
               az fidalgo environment-type list --project-name "{projectName}" --dev-center "{devCenter}"
"""

helps['fidalgo environment'] = """
    type: group
    short-summary: Manage environment with fidalgo
"""

helps['fidalgo environment list'] = """
    type: command
    short-summary: "Lists the environments for a project."
    examples:
      - name: Environments_ListByProject
        text: |-
               az fidalgo environment list --project-name "{projectName}" --dev-center "{devCenter}" --fidalgo-dns-suffix "fidalgo.azure.net"
"""

helps['fidalgo environment show'] = """
    type: command
    short-summary: "Gets an environment."
    examples:
      - name: Environments_Get
        text: |-
               az fidalgo environment show --name "{environmentName}" --project-name "{projectName}" \
--dev-center "{devCenter}" --fidalgo-dns-suffix "fidalgo.azure.net"
"""

helps['fidalgo environment create'] = """
    type: command
    short-summary: "Create an environment."
    examples:
      - name: Environments_CreateByCatalogItem
        text: |-
               az fidalgo environment create --dev-center "{devCenter}" --description "Personal Dev Environment" \
--catalog-item-name "helloworld" --deployment-parameters "{\\"app_name\\":\\"mydevApi\\"}" --environment-type \
"DevTest" --tags ProjectType="WebApi" Role="Development" Tech="NetCore" --name "{environmentName}" --project-name \
"{projectName}" --fidalgo-dns-suffix "fidalgo.azure.net"
"""

helps['fidalgo environment update'] = """
    type: command
    short-summary: "Partially updates an environment."
    examples:
      - name: Environments_Update
        text: |-
               az fidalgo environment update --description "Personal Dev Environment 2" --tags ProjectType="WebApi" \
Role="Development" Tech="NetCore" --name "{environmentName}" --project-name "{projectName}" --dev-center "{devCenter}" \
--fidalgo-dns-suffix "fidalgo.azure.net"    
"""

helps['fidalgo environment delete'] = """
    type: command
    short-summary: "Deletes an environment and all it's associated resources."
    examples:
      - name: Environments_Delete
        text: |-
               az fidalgo environment delete --name "{environmentName}" --project-name "{projectName}" \
--dev-center "{devCenter} --fidalgo-dns-suffix "fidalgo.azure.net"
"""

helps['fidalgo environment deploy'] = """
    type: command
    short-summary: "Deploys an environment's resources."
    examples:
      - name: Environments_Deploy
        text: |-
               az fidalgo environment deploy --name "{environmentName}" --project-name "{projectName}" \
--dev-center "{devCenter} --fidalgo-dns-suffix "fidalgo.azure.net"
"""