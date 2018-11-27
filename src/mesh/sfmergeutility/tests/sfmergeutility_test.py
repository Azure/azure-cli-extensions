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
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'sfmergeutility')))
from sfmergeutility import SFMergeUtility
from sfmergeutility.utility import get_resource_type, get_resource_name, list_files_in_directory, ResourceType


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
        SFMergeUtility.sf_merge_utility(yaml_file_path_list, "SF_SBZ_JSON", parameters=None, output_dir=output_dir, prefix="resource", region="westus") # pylint: disable=line-too-long
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
        SFMergeUtility.sf_merge_utility(yaml_file_path_list, "SF_SBZ_RP_JSON", parameters=None, output_dir=None, prefix="merged-", region="westus") # pylint: disable=line-too-long
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

    def test_resource_type(self):
        """Test if resource type is correctly identified or not"""
        resource_type = get_resource_type("merged-0006_application_counterApp-AZFiles.json")  # pylint: disable=line-too-long
        self.assertEqual(resource_type, ResourceType.application)
        resource_type = get_resource_type("merged-0001_secret_azurefilesecret.json")
        self.assertEqual(resource_type, ResourceType.secret)
        resource_type = get_resource_type("merged-0002_secretValue_azurefilesecret_v1.json")  # pylint: disable=line-too-long
        self.assertEqual(resource_type, ResourceType.secretValue)
        resource_type = get_resource_type("merged-0003_volume_counterVolumeWindows.json")  # pylint: disable=line-too-long
        self.assertEqual(resource_type, ResourceType.volume)
        resource_type = get_resource_type("merged-0004_network_counterAppNetwork.json")
        self.assertEqual(resource_type, ResourceType.network)
        resource_type = get_resource_type("merged-0005_gateway_counterAppGateway.json")
        self.assertEqual(resource_type, ResourceType.gateway)
        with self.assertRaises(Exception):
            resource_type = get_resource_type("merged-0005_something_counterAppGateway.json")  # pylint: disable=line-too-long
        with self.assertRaises(Exception):
            resource_type = get_resource_type("invalid-file-name.json")

    def test_resource_name(self):
        """Test if resource name is correctly identified or not"""
        resource_name = get_resource_name("merged-0006_application_counterApp-AZFiles.json")  # pylint: disable=line-too-long
        self.assertEqual("counterApp-AZFiles", resource_name)
        with self.assertRaises(Exception):
            resource_name = get_resource_type("invalid-file-name.json")

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
