# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.communication.identity import CommunicationUserIdentifier


def issue_access_token(client, scopes, userid=None):
    user_token_data = {"user_id": userid, "token": "", "expires_on": ""}
    if userid is not None:
        user = CommunicationUserIdentifier(userid)
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


def communication_send_sms(client, sender, recipients, message):
    return client.send(from_=sender, to=recipients, message=message)


def communication_list_phonenumbers(client):
    return client.list_purchased_phone_numbers()


def communication_show_phonenumber(client, phonenumber):
    return client.get_purchased_phone_number(phonenumber)
