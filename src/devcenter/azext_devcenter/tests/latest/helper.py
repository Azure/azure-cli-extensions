# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# --------------------------------------------------------------------------
def create_dev_center(self):
    dev_center = self.cmd('az devcenter admin devcenter create '
                          '--location "{location}" '
                          '--tags CostCode="12345" '
                          '--name "{devcenterName}" '
                          '--resource-group "{rg}"').get_output_in_json()

    self.kwargs.update({
        'devCenterId': dev_center['id'],
    })


def create_identity(self):
    return self.cmd('az identity create '
                    '--resource-group {rg} '
                    '--name {identityName}').get_output_in_json()


def create_dev_center_with_identity(self):
    self.kwargs.update({
        'devcenterName': self.create_random_name(prefix='cli', length=24),
        'identityName': self.create_random_name(prefix='testid_', length=24)
    })

    test_identity = create_identity(self)

    self.kwargs.update({
        'userAssignedIdentity': test_identity['id'],
        'identityPrincipalId': test_identity['principalId']
    })

    dev_center = self.cmd('az devcenter admin devcenter create '
                          '--identity-type "UserAssigned" '
                          '--user-assigned-identities "{{\\"{userAssignedIdentity}\\":{{}}}}" '
                          '--location "{location}" '
                          '--tags CostCode="12345" '
                          '--name "{devcenterName}" '
                          '--resource-group "{rg}"').get_output_in_json()

    self.kwargs.update({
        'devCenterId': dev_center['id']
    })


def create_virtual_network_with_subnet(self):
    self.kwargs.update({
        'vNetName': self.create_random_name(prefix='cli', length=24),
        'subnetName': self.create_random_name(prefix='cli', length=24),
        'nsgName': self.create_random_name(prefix='cli', length=12),
    })

    self.cmd(
        'az network vnet create -n "{vNetName}" --location "{location}" -g "{rg}"')
    
    self.cmd(
        'az network nsg create -n "{nsgName}" --location "{location}" -g "{rg}"')

    return self.cmd('az network vnet subnet create --nsg "{nsgName}" -n "{subnetName}" --vnet-name "{vNetName}" -g "{rg}" --address-prefixes "10.0.0.0/21"').get_output_in_json()


def create_sig(self):
    self.kwargs.update({
        'sigName': self.create_random_name(prefix='cli', length=24),
        'imageDefName': self.create_random_name(prefix='cli', length=12),
        'computeVmName': self.create_random_name(prefix='cli', length=12),
        'computeVmPassword': 'Cli!123123fakepassword',
        'computeUserName': self.create_random_name(prefix='cli', length=12),
        'publisher': "MicrosoftWindowsDesktop",
        'offer': "Windows-10",
        'sku': "win10-21h2-entn-g2",
        'imageVersion': "1.0.0",
        'nsgName': self.create_random_name(prefix='cli', length=12),
    })

    sig = self.cmd(
        'az sig create -r "{sigName}" --location "{location}" -g "{rg}"').get_output_in_json()

    self.cmd('az sig image-definition create -i "{imageDefName}" -p "{publisher}" '
             '-g "{rg}" -f "{offer}" -s "{sku}" --location "{location}" '
             '--os-type "Windows" -r "{sigName}" --hyper-v-generation "V2" --features SecurityType=TrustedLaunch')

    self.kwargs.update({
        'sigId': sig['id']
    })

    create_virtual_network_with_subnet(self);

    # Create compute virtual machine
    self.cmd('az vm create -n "{computeVmName}" '
             '-g "{rg}" '
             '--image "MicrosoftWindowsDesktop:Windows-10:win10-21h2-entn-g2:19044.2486.230107" '
             '--location "{location}" '
             '--security-type TrustedLaunch '
             '--admin-password "{computeVmPassword}" '
             '--vnet-name "{vNetName}" '
             '--subnet "{subnetName}" '
             '--admin-username "{computeUserName}"')

    compute_vm = self.cmd('az vm show -n "{computeVmName}" '
                          '-g "{rg}" ').get_output_in_json()

    self.kwargs.update({
        'diskId': compute_vm['storageProfile']['osDisk']['managedDisk']['id'],
    })

    self.cmd('az sig image-version create '
             '-g "{rg}" '
             '--gallery-name "{sigName}" '
             '--gallery-image-definition "{imageDefName}" '
             '--location "{location}" '
             '--gallery-image-version {imageVersion} '
             '--os-snapshot "{diskId}" ')


