# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=W0703


import sys
import ast
from azure.core.exceptions import HttpResponseError
import base64
import hashlib
import hmac
import requests
from datetime import datetime
from urllib.parse import urlparse


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


def communication_send_sms(client, sender, recipients, message, delivery_report=False, tag=None):
    return client.send(from_=sender, to=recipients, message=message, enable_delivery_report=delivery_report, tag=tag)


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


def __to_room_participant(presenters, attendees, consumers, collaborators):
    from azure.communication.identity._shared.models import identifier_from_raw_id
    from azure.communication.rooms import RoomParticipant, ParticipantRole

    participants = []

    if presenters is not None:
        identifiers = [identifier_from_raw_id(p) for p in presenters]
        participants.extend([RoomParticipant(communication_identifier=i,
                                             role=ParticipantRole.PRESENTER) for i in identifiers])

    if attendees is not None:
        identifiers = [identifier_from_raw_id(p) for p in attendees]
        participants.extend([RoomParticipant(communication_identifier=i,
                                             role=ParticipantRole.ATTENDEE) for i in identifiers])

    if consumers is not None:
        identifiers = [identifier_from_raw_id(p) for p in consumers]
        participants.extend([RoomParticipant(communication_identifier=i,
                                             role=ParticipantRole.CONSUMER) for i in identifiers])

    if collaborators is not None:
        identifiers = [identifier_from_raw_id(p) for p in collaborators]
        participants.extend([RoomParticipant(communication_identifier=i,
                                             role=ParticipantRole.COLLABORATOR) for i in identifiers])

    return participants


def __to_room_pstn_dial_out_enabled(pstn_dial_out_enabled):
    pstn_enabled_str = pstn_dial_out_enabled

    if pstn_enabled_str is None:
        return pstn_enabled_str

    if pstn_dial_out_enabled.lower() == "false":
        pstn_enabled_str = "False"
    elif pstn_dial_out_enabled.lower() == "true":
        pstn_enabled_str = "True"

    return pstn_enabled_str


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
                                    pstn_dial_out_enabled=None,
                                    presenters=None,
                                    attendees=None,
                                    consumers=None,
                                    collaborators=None):
    try:
        room_participants = __to_room_participant(presenters, attendees, consumers, collaborators)
        pstn_dialed_out_enabled_str = __to_room_pstn_dial_out_enabled(pstn_dial_out_enabled)

        if pstn_dialed_out_enabled_str is None:
            pstn_dialed_out_enabled_str = "False"

        pstn_enabled = ast.literal_eval(pstn_dialed_out_enabled_str)

        return client.create_room(
            valid_from=valid_from,
            valid_until=valid_until,
            pstn_dial_out_enabled=pstn_enabled,
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
                                    pstn_dial_out_enabled=None):
    try:
        pstn_dialed_out_enabled_str = __to_room_pstn_dial_out_enabled(pstn_dial_out_enabled)
        pstn_enabled = None

        if pstn_dialed_out_enabled_str is not None:
            pstn_enabled = ast.literal_eval(pstn_dialed_out_enabled_str)

        return client.update_room(
            room_id=room_id,
            valid_from=valid_from,
            valid_until=valid_until,
            pstn_dial_out_enabled=pstn_enabled)
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_list_rooms(client):
    try:
        return client.list_rooms()
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_get_participants(client, room_id):
    try:
        return client.list_participants(room_id)
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_add_or_update_participants(client, room_id,
                                                   presenters=None,
                                                   attendees=None,
                                                   consumers=None,
                                                   collaborators=None):
    try:
        return client.add_or_update_participants(
            room_id=room_id,
            participants=__to_room_participant(presenters, attendees, consumers, collaborators))
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def communication_rooms_remove_participants(client, room_id, participants):
    try:
        return client.remove_participants(
            room_id=room_id,
            participants=__to_communication_identifier(participants))
    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def __get_attachment_content(filename, filetype, content_id=None):

    import json
    import os

    _, tail = os.path.split(filename)

    with open(filename, "rb") as file:
        file_bytes = file.read()
    file_bytes_b64 = base64.b64encode(file_bytes)

    attachment = {
        "name": tail,
        "contentType": filetype,
        "contentInBase64": file_bytes_b64.decode(),
    }

    if content_id is not None:
        attachment["contentId"] = content_id

    return json.dumps(attachment)


