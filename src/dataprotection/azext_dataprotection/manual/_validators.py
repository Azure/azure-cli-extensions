# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.validators import (
    validate_file_or_dict
)
from dateutil import parser


def datetime_type(string):
    """ Validate UTC datettime in accepted format. Examples: 31-12-2017, 31-12-2017-05:30:00 """
    # accepted_date_formats = ['%Y-%m-%dT%H:%M:%S']
    try:
        newtime = parser.isoparse(string).strftime("%Y-%m-%dT%H:%M:%S.%f") + "0Z"
        return newtime
    except ValueError:  # checks next format
        pass
    raise ValueError(f"Input '{string}' not valid. Valid example:2017-12-31T05:30:00")


def schedule_days_type(string):
    # accepted_date_formats = ['%Y-%m-%dT%H:%M:%S']
    try:
        return string
    except ValueError:  # checks next format
        pass
    raise ValueError(f"Input '{string}' not valid. Valid example: 2017-12-31T05:30:00")


def namespaced_name_resource_type(list_of_dict):
    try:
        list_of_dict = validate_file_or_dict(list_of_dict)
        for dictionary in list_of_dict:
            if not (len(dictionary) == 2 and 'name' in dictionary and 'namespace' in dictionary):
                raise ValueError(f"Input {list_of_dict} is not valid. Keys should be 'name' and 'namespace'.")
        return list_of_dict
    except ValueError:
        pass
    raise ValueError(f"Input {list_of_dict} is not valid.")
