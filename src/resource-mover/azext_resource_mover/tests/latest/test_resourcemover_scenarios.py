# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import tempfile
import json
import time

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure_devtools.scenario_tests import RecordingProcessor


class RoleAssignmentReplacer(RecordingProcessor):

    def process_request(self, request):
        if '/providers/Microsoft.Authorization/roleAssignments/' in request.uri:
            uri_pieces = request.uri.split('/')
            uri_pieces[-1] = '00000000-0000-0000-0000-000000000000'
            request.uri = '/'.join(uri_pieces)
        return request


class ResourceMoverMoveCollectionScenarioTest(ScenarioTest):

    def __init__(self, method_name):
        super(ResourceMoverMoveCollectionScenarioTest, self).__init__(
            method_name,
            recording_processors=[RoleAssignmentReplacer()],
            replay_processors=[RoleAssignmentReplacer()]
        )

    # We don't use the ResourceGroupPrepare here for the reason that
    # move-collection is difficult to delete
    def test_resourcemover_movecollection_basic(self):
        self.kwargs.update({
            'collection_rg': 'clitest_resourcemover_collection_rg',
            'collection_name': 'clitest-movecollection-27',
            'location': 'eastus2',
            'source_region': 'eastus',
            'target_region': 'westus'
        })

        # check basic properties of the move-collection
        basic_checks = [
            self.check('name', '{collection_name}'),
            self.check('location', '{location}'),
            self.check('type', 'Microsoft.Migrate/moveCollections'),
            self.check('properties.sourceRegion', '{source_region}'),
            self.check('properties.targetRegion', '{target_region}')
        ]

        # check creating a move-collection
        self.cmd('az group create -n {collection_rg} -l {location}')
        self.cmd('az resource-mover move-collection create --location {location} --source-region {source_region} '
                 '--target-region {target_region} --name {collection_name} --resource-group {collection_rg}', checks=basic_checks)

        # check updating a move-collection
        self.cmd('az resource-mover move-collection update --name {collection_name} '
                 '--resource-group {collection_rg} --identity type=SystemAssigned', checks=basic_checks + [
                     self.check('identity.type', 'SystemAssigned')])

        # check showing a move-collection
        self.cmd('az resource-mover move-collection show --resource-group {collection_rg} --name {collection_name}',
                 checks=basic_checks)

        # check listing a move-collection by subscription
        # Service has some issues when there are multiple move-collections in a subscription, skip the step here
        # self.cmd('az resource-mover move-collection list',checks=[
        #     self.check('length(@)', 1)
        # ])

        # check deleting a move-collection
        self.cmd('az resource-mover move-collection delete --resource-group {collection_rg} --name {collection_name} --yes')

        # check listing a move-collection by resource group
        self.cmd('az resource-mover move-collection list --resource-group {collection_rg}', checks=[
                 self.check('length(@)', 0)])

        # delete the resource group
        self.cmd('az group delete -n {collection_rg} --yes')

    def test_resourcemover_movecollection_e2e(self):

        self.kwargs.update({
            'collection_rg': 'clitest_resourcemover_collection_rg',
            'collection_name': 'clitest-movecollection-25',
            'location': 'eastus2',
            'source_region': 'eastus',
            'target_region': 'westus',
            'source_vnet': 'vnet-in-source-region',
            'target_vnet': 'vnet-in-target-region',
            'move_resource_vnet': 'vnet-as-move-resource',
            'source_rg': 'clitest_resourcemover_source_rg',
            'target_rg': 'clitest_resourcemover_target_rg',
            'move_resource_rg': 'rg-as-move-resource'
        })

        # create a resource group and a move-collection
        self.cmd('az group create -n {collection_rg} -l {location}')
        move_collection = self.cmd('az resource-mover move-collection create --location {location} --source-region {source_region} '
                                   '--target-region {target_region} --name {collection_name} --resource-group {collection_rg} '
                                   '--identity type=SystemAssigned').get_output_in_json()
        # keep the collection principal id for role assignment
        # keep the subscription ARM id as role assignment scope
        self.kwargs.update({
            'collection_principal_id': move_collection['identity']['principalId'],
            'role_assignment_scope': '/'.join(move_collection['id'].split('/')[1:3])
        })

        # create a resource group and a vNet as the target resource to move
        source_rg_id = self.cmd('az group create -n {source_rg} -l {source_region}').get_output_in_json().get('id', None)
        source_vnet = self.cmd('az network vnet create --resource-group {source_rg} --name {source_vnet} '
                               '--location {source_region}', checks=[
                                   self.check('newVNet.resourceGroup', '{source_rg}'),
                                   self.check('newVNet.type', 'Microsoft.Network/virtualNetworks'),
                                   self.check('newVNet.name', '{source_vnet}'),
                                   self.check('newVNet.location', '{source_region}')]).get_output_in_json()
        # keep the vNet ARM id to add move-resource
        self.kwargs.update({
            'source_vnet_id': source_vnet['newVNet']['id'],
            'source_rg_id': source_rg_id
        })

        # prepare the --resource-settings json file
        vnet_resource_settings = {
            'resourceType': 'Microsoft.Network/virtualNetworks',
            'targetResourceName': self.kwargs.get('target_vnet', None)
        }
        _, vnet_temp_file = tempfile.mkstemp()
        with open(vnet_temp_file, 'w') as f:
            json.dump(vnet_resource_settings, f)

        rg_resource_settings = {
            'resourceType': 'resourceGroups',
            'targetResourceName': self.kwargs.get('target_rg', None)
        }
        _, rg_temp_file = tempfile.mkstemp()
        with open(rg_temp_file, 'w') as f:
            json.dump(rg_resource_settings, f)

        self.kwargs.update({
            'vnet_resource_settings': vnet_temp_file.replace('\\', '\\\\'),
            'rg_resource_settings': rg_temp_file.replace('\\', '\\\\')
        })

        # role assignments for the move-collection
        self.cmd('az role assignment create --assignee-object-id {collection_principal_id} --role Contributor '
                 '--scope {role_assignment_scope}')
        self.cmd('az role assignment create --assignee-object-id {collection_principal_id} --role "User Access Administrator" '
                 '--scope {role_assignment_scope}')

        # add the vNet as a move-resource to the move-collection
        self.cmd('az resource-mover move-resource add --resource-group {collection_rg} --move-collection-name {collection_name} '
                 '--name {move_resource_vnet} --source-id {source_vnet_id} --resource-settings {vnet_resource_settings}')
        self.cmd('az resource-mover move-resource add --resource-group {collection_rg} --move-collection-name {collection_name} '
                 '--name {move_resource_rg} --source-id {source_rg_id} --resource-settings {rg_resource_settings}')

        # list-required-for
        self.cmd('az resource-mover move-collection list-required-for --resource-group {collection_rg} --move-collection-name '
                 '{collection_name} --source-id {source_vnet_id}', checks=[
                     self.check('length(sourceIds)', 0)])

        # list-unresolved-dependency
        self.cmd('az resource-mover move-collection list-unresolved-dependency --resource-group {collection_rg} '
                 '--move-collection-name {collection_name}', checks=[
                     self.check('length(@)', 0)])

        # resolve-dependency
        self.cmd('az resource-mover move-collection resolve-dependency --resource-group {collection_rg} '
                 '--move-collection-name {collection_name}', checks=[
                     self.check('resourceGroup', '{collection_rg}'),
                     self.check('status', 'Succeeded')])

        # list all the move-resources in move-collection
        move_resources = self.cmd('az resource-mover move-resource list --resource-group {collection_rg} '
                                  '--move-collection-name {collection_name}', checks=[
                                      self.check('length(@)', 2)]).get_output_in_json()

        # update move resource id of vNet and the resource group
        for move_resource in move_resources:
            resource_id = move_resource['id']
            if move_resource['properties']['resourceSettings']['resourceType'] == 'resourceGroups':
                self.kwargs.update({
                    'move_resource_rg_id': resource_id
                })
            if move_resource['properties']['resourceSettings']['resourceType'] == 'Microsoft.Network/virtualNetworks':
                self.kwargs.update({
                    'move_resource_vnet_id': resource_id
                })

        def check_move_state(target_state):
            # showing the move-resource in move-collection, chen the move-resource's moveState
            self.cmd('az resource-mover move-resource show --resource-group {collection_rg} '
                     '--move-collection-name {collection_name} --name {move_resource_vnet}', checks=[
                         self.check('name', '{move_resource_vnet}'),
                         self.check('properties.sourceId', '{source_vnet_id}'),
                         self.check('properties.moveStatus.moveState', target_state)])
            self.cmd('az resource-mover move-resource show --resource-group {collection_rg} '
                     '--move-collection-name {collection_name} --name {move_resource_rg}', checks=[
                         self.check('name', '{move_resource_rg}'),
                         self.check('properties.sourceId', '{source_rg_id}'),
                         self.check('properties.moveStatus.moveState', target_state)])

        check_move_state('PreparePending')

        # prepare
        self.cmd('az resource-mover move-collection prepare --move-resources {move_resource_vnet_id} '
                 '{move_resource_rg_id} --name {collection_name} --resource-group {collection_rg}', checks=[
                     self.check('resourceGroup', '{collection_rg}'),
                     self.check('status', 'Succeeded')])
        check_move_state('MovePending')

        # initiate-move
        self.cmd('az resource-mover move-collection initiate-move --move-resources {move_resource_vnet_id} '
                 '{move_resource_rg_id} --name {collection_name} --resource-group {collection_rg}', checks=[
                     self.check('resourceGroup', '{collection_rg}'),
                     self.check('status', 'Succeeded')])
        check_move_state('CommitPending')

        # commit
        self.cmd('az resource-mover move-collection commit --move-resources {move_resource_vnet_id} '
                 '{move_resource_rg_id} --name {collection_name} --resource-group {collection_rg}', checks=[
                     self.check('resourceGroup', '{collection_rg}'),
                     self.check('status', 'Succeeded')])
        check_move_state('DeleteSourcePending')

        # delete the source resources
        self.cmd('az network vnet delete -g {source_rg} -n {source_vnet}')
        self.cmd('az group delete -g {source_rg} --yes')
        time.sleep(60)  # sleep to wait moveState change
        check_move_state('ResourceMoveCompleted')

        # check the move-resources are deployed in target region
        self.cmd('az group show -n {target_rg}', checks=[
            self.check('location', '{target_region}')])
        self.cmd('az network vnet show -g {target_rg} -n {target_vnet}', checks=[
            self.check('location', '{target_region}')])

        # delete the move-resources, the move collection and the resource group
        self.cmd('az resource-mover move-collection bulk-remove --move-resources {move_resource_vnet_id} '
                 '{move_resource_rg_id} --name {collection_name} --resource-group {collection_rg}', checks=[
                     self.check('resourceGroup', '{collection_rg}'),
                     self.check('status', 'Succeeded')])
        self.cmd('az resource-mover move-collection delete --name {collection_name} --resource-group '
                 '{collection_rg} --yes')
        self.cmd('az group delete -n {collection_rg} --yes')


