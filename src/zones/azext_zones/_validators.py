# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re


def validate_command_args(namespace):
    # Validate resource group input:
    if not is_valid_resource_group_list(namespace.resource_group_names):
        raise ValueError(
            "Resource Groups must be single resource group name or a comma-separated list of valid resource groups"
        )

    # Validate tags input:
    if not is_valid_tags_list(namespace.tags):
        raise ValueError(
            "Tags must be a comma-separated list of key-value pairs in the format 'key=value'"
        )


def is_valid_resource_group_list(input_string):
    if input_string is None:
        return True
    pattern = r"^(?!.*\.\.)(?!.*\.$)[\w\-\.\(\)]{1,90}$"
    names = [name.strip() for name in input_string.split(",")]
    return all(re.match(pattern, name, re.IGNORECASE) for name in names)


def is_valid_tags_list(input_string):
    if input_string is None:
        return True
    tag_pattern = r"^[^=,\s][^=,]{0,510}=[^=,]{0,256}$"
    tags = [tag.strip() for tag in input_string.split(",")]
    return all(re.match(tag_pattern, tag) for tag in tags)
