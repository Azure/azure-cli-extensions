# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from .preparers import CommunicationResourcePreparer
from .recording_processors import BodyReplacerProcessor, URIIdentityReplacer


class CommunicationRoomsScenarios(ScenarioTest):

    def __rooms_create(self, communication_resource_info):
        connection_str = communication_resource_info[1]
        if self.is_live or self.in_recording:
            self.kwargs.update({ 'connection_string': connection_str})
        else:
            os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = connection_str
        
        res = self.cmd('az communication rooms create --rooms --participants{participants_id}').get_output._in_json()
        return res['rooms']
        
    def __get_connectionString_from_resource_info(self, communication_resource_info):
        return communication_resource_info[2]
       
    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_communication_rooms_create(self, communication_resource_info):
        
        room = self.cmd('az communication rooms create').get_output_in_json()
        
        id = room['id']
        participants = room['participants']
        roomJoinPolicy = room['roomJoinPolicy']
        
        assert len(id) > 8
        assert len (participants) == 0
        assert roomJoinPolicy == 'InviteOnly'

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def  test_communication_rooms_create_bad_join_policy(self, communication_resource_info):
        
        # add invalid join policy to the rooms
        self.kwargs.update({
            'join_policy': 'azure12345'})
 
        with self.assertRaises(Exception) as raises:
            self.cmd('az communication rooms create --join-policy {join_policy}', checks = [
                self.check('CommunicationError.code', 'Bad Request')])
        
    
    