# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
import os
from .recording_processors import URIIdentityReplacer, BodyReplacerProcessor
from .preparers import CommunicationResourcePreparer

class CommunicationChatScenarios(ScenarioTest):

    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[
            URIIdentityReplacer(),
            BodyReplacerProcessor(keys=["id", "token", "rawId"]),
        ])


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_threads_with_env_auth(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]
        threads = self.cmd('az communication chat list-threads').get_output_in_json()
        assert len(threads) == 0
        

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_threads_with_cmdline_auth(self, communication_resource_chat_info):
        self.kwargs.update({
            'access_token': communication_resource_chat_info[3],
            'endpoint': communication_resource_chat_info[1] })
        threads = self.cmd('az communication chat list-threads --endpoint \"{endpoint}\" --access-token \"{access_token}\"').get_output_in_json()
        assert len(threads) == 0
        

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_threads_no_endpoint(self, communication_resource_chat_info):
        from azure.cli.core.azclierror import RequiredArgumentMissingError
        
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]
        self.kwargs.pop('endpoint', None)
        os.environ.pop('AZURE_COMMUNICATION_ENDPOINT', None)

        with self.assertRaises(RequiredArgumentMissingError) as raises:
            self.cmd('az communication chat list-threads').get_output_in_json()

        assert '--endpoint' in str(raises.exception)
        assert 'AZURE_COMMUNICATION_ENDPOINT' in str(raises.exception)


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_threads_no_token(self, communication_resource_chat_info):
        from azure.cli.core.azclierror import RequiredArgumentMissingError
        
        self.kwargs.update({'endpoint': communication_resource_chat_info[1]})
        self.kwargs.pop('access-token', None)
        os.environ.pop('AZURE_COMMUNICATION_ACCESS_TOKEN', None)

        with self.assertRaises(RequiredArgumentMissingError) as raises:
            self.cmd('az communication chat list-threads --endpoint {endpoint}').get_output_in_json()

        assert '--access-token' in str(raises.exception)
        assert 'AZURE_COMMUNICATION_ACCESS_TOKEN' in str(raises.exception)


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_create_thread(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        chat_topic = 'some-topic'
        self.kwargs.update({
            'topic': chat_topic })
        self.cmd('az communication chat create-thread --topic \"{topic}\"', checks = [
            self.check("errors", None),
            self.check("chatThread.topic", chat_topic),
        ])


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_create_thread_without_topic(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        with self.assertRaises(SystemExit) as raises:
            self.cmd('az communication chat create-thread').get_output_in_json()
        assert raises.exception.code == 2


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_participants(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        chat_topic = 'some-topic'
        self.kwargs.update({
            'topic': chat_topic })
        thread = self.cmd('az communication chat create-thread --topic \"{topic}\"').get_output_in_json()
        thread_id = thread['chatThread']['id']
        self.kwargs.update({
            'thread_id': thread_id })
        participants = self.cmd('az communication chat list-participants --thread-id {thread_id}').get_output_in_json()
        assert len(participants) == 1
        assert participants[0]['shareHistoryTime'] == '1970-01-01T00:00:00+00:00'


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_participants_bad_thread_id(self, communication_resource_chat_info):
        from azure.core.exceptions import HttpResponseError

        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        thread_id = 'sanitized'
        self.kwargs.update({
            'thread_id': thread_id })
        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication chat list-participants --thread-id {thread_id}', checks = [
                self.check('httpStatusCode', '400')])


    def __create_thread(self, topic):
        self.kwargs.update({
            'topic': topic })
        return self.cmd('az communication chat create-thread --topic \"{topic}\"').get_output_in_json()


    def __create_user(self, connection_str):
        if self.is_live or self.in_recording:
            self.kwargs.update({ 'connection_string':  connection_str})
        else:
            os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = connection_str
        res = self.cmd('az communication identity issue-access-token --scope chat').get_output_in_json()
        return res['user_id']


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_add_participant(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        user_id = self.__create_user(communication_resource_chat_info[4])

        # create a new thread
        self.kwargs.update({
            'topic': "chat-topic" })

        thread = self.cmd('az communication chat create-thread --topic \"{topic}\"').get_output_in_json()
        thread_id = thread['chatThread']['id']

        # add the new user to the chat thread
        self.kwargs.update({
            'thread_id': thread_id,
            'user_id': user_id,
            'access_token': communication_resource_chat_info[3] })

        add_res = self.cmd('az communication chat add-participant --thread-id {thread_id} --user-id {user_id}').get_output_in_json()

        assert len(add_res) == 0


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_add_participant_bad_user(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread
        self.kwargs.update({
            'topic': "chat-topic" })
        thread = self.cmd('az communication chat create-thread --topic \"{topic}\"').get_output_in_json()
        thread_id = thread['chatThread']['id']

        # add a fake user to the chat thread
        user_id = '8:acs:00000000-1111-2222-3333-444444444444_55555555-6666-7777-8888-999999999999'
        self.kwargs.update({
            'thread_id': thread_id,
            'user_id': user_id,
            'access_token': communication_resource_chat_info[3] })

        add_res = self.cmd('az communication chat add-participant --thread-id {thread_id} --user-id {user_id}', checks = [
            self.check('[0].code', '403'),
            self.check('[0].message', 'Permissions check failed'),
            self.check('[0].target', user_id) ]).get_output_in_json()
        
        assert len(add_res) == 1

        # add invalid user id to the chat thread
        self.kwargs.update({
            'user_id': '8:acs:fakeid===' })

        with self.assertRaises(Exception) as raises:
            self.cmd('az communication chat add-participant --thread-id {thread_id} --user-id {user_id}', checks = [
                self.check('CommunicationError.code', 'Bad Request')])

        assert 'Identifier format is invalid' in str(raises.exception)

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_remove_participants(self, communication_resource_chat_info):
        from azure.core.exceptions import HttpResponseError

        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        user_id = self.__create_user(communication_resource_chat_info[4])

        # create a new thread
        thread = self.__create_thread('chat-topic')
        thread_id = thread['chatThread']['id']
        owner_id = thread['chatThread']['createdBy']['properties']['id']

        # add the new user to the chat thread
        self.kwargs.update({
            'thread_id': thread_id,
            'user_id': user_id })

        add_res = self.cmd('az communication chat add-participant --thread-id {thread_id} --user-id {user_id}').get_output_in_json()
        assert len(add_res) == 0

        # remove the new user from the chat thread
        self.cmd('az communication chat remove-participant --thread-id {thread_id} --user-id {user_id}')        

        # try to remove a user with invalid id
        self.kwargs.update({
            'user_id': '8:acs:fakeid' })

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication chat remove-participant --thread-id {thread_id} --user-id {user_id}', checks = [
                self.check('CommunicationError.code', 'Bad Request')])        

        assert 'Identifier format is invalid' in str(raises.exception)

        # remove the original user from the chat thread
        self.kwargs.update({
            'user_id': owner_id })
        self.cmd('az communication chat remove-participant --thread-id {thread_id} --user-id {user_id}')

        # try to remove the original user again, should raise an error
        with self.assertRaises(HttpResponseError) as raises:
            self.cmd('az communication chat remove-participant --thread-id {thread_id} --user-id {user_id}')
        assert 'The initiator doesn\'t have the permission to perform the requested operation.' in str(raises.exception)


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_add_participant_with_display_name(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread
        thread = self.__create_thread('chat-topic')
        thread_id = thread['chatThread']['id']

        user_id = self.__create_user(communication_resource_chat_info[4])

        # add the new user to the chat thread
        display_name = '\"John Doe\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'user_id': user_id,
            'display_name': display_name })
        add_res = self.cmd('az communication chat add-participant --thread-id {thread_id} --user-id {user_id} --display-name {display_name}').get_output_in_json()
        assert len(add_res) == 0


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_add_participant_with_history_time(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread
        thread = self.__create_thread('chat-topic')
        thread_id = thread['chatThread']['id']

        user_id = self.__create_user(communication_resource_chat_info[4])

        # add the new user to the chat thread
        start_time = '2022-01-01T00:00:00'
        self.kwargs.update({
            'thread_id': thread_id,
            'user_id': user_id,
            'start_time': start_time})
        add_res = self.cmd('az communication chat add-participant --thread-id {thread_id} --user-id {user_id} --start-time {start_time}').get_output_in_json()
        assert len(add_res) == 0


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_messages(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('another-topic')
        thread_id = thread['chatThread']['id']

        self.kwargs.update({
            'thread_id': thread_id })
        messages = self.cmd('az communication chat list-messages --thread-id {thread_id}').get_output_in_json()
        assert len(messages) > 0


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_list_messages(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('another-topic')
        thread_id = thread['chatThread']['id']

        start_time = '2022-01-01T00:00:00'
        self.kwargs.update({
            'thread_id': thread_id,
            'start_time': start_time })
        messages = self.cmd('az communication chat list-messages --thread-id {thread_id} --start-time {start_time}').get_output_in_json()
        assert len(messages) > 0


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_send_message(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('some-other-topic')
        thread_id = thread['chatThread']['id']

        content = '\"Hello!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content })
        message = self.cmd('az communication chat send-message --thread-id {thread_id} --content {content}').get_output_in_json()
        assert message['id'] is not None
        

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_send_message_without_content(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('yet-another-topic')
        thread_id = thread['chatThread']['id']

        self.kwargs.update({
            'thread_id': thread_id })
        with self.assertRaises(SystemExit) as raises:
            self.cmd('az communication chat send-message --thread-id {thread_id}').get_output_in_json()
        assert raises.exception.code == 2

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_send_text_message(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('yet-another-topic')
        thread_id = thread['chatThread']['id']

        content = '\"Hello!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content })
        message = self.cmd('az communication chat send-message --thread-id {thread_id} --content {content} --message-type text').get_output_in_json()
        assert message['id'] is not None


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_send_html_message(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('yet-another-topic')
        thread_id = thread['chatThread']['id']

        content = '<br>hello!<br>'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content })
        message = self.cmd('az communication chat send-message --thread-id {thread_id} --content {content} --message-type html').get_output_in_json()
        assert message['id'] is not None


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_get_message(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('new-topic')
        thread_id = thread['chatThread']['id']

        content = 'hello!'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content })
        sent_message = self.cmd('az communication chat send-message --thread-id {thread_id} --content {content} --message-type html').get_output_in_json()

        self.kwargs.update({
            'message_id': sent_message['id'] })
        message = self.cmd('az communication chat get-message --thread-id {thread_id} --message-id {message_id}').get_output_in_json()
        assert message['content']['message'] == content


    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_update_message(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('some-other-topic')
        thread_id = thread['chatThread']['id']

        # then send a message to the thread
        content = '\"Hello!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content })
        message = self.cmd('az communication chat send-message --thread-id {thread_id} --content {content}').get_output_in_json()

        # and update it
        new_content = '\"Hello there!\"'
        self.kwargs.update({
            'content': new_content,
            'message_id': message['id'] })
        self.cmd('az communication chat update-message --thread-id {thread_id} --message-id {message_id} --content {content}')
        

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_delete_message(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('some-other-topic')
        thread_id = thread['chatThread']['id']

        # then send a message to the thread
        content = '\"Hello!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content })
        message = self.cmd('az communication chat send-message --thread-id {thread_id} --content {content}').get_output_in_json()

        # and delete it
        self.kwargs.update({
            'message_id': message['id'] })
        self.cmd('az communication chat delete-message --thread-id {thread_id} --message-id {message_id}')
        

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_update_message(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('thread-topic')
        thread_id = thread['chatThread']['id']

        # then send a message to the thread
        content = '\"Hello!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'content': content })
        message = self.cmd('az communication chat send-message --thread-id {thread_id} --content {content}').get_output_in_json()

        new_content = '\"Hello there!\"'
        self.kwargs.update({
            'content': new_content,
            'message_id': message['id'] })
        self.cmd('az communication chat update-message --thread-id {thread_id} --message-id {message_id} --content {content}')
        

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_update_topic(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('thread-topic')
        thread_id = thread['chatThread']['id']

        # then update the topic
        new_topic = '\"new-topic!\"'
        self.kwargs.update({
            'thread_id': thread_id,
            'topic': new_topic })
        self.cmd('az communication chat update-topic --thread-id {thread_id} --topic {topic}')
        

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_chat_read_receipts(self, communication_resource_chat_info):
        os.environ['AZURE_COMMUNICATION_ENDPOINT'] = communication_resource_chat_info[1]
        os.environ['AZURE_COMMUNICATION_ACCESS_TOKEN'] = communication_resource_chat_info[3]

        # create a new thread first
        thread = self.__create_thread('thread-topic')
        thread_id = thread['chatThread']['id']

        self.kwargs.update({
            'thread_id': thread_id })
        receipts = self.cmd('az communication chat list-read-receipts --thread-id {thread_id}').get_output_in_json()
        assert len(receipts) == 0
        
        messages = self.cmd('az communication chat list-messages --thread-id {thread_id}').get_output_in_json()
        message_id = messages[0]['id']

        self.kwargs.update({
            'message_id': message_id })
        self.cmd('az communication chat send-read-receipt --thread-id {thread_id} --message-id {message_id}')

        receipts = self.cmd('az communication chat list-read-receipts --thread-id {thread_id}').get_output_in_json()
        assert len(receipts) == 1

        

