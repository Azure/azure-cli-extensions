# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def datetime_type(string):
    """ Validate UTC datettime in accepted format. Examples: 31-12-2017, 31-12-2017-05:30:00 """
    accepted_date_formats = ['%Y-%m-%dT%H:%M:%S']
    for form in accepted_date_formats:
        try:
            return string + ".0000000Z"
        except ValueError:  # checks next format
            pass
    raise ValueError("Input '{}' not valid. Valid example:2017-12-31T05:30:00".format(string))


def schedule_days_type(string):
    accepted_date_formats = ['%Y-%m-%dT%H:%M:%S']
    for form in accepted_date_formats:
        try:
            return string
        except ValueError:  # checks next format
            pass
    raise ValueError("Input '{}' not valid. Valid example: 2017-12-31T05:30:00".format(string))
