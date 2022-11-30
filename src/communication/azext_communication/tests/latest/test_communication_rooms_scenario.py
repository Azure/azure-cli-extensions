# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from .preparers import CommunicationResourcePreparer
from .recording_processors import URIIdentityReplacer, BodyReplacerProcessor

class CommunicationRoomsScenarios(ScenarioTest):

    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[
            URIIdentityReplacer(),
            BodyReplacerProcessor(keys=["id"])
        ])


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        room = self.cmd('az communication rooms create').get_output_in_json()
        
        id = room['id']
        participants = room['participants']
        roomJoinPolicy = room['roomJoinPolicy']
        
        assert len(id) > 8
        assert len (participants) == 0
        assert roomJoinPolicy == 'InviteOnly'


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_bad_join_policy(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # add invalid join policy to the rooms
        self.kwargs.update({
            'join_policy': 'azure12345'})
 
        with self.assertRaises(Exception):
            self.cmd('az communication rooms create --join-policy {join_policy}', checks = [
                self.check('CommunicationError.code', 'Bad Request')])
        

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_delete(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
       
        # create a room and delete it with room id
        room = self.cmd('az communication rooms create').get_output_in_json()
        self.kwargs.update({
            'room_id': room['id']})
        
        self.cmd('az communication rooms delete --room {room_id}')
        

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_delete_with_invalid_id(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        from azure.core.exceptions import HttpResponseError
       
        # delete valid room with invalid room id
        self.kwargs.update({
            'room_id': '12345678'})
        
        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms delete --room {room_id}', checks = [
                self.check('httpStatusCode', '400')])  

        assert 'Invalid Room ID length' in str(raises.exception)
        

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_get(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
       
        # create a room first
        room = self.cmd('az communication rooms create').get_output_in_json()
        self.kwargs.update({
            'room_id': room['id']})

        self.cmd('az communication rooms get --room {room_id}') 
    

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_join_policy(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        
        # create a room first 
        room = self.cmd('az communication rooms create').get_output_in_json()
        self.kwargs.update({
            'room_id': room['id'],
            'join_policy': 'CommunicationServiceUsers'})

        # update the room join policy
        with self.assertRaises(Exception):
            self.cmd('az communication rooms update --room {room_id}', checks = [
                self.check('InvalidInput', 'Room join policy cannot be updated after room start time has elapsed')])
        

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_valid_elapsed_time(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        
        # create a room first
        room = self.cmd('az communication rooms create').get_output_in_json()

        # update the room with valid elapsed time (to do: joanna_jiang updates the validation time range in every 180 dyas) 
        validFrom = '2022-11-24T23:09:10.357939+00:00'
        validUntil = '2022-11-25T23:09:10.357939+00:00'
        
        self.kwargs.update({
            'room_id': room['id'],
            'validFrom': validFrom,
            'validUntil': validUntil})
        self.cmd('az communication rooms update --room {room_id} --valid-from {validFrom} --valid-until {validUntil}')
        

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

        with self.assertRaises(Exception):
            self.cmd('az communication rooms update --room {room_id} --valid-from {validFrom} --valid-until {validUntil}',checks = [
                self.check('Invalid Elaspsed Time', '2022-11-23 is not a valid ISO-8601 datetime')])


    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_attendee_participant(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
   
        # create a new room and a new participant
        room = self.cmd('az communication rooms create').get_output_in_json()
        participant = self.cmd('az communication identity user create').get_output_in_json()
        attendee_participants_id = participant['properties']['id']
        
        # update the room with newly created attendee participant
        self.kwargs.update({
            'room_id': room['id'],
            'attendee_participants_id': attendee_participants_id,
            'attendee_participants_role':'Attendee'})
        self.cmd('az communication rooms update --room {room_id} --attendee-participants {attendee_participants_id}')
        room_after_update = self.cmd('az communication rooms get --room {room_id}').get_output_in_json()
        attendee_participant = room_after_update['participants']
        attendee_participant_role = attendee_participant[0]['role']

        # verify the participants role and the number of participants 
        assert len (attendee_participant) == 1
        assert attendee_participant_role == 'Attendee'
       

    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_get_default_participant(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room 
        room = self.cmd('az communication rooms create').get_output_in_json()

        # get the default null participant from the newly created room 
        self.kwargs.update({
            'room_id': room['id']})
        self.cmd('az communication rooms participant get --room {room_id}')
        get_participant = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()
        participant = get_participant['participants']

        # verify the defualt participants is null 
        assert len(participant) == 0

       
    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_add_valid_presenter_participant(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room 
        room = self.cmd('az communication rooms create').get_output_in_json()

        # create a valid participant
        participant = self.cmd('az communication identity user create').get_output_in_json()
        presenter_participants_id = participant['properties']['id']

        # add valid participant into the created room
        self.kwargs.update({
            'room_id': room['id'],
            'participants_id': presenter_participants_id})
        self.cmd('az communication rooms participant add --presenter-participants {participants_id} --room {room_id}')
        get_participant = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()
        presenter_participants = get_participant['participants'][0]['role']

        # verify the type of added participant
        assert presenter_participants == 'Presenter'

    
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
        
        with self.assertRaises(Exception):
            self.cmd('az communication rooms participant add --consumer-participants {participants_id} --room {room_id}',checks = [
                self.check('Identifier format is invalid')])


    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_participant_with_same_participant_id(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room 
        room = self.cmd('az communication rooms create').get_output_in_json()

        # create a valid participant
        participant = self.cmd('az communication identity user create').get_output_in_json()
        participant_id = participant['properties']['id']

        # add valid participant into the created room 
        self.kwargs.update({
            'room id': room['id'],
            'participants_id': participant_id})
     
        # update the type of participants from presenter to attendee with the same participant id 
        with self.assertRaises(Exception):
            self.cmd('az communication rooms paritcipant update --presenter-participants {participants_id} --attendee-participants {participants_id} --room {room_id}',checks = [
                self.check('Bad Request')])


    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_multiple_participants(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room 
        room = self.cmd('az communication rooms create').get_output_in_json()

        # create valid participants
        first_participant = self.cmd('az communication identity user create').get_output_in_json()
        second_participant = self.cmd('az communication identity user create').get_output_in_json()

        presenter_participant_id = first_participant['properties']['id']
        consumer_participant_id = second_participant['properties']['id']

        # add participants into created room 
        self.kwargs.update({
            'room_id': room['id'],
            'presenter_participant_id': presenter_participant_id, 
            'consumer_participant_id': consumer_participant_id})
        self.cmd('az communication rooms participant add --presenter-participants {presenter_participant_id} --consumer-participants {consumer_participant_id} --room {room_id}')
        get_participant = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()
        presenter_participant = get_participant['participants'][0]['role']
        consumer_participant = get_participant['participants'][1]['role']
        participant = get_participant['participants']
        
        # verify the type of participants and the length of participant
        assert presenter_participant == 'Presenter'
        assert consumer_participant == 'Consumer'
        assert len(participant) == 2 

    
    @ResourceGroupPreparer(name_prefix ='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_delete_participants(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room
        room = self.cmd('az communication rooms create').get_output_in_json()

        # create a valid participants
        participant = self.cmd('az communication identity user create').get_output_in_json()
        participant_id = participant['properties']['id']

        # add the participant into created room 
        self.kwargs.update({
            'room_id': room['id'],
            'participant_id': participant_id})
        self.cmd('az communication rooms participant add --consumer-participants {participant_id} --room {room_id}')
       
        # delete the participant from the created room 
        self.cmd('az communication rooms participant remove --participants {participant_id} --room {room_id}')
        get_participant = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()
        participant = get_participant['participants']

        # verify the participant is null 
        assert len(participant) == 0 




   
        