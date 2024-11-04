# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError

def capacity(cmd, api_version, model_format, model_name, model_version):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from azure.cli.core._profile import Profile
    subscription=get_subscription_id(cmd.cli_ctx)
    access_token = Profile(cli_ctx=cmd.cli_ctx).get_raw_token()[0][2].get("accessToken")
    print("subscription: " + subscription)
    result = list_modelCapacities(subscription, api_version, model_format, model_name, model_version, access_token)
    return result

def list_modelCapacities(subscription_id, api_version, model_format, model_name, model_version, access_token):
    import requests
    import json
    based_url = f"https://management.azure.com/subscriptions/"
    url_api = f"{subscription_id}/providers/Microsoft.CognitiveServices/modelCapacities"
    params1 = f"?api-version={api_version}&modelFormat={model_format}"
    params2 = f"&modelName={model_name}&modelVersion={model_version}"
    url = f"{based_url}{url_api}{params1}{params2}" 
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    params = {
        "modelFormat": model_format,
        "modelName": model_name,
        "modelVersion": model_version
    }
    #print(url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        extracted_data = [
            {
                'location': item['location'],
                'skuName': item['properties']['skuName'],
                'availableCapacity': item['properties']['availableCapacity']
            }
            for item in data['value']
        ]
        return extracted_data
    else:
        return {"error": response.status_code, "message": response.text}