def prepare_attachments(attachments, attachment_types, inline_attachments):
    from knack.util import CLIError

    attachments_list = []

    if inline_attachments is None:
        inline_attachments = []

    if attachments is None:
        attachments = []

    if attachment_types is None:
        attachment_types = []

    if attachments is None and attachment_types is None:
        attachments_list = None
    elif len(attachments) + len(inline_attachments) != len(attachment_types):
        raise CLIError(
            f'Mismatch: {len(attachments)} standard attachments + '
            f'{len(inline_attachments)} inline attachments '
            f'does not equal {len(attachment_types)} attachment types.'
        )
    else:
        content_id = None
        # Process standard attachments
        for i, attachment in enumerate(attachments):
            attachment_content = __get_attachment_content(
                attachment,
                attachment_types[i],
                content_id
            )
            attachments_list.append(attachment_content)

        # Process inline attachments
        for j, inline_attachment in enumerate(inline_attachments):
            if inline_attachment.count('/') != 1:
                raise CLIError(
                    f'Incorrect format for inline attachment: {inline_attachment}. '
                    'Format should be: FileLocation/ContentId, example: "ImageName.png/image".'
                )
            attachment_name, content_id = inline_attachment.split('/')
            inline_attachment_type = attachment_types[len(attachments) + (j)]
            attachment_content = __get_attachment_content(
                attachment_name,
                inline_attachment_type,
                content_id
            )
            attachments_list.append(attachment_content)

    return attachments_list


def communication_email_send(client,
                             subject,
                             sender,
                             recipients_to=None,
                             disable_tracking=False,
                             text=None,
                             html=None,
                             importance='normal',
                             recipients_cc=None,
                             recipients_bcc=None,
                             reply_to=None,
                             attachments=None,
                             attachment_types=None,
                             inline_attachments=None,
                             waitUntil='completed'):

    import json
    from knack.util import CLIError
    import uuid

    try:

        if recipients_to is None and recipients_cc is None and recipients_bcc is None:
            raise CLIError('At least one recipient is required.')

        if importance == 'low':
            priority = '5'
        elif importance == 'high':
            priority = '1'
        else:
            priority = '3'

        attachments_list = prepare_attachments(attachments, attachment_types, inline_attachments)

        message = {
            "content": {
                "subject": subject,
                "plainText": text,
                "html": html
            },
            "recipients": {
                "to": None if recipients_to is None else [{"address": recipient}
                                                          for recipient in recipients_to[0].split(',')],
                "cc": None if recipients_cc is None else [{"address": recipient}
                                                          for recipient in recipients_cc[0].split(',')],
                "bcc": None if recipients_bcc is None else [{"address": recipient}
                                                            for recipient in recipients_bcc[0].split(',')]
            },
            "replyTo": None if reply_to is None else [{"address": reply_to}],
            "attachments": [] if attachments_list is None else [json.loads(attachment)
                                                                for attachment in attachments_list],
            "senderAddress": sender,
            "userEngagementTrackingDisabled": disable_tracking,
            "headers": {
                "x-priority": priority
            }
        }

        operationId = str(uuid.uuid4())

        poller = client.begin_send(message, operation_id=operationId)

        if waitUntil == 'started' or waitUntil == '1':
            print("Email send started")
            print(f"Operation id : {operationId}, status : {poller.status()} ")
        elif waitUntil == 'completed' or waitUntil == '0':
            # Wait until the email is sent and get the result
            return poller
        else:
            raise ValueError("Invalid value for waitUntil. Expected 'started' or 'completed'.")

    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))


def parse_connection_string(connection_string):
    """
    Parse the connection string to extract the endpoint and API key.
    """
    params = {}
    for item in connection_string.split(';'):
        key, value = item.split('=', 1)
        params[key.strip()] = value.strip()

    api_endpoint = params.get('endpoint')
    api_key = params.get('accesskey')

    if not api_endpoint or not api_key:
        raise ValueError("Connection string is missing required parameters.")

    return api_endpoint, api_key


def create_signature_header(method, url, host, api_key):

    date_str = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    hashed_body = hashlib.sha256(b'').digest()
    hashed_body_base64 = base64.b64encode(hashed_body).decode('utf-8')

    string_to_sign = f"{method}\n{url}\n{date_str};{host};{hashed_body_base64}"
    signing_key = base64.b64decode(api_key)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).digest()
    signature_base64 = base64.b64encode(signature).decode('utf-8')

    headers = {
        'x-ms-date': date_str,
        'x-ms-content-sha256': hashed_body_base64,
        'Authorization': f"HMAC-SHA256 SignedHeaders=x-ms-date;host;x-ms-content-sha256&Signature={signature_base64}"
    }

    return headers


def communication_email_get_status(connection_string, operation_id):
    try:
        api_endpoint, api_key = parse_connection_string(connection_string)

        status_endpoint = f"{api_endpoint}emails/operations/{operation_id}?api-version=2023-03-31"

        method = "GET"
        url = f'/emails/operations/{operation_id}?api-version=2023-03-31'
        parsed_url = urlparse(api_endpoint)
        host = parsed_url.netloc

        headers = create_signature_header(method, url, host, api_key)

        response = requests.get(status_endpoint, headers=headers)

        if response.status_code == 200:
            return response.json()

        response.raise_for_status()

    except HttpResponseError:
        raise
    except Exception as ex:
        sys.exit(str(ex))
