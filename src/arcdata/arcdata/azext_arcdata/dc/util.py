# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import json
import os

import azext_arcdata.dc.constants as instance_properties
from azext_arcdata.core.configuration import Configuration
from azext_arcdata.core.prompt import prompt, prompt_y_n
from azext_arcdata.core.util import display
from azext_arcdata.arm_sdk.azure import constants as azure_constants
from knack.log import get_logger
from knack.prompting import NoTTYException

logger = get_logger(__name__)


def get_config_file_path(filename):
    logger.debug("get_config_file_path: %s", filename)
    logger.debug(
        os.path.join(
            Configuration().extension_dir,
            "{}-{}".format(Configuration().EXT_NAME, filename),
        )
    )

    return os.path.join(
        Configuration().extension_dir,
        "{}-{}".format(Configuration().EXT_NAME, filename),
    )


def get_config_file(filename, throw_exception=True):
    query_file = get_config_file_path(filename)
    query_file_exists = os.path.exists(query_file)

    if not query_file_exists and throw_exception:
        raise ValueError('Please make sure "{}" exists'.format(query_file))
    return query_file


# ##############################################################################
# Metric/log common functions
# ##############################################################################


def get_resource_uri(resource, data_controller):
    resource_kind = resource[instance_properties.KIND]

    if resource_kind in azure_constants.RESOURCE_TYPE_FOR_KIND:
        return azure_constants.RESOURCE_URI.format(
            data_controller[instance_properties.SUBSCRIPTION_ID],
            data_controller[instance_properties.RESOURCE_GROUP],
            azure_constants.RESOURCE_TYPE_FOR_KIND[resource_kind],
            resource[instance_properties.INSTANCE_NAME],
        )
    else:
        display(
            '"{}" instance type "{}" is not supported.'.format(
                resource[instance_properties.INSTANCE_NAME], resource_kind
            )
        )
        return None


def get_output_file(file_path, force):
    # Check export file exists or not
    msg = "Please provide a file name with the path: "
    export_file_exists = True
    overwritten = False

    while export_file_exists and not overwritten:
        export_file_exists = os.path.exists(file_path)
        if not force and export_file_exists:
            try:
                yes = prompt_y_n(
                    "{} exists already, do you want to overwrite it?".format(
                        file_path
                    )
                )
            except NoTTYException as e:
                raise NoTTYException(
                    "{} Please make sure the file does not exist in a "
                    "non-interactive environment".format(e)
                )

            overwritten = True if yes else False

            if not overwritten:
                file_path = prompt(msg)
                export_file_exists = True
                overwritten = False
            else:
                os.remove(file_path)
        elif force:
            overwritten = True
            if export_file_exists:
                os.remove(file_path)

    return file_path


def write_file(file_path, data, export_type, data_timestamp=None):
    result = {
        "exportType": export_type,
        "dataTimestamp": data_timestamp,
        "data": data,
    }
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, indent=4)

    output_type = export_type
    display(
        "\t\t{} are exported to {}.".format(output_type.capitalize(), file_path)
    )


def write_output_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(content, json_file, indent=4)
