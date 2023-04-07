# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.core.exceptions import HttpResponseError
from .preparers import CommunicationResourcePreparer
from .recording_processors import URIIdentityReplacer, BodyReplacerProcessor

class CommunicationRoomsScenarios(ScenarioTest):

    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[
            URIIdentityReplacer(),
            BodyReplacerProcessor(keys=["id", "rawId"])
        ])


    def __create_user(self, communication_resource_info):
        connection_str = communication_resource_info[1]
        if self.is_live or self.in_recording:
            self.kwargs.update({ 'connection_string':  connection_str})
        else:
            os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = connection_str

        res = self.cmd('az communication identity user create').get_output_in_json()

        return res['properties']['id']


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        room = self.cmd('az communication rooms create').get_output_in_json()
        
        id = room['id']
        participants = room['participants']
        roomJoinPolicy = room['roomJoinPolicy']
        
        assert len(id) > 0
        assert len (participants) == 0
        assert roomJoinPolicy == 'InviteOnly'


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_bad_join_policy(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # add invalid join policy to the rooms
        self.kwargs.update({
            'join_policy': 'azure12345'})
 
        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms create --join-policy {join_policy}')

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        
        res = raises.exception.model.additional_properties
        assert res['status'] == 400
        assert res['traceId'] is not None
        assert 'validation errors' in str(res['title'])
        

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_delete(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
       
        # create a room and delete it with room id
        room = self.cmd('az communication rooms create').get_output_in_json()
        self.kwargs.update({
            'room_id': room['id']})
        
        self.cmd('az communication rooms delete --room {room_id} --yes')
        

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_delete_with_id_with_invalid_length(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
       
        # delete valid room with invalid room id
        self.kwargs.update({
            'room_id': 'f-1234567890'})
        
        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms delete --room {room_id} --yes')  

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        
        err = raises.exception.model.error
        assert err.code == 'InvalidInput'
        assert 'Invalid Room ID length' in err.message
        

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_delete_with_invalid_id(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
       
        # delete valid room with invalid room id
        self.kwargs.update({
            'room_id': 'f-123456789012345'})
        
        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms delete --room {room_id} --yes')  

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        
        err = raises.exception.model.error
        assert err.code == 'InvalidInput'
        assert 'Room ID is invalid' in err.message
        

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_get(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
       
        # create a room first
        room = self.cmd('az communication rooms create').get_output_in_json()
        self.kwargs.update({
            'room_id': room['id']})

        get_room = self.cmd('az communication rooms get --room {room_id}').get_output_in_json() 

        assert room['id'] == get_room['id']
    

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_join_policy(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        
        # create a room first, it should be in the future so we can update the policy 
        room = self.cmd('az communication rooms create --valid-from 2023-04-01T13:35').get_output_in_json()
        
        self.kwargs.update({
            'room_id': room['id'],
            'join_policy': 'CommunicationServiceUsers'})

        # update the room join policy
        updated_room = self.cmd('az communication rooms update --room {room_id} --join-policy {join_policy}').get_output_in_json()
        
        assert room['id'] == updated_room['id']
        assert room['roomJoinPolicy'] == "InviteOnly"
        assert updated_room['roomJoinPolicy'] == "CommunicationServiceUsers"


    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_join_policy_after_start(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        
        # create a room first 
        room = self.cmd('az communication rooms create').get_output_in_json()
        self.kwargs.update({
            'room_id': room['id'],
            'join_policy': 'CommunicationServiceUsers'})

        # update the room join policy
        with self.assertRaises(Exception) as raises:
            self.cmd('az communication rooms update --room {room_id} --join-policy {join_policy}')

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        
        err = raises.exception.model.error
        assert err.code == 'InvalidInput'
        assert 'Room join policy cannot be updated after room start time has elapsed' in err.message
        

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_valid_elapsed_time(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        
        # create a room first
        room = self.cmd('az communication rooms create').get_output_in_json()

        # update the room with valid elapsed time (to do: joanna_jiang updates the validation time range in every 180 dyas) 
        validFrom = '2023-01-24T23:09:10.357939+00:00'
        validUntil = '2023-06-25T13:09:10.357939+00:00'
        
        self.kwargs.update({
            'room_id': room['id'],
            'validFrom': validFrom,
            'validUntil': validUntil})
        
        updated_room = self.cmd('az communication rooms update --room {room_id} --valid-from {validFrom} --valid-until {validUntil}').get_output_in_json()

        assert room['id'] == updated_room['id']
        assert room['validFrom'] != updated_room['validFrom']
        assert room['validUntil'] != updated_room['validUntil']
        

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_invalid_elapsed_time(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        
        # create a room first
        room = self.cmd('az communication rooms create').get_output_in_json()
       
        # update the room with invalid elapsed time 
        validFrom = '2022-11-22T19:14:59.829926+00:00'
        validUntil = '2022-11-23'
        
        self.kwargs.update({
            'room_id': room['id'],
            'validFrom': validFrom,
            'validUntil': validUntil})

        with self.assertRaises(SystemExit) as raises:
            self.cmd('az communication rooms update --room {room_id} --valid-from {validFrom} --valid-until {validUntil}')

        assert 'is not a valid ISO-8601 datetime' in str(raises.exception)


    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_attendee_participant(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
   
        # create a new room and a new participant
        room = self.cmd('az communication rooms create').get_output_in_json()
        attendee_participants_id = self.__create_user(communication_resource_info)
        
        # update the room with newly created attendee participant
        self.kwargs.update({
            'room_id': room['id'],
            'attendee_participants_id': attendee_participants_id})
        self.cmd('az communication rooms update --room {room_id} --attendee-participants {attendee_participants_id}')

        updated_room = self.cmd('az communication rooms get --room {room_id}').get_output_in_json()
        participants = updated_room['participants']

        # verify the participants role and the number of participants 
        assert len(participants) == 1
        assert participants[0]['role'] == 'Attendee'
       

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_get_default_participants(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room 
        room = self.cmd('az communication rooms create').get_output_in_json()

        # get the default null participant from the newly created room 
        self.kwargs.update({
            'room_id': room['id']})
        self.cmd('az communication rooms participant get --room {room_id}')
        get_participant = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()
        participants = get_participant['participants']

        # verify the defualt participants is null 
        assert len(participants) == 0

       
    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_add_valid_presenter_participant(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room 
        room = self.cmd('az communication rooms create').get_output_in_json()

        # create a valid participant
        participant_id = self.__create_user(communication_resource_info)

        # add valid participant into the created room
        self.kwargs.update({
            'room_id': room['id'],
            'participants_id': participant_id})
        self.cmd('az communication rooms participant add --presenter-participants {participants_id} --room {room_id}')
        
        get_participant = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()
        
        assert len(get_participant['participants']) == 1
        role = get_participant['participants'][0]['role']

        # verify the type of added participant
        assert role == 'Presenter'

    
    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_add_invalid_consumer_participant(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room
        room = self.cmd('az communication rooms create').get_output_in_json()

        # create a invalid participant 
        participant_id = '8:acs:123456c'

        # add invalid participant into the created room
        self.kwargs.update({
            'room_id': room['id'],
            'participants_id': participant_id})
        
        with self.assertRaises(Exception) as raises:
            self.cmd('az communication rooms participant add --consumer-participants {participants_id} --room {room_id}')

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        
        err = raises.exception.model.error
        assert err.code == 'InvalidInput'
        assert 'Identifier format is invalid' in err.message


    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_participant_with_same_participant_id(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room 
        room = self.cmd('az communication rooms create').get_output_in_json()

        # create a valid participant
        participant_id = self.__create_user(communication_resource_info)

        # add valid participant into the created room 
        self.kwargs.update({
            'room_id': room['id'],
            'participants_id': participant_id})
     
        # update the type of participants from presenter to attendee with the same participant id 
        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms participant update --presenter-participants {participants_id} --attendee-participants {participants_id} --room {room_id}')

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        
        res = raises.exception.model.additional_properties
        assert res['status'] == 400
        assert res['traceId'] is not None
        assert 'validation errors' in str(res['title'])
        assert len(res['errors']['Participants']) == 1
        assert 'duplicate participant' in str(res['errors']['Participants'])


    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_multiple_participants(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room 
        room = self.cmd('az communication rooms create').get_output_in_json()

        # create valid participants
        presenter_id = self.__create_user(communication_resource_info)
        consumer_id = self.__create_user(communication_resource_info)

        # add participants into created room 
        self.kwargs.update({
            'room_id': room['id'],
            'presenter_id': presenter_id, 
            'consumer_id': consumer_id})
        
        self.cmd('az communication rooms participant add --presenter-participants {presenter_id} --consumer-participants {consumer_id} --room {room_id}')
        
        # get updated room properties
        updated_room = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()

        # verify the length of participant
        participants = updated_room['participants']
        assert len(participants) == 2 
        
        presenter_role = participants[0]['role']
        consumer_role = participants[1]['role']

        # verify the type of participants
        assert presenter_role == 'Presenter'
        assert consumer_role == 'Consumer'

    
    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_delete_participants(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room
        room = self.cmd('az communication rooms create').get_output_in_json()

        # create a valid participants
        participant_id = self.__create_user(communication_resource_info)

        # add the participant into created room 
        self.kwargs.update({
            'room_id': room['id'],
            'participant_id': participant_id})
        self.cmd('az communication rooms participant add --consumer-participants {participant_id} --room {room_id}')
       
        # remove the participant from the created room 
        self.cmd('az communication rooms participant remove --participants {participant_id} --room {room_id} --yes')
        get_participant = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()
        participant = get_participant['participants']

        # verify the participant list is empty
        assert len(participant) == 0 

