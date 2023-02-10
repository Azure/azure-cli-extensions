# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=W0703


import sys
from azure.core.exceptions import HttpResponseError


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


def __to_communication_identifier(participants):
    from azure.communication.identity._shared.models import identifier_from_raw_id

    if participants is None:
        return None

    return [identifier_from_raw_id(p) for p in participants]


def __to_room_participant(presenters, attendees, consumers):
    from azure.communication.identity._shared.models import identifier_from_raw_id
    from azure.communication.rooms import RoomParticipant, RoleType

    participants = []

    if presenters is not None:
        identifiers = [identifier_from_raw_id(p) for p in presenters]
        participants.extend([RoomParticipant(communication_identifier=i, role=RoleType.PRESENTER) for i in identifiers])

    if attendees is not None:
        identifiers = [identifier_from_raw_id(p) for p in attendees]
        participants.extend([RoomParticipant(communication_identifier=i, role=RoleType.ATTENDEE) for i in identifiers])

    if consumers is not None:
        identifiers = [identifier_from_raw_id(p) for p in consumers]
        participants.extend([RoomParticipant(communication_identifier=i, role=RoleType.CONSUMER) for i in identifiers])

    return participants


def communication_rooms_get_room(client, room_id):
    try:
        return client.get_room(room_id)
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_create_room(client,
                                    valid_from=None,
                                    valid_until=None,
                                    join_policy=None,
                                    presenters=None,
                                    attendees=None,
                                    consumers=None):
    try:
        room_participants = __to_room_participant(presenters, attendees, consumers)

        return client.create_room(
            valid_from=valid_from,
            valid_until=valid_until,
            room_join_policy=join_policy,
            participants=room_participants)
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_delete_room(client, room_id):
    try:
        return client.delete_room(room_id)
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_update_room(client, room_id,
                                    valid_from=None,
                                    valid_until=None,
                                    join_policy=None,
                                    presenters=None,
                                    attendees=None,
                                    consumers=None):
    try:
        room_participants = __to_room_participant(presenters, attendees, consumers)

        return client.update_room(
            room_id=room_id,
            valid_from=valid_from,
            valid_until=valid_until,
            room_join_policy=join_policy,
            participants=room_participants)
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_get_participants(client, room_id):
    try:
        return client.get_participants(room_id)
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_add_participants(client, room_id,
                                         presenters=None,
                                         attendees=None,
                                         consumers=None):
    try:
        return client.add_participants(
            room_id=room_id,
            participants=__to_room_participant(presenters, attendees, consumers))
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_update_participants(client, room_id,
                                            presenters=None,
                                            attendees=None,
                                            consumers=None):
    try:
        return client.update_participants(
            room_id=room_id,
            participants=__to_room_participant(presenters, attendees, consumers))
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_remove_participants(client, room_id, participants):
    try:
        return client.remove_participants(
            room_id=room_id,
            communication_identifiers=__to_communication_identifier(participants))
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def __get_attachment_content(filename, filetype):
    import base64
    import os
    from azure.communication.email import EmailAttachment

    _, tail = os.path.split(filename)
    with open(filename, "r", encoding="utf-8") as file:
        file_content = file.read()

    base64_content = base64.b64encode(bytes(file_content, 'utf-8'))

    return EmailAttachment(
        name=tail,
        attachment_type=filetype,
        content_bytes_base64=base64_content.decode(),
    )


def communication_email_send(client,
                             subject,
                             sender,
                             recipients_to,
                             disable_tracking=False,
                             text=None,
                             html=None,
                             importance='normal',
                             recipients_cc=None,
                             recipients_bcc=None,
                             reply_to=None,
                             attachments=None,
                             attachment_types=None):

    from azure.communication.email import EmailContent, EmailAddress, EmailMessage, EmailRecipients
    from knack.util import CLIError

    try:
        email_content = EmailContent(
            subject=subject,
            plain_text=text,
            html=html,
        )

        to_address = [EmailAddress(email=r) for r in recipients_to]

        reply_to_address = None if reply_to is None else [EmailAddress(email=reply_to)]

        if attachments is None and attachment_types is None:
            attachments_list = None
        elif attachments is None or attachment_types is None:
            raise CLIError('Number of attachments and attachment-types should match.')
        elif len(attachments) != len(attachment_types):
            raise CLIError('Number of attachments and attachment-types should match.')
        else:
            attachments_list = [
                __get_attachment_content(attachments[i], attachment_types[i])
                for i in range(len(attachments))
            ]

        message = EmailMessage(
            sender=sender,
            content=email_content,
            recipients=EmailRecipients(
                to=to_address,
                cc=[] if recipients_cc is None else [EmailAddress(email=r) for r in recipients_cc],
                bcc=[] if recipients_bcc is None else [EmailAddress(email=r) for r in recipients_bcc]),
            importance=importance,
            reply_to=reply_to_address,
            disable_user_engagement_tracking=disable_tracking,
            attachments=attachments_list,
        )

        return client.send(message)
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_email_get_status(client, message_id):
    try:
        return client.get_send_status(message_id)
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))
