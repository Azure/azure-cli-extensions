# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# This file contains recording processors which are used to modify the testing recordings
# before they are saved to file. This is useful for removing sensitive information from
# the recordings so that we can avoid checking in secrets to the repo.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.scenario_tests import RecordingProcessor
from azure.cli.testsdk.scenario_tests.utilities import is_text_payload
import json
import re

MOCK_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
MOCK_SAS_URI = "https://xxxxxxxxxxxxxxx.blob.core.windows.net"
MOCK_STORAGE_ACCOUNT_SR = "&si=StorageAccountAccessPolicy&sr=xxxxxxxxxxxxxxxxxxxx"
BLOB_STORE_URI_REGEX = r"https:\/\/[a-zA-Z0-9]+\.blob\.core\.windows\.net"
STORAGE_ACCOUNT_SR_REGEX = r"&si=StorageAccountAccessPolicy&sr=.*"


class TokenReplacer(RecordingProcessor):
    def process_response(self, response):
        ACR_TOKEN = "acrToken"
        ACCESS_TOKEN = "access_token"
        if is_text_payload(response) and response["body"]["string"]:
            try:
                response_body = json.loads(response["body"]["string"])
                if ACR_TOKEN in response_body:
                    response_body[ACR_TOKEN] = MOCK_TOKEN
                if ACCESS_TOKEN in response_body:
                    response_body[ACCESS_TOKEN] = MOCK_TOKEN
                response["body"]["string"] = json.dumps(response_body)
            except TypeError:
                pass
        return response


class SasUriReplacer(RecordingProcessor):
    def process_response(self, response):
        CONTAINER_CREDENTIALS = "containerCredentials"
        CONTAINER_SAS_URI = "containerSasUri"
        if not (is_text_payload(response) and response["body"]["string"]):
            return response

        response_body = json.loads(response["body"]["string"])
        try:
            if CONTAINER_CREDENTIALS not in response_body:
                return response

            credentials_list = response_body[CONTAINER_CREDENTIALS]
            new_credentials_list = []

            for credential in credentials_list:
                if CONTAINER_SAS_URI in credential:
                    credential[CONTAINER_SAS_URI] = re.sub(
                        BLOB_STORE_URI_REGEX,
                        MOCK_SAS_URI,
                        credential[CONTAINER_SAS_URI],
                    )
                    credential[CONTAINER_SAS_URI] = re.sub(
                        STORAGE_ACCOUNT_SR_REGEX,
                        MOCK_STORAGE_ACCOUNT_SR,
                        credential[CONTAINER_SAS_URI],
                    )
                new_credentials_list.append(credential)

            response_body[CONTAINER_CREDENTIALS] = new_credentials_list
            response["body"]["string"] = json.dumps(response_body)
        except TypeError:
            pass

        return response


class BlobStoreUriReplacer(RecordingProcessor):
    def process_request(self, request):
        try:
            request.uri = re.sub(BLOB_STORE_URI_REGEX, MOCK_SAS_URI, request.uri)
            request.uri = re.sub(
                STORAGE_ACCOUNT_SR_REGEX, MOCK_STORAGE_ACCOUNT_SR, request.uri
            )

        except TypeError:
            pass

        return request
