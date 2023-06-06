# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
import configparser
import requests
import re
import csv
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from azext_command_change._const import CONFIG_FILE_PATH, CHANGE_RULE_MESSAGE_MAPPING, CHANGE_SUGGEST_MESSAGE_MAPPING, \
    EXPORTED_CSV_META_HEADER, DOWNLOAD_THREADS
from knack.log import get_logger
logger = get_logger(__name__)


MODULE_NAME_PATTERN = re.compile(r"az_([a-zA-Z0-9\-\_]+)_meta.json")
SUBGROUP_NAME_PATTERN = re.compile(r"\[\'sub_groups\'\]\[\'([a-zA-Z0-9\-\s]+)\'\]")
CMD_NAME_PATTERN = re.compile(r"\[\'commands\'\]\[\'([a-zA-Z0-9\-\s]+)\'\]")
CMD_PARAMETER_PROPERTY_PATTERN = re.compile(r"\[(.*?)\]")


def load_blob_config_file():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config


def get_blob_config(config):
    blob_url = config.get("BLOB", "primary_endpoint")
    meta_path_prefix = config.get("BLOB", "metadata_path_prefix")
    index_file = config.get("BLOB", "metadata_module_index_file")
    return blob_url, meta_path_prefix, index_file


def get_change_rule_template(rule_id="1000"):
    """ Return the rule message template"""
    return CHANGE_RULE_MESSAGE_MAPPING.get(rule_id, "Non applicable")


def get_change_suggest_template(rule_id="1000"):
    """ Return the change suggest message template"""
    return CHANGE_SUGGEST_MESSAGE_MAPPING.get(rule_id, "Non applicable")


class ChangeType(int, Enum):
    DEFAULT = 0
    ADD = 1
    CHANGE = 2
    REMOVE = 3


def get_command_tree(command_name):
    """
    input: monitor log-profiles create
    ret:
    {
        is_group: True,
        group_name: 'monitor',
        sub_info: {
            is_group: True,
            group_name: 'monitor log-profiles',
            sub_info: {
                is_group: False,
                cmd_name: 'monitor log-profiles create'
            }
        }
    }
    """
    name_arr = command_name.split()
    ret = {}
    name_arr.reverse()
    for i, _ in enumerate(name_arr):
        tmp = {}
        if i == 0:
            tmp = {
                "is_group": False,
                "cmd_name": " ".join(name_arr[::-1])
            }
        else:
            tmp = {
                "is_group": True,
                "group_name": " ".join(name_arr[len(name_arr): (i - 1): -1]),
                "sub_info": ret
            }
        ret = tmp
    return ret


def module_meta_file_downloader(meta_file_url, meta_file_save_path, module_file):
    print("Downloading {0} for {1}".format(meta_file_url, module_file))
    try:
        res = requests.get(meta_file_url)
        with open(meta_file_save_path, "w") as f:
            f.write(json.dumps(res.json(), indent=4))
    except Exception as e:
        print(str(e))


def get_target_version_modules(blob_url, path_prefix, index_file, version):
    version_meta_path = path_prefix + version
    version_meta_index_file = blob_url + "/" + version_meta_path + "/" + index_file
    version_meta_module_file_list = []
    try:
        res = requests.get(version_meta_index_file)
        module_file_list = res.text.split("\n")
        version_meta_folder = os.getcwd() + "/" + version_meta_path
        if not os.path.exists(version_meta_folder):
            os.makedirs(version_meta_folder)
        version_meta_module_file_list = [(blob_url + "/" + version_meta_path + "/" + module_file,
                                          version_meta_folder + "/" + module_file,
                                          module_file) for module_file in module_file_list if module_file]
        with ThreadPoolExecutor(max_workers=DOWNLOAD_THREADS) as pool:
            download_module_jobs = [pool.submit(module_meta_file_downloader, _url, _save_path, module_file)
                                    for _url, _save_path, module_file in version_meta_module_file_list]
            wait(download_module_jobs, return_when=ALL_COMPLETED)
    except Exception as e:
        print(str(e))
    finally:
        return version_meta_module_file_list


def extrct_module_name_from_meta_file(file_name):
    name_res = re.findall(MODULE_NAME_PATTERN, file_name)
    if not name_res or len(name_res) == 0:
        return None
    return name_res[0]


def extract_subgroup_name(key):
    subgroup_ame_res = re.findall(SUBGROUP_NAME_PATTERN, key)
    if not subgroup_ame_res or len(subgroup_ame_res) == 0:
        return False, None
    return True, subgroup_ame_res[-1]


def extract_cmd_name(key):
    cmd_name_res = re.findall(CMD_NAME_PATTERN, key)
    if not cmd_name_res or len(cmd_name_res) == 0:
        return False, None
    return True, cmd_name_res[0]


def extract_cmd_property(key, cmd_name):
    cmd_key_pattern = re.compile(cmd_name + r"\'\]\[\'([a-zA-Z0-9\-\_]+)\'\]")
    cmd_key_res = re.findall(cmd_key_pattern, key)
    if not cmd_key_res or len(cmd_key_res) == 0:
        return False, None
    return True, cmd_key_res[0]


def extract_para_info(key):
    parameters_ind = key.find("['parameters']")
    property_ind = key.find("[", parameters_ind + 1)
    property_res = re.findall(CMD_PARAMETER_PROPERTY_PATTERN, key[property_ind:])
    if not property_res:
        return None
    return property_res


def export_meta_changes_to_json(output, output_file):
    if not output_file:
        return output
    output_file_folder = os.path.dirname(output_file)
    if output_file_folder and not os.path.exists(output_file_folder):
        os.makedirs(output_file_folder)
    with open(output_file, "w") as f_out:
        if output:
            f_out.write(json.dumps(output, indent=4))
    return None


def format_module_diff_csv(module_diffs):
    csv_res = [EXPORTED_CSV_META_HEADER]
    for diff_obj in module_diffs:
        _row = []
        for attr in EXPORTED_CSV_META_HEADER:
            if attr == "cmd_name":
                _row.append(diff_obj.get(attr, None) or diff_obj.get("subgroup_name", "-"))
            else:
                _row.append(diff_obj.get(attr, None))
        csv_res.append(_row)
    return csv_res


def export_meta_changes_to_csv(module_diffs, version_diff_file):
    csv_res = format_module_diff_csv(module_diffs)
    if not version_diff_file:
        return csv_res
    diff_file_folder = os.path.dirname(version_diff_file)
    if diff_file_folder and not os.path.exists(diff_file_folder):
        os.makedirs(diff_file_folder)
    with open(version_diff_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_res)
    return None


if __name__ == "__main__":
    get_target_version_modules("https://versionmeta.z13.web.core.windows.net/", "azure-cli-", "index.txt", "2.49.0")