class ResourceMoverMoveResourceScenarioTest(ScenarioTest):

    def __init__(self, method_name):
        super(ResourceMoverMoveResourceScenarioTest, self).__init__(
            method_name,
            recording_processors=[RoleAssignmentReplacer()],
            replay_processors=[RoleAssignmentReplacer()]
        )

    def test_resourcemover_moveresource_basic(self):
        self.kwargs.update({
            'collection_rg': 'clitest_resourcemover_collection_rg',
            'collection_name': 'clitest-movecollection-16',
            'location': 'eastus2',
            'source_region': 'eastus',
            'target_region': 'westus',
            'source_vnet': 'vnet-in-source-region',
            'target_vnet': 'vnet-in-target-region',
            'move_resource_vnet': 'vnet-as-move-resource',
            'source_rg': 'clitest_resourcemover_source_rg',
            'target_rg': 'clitest_resourcemover_target_rg'
        })

        # create a resource group and a move-collection
        self.cmd('az group create -n {collection_rg} -l {location}')
        move_collection = self.cmd('az resource-mover move-collection create --location {location} --source-region {source_region} '
                                   '--target-region {target_region} --name {collection_name} --resource-group {collection_rg} '
                                   '--identity type=SystemAssigned').get_output_in_json()
        # keep the collection principal id for role assignment
        # keep the subscription ARM id as role assignment scope
        self.kwargs.update({
            'collection_principal_id': move_collection['identity']['principalId'],
            'role_assignment_scope': '/'.join(move_collection['id'].split('/')[1:3])})

        # create a resource group and a vNet as the target resource to move
        self.cmd('az group create -n {source_rg} -l {source_region}').get_output_in_json().get('id', None)
        source_vnet = self.cmd('az network vnet create --resource-group {source_rg} --name {source_vnet} '
                               '--location {source_region}', checks=[
                                   self.check('newVNet.resourceGroup', '{source_rg}'),
                                   self.check('newVNet.type', 'Microsoft.Network/virtualNetworks'),
                                   self.check('newVNet.name', '{source_vnet}'),
                                   self.check('newVNet.location', '{source_region}')]).get_output_in_json()
        # keep the vNet ARM id to add move-resource
        self.kwargs.update({
            'source_vnet_id': source_vnet['newVNet']['id']})

        # prepare the --resource-settings json file
        resource_settings = {
            'resourceType': 'Microsoft.Network/virtualNetworks',
            'targetResourceName': self.kwargs.get('target_vnet', None)
        }
        _, temp_file = tempfile.mkstemp()
        with open(temp_file, 'w') as f:
            json.dump(resource_settings, f)
        self.kwargs.update({
            'resource_settings': temp_file.replace('\\', '\\\\'),
        })

        # role assignments for the move-collection
        self.cmd('az role assignment create --assignee-object-id {collection_principal_id} --role Contributor '
                 '--scope {role_assignment_scope}')
        self.cmd('az role assignment create --assignee-object-id {collection_principal_id} --role "User Access Administrator" '
                 '--scope {role_assignment_scope}')

        # add the vNet as a move-resource to the move-collection
        self.cmd('az resource-mover move-resource add --resource-group {collection_rg} --move-collection-name '
                 '{collection_name} --name {move_resource_vnet} --source-id {source_vnet_id} --resource-settings {resource_settings}')

        # list all the move-resources in move-collection
        self.cmd('az resource-mover move-resource list --resource-group {collection_rg} '
                 '--move-collection-name {collection_name}', checks=[
                     self.check('length(@)', 1)])

        # test showing the move-resource in move-collection
        self.cmd('az resource-mover move-resource show --resource-group {collection_rg} --move-collection-name {collection_name} '
                 '--name {move_resource_vnet}', checks=[
                     self.check('name', '{move_resource_vnet}'),
                     self.check('properties.sourceId', '{source_vnet_id}'),
                     self.check('properties.moveStatus.moveState', 'PreparePending')])

        # test deleting the move-resource in the move-collection
        self.cmd('az resource-mover move-resource delete --resource-group {collection_rg} --move-collection-name {collection_name} '
                 '--name {move_resource_vnet} --yes')

        # delete the move-collection and resource group
        self.cmd('az resource-mover move-collection delete --name {collection_name} --resource-group {collection_rg} --yes')
        self.cmd('az group delete -n {collection_rg} --yes')

        # delete the vNet and resource group
        self.cmd('az network vnet delete -g {source_rg} -n {source_vnet}')
        self.cmd('az group delete -n {source_rg} --yes')
