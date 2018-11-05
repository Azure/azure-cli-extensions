# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Custom mesh command tests"""

import enum
import unittest
import json
import os
import shutil
from sfmergeutility import SFMergeUtility

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

class SFMergeUtilityTests(unittest.TestCase):
    """SF Merge utility tests """

    sample_json_path = os.path.join(os.path.dirname(__file__), 'sample_json')
    sample_yaml_path = os.path.join(os.path.dirname(__file__), 'sample_yaml')
    local_deployment_folder_name = "meshDeploy"
    arm_template_file_name = 'merged-arm_rp.json'

    def test_merge_utility_local(self):
        """Test if merge utility is generating the correct jsons"""
        yaml_file_path_list = list_files_in_directory(self.sample_yaml_path, ".yaml")
        output_dir = os.path.join(os.path.dirname(__file__), self.local_deployment_folder_name)
        SFMergeUtility.sf_merge_utility(yaml_file_path_list, "SF_SBZ_JSON", parameter_file=None, output_dir=output_dir, prefix="resource", region="westus") # pylint: disable=line-too-long
        generated_json_files = list_files_in_directory(output_dir, ".json")
        actual_json_files = list_files_in_directory(self.sample_json_path, ".json")
        del actual_json_files[actual_json_files.index(os.path.join(self.sample_json_path, self.arm_template_file_name))]
        for generated_json_file in generated_json_files:
            generated_json_file_fp = open(generated_json_file, "r")
            generated_json = json.load(generated_json_file_fp)
            generated_json_file_fp.close()
            actual_json_file = get_actual_json_file(actual_json_files, generated_json_file)
            actual_json_file_fp = open(actual_json_file, "r")
            actual_json = json.load(actual_json_file_fp)
            actual_json_file_fp.close()
            self.assertEqual(ordered_json(generated_json), ordered_json(actual_json))
        shutil.rmtree(output_dir, ignore_errors=True)

    def test_merge_utility_cloud(self):
        """Test if merge utility if is generating the correct ARM template"""
        yaml_file_path_list = list_files_in_directory(self.sample_yaml_path, ".yaml")
        output_file_path = os.path.join(os.getcwd(), self.arm_template_file_name)
        SFMergeUtility.sf_merge_utility(yaml_file_path_list, "SF_SBZ_RP_JSON", parameter_file=None, output_dir=None, prefix="merged-", region="westus") # pylint: disable=line-too-long
        generated_json_file_fp = open(output_file_path, "r")
        generated_json = json.load(generated_json_file_fp)
        generated_json_file_fp.close()
        actual_json_file = os.path.join(self.sample_json_path, self.arm_template_file_name)
        actual_json_file_fp = open(actual_json_file, "r")
        actual_json = json.load(actual_json_file_fp)
        actual_json_file_fp.close()
        self.assertEqual(ordered_json(generated_json), ordered_json(actual_json))
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

def list_files_in_directory(directory, extension):
    """ List files of a directory recursively w.r.t the extension provided"""
    file_path_list = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extension):
                file_path_list.append(os.path.join(root, filename))
    return file_path_list

def get_resource_type(file_name):
    """ Gets the resource type form the file name"""
    file_name = os.path.basename(file_name)
    file_name_splitted = file_name.split('_')
    if len(file_name_splitted) < 3:
        raise Exception('Invalid resource file name %s. The file name should be of format id_resourcetype_resourcename.json' %(file_name)) # pylint: disable=line-too-long
    resource_type = file_name_splitted[1]
    try:
        return ResourceType[resource_type]
    except:
        raise Exception('The resource type %s is unknown' %(resource_type))

def get_resource_name(file_name):
    """ Gets resource name form the file name"""
    file_name = os.path.basename(file_name)
    file_name_splitted = file_name.split('_')
    if len(file_name_splitted) < 3:
        raise Exception('Invalid resource file name %s. The file name should be of format id_resourcetype_resourcename.json' %(file_name)) # pylint: disable=line-too-long
    file_name_with_extension = file_name_splitted[2]
    resource_name = file_name_with_extension.split('.')
    return resource_name[0]

def get_actual_json_file(actual_json_files, generated_json_file):
    """Gets the actual json file w.r.t the generated json file"""
    resource_name = get_resource_name(generated_json_file)
    generated_resource_type = get_resource_type(generated_json_file)
    return_file = None
    for actual_json_file in actual_json_files:
        actual_resource_type = get_resource_type(actual_json_file)
        if resource_name in actual_json_file and generated_resource_type == actual_resource_type: # pylint: disable=line-too-long
            return_file = actual_json_file
            break
    return return_file

def ordered_json(json_dict):
    """Creates a ordered json for comparison"""
    if isinstance(json_dict, dict):
        return sorted((k, ordered_json(v)) for k, v in json_dict.items())
    if isinstance(json_dict, list):
        return sorted(ordered_json(x) for x in json_dict)
    return json_dict

if __name__ == "__main__":
    unittest.main()