def create_sig_role_assignments(self):
    self.kwargs.update({
        'windows365ObjectId': '8eec7c09-06ae-48e9-aafd-9fb31a5d5175'
    })

    self.cmd('az role assignment create --role "Contributor" '
             '--assignee "{identityPrincipalId}" '
             '--scope "{sigId}"')

    self.cmd('az role assignment create --role "Reader" '
             '--assignee "{windows365ObjectId}" '
             '--scope "{sigId}"')


def create_kv_policy(self):
    if (self.is_live):
        self.cmd('az keyvault set-policy -n "dummy" '
                '--secret-permissions get list '
                '--object-id "{identityPrincipalId}"')


def create_project(self):
    self.kwargs.update({
        'projectName': self.create_random_name(prefix='cli', length=24)
    })

    self.cmd('az devcenter admin project create '
             '--location "{location}" '
             '--name "{projectName}" '
             '--dev-center-id "{devCenterId}" '
             '--resource-group "{rg}"')


def create_network_connection(self):
    subnet = create_virtual_network_with_subnet(self)

    self.kwargs.update({
        'subnetId': subnet['id'],
        'networkConnectionName': self.create_random_name(prefix='cli', length=24),
        'networkingRgName1': self.create_random_name(prefix='cli', length=24),
    })

    network_connection = self.cmd('az devcenter admin network-connection create '
                                  '--location "{location}" '
                                  '--tags CostCode="12345" '
                                  '--name "{networkConnectionName}" '
                                  '--domain-join-type "AzureADJoin" '
                                  '--subnet-id "{subnetId}" '
                                  '--networking-resource-group-name "{networkingRgName1}" '
                                  '--resource-group "{rg}"').get_output_in_json()

    self.kwargs.update({
        'networkConnectionId': network_connection['id'],
    })

def create_network_connection_dp(self):
    subnet = create_virtual_network_with_subnet_dp(self)

    self.kwargs.update({
        'subnetId': subnet['id'],
        'networkConnectionName': self.create_random_name(prefix='cli', length=24),
        'networkingRgName1': self.create_random_name(prefix='cli', length=24),
    })

    network_connection = self.cmd('az devcenter admin network-connection create '
                                  '--location "{location}" '
                                  '--tags CostCode="12345" '
                                  '--name "{networkConnectionName}" '
                                  '--domain-join-type "AzureADJoin" '
                                  '--subnet-id "{subnetId}" '
                                  '--networking-resource-group-name "{networkingRgName1}" '
                                  '--resource-group "{rg}"').get_output_in_json()

    self.kwargs.update({
        'networkConnectionId': network_connection['id'],
    })

def create_virtual_network_with_subnet_dp(self):
    self.kwargs.update({
        'vNetName': self.create_random_name(prefix='cli', length=24),
        'subnetName': self.create_random_name(prefix='cli', length=24)
    })

    self.cmd(
        'az network vnet create -n "{vNetName}" --location "{location}" -g "{rg}"')

    return self.cmd('az network vnet subnet create -n "{subnetName}" --vnet-name "{vNetName}" -g "{rg}" --address-prefixes "10.0.0.0/21"').get_output_in_json()


def create_attached_network_dev_box_definition(self):
    self.kwargs.update({
        'devcenterName': self.create_random_name(prefix='cli', length=24),
    })

    create_dev_center(self)
    create_project(self)
    create_network_connection(self)
    self.kwargs.update({
        'imageRefId': "/subscriptions/{subscriptionId}/resourceGroups/{rg}/providers/Microsoft.DevCenter/devcenters/{devcenterName}/galleries/default/images/microsoftwindowsdesktop_windows-ent-cpc_win11-22h2-ent-cpc-os",
        'devBoxDefinitionName': self.create_random_name(prefix='c1', length=12),
        'osStorageType': "ssd_1024gb",
        'skuName': "general_a_8c32gb_v1",
        'attachedNetworkName': self.create_random_name(prefix='c2', length=12),
        'devBoxDefinitionName2': self.create_random_name(prefix='c2', length=12)
    })

    self.cmd('az devcenter admin attached-network create '
             '--dev-center "{devcenterName}" '
             '--name "{attachedNetworkName}" '
             '--network-connection-id "{networkConnectionId}" '
             '--resource-group "{rg}" '
             )

    self.cmd('az devcenter admin devbox-definition create '
             '--dev-center "{devcenterName}" '
             '--name "{devBoxDefinitionName}" '
             '--image-reference id="{imageRefId}" '
             '--resource-group "{rg}" '
             '--os-storage-type "{osStorageType}" '
             '--sku name="{skuName}" '
             '--location "{location}" '
             )

    self.cmd('az devcenter admin devbox-definition create '
             '--dev-center "{devcenterName}" '
             '--name "{devBoxDefinitionName2}" '
             '--image-reference id="{imageRefId}" '
             '--resource-group "{rg}" '
             '--os-storage-type "{osStorageType}" '
             '--sku name="{skuName}" '
             '--location "{location}" '
             )


