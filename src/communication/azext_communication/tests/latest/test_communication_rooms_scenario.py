# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest, live_only
from azure.core.exceptions import HttpResponseError
from datetime import timezone
from .preparers import CommunicationResourcePreparer
from .recording_processors import URIIdentityReplacer, BodyReplacerProcessor
from datetime import datetime, timedelta


class CommunicationRoomsScenarios(ScenarioTest):

    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[
            URIIdentityReplacer(),
            BodyReplacerProcessor(keys=["id", "rawId"])
        ])

    def __create_user(self, communication_resource_info):
        connection_str = communication_resource_info[1]
        if self.is_live or self.in_recording:
            self.kwargs.update({'connection_string': connection_str})
        else:
            os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = connection_str

        res = self.cmd('az communication identity user create').get_output_in_json()

        return res['properties']['id']

    # room management test
    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        room = self.cmd('az communication rooms create').get_output_in_json()

        id = room['id']
        assert len(id) > 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_with_participants_attributes(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create valid participants
        presenter_id = self.__create_user(communication_resource_info)

        self.kwargs.update({
            'presenter_id': presenter_id})

        room = self.cmd('az communication rooms create --presenter-participants {presenter_id}').get_output_in_json()

        id = room['id']
        assert len(id) > 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_with_invalid_participants_MRI(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create valid participants
        presenter_id = "acs:8-invalidMRI"
        self.kwargs.update({
            'presenter_id': presenter_id})

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms create --presenter-participants {presenter_id}').get_output_in_json()

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        assert 'Invalid format for communication identifier.' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_with_valid_time_attributes(self, communication_resource_info):
        # sourcery skip: aware-datetime-for-utc
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        validFrom = (datetime.utcnow() + timedelta(minutes=60)).isoformat()
        validUntil = (datetime.utcnow() + timedelta(minutes=120)).isoformat()

        self.kwargs.update({
            'validFrom': validFrom,
            'validUntil': validUntil})

        room = self.cmd('az communication rooms create --valid-from {validFrom} --valid-until {validUntil}').get_output_in_json()

        id = room['id']
        assert len(id) > 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_with_validUntil_Exceed_180days(self, communication_resource_info):
        # sourcery skip: aware-datetime-for-utc
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        validFrom = (datetime.utcnow() + timedelta(minutes=60)).isoformat()
        validUntil = (datetime.utcnow() + timedelta(days=200)).isoformat()

        self.kwargs.update({
            'validFrom': validFrom,
            'validUntil': validUntil})

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms create --valid-from {validFrom} --valid-until {validUntil}').get_output_in_json()

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        assert 'The request could not be understood by the server due to malformed syntax.' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_with_expired_validUntil(self, communication_resource_info):
        # sourcery skip: aware-datetime-for-utc
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        validFrom = (datetime.utcnow() + timedelta(minutes=60)).isoformat()
        validUntil = (datetime.utcnow() + timedelta(minutes=-120)).isoformat()

        self.kwargs.update({
            'validFrom': validFrom,
            'validUntil': validUntil})

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms create --valid-from {validFrom} --valid-until {validUntil}').get_output_in_json()

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        assert 'The request could not be understood by the server due to malformed syntax.' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_with_pstn_dial_out_enabled(self, communication_resource_info):
        # sourcery skip: aware-datetime-for-utc
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        pstnEnabled = True
        self.kwargs.update({
            'pstnEnabled': pstnEnabled})
        room = self.cmd('az communication rooms create --pstn-dial-out-enabled {pstnEnabled}').get_output_in_json()

        id = room['id']
        pstnEnabled = room['pstnDialOutEnabled']
        assert len(id) > 0
        assert pstnEnabled is True

        pstnEnabled = False
        self.kwargs.update({
            'pstnEnabled': pstnEnabled})
        room = self.cmd('az communication rooms create --pstn-dial-out-enabled {pstnEnabled}').get_output_in_json()

        id = room['id']
        pstnEnabled = room['pstnDialOutEnabled']
        assert len(id) > 0
        assert pstnEnabled is False

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_with_valid_time_pstn_dial_out_attributes(self, communication_resource_info):
        # sourcery skip: aware-datetime-for-utc
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        validFrom = (datetime.utcnow() + timedelta(minutes=60)).isoformat()
        validUntil = (datetime.utcnow() + timedelta(minutes=120)).isoformat()
        pstnEnabled = True

        self.kwargs.update({
            'validFrom': validFrom,
            'validUntil': validUntil,
            'pstnEnabled': pstnEnabled})

        room = self.cmd('az communication rooms create --valid-from {validFrom} --valid-until {validUntil} --pstn-dial-out-enabled {pstnEnabled} ').get_output_in_json()

        id = room['id']
        pstnEnabled = room['pstnDialOutEnabled']

        assert len(id) > 0
        assert pstnEnabled is True

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_with_valid_participants_pstn_dial_out_attributes(self, communication_resource_info):
        # sourcery skip: aware-datetime-for-utc
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        presenter_id = self.__create_user(communication_resource_info)
        pstnEnabled = True

        self.kwargs.update({
            'pstnEnabled': pstnEnabled,
            'presenter_id': presenter_id})

        room = self.cmd('az communication rooms create --pstn-dial-out-enabled {pstnEnabled} --presenter-participants {presenter_id}').get_output_in_json()

        id = room['id']
        pstnEnabled = room['pstnDialOutEnabled']

        assert len(id) > 0
        assert pstnEnabled is True

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_create_with_all_optional_attributes(self, communication_resource_info):
        # sourcery skip: aware-datetime-for-utc
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        validFrom = (datetime.utcnow() + timedelta(minutes=60)).isoformat()
        validUntil = (datetime.utcnow() + timedelta(minutes=120)).isoformat()
        presenter_id = self.__create_user(communication_resource_info)
        pstnEnabled = True

        self.kwargs.update({
            'validFrom': validFrom,
            'validUntil': validUntil,
            'pstnEnabled': pstnEnabled,
            'presenter_id': presenter_id})

        room = self.cmd('az communication rooms create --valid-from {validFrom} --valid-until {validUntil} --pstn-dial-out-enabled {pstnEnabled} --presenter-participants {presenter_id}').get_output_in_json()

        id = room['id']
        assert len(id) > 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_get_with_valid_roomId(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a room first
        room = self.cmd('az communication rooms create').get_output_in_json()
        self.kwargs.update({
            'room_id': room['id']})

        get_room = self.cmd('az communication rooms get --room {room_id}').get_output_in_json()

        assert room['id'] == get_room['id']

    @live_only()
    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_get_with_nonexisting_roomId(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        NotExistingRoomId = "9949484443000000"
        self.kwargs.update({
            'room_id': NotExistingRoomId})

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms get --room {room_id}').get_output_in_json()

        assert raises.exception.status_code == 404
        assert '(NotFound) The server cannot find the requested resource.' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_get_with_invalid_roomId(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        invalidRoomId = "123-invalidId"
        self.kwargs.update({
            'room_id': invalidRoomId})

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms get --room {room_id}').get_output_in_json()

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        assert 'Invalid room ID length.' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_delete(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a room and delete it with room id
        room = self.cmd('az communication rooms create').get_output_in_json()
        self.kwargs.update({
            'room_id': room['id']})

        self.cmd('az communication rooms delete --room {room_id} --yes')

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
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
        assert 'Invalid room ID' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_valid_elapsed_time(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a room first
        room = self.cmd('az communication rooms create').get_output_in_json()

        # update the room with valid elapsed time
        validFrom = (datetime.utcnow() + timedelta(minutes=60)).isoformat()
        validUntil = (datetime.utcnow() + timedelta(minutes=120)).isoformat()

        self.kwargs.update({
            'room_id': room['id'],
            'validFrom': validFrom,
            'validUntil': validUntil})

        updated_room = self.cmd('az communication rooms update --room {room_id} --valid-from {validFrom} --valid-until {validUntil}').get_output_in_json()

        assert room['id'] == updated_room['id']
        assert room['validFrom'] != updated_room['validFrom']
        assert room['validUntil'] != updated_room['validUntil']

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_expired_validUntil(self, communication_resource_info):
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

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms update --room {room_id} --valid-from {validFrom} --valid-until {validUntil}')

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        assert 'The time range end is in the past' in str(raises.exception.message)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_validUntil_Exceeds_180days(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a room first
        room = self.cmd('az communication rooms create').get_output_in_json()

        # update the room with invalid elapsed time
        validFrom = (datetime.utcnow() + timedelta(minutes=60)).isoformat()
        validUntil = (datetime.utcnow() + timedelta(days=200)).isoformat()

        self.kwargs.update({
            'room_id': room['id'],
            'validFrom': validFrom,
            'validUntil': validUntil})

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication rooms update --room {room_id} --valid-from {validFrom} --valid-until {validUntil}')

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        assert 'The request could not be understood by the server due to malformed syntax.' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_pstn_dial_out_enabled(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a room first
        room = self.cmd('az communication rooms create').get_output_in_json()

        # update the room with valid elapsed time
        pstnEnabled = True

        self.kwargs.update({
            'room_id': room['id'],
            'pstnEnabled': pstnEnabled})

        updated_room = self.cmd('az communication rooms update --room {room_id} --pstn-dial-out-enabled {pstnEnabled}').get_output_in_json()

        assert room['id'] == updated_room['id']
        assert updated_room['pstnDialOutEnabled'] is True

        pstnEnabled = False
        self.kwargs.update({
            'room_id': room['id'],
            'pstnEnabled': pstnEnabled})

        updated_room = self.cmd('az communication rooms update --room {room_id} --pstn-dial-out-enabled {pstnEnabled}').get_output_in_json()

        assert room['id'] == updated_room['id']
        assert updated_room['pstnDialOutEnabled'] is False

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_update_valid_elapsed_time_pstn_dial_out_enabled(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a room first
        room = self.cmd('az communication rooms create').get_output_in_json()

        # update the room with valid elapsed time
        validFrom = (datetime.utcnow() + timedelta(minutes=60)).isoformat()
        validUntil = (datetime.utcnow() + timedelta(minutes=120)).isoformat()
        pstnEnabled = True

        self.kwargs.update({
            'room_id': room['id'],
            'validFrom': validFrom,
            'validUntil': validUntil,
            'pstnEnabled': pstnEnabled})

        updated_room = self.cmd('az communication rooms update --room {room_id} --valid-from {validFrom} --valid-until {validUntil} --pstn-dial-out-enabled {pstnEnabled}').get_output_in_json()

        assert room['id'] == updated_room['id']
        assert room['validFrom'] != updated_room['validFrom']
        assert room['validUntil'] != updated_room['validUntil']
        assert room['pstnDialOutEnabled'] is False
        assert updated_room['pstnDialOutEnabled'] is True

    @live_only()
    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_list(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
        self.cmd('az communication rooms list').get_output_in_json()

    # rooms participant management test
    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_get_default_participants(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room
        room = self.cmd('az communication rooms create').get_output_in_json()

        # get the default null participant from the newly created room
        self.kwargs.update({
            'room_id': room['id']})
        get_participant = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()

        # verify the defualt participants is null
        assert len(get_participant) == 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
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
        self.cmd('az communication rooms participant add-or-update --presenter-participants {participants_id} --room {room_id}')

        get_participant = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()

        assert len(get_participant) == 1
        role = get_participant[0]['role']

        # verify the type of added participant
        assert role == 'Presenter'

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
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
            self.cmd('az communication rooms participant add-or-update --consumer-participants {participants_id} --room {room_id}')

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        assert 'Invalid value for the Participants' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
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

        self.cmd('az communication rooms participant add-or-update --presenter-participants {presenter_id} --consumer-participants {consumer_id} --room {room_id}')

        # get updated room properties
        participants = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()

        # verify the length of participant
        assert len(participants) == 2

        presenter_role = participants[0]['role']
        consumer_role = participants[1]['role']

        # verify the type of participants
        assert presenter_role == 'Presenter'
        assert consumer_role == 'Consumer'

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
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
        self.cmd('az communication rooms participant add-or-update --consumer-participants {participant_id} --room {room_id}')

        # remove the participant from the created room
        self.cmd('az communication rooms participant remove --participants {participant_id} --room {room_id} --yes')
        participants = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()

        # verify the participant list is empty
        assert len(participants) == 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_delete_participants_not_exist_in_room(self, communication_resource_info):
        os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]

        # create a new room
        room = self.cmd('az communication rooms create').get_output_in_json()

        # create a valid participants
        participant_id = self.__create_user(communication_resource_info)
        participant_id_not_exist = self.__create_user(communication_resource_info)
        # add the participant into created room
        self.kwargs.update({
            'room_id': room['id'],
            'participant_id': participant_id,
            'participant_id_not_exist': participant_id_not_exist,
        })
        self.cmd('az communication rooms participant add-or-update --consumer-participants {participant_id} --room {room_id}')

        # remove the participant who does not exist in the created room
        self.cmd('az communication rooms participant remove --participants {participant_id_not_exist} --room {room_id} --yes')
        participants = self.cmd('az communication rooms participant get --room {room_id}').get_output_in_json()

        # verify the participant list is 1
        assert len(participants) == 1

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_rooms_delete_participants_with_invalid_MRI(self, communication_resource_info):
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
            self.cmd('az communication rooms participant remove --participants {participant_id} --room {room_id} --yes')

        assert 'not found' in str(raises.exception)
