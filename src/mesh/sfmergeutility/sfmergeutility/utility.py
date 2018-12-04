# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import enum
import json
import os

class ResourceType(enum.Enum):
    """ Defines the valid yaml resource types
        which are parseable by CLI
    """
    application = 1
    volume = 2
    network = 3
    secret = 4
    secretValue = 5
    gateway = 6

def list_files_in_directory(directory, extension):
    """ List files of a directory (relative/absolute) path recursively w.r.t the extension provided"""
    file_path_list = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extension):
                file_path_list.append(os.path.join(root, filename))
    return file_path_list

def get_resource_type(file_path):
    """ Gets the resource type form the relative/absolute file path"""
    file_name = os.path.basename(file_path)
    file_name_split = file_name.split('_')
    if len(file_name_split) < 3:
        raise Exception('Invalid resource file name "%s". The file name should have format id_resourcetype_resourcename.json' %(file_name)) # pylint: disable=line-too-long
    resource_type = file_name_split[1]
    try:
        return ResourceType[resource_type]
    except:
        raise Exception('The resource type "%s" is unknown' %(resource_type))

def get_resource_name(file_path):
    """ Gets resource name form the relative/absolute file path"""
    file_name = os.path.basename(file_path)
    file_name_split = file_name.split('_')
    if len(file_name_split) < 3:
        raise Exception('Invalid resource file name "%s". The file name should have format id_resourcetype_resourcename.json' %(file_name)) # pylint: disable=line-too-long
    resource_name_with_extension = file_name_split[2]
    resource_name = resource_name_with_extension.split('.')
    return resource_name[0]

def load_json(file_path):
    """ Converts the yaml content to json object from the relative/absolute file path
    """
    with open(file_path, 'r') as file_pointer:
        content = file_pointer.read()
        try:
            json_obj = json.loads(json.loads(json.dumps(content)))
        except:
            raise Exception('The "%s" is not a valid json' %(file_path))
    return json_obj
