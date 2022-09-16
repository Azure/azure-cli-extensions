# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def communication_identity_create_user(client):
    return client.create_user()


def communication_identity_delete_user(client, user_id):
    from azure.communication.identity import CommunicationUserIdentifier

    return client.delete_user(CommunicationUserIdentifier(user_id))


def communication_identity_issue_access_token(client, scopes, user_id=None):
    from azure.communication.identity import CommunicationUserIdentifier
    user_token_data = {"user_id": user_id, "token": "", "expires_on": ""}
    if user_id is not None:
        user = CommunicationUserIdentifier(user_id)
        token_data = client.get_token(user, scopes)
        user_token_data["token"] = token_data.token
        user_token_data["expires_on"] = str(token_data.expires_on)
    else:
        identity_token_result = client.create_user_and_token(scopes)
        if len(identity_token_result) >= 2:
            user_token_data["user_id"] = identity_token_result[0].properties['id']
            user_token_data["token"] = identity_token_result[1].token
            user_token_data["expires_on"] = str(identity_token_result[1].expires_on)

    return user_token_data


def communication_identity_revoke_access_tokens(client, user_id):
    from azure.communication.identity import CommunicationUserIdentifier

    return client.revoke_tokens(CommunicationUserIdentifier(user_id))


def communication_identity_get_token_for_teams_user(client, aad_token, client_id, user_object_id):
    return client.get_token_for_teams_user(aad_token, client_id, user_object_id)


def communication_send_sms(client, sender, recipients, message):
    return client.send(from_=sender, to=recipients, message=message)


def communication_list_phonenumbers(client):
    return client.list_purchased_phone_numbers()


def communication_show_phonenumber(client, phonenumber):
    return client.get_purchased_phone_number(phonenumber)


def communication_chat_list_threads(client, start_time=None):
    args = {
        'start_time': start_time,
    }
    return client.list_chat_threads(**args)


def communication_chat_create_thread(client, topic, idempotency_token=None):
    args = {
        'idempotency_token': idempotency_token
    }
    return client.create_chat_thread(topic, **args)


def communication_chat_delete_thread(client, thread_id):
    return client.delete_chat_thread(thread_id)


def communication_chat_list_participants(client, thread_id, skip=None):
    args = {
        'skip': skip
    }
    chat_thread_client = client.get_chat_thread_client(thread_id)
    return chat_thread_client.list_participants(**args)


def communication_chat_add_participant(client, thread_id, user_id, display_name=None, start_time=None):
    from azure.communication.chat import ChatParticipant
    from azure.communication.identity import CommunicationUserIdentifier

    chat_thread_client = client.get_chat_thread_client(thread_id)
    participant = ChatParticipant(
        identifier=CommunicationUserIdentifier(user_id),
        display_name=display_name,
        share_history_time=start_time
    )
    res = chat_thread_client.add_participants([participant])
    return [r[1] for r in res]


def communication_chat_remove_participant(client, thread_id, user_id):
    from azure.communication.identity import CommunicationUserIdentifier
    chat_thread_client = client.get_chat_thread_client(thread_id)
    return chat_thread_client.remove_participant(CommunicationUserIdentifier(user_id))


def communication_chat_send_message(client, thread_id, message_content, message_type=None, display_name=None):
    args = {
        'chat_message_type': message_type,
        'sender_display_name': display_name
    }
    chat_thread_client = client.get_chat_thread_client(thread_id)
    return chat_thread_client.send_message(message_content, **args)


def communication_chat_list_messages(client, thread_id, start_time=None):
    args = {
        'start_time': start_time
    }
    chat_thread_client = client.get_chat_thread_client(thread_id)
    return chat_thread_client.list_messages(**args)


def communication_chat_get_message(client, thread_id, message_id):
    chat_thread_client = client.get_chat_thread_client(thread_id)
    return chat_thread_client.get_message(message_id)


def communication_chat_update_message(client, thread_id, message_id, message_content):
    chat_thread_client = client.get_chat_thread_client(thread_id)
    return chat_thread_client.update_message(message_id, message_content)


def communication_chat_delete_message(client, thread_id, message_id):
    chat_thread_client = client.get_chat_thread_client(thread_id)
    return chat_thread_client.delete_message(message_id)


def communication_chat_update_topic(client, thread_id, topic):
    chat_thread_client = client.get_chat_thread_client(thread_id)
    return chat_thread_client.update_topic(topic)


def communication_chat_list_read_receipts(client, thread_id, skip=None):
    args = {
        'skip': skip
    }
    chat_thread_client = client.get_chat_thread_client(thread_id)
    return chat_thread_client.list_read_receipts(**args)


def communication_chat_send_read_receipt(client, thread_id, message_id):
    chat_thread_client = client.get_chat_thread_client(thread_id)
    return chat_thread_client.send_read_receipt(message_id)
