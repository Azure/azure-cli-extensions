from azure.communication.identity import CommunicationUserIdentifier

def issue_access_token(client, scopes, id=None):
    user_token_data = {"user_id": id, "token": "", "expires_on": ""}
    if id is not None:
        user = CommunicationUserIdentifier(id)
        token_data = client.get_token(user, scopes)
        user_token_data["token"]=token_data.token
        user_token_data["expires_on"]=str(token_data.expires_on)
    else:
        identity_token_result  = client.create_user_and_token(scopes)
        if len(identity_token_result)>=2:
            user_token_data["user_id"]=identity_token_result[0].properties['id']
            user_token_data["token"]=identity_token_result[1].token
            user_token_data["expires_on"]=str(identity_token_result[1].expires_on)

    return user_token_data

def communication_send_sms(client, sender, recipient, message):
    return client.send(from_=sender, to=recipient, message=message)

def communication_list_phonenumbers(client):
    return client.list_purchased_phone_numbers()

def communication_show_phonenumber(client, phone_number):
    return client.get_purchased_phone_number(phone_number)