def create_env_type(self):
    self.kwargs.update({
        'envTypeName': self.create_random_name(prefix='c', length=24),
        'tagVal1': 'val1',
        'tagKey1': "key1",
    })

    self.cmd('az devcenter admin environment-type create '
             '--dev-center "{devcenterName}" '
             '--resource-group "{rg}" '
             '--name "{envTypeName}" '
             '--tags {tagVal1}="{tagKey1}" ',
             checks=[
                 self.check('name', "{envTypeName}"),
                 self.check('resourceGroup', "{rg}"),
                 self.check('tags.val1', "{tagKey1}"),
             ]
             )


def add_dev_box_user_role_to_project(self):
    project = self.cmd('az devcenter admin project show '
                       '--name "{projectName}" '
                       '--resource-group "{rg}"').get_output_in_json()

    self.kwargs.update({
        'projectId': project['id']
    })

    if (self.is_live):
        user = self.cmd('az ad signed-in-user show').get_output_in_json()
        self.kwargs.update({
            'userId': user['id'],
        })

        self.cmd('az role assignment create --role "DevCenter Dev Box User" '
                 '--assignee "{userId}" '
                 '--scope "{projectId}"')

def create_pool(self):
    self.cmd('az devcenter admin attached-network create '
             '--dev-center "{devcenterName}" '
             '--name "{attachedNetworkName}" '
             '--network-connection-id "{networkConnectionId}" '
             '--resource-group "{rg}" '
             )

    self.cmd('az devcenter admin devbox-definition create '
             '--dev-center "{devcenterName}" '
             '--name "{devBoxDefinitionName}" '
             '--image-reference id="{imageRefId}" '
             '--hibernate-support "Enabled" '
             '--resource-group "{rg}" '
             '--os-storage-type "{osStorageType}" '
             '--sku name="{skuName}" '
             '--location "{location}" '
             )
    
    self.kwargs.update({
            'poolName': self.create_random_name(prefix='c3', length=12)
        })

    self.cmd('az devcenter admin pool create '
                 '-d "{devBoxDefinitionName}" '
                 '--location "{location}" '
                 '--local-administrator "Enabled" '
                 '--name "{poolName}" '
                 '-c "{attachedNetworkName}" '
                 '--project-name "{projectName}" '
                 '--resource-group "{rg}" '
                 )

    self.cmd('az devcenter admin schedule create '
                 '--pool-name "{poolName}" '
                 '--project-name "{projectName}" '
                 '--resource-group "{rg}" '
                 '--time "{time}" '
                 '--time-zone "{timeZone}" '
                 )    

def create_pool_dataplane_dependencies(self):
    
    create_network_connection_dp(self)

    self.kwargs.update({
        'imageRefId': "/subscriptions/{subscriptionId}/resourceGroups/{rg}/providers/Microsoft.DevCenter/devcenters/{devcenterName}/galleries/default/images/microsoftwindowsdesktop_windows-ent-cpc_win11-21h2-ent-cpc-m365",
        'devBoxDefinitionName': self.create_random_name(prefix='c1', length=12),
        'osStorageType': "ssd_1024gb",
        'skuName': "general_a_8c32gb_v1",
        'attachedNetworkName': self.create_random_name(prefix='c2', length=12),
        'time': "13:00",
        'timeZone': "America/Los_Angeles"
    })

    create_pool(self)

def add_deployment_env_user_role_to_project(self):
    project = self.cmd('az devcenter admin project show '
                       '--name "{projectName}" '
                       '--resource-group "{rg}"').get_output_in_json()

    self.kwargs.update({
        'projectId': project['id']
    })

    if (self.is_live):
        user = self.cmd('az ad signed-in-user show').get_output_in_json()
        self.kwargs.update({
            'userId': user['id'],
        })

        self.cmd('az role assignment create --role "/subscriptions/{subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/18e40d4e-8d2e-438d-97e1-9528336e149c" '
                 '--assignee "{userId}" '
                 '--scope "{projectId}"')

