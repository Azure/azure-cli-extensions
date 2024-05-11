# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import os
import math
import base64
from knack.log import get_logger

logger = get_logger(__name__)

# costants for file upload
max_chunk_size = 1024 * 1024 * 2.5  # 2.5MB


def is_billing_ticket(service_name):
    return "517f2da6-78fd-0498-4e22-ad26996b1dfc" in service_name


def is_quota_ticket(service_name):
    return "06bfd9d3-516b-d5c6-5802-169c800dec89" in service_name


def is_subscription_mgmt_ticket(service_name):
    return "f3dc5421-79ef-1efa-41a5-42bf3cbb52c6" in service_name


def is_technical_ticket(service_name):
    return (not is_billing_ticket(service_name)) and \
           (not is_quota_ticket(service_name)) and \
           (not is_subscription_mgmt_ticket(service_name))


def parse_support_area_path(problem_classification_id):
    service_id_prefix = "/providers/Microsoft.Support/services/".lower()
    guid_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    sap_regex = re.compile('^{0}({1})/problemclassifications/({1})$'.format(service_id_prefix, guid_regex))
    match = sap_regex.search(problem_classification_id.lower())

    if match is not None and len(match.groups()) == 2:
        return {"service_name": match.group(1), "problem_classifications_name": match.group(2)}

    return None


def encode_string_content(chunk_content):
    return str(base64.b64encode(chunk_content).decode("utf-8"))


def get_file_content(file_path):
    with open(file_path, "rb") as file:
        content_bytes = file.read()
    return content_bytes


def get_file_name_info(file_path):
    full_file_name = os.path.split(file_path)[1]
    file_name_without_extension, file_extension = os.path.splitext(full_file_name)
    return full_file_name, file_name_without_extension, file_extension


def upload_file(
    cmd,
    file_path,
    file_workspace_name,
    Create,
    Upload,
):
    from azext_support._validators import _validate_file_path, _validate_file_size
    from azext_support._validators import _validate_file_extension, _validate_file_name

    _validate_file_path(file_path)

    full_file_name, file_name_without_extension, file_extension = get_file_name_info(
        file_path
    )
    _validate_file_extension(file_extension)
    _validate_file_name(file_name_without_extension)

    content = get_file_content(file_path)

    file_size = int(len(content))
    _validate_file_size(file_size)

    chunk_size = int(min(max_chunk_size, file_size))
    number_of_chunks = int(math.ceil(file_size / chunk_size))

    create_input = {
        "file_name": full_file_name,
        "file_workspace_name": file_workspace_name,
        "file_size": file_size,
        "chunk_size": chunk_size,
        "number_of_chunks": number_of_chunks,
    }

    Create(cli_ctx=cmd.cli_ctx)(command_args=create_input)

    for chunk_index in range(number_of_chunks):
        chunk_content = content[
            chunk_index * chunk_size: (chunk_index + 1) * chunk_size
        ]
        string_encoded_content = encode_string_content(chunk_content)

        upload_input = {
            "file_name": full_file_name,
            "file_workspace_name": file_workspace_name,
            "chunk_index": chunk_index,
            "content": string_encoded_content,
        }

        Upload(cli_ctx=cmd.cli_ctx)(command_args=upload_input)
    print("File '{}' has been successfully uploaded.".format(full_file_name))
