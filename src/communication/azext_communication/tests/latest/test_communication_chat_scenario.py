# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.core.exceptions import HttpResponseError
import os
from .recording_processors import URIIdentityReplacer, BodyReplacerProcessor
from .preparers import CommunicationResourcePreparer


class CommunicationChatScenarios(ScenarioTest):

    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[
            URIIdentityReplacer(),
            BodyReplacerProcessor(keys=["id", "token", "rawId"]),
        ])

    def __create_thread(self, topic):
        self.kwargs.update({
            'topic': topic})
        return self.cmd('az communication chat thread create --topic \"{topic}\"').get_output_in_json()

    def __create_user(self, communication_resource_info):
        connection_str = communication_resource_info[1]
        if self.is_live or self.in_recording:
            self.kwargs.update({'connection_string': connection_str})
        else:
            os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = connection_str
        res = self.cmd('az communication user-identity token issue --scope chat').get_output_in_json()
        return res['user_id']

    def __get_endpoint_from_resource_info(self, communication_resource_info):
        return communication_resource_info[2]

    def __get_or_create_token(self, communication_resource_info):
        if self.is_live or self.in_recording:
            os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = communication_resource_info[1]
            self.kwargs.update({'connection_string': communication_resource_info[1]})
            res = self.cmd('az communication user-identity token issue --scope chat').get_output_in_json()
            return res['token']
        else:
            # header is encoded form of
            # {"alg":"sanitized","kid":"1","x5t":"sanitized","typ":"sanitized"}
            header = 'eyJhbGciOiJzYW5pdGl6ZWQiLCJraWQiOiIxIiwieDV0Ijoic2FuaXRpemVkIiwidHlwIjoic2FuaXRpemVkIn0='

            # payload is encoded form of
            # {"skypeid":"acs:sanitized","scp":1792,"csi":"1657788332","exp":1657874732,"acsScope":"chat","resourceId":"sanitized","iat":1657788332}
            payload = 'eyJza3lwZWlkIjoiYWNzOnNhbml0aXplZCIsInNjcCI6MTc5MiwiY3NpIjoiMTY1Nzc4ODMzMiIsImV4cCI6MTY1Nzg3NDczMiwiYWNzU2NvcGUiOiJjaGF0IiwicmVzb3VyY2VJZCI6InNhbml0aXplZCIsImlhdCI6MTY1Nzc4ODMzMn0='

            signature = '1234'

            return '{header}.{payload}.{signature}'.format(header=header, payload=payload, signature=signature)

    def __update_environ(self, communication_resource_info):
        endpoint = self.__get_endpoint_from_resource_info(communication_resource_info)
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = endpoint

        token = self.__get_or_create_token(communication_resource_info)
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = token

        return endpoint, token

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_threads_with_env_auth(self, communication_resource_info):
        self.__update_environ(communication_resource_info)
        threads = self.cmd('az communication chat thread list').get_output_in_json()
        assert len(threads) == 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_threads_with_cmdline_auth(self, communication_resource_info):
        endpoint, token = self.__update_environ(communication_resource_info)
        self.kwargs.update({
            'access_token': token,
            'endpoint': endpoint})
        threads = self.cmd('az communication chat thread list --endpoint \"{endpoint}\" --access-token \"{access_token}\"').get_output_in_json()
        assert len(threads) == 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_threads_no_endpoint(self, communication_resource_info):
        from azure.cli.core.azclierror import RequiredArgumentMissingError

        token = self.__get_or_create_token(communication_resource_info)
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = token

        self.kwargs.pop('endpoint', None)
        os.environ.pop('AZURE_COMMUNICATION_ENDPOINT', None)

        with self.assertRaises(RequiredArgumentMissingError) as raises:
            self.cmd('az communication chat thread list').get_output_in_json()

        assert '--endpoint' in str(raises.exception)
        assert 'AZURE_COMMUNICATION_ENDPOINT' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_create_thread(self, communication_resource_info):
        self.__update_environ(communication_resource_info)
        checkValue = []
        chat_topic = 'some-topic'
        self.kwargs.update({
            'topic': chat_topic})
        self.cmd('az communication chat thread create --topic \"{topic}\"', checks=[
            self.check("errors", checkValue),
            self.check("chatThread.topic", chat_topic),
        ])

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_create_thread_without_topic(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        with self.assertRaises(SystemExit) as raises:
            self.cmd('az communication chat thread create').get_output_in_json()
        assert raises.exception.code == 2

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_delete_thread(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        chat_topic = 'some-topic'
        self.kwargs.update({
            'topic': chat_topic})
        res = self.__create_thread(chat_topic)
        thread_id = res['chatThread']['id']

        self.kwargs.update({'thread_id': thread_id})
        self.cmd('az communication chat thread delete --thread {thread_id} --yes')

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_participants(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        chat_topic = 'some-topic'
        self.kwargs.update({
            'topic': chat_topic})
        thread = self.cmd('az communication chat thread create --topic \"{topic}\"').get_output_in_json()
        thread_id = thread['chatThread']['id']
        self.kwargs.update({
            'thread_id': thread_id})
        participants = self.cmd('az communication chat participant list --thread {thread_id}').get_output_in_json()
        assert len(participants) == 1
        assert participants[0]['shareHistoryTime'] == '1970-01-01T00:00:00+00:00'

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_participants_bad_thread_id(self, communication_resource_info):
        from azure.core.exceptions import ResourceNotFoundError

        self.__update_environ(communication_resource_info)

        thread_id = 'sanitized'
        self.kwargs.update({
            'thread_id': thread_id})
        with self.assertRaises(ResourceNotFoundError) as raises:
            self.cmd('az communication chat participant list --thread {thread_id}')

        assert 'Not Found' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_add_participant(self, communication_resource_info):
        endpoint, token = self.__update_environ(communication_resource_info)

        user_id = self.__create_user(communication_resource_info)

        # create a new thread
        self.kwargs.update({
            'topic': "chat-topic"})

        thread = self.cmd('az communication chat thread create --topic \"{topic}\"').get_output_in_json()
        thread_id = thread['chatThread']['id']

        # add the new user to the chat thread
        self.kwargs.update({
            'thread_id': thread_id,
            'user_id': user_id,
            'access_token': token})

        add_res = self.cmd('az communication chat participant add --thread {thread_id} --user {user_id}').get_output_in_json()

        assert len(add_res) == 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_add_participant_bad_user(self, communication_resource_info):
        endpoint, token = self.__update_environ(communication_resource_info)

        # create a new thread
        self.kwargs.update({
            'topic': "chat-topic"})
        thread = self.cmd('az communication chat thread create --topic \"{topic}\"').get_output_in_json()
        thread_id = thread['chatThread']['id']

        # add a fake user to the chat thread
        user_id = '8:acs:00000000-1111-2222-3333-444444444444_55555555-6666-7777-8888-999999999999'
        self.kwargs.update({
            'thread_id': thread_id,
            'user_id': user_id,
            'access_token': token})

        add_res = self.cmd('az communication chat participant add --thread {thread_id} --user {user_id}', checks=[
            self.check('[0].code', '403'),
            self.check('[0].message', 'Permissions check failed'),
            self.check('[0].target', user_id)]).get_output_in_json()

        assert len(add_res) == 1

        # add invalid user id to the chat thread
        self.kwargs.update({
            'user_id': '8:acs:fakeid==='})

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication chat participant add --thread {thread_id} --user {user_id}')

        assert 'Identifier format is invalid' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_remove_participants(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        user_id = self.__create_user(communication_resource_info)

        # create a new thread
        thread = self.__create_thread('chat-topic')
        thread_id = thread['chatThread']['id']
        owner_id = thread['chatThread']['createdBy']['properties']['id']

        # add the new user to the chat thread
        self.kwargs.update({
            'thread_id': thread_id,
            'user_id': user_id})

        add_res = self.cmd('az communication chat participant add --thread {thread_id} --user {user_id}').get_output_in_json()
        assert len(add_res) == 0

        # remove the new user from the chat thread
        self.cmd('az communication chat participant remove --thread {thread_id} --user {user_id} --yes')

        # try to remove a user with invalid id
        self.kwargs.update({
            'user_id': '8:acs:fakeid'})

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication chat participant remove --thread {thread_id} --user {user_id} --yes')

        assert 'Identifier format is invalid' in str(raises.exception)

        # remove the original user from the chat thread
        self.kwargs.update({
            'user_id': owner_id})
        self.cmd('az communication chat participant remove --thread {thread_id} --user {user_id} --yes')

        # try to remove the original user again, should raise an error
        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication chat participant remove --thread {thread_id} --user {user_id} --yes')

        # assert 'The initiator doesn\'t have the permission to perform the requested operation.' in str(raises.exception)
        # For now rest endpoint returns a 500 error, so we are checking for that
        assert 'Operation returned an invalid status \'Internal Server Error\'' in str(raises.exception)


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_add_participant_with_display_name(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread
        thread = self.__create_thread('chat-topic')
        thread_id = thread['chatThread']['id']

        user_id = self.__create_user(communication_resource_info)

        # add the new user to the chat thread
        display_name = '\"John Doe\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'user_id': user_id,
            'display_name': display_name})
        add_res = self.cmd('az communication chat participant add --thread {thread_id} --user {user_id} --display-name {display_name}').get_output_in_json()
        assert len(add_res) == 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_add_participant_with_history_time(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread
        thread = self.__create_thread('chat-topic')
        thread_id = thread['chatThread']['id']

        user_id = self.__create_user(communication_resource_info)

        # add the new user to the chat thread
        start_time = '2022-01-01T00:00:00'
        self.kwargs.update({
            'thread_id': thread_id,
            'user_id': user_id,
            'start_time': start_time})
        add_res = self.cmd('az communication chat participant add --thread {thread_id} --user {user_id} --start-time {start_time}').get_output_in_json()
        assert len(add_res) == 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_messages(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('another-topic')
        thread_id = thread['chatThread']['id']

        self.kwargs.update({
            'thread_id': thread_id})
        messages = self.cmd('az communication chat message list --thread {thread_id}').get_output_in_json()
        assert len(messages) > 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_messages(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('another-topic')
        thread_id = thread['chatThread']['id']

        start_time = '2022-01-01T00:00:00'
        self.kwargs.update({
            'thread_id': thread_id,
            'start_time': start_time})
        messages = self.cmd('az communication chat message list --thread {thread_id} --start-time {start_time}').get_output_in_json()
        assert len(messages) > 0

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_send_message(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('some-other-topic')
        thread_id = thread['chatThread']['id']

        content = '\"Hello!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content})
        message = self.cmd('az communication chat message send --thread {thread_id} --content {content}').get_output_in_json()
        assert message['id'] is not None

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_send_message_without_content(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('yet-another-topic')
        thread_id = thread['chatThread']['id']

        self.kwargs.update({
            'thread_id': thread_id})
        with self.assertRaises(SystemExit) as raises:
            self.cmd('az communication chat message send --thread {thread_id}').get_output_in_json()
        assert raises.exception.code == 2

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_send_text_message(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('yet-another-topic')
        thread_id = thread['chatThread']['id']

        content = '\"Hello!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content})
        message = self.cmd('az communication chat message send --thread {thread_id} --content {content} --message-type text').get_output_in_json()
        assert message['id'] is not None

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_send_html_message(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('yet-another-topic')
        thread_id = thread['chatThread']['id']

        content = '<br>hello!<br>'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content})
        message = self.cmd('az communication chat message send --thread {thread_id} --content {content} --message-type html').get_output_in_json()
        assert message['id'] is not None

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_get_message(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('new-topic')
        thread_id = thread['chatThread']['id']

        content = 'hello!'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content})
        sent_message = self.cmd('az communication chat message send --thread {thread_id} --content {content} --message-type html').get_output_in_json()

        self.kwargs.update({
            'message_id': sent_message['id']})
        message = self.cmd('az communication chat message get --thread {thread_id} --message-id {message_id}').get_output_in_json()
        assert message['content']['message'] == content

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_update_message(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('some-other-topic')
        thread_id = thread['chatThread']['id']

        # then send a message to the thread
        content = '\"Hello!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content})
        message = self.cmd('az communication chat message send --thread {thread_id} --content {content}').get_output_in_json()

        # and update it
        new_content = '\"Hello there!\"'
        self.kwargs.update({
            'content': new_content,
            'message_id': message['id']})
        self.cmd('az communication chat message update --thread {thread_id} --message-id {message_id} --content {content}')

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_delete_message(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('some-other-topic')
        thread_id = thread['chatThread']['id']

        # then send a message to the thread
        content = '\"Hello!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content})
        message = self.cmd('az communication chat message send --thread {thread_id} --content {content}').get_output_in_json()

        # check that the message is there, and it is not deleted
        self.kwargs.update({
            'message_id': message['id']})
        self.cmd('az communication chat message get --thread {thread_id} --message-id {message_id}', checks=[
            self.check('deletedOn', None)
        ])

        # and delete it
        self.kwargs.update({
            'message_id': message['id']})
        self.cmd('az communication chat message delete --thread {thread_id} --message-id {message_id} --yes')

        # now, check that it is actually deleted
        self.kwargs.update({
            'message_id': message['id']})
        deletedMessage = self.cmd('az communication chat message get --thread {thread_id} --message-id {message_id}').get_output_in_json()
        assert deletedMessage['deletedOn'] is not None

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_update_message(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('thread-topic')
        thread_id = thread['chatThread']['id']

        # then send a message to the thread
        content = '\"Hello!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content})
        message = self.cmd('az communication chat message send --thread {thread_id} --content {content}').get_output_in_json()

        new_content = '\"Hello there!\"'
        self.kwargs.update({
            'content': new_content,
            'message_id': message['id']})
        self.cmd('az communication chat message update --thread {thread_id} --message-id {message_id} --content {content}')

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_update_topic(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('thread-topic')
        thread_id = thread['chatThread']['id']

        # then update the topic
        new_topic = '\"new-topic!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'topic': new_topic})
        self.cmd('az communication chat thread update-topic --thread {thread_id} --topic {topic}')

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_read_receipts(self, communication_resource_info):
        self.__update_environ(communication_resource_info)

        # create a new thread first
        thread = self.__create_thread('thread-topic')
        thread_id = thread['chatThread']['id']

        self.kwargs.update({
            'thread_id': thread_id})
        receipts = self.cmd('az communication chat message receipt list --thread {thread_id}').get_output_in_json()
        assert len(receipts) == 0

        messages = self.cmd('az communication chat message list --thread {thread_id}').get_output_in_json()
        message_id = messages[0]['id']

        self.kwargs.update({
            'message_id': message_id})
        self.cmd('az communication chat message receipt send --thread {thread_id} --message-id {message_id}')

        receipts = self.cmd('az communication chat message receipt list --thread {thread_id}').get_output_in_json()
        assert len(receipts) == 1