def catalog_create_and_sync_cmds(self):
    self.kwargs.update({
        'catalogName': self.create_random_name(prefix='c2', length=12),
        'branch': 'main',
        'path': "/Catalog_v2",
        'secretIdentifier': "https://dummy.fake.net/secrets/dummy/0000000000000000000000000000000",
        'uri': "https://domain.com/dummy/dummy.git"
    })

    self.cmd('az devcenter admin catalog create '
                '--dev-center "{devcenterName}" '
                '--name "{catalogName}" '
                '--git-hub path="{path}" branch="{branch}" '
                'secret-identifier="{secretIdentifier}" uri="{uri}" '
                '--resource-group "{rg}" '
                )
    
    self.cmd('az devcenter admin catalog sync '
            '--dev-center "{devcenterName}" '
            '--name "{catalogName}" '
            '--resource-group "{rg}" '
            )

def create_catalog(self):
    create_dev_center_with_identity(self)
    create_kv_policy(self)
    create_project(self)
    add_deployment_env_user_role_to_project(self)
    catalog_create_and_sync_cmds(self)

    tenantId = self.cmd('az account show').get_output_in_json()['tenantId']
    catalogItemId = f"{tenantId}:{self.kwargs.get('devcenterName', '')}:{self.kwargs.get('catalogName', '')}:empty"
    self.kwargs.update({
            'catalogItemId': catalogItemId,
        })

def create_proj_env_type(self):
    self.kwargs.update({
        'ownerRole': "8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
    })

    create_dev_center_with_identities(self)
    create_project(self)
    add_deployment_env_user_role_to_project(self)
    create_env_type(self)

    self.cmd('az devcenter admin project-environment-type create '
                '--project "{projectName}" '
                '--environment-type-name "{envTypeName}" '
                '--deployment-target-id "/subscriptions/{subscriptionId}" '
                '--status "Enabled" '
                '--identity-type "SystemAssigned, UserAssigned" '
                '--user-assigned-identities "{{\\"{userAssignedIdentity}\\":{{}}}}" '
                '--user-role-assignments "{{\\"{identityPrincipalId}\\":{{\\"roles\\":{{\\"{ownerRole}\\":{{}}}}}}}}" '
                '--location "{location}" '
                '--roles "{{\\"{ownerRole}\\":{{}}}}" '
                '--resource-group "{rg}"'
                )

def add_role_to_subscription(self):
    if (self.is_live):
        self.cmd('az role assignment create --role "Owner" '
                 '--assignee "{identityPrincipalId}" '
                 '--scope "/subscriptions/{subscriptionId}"')


def create_dev_center_with_identities(self):
    self.kwargs.update({
        'devcenterName': self.create_random_name(prefix='cli', length=24),
        'identityName': self.create_random_name(prefix='testid_', length=24)
    })

    test_identity = create_identity(self)

    self.kwargs.update({
        'userAssignedIdentity': test_identity['id'],
        'identityPrincipalId': test_identity['principalId']
    })

    dev_center = self.cmd('az devcenter admin devcenter create '
                          '--identity-type "SystemAssigned, UserAssigned" '
                          '--user-assigned-identities "{{\\"{userAssignedIdentity}\\":{{}}}}" '
                          '--location "{location}" '
                          '--tags CostCode="12345" '
                          '--name "{devcenterName}" '
                          '--resource-group "{rg}"').get_output_in_json()

    self.kwargs.update({
        'devCenterId': dev_center['id']
    })


def create_environment_dependencies(self):
    create_proj_env_type(self)
    add_role_to_subscription(self)
    create_kv_policy(self)
    catalog_create_and_sync_cmds(self)

def create_dev_box_dependencies(self):
    self.kwargs.update({
        'devcenterName': self.create_random_name(prefix='cli', length=24),
    })

    create_dev_center(self)
    create_project(self)
    add_dev_box_user_role_to_project(self)
    create_network_connection_dp(self)

    self.kwargs.update({
        'imageRefId': "/subscriptions/{subscriptionId}/resourceGroups/{rg}/providers/Microsoft.DevCenter/devcenters/{devcenterName}/galleries/default/images/microsoftwindowsdesktop_windows-ent-cpc_win11-22h2-ent-cpc-os",
        'devBoxDefinitionName': self.create_random_name(prefix='c1', length=12),
        'osStorageType': "ssd_1024gb",
        'skuName': "general_a_8c32gb_v1",
        'attachedNetworkName': self.create_random_name(prefix='c2', length=12),
        'time': "18:30",
        'timeZone': "America/Los_Angeles"
    })

    create_pool(self)

