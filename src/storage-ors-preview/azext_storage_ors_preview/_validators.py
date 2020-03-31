# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
from azure.cli.core.util import get_file_json, shell_safe_json_parse


def validate_ors_policy(namespace):
    error_elements = []
    if namespace.properties is None:
        error_msg = "Please provide --policy in JSON format or the following arguments: "
        if namespace.source_account is None:
            error_elements.append("--source-account")
        if namespace.destination_account is None:
            error_elements.append("--destination-account")

        if error_elements:
            error_msg += ", ".join(error_elements)
            error_msg += " to initialize ORS Policy for storage account."
            raise ValueError(error_msg)
    else:
        if os.path.exists(namespace.properties):
            ors_policy = get_file_json(namespace.properties)
        else:
            ors_policy = shell_safe_json_parse(namespace.properties)

        try:
            namespace.source_account = ors_policy["sourceAccount"]
        except KeyError:
            namespace.source_account = ors_policy["source_account"]
        if namespace.source_account is None:
            error_elements.append("source_account")

        try:
            namespace.destination_account = ors_policy["destinationAccount"]
        except KeyError:
            namespace.destination_account = ors_policy["destination_account"]
        if namespace.source_account is None:
            error_elements.append("destination_account")

        if "rules" not in ors_policy.keys() or not ors_policy["rules"]:
            error_elements.append("rules")
        error_msg = "Missing input parameters: "
        if error_elements:
            error_msg += ", ".join(error_elements)
            error_msg += " in properties to initialize ORS Policy for storage account."
            raise ValueError(error_msg)
        namespace.properties = ors_policy

        if "policyId" in ors_policy.keys() and ors_policy["policyId"]:
            namespace.policy_id = ors_policy['policyId']


def get_datetime_type(to_string):
    """ Validates UTC datetime. Examples of accepted forms:
    2017-12-31T01:11:59Z,2017-12-31T01:11Z or 2017-12-31T01Z or 2017-12-31 """
    from datetime import datetime

    def datetime_type(string):
        """ Validates UTC datetime. Examples of accepted forms:
        2017-12-31T01:11:59Z,2017-12-31T01:11Z or 2017-12-31T01Z or 2017-12-31 """
        accepted_date_formats = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%MZ',
                                 '%Y-%m-%dT%HZ', '%Y-%m-%d']
        target_format = '%Y-%m-%dT%H:%M:%SZ'
        for form in accepted_date_formats:
            try:
                if to_string:
                    return datetime.strptime(string, form).strftime(target_format)

                return datetime.strptime(string, form)
            except ValueError:
                continue
        raise ValueError("Input '{}' not valid. Valid example: 2000-12-31T12:59:59Z".format(string))

    return datetime_type
