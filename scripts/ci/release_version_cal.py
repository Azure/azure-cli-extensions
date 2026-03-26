#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
import os
import re
import json
import subprocess
from packaging.version import parse

from azdev.utilities.path import get_cli_repo_path, get_ext_repo_paths
from azdev.operations.extensions import cal_next_version
from azdev.operations.constant import (PREVIEW_INIT_SUFFIX, VERSION_MAJOR_TAG, VERSION_MINOR_TAG,
                                       VERSION_PATCH_TAG, VERSION_STABLE_TAG, VERSION_PREVIEW_TAG, VERSION_PRE_TAG)
from util import get_index_data

base_meta_path = os.environ.get('base_meta_path', None)
diff_meta_path = os.environ.get('diff_meta_path', None)
result_path = os.environ.get('result_path', None)
output_file = os.environ.get('output_file', None)
add_labels_file = os.environ.get('add_labels_file', None)
remove_labels_file = os.environ.get('remove_labels_file', None)
pr_user = os.environ.get('pr_user', "")

changed_module_list = os.environ.get('changed_module_list', "").split()
diff_code_file = os.environ.get('diff_code_file', "")
print("diff_code_file:", diff_code_file)
pr_label_list = os.environ.get('pr_label_list', "")
pr_label_list = [name.lower().strip().strip('"').strip("'") for name in json.loads(pr_label_list)]

DEFAULT_VERSION = "0.0.0"
INIT_RELEASE_VERSION = "1.0.0b1"
DEFAULT_MESSAGE = " - For more info about extension versioning, please refer to [Extension version schema](https://github.com/Azure/azure-cli/blob/release/doc/extensions/versioning_guidelines.md)"
block_pr = 0

cli_ext_path = get_ext_repo_paths()[0]
print("get_cli_repo_path: ", get_cli_repo_path())
print("get_ext_repo_paths: ", cli_ext_path)


def extract_module_history_update_info(mod_update_info, mod):
    """
    re pattern:
    --- a/src/monitor-control-service/HISTORY.(rst|md)
    +++ b/src/monitor-control-service/HISTORY.(rst|md)
    """
    mod_update_info["history_updated"] = False
    module_history_update_pattern = re.compile(r"\+\+\+.*?src/%s/HISTORY\.(rst|md)" % mod)
    with open(diff_code_file, "r") as f:
        for line in f:
            mod_history_update_match = re.findall(module_history_update_pattern, line)
            if mod_history_update_match:
                mod_update_info["history_updated"] = True


def extract_module_version_update_info(mod_update_info, mod):
    """
    re pattern:
    --- a/src/monitor-control-service/setup.py
    +++ b/src/monitor-control-service/setup.py
    -VERSION = '1.0.1'
    +VERSION = '1.1.1'
    --- a/src/monitor-control-service/HISTORY.RST
    py files exclude tests, vendored_sdks and aaz folder
    """
    diff_file_started = False
    module_setup_update_pattern = re.compile(r"\+\+\+.*?src/%s/(?!.*(?:tests|vendored_sdks|aaz)/).*?.py" % mod)
    module_version_update_pattern = re.compile(r"\+\s?VERSION\s?\=\s?[\'\"]([0-9\.b]+)[\'\"]")
    with open(diff_code_file, "r") as f:
        for line in f:
            if diff_file_started:
                if mod_update_info.get("version_diff", None):
                    break
                if line.find("diff") == 0:
                    diff_file_started = False
                    continue
                mod_version_update_match = re.findall(module_version_update_pattern, line)
                if mod_version_update_match and len(mod_version_update_match) == 1:
                    mod_update_info["version_diff"] = mod_version_update_match[0]
            else:
                mod_setup_update_match = re.findall(module_setup_update_pattern, line)
                if mod_setup_update_match:
                    diff_file_started = True


def extract_module_metadata_update_info_pre(mod_update_info, mod):
    """
    re pattern:
    --- a/src/monitor-control-service/azext_amcs/azext_metadata.json
    +++ b/src/monitor-control-service/azext_amcs/azext_metadata.json
    -    "azext.isPreview": true
    +    "azext.isPreview": true
    --- a/src/monitor-control-service/HISTORY.RST
    not robust, use previous version's metatata and current metadata to compare
    """
    mod_update_info["meta_updated"] = False
    module_meta_update_pattern = re.compile(r"\+\+\+.*?src/%s/azext_.*?/azext_metadata.json" % mod)
    module_ispreview_add_pattern = re.compile(r"\+.*?azext.isPreview.*?true")
    module_ispreview_remove_pattern = re.compile(r"\-.*?azext.isPreview.*?true")
    module_isexp_add_pattern = re.compile(r"\+.*?azext.isExperimental.*?true")
    module_isexp_remove_pattern = re.compile(r"\-.*?azext.isExperimental.*?true")
    with open(diff_code_file, "r") as f:
        for line in f:
            if mod_update_info["meta_updated"]:
                if line.find("---") == 0:
                    break
                ispreview_add_match = re.findall(module_ispreview_add_pattern, line)
                if ispreview_add_match and len(ispreview_add_match):
                    mod_update_info["preview_tag_diff"] = "add"
                ispreview_remove_match = re.findall(module_ispreview_remove_pattern, line)
                if ispreview_remove_match and len(ispreview_remove_match):
                    mod_update_info["preview_tag_diff"] = "remove"
                isexp_add_match = re.findall(module_isexp_add_pattern, line)
                if isexp_add_match and len(isexp_add_match):
                    mod_update_info["exp_tag_diff"] = "add"
                isexp_remove_match = re.findall(module_isexp_remove_pattern, line)
                if isexp_remove_match and len(isexp_remove_match):
                    mod_update_info["exp_tag_diff"] = "remove"
            else:
                module_meta_update_match = re.findall(module_meta_update_pattern, line)
                if module_meta_update_match:
                    mod_update_info["meta_updated"] = True

def check_extension_list():
    cmd = ["az", "extension", "list", "-o", "table"]
    print("cmd: ", cmd)
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    print(res.stdout.decode("utf8"))

def clean_mod_of_azdev(mod):
    """
    be sure to get all the required info before removing mod in azdev
    """
    print("removing azdev extensions: ", mod)
    cmd = ["azdev", "extension", "remove", mod]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode:
        raise Exception(f'Error when removing {mod} from azdev')
    # remove extension source code
    cmd = ["rm", "-rf", "./src/" + mod]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode:
        raise Exception(f'Error when removing {mod} from src')


def install_mod_of_last_version(pkg_name, pre_release):
    whl_file_url = pre_release['downloadUrl']
    cmd = ["az", "extension", "add", "-s", whl_file_url, "-y"]
    print("cmd: ", cmd)
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode:
        raise Exception(f'Error when adding {pkg_name} from source {whl_file_url}')
    check_extension_list()


def remove_mod_of_last_version(pkg_name):
    cmd = ['az', 'extension', 'remove', '-n', pkg_name]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode:
        raise Exception(f'Error when removing {pkg_name}')
    check_extension_list()

def gen_metadata_from_whl(pkg_name, target_folder):
    cmd = ['azdev', 'command-change', 'meta-export', pkg_name, '--include-whl-extensions', '--meta-output-path', target_folder, "--debug"]
    print("cmd: ", cmd)
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode:
        raise Exception(f'Error when generating metadata from whl for {pkg_name}')


def get_mod_package_name(mod):
    """
    the preliminary step for running following cmd is installing extension using azdev
    """
    cmd = ["azdev", "extension", "show", "--mod-name", mod, "--query", "pkg_name", "-o", "tsv"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode == 0:
        mod = result.stdout.decode("utf8").strip()
    return mod


def get_module_metadata_of_max_version(mod):
    if mod not in get_index_data()['extensions']:
        print("No previous release for {0}".format(mod))
        return None
    pre_releases = get_index_data()['extensions'][mod]
    candidates_sorted = sorted(pre_releases, key=lambda c: parse(c['metadata']['version']), reverse=True)
    chosen = candidates_sorted[0]
    return chosen


def find_module_metadata_of_latest_version(mod):
    pkg_name = get_mod_package_name(mod)
    return get_module_metadata_of_max_version(pkg_name)


def find_module_metadata_of_current_version(mod):
    mod_directory = cli_ext_path +  "/src/" + mod
    for root, dirs, files in os.walk(mod_directory):
        if 'azext_metadata.json' in files:
            file_path = os.path.join(root, 'azext_metadata.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"Found azext_metadata.json at: {file_path}")
                    return data
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return None
    print(f"Mod: {mod} does not have azext_metadata.json, please check")
    return None

def extract_module_metadata_update_info(mod_update_info, mod):
    """
     use previous version's metatata and current metadata to compare
     relevent mod files should be in diff branch
    """
    mod_update_info["meta_updated"] = False
    # metadata is required for this task, (and also az extension *)
    pre_release = find_module_metadata_of_latest_version(mod)
    last_meta_data = pre_release.get("metadata", {}) if pre_release else None
    current_meta_data = find_module_metadata_of_current_version(mod)
    if not current_meta_data:
        raise Exception(f"Please check {mod}: azext_metadata.json file")
    if not last_meta_data:
        if current_meta_data.get("azext.isPreview", None):
            mod_update_info["meta_updated"] = True
            mod_update_info["preview_tag_diff"] = "add"
        return
    if last_meta_data.get("azext.isExperimental", False) and not current_meta_data.get("azext.isExperimental", False):
        mod_update_info["exp_tag_diff"] = "remove"
        mod_update_info["meta_updated"] = True
    if not last_meta_data.get("azext.isExperimental", False) and current_meta_data.get("azext.isExperimental", False):
        mod_update_info["exp_tag_diff"] = "add"
        mod_update_info["meta_updated"] = True
    if last_meta_data.get("azext.isPreview", False) and not current_meta_data.get("azext.isPreview", False):
        mod_update_info["preview_tag_diff"] = "remove"
        mod_update_info["meta_updated"] = True
    if not last_meta_data.get("azext.isPreview", False) and current_meta_data.get("azext.isPreview", False):
        mod_update_info["preview_tag_diff"] = "add"
        mod_update_info["meta_updated"] = True


def extract_module_version_info(mod_update_info, mod):
    next_version_pre_tag = get_next_version_pre_tag()
    next_version_segment_tag = get_next_version_segment_tag()
    print("next_version_pre_tag: ", next_version_pre_tag)
    print("next_version_segment_tag: ", next_version_segment_tag)
    pkg_name = get_mod_package_name(mod)
    print(f"get pkg name: {pkg_name} for mod: {mod}")
    pre_release = get_module_metadata_of_max_version(pkg_name)
    clean_mod_of_azdev(mod)
    if pre_release:
        print(f"Get prerelease info for mod: {mod} as below:")
        print(json.dumps(pre_release))
        print("Start generating base metadata")
        install_mod_of_last_version(pkg_name, pre_release)
        base_meta_folder = os.path.join(cli_ext_path, base_meta_path)
        gen_metadata_from_whl(pkg_name, base_meta_folder)
        remove_mod_of_last_version(pkg_name)
        print("End generating base metadata")
    base_meta_file = os.path.join(cli_ext_path, base_meta_path, "az_" + pkg_name + "_meta.json")
    diff_meta_file = os.path.join(cli_ext_path, diff_meta_path, "az_" + mod + "_meta.json")
    if not os.path.exists(base_meta_file) and not os.path.exists(diff_meta_file):
        print("no base and diff meta file found for {0}".format(mod))
        return
    elif not os.path.exists(base_meta_file) and os.path.exists(diff_meta_file):
        print("no base meta file found for {0}".format(mod))
        mod_update_info.update({"version": INIT_RELEASE_VERSION, "preview_tag": "add"})
        return
    elif not os.path.exists(diff_meta_file):
        print("no diff meta file found for {0}".format(mod))
        return
    if pre_release is None:
        next_version = cal_next_version(base_meta_file=base_meta_file, diff_meta_file=diff_meta_file,
                                        current_version=DEFAULT_VERSION,
                                        next_version_pre_tag=next_version_pre_tag,
                                        next_version_segment_tag=next_version_segment_tag)
    else:
        next_version = cal_next_version(base_meta_file=base_meta_file, diff_meta_file=diff_meta_file,
                                        current_version=pre_release['metadata']['version'],
                                        is_preview=pre_release['metadata'].get("azext.isPreview", None),
                                        is_experimental=pre_release['metadata'].get("azext.isExperimental", None),
                                        next_version_pre_tag=next_version_pre_tag,
                                        next_version_segment_tag=next_version_segment_tag)
    mod_update_info.update(next_version)


def fill_module_update_info(mods_update_info):
    for mod in changed_module_list:
        update_info = {}
        extract_module_history_update_info(update_info, mod)
        extract_module_version_update_info(update_info, mod)
        extract_module_metadata_update_info(update_info, mod)
        extract_module_version_info(update_info, mod)
        mods_update_info[mod] = update_info
    print("mods_update_info")
    print(mods_update_info)


def get_next_version_pre_tag():
    if VERSION_STABLE_TAG in pr_label_list:
        return VERSION_STABLE_TAG
    elif VERSION_PREVIEW_TAG in pr_label_list:
        return VERSION_PREVIEW_TAG
    else:
        return None


def get_next_version_segment_tag():
    """
    manual label order:
    major > minor > patch > pre
    """
    if VERSION_MAJOR_TAG in pr_label_list:
        return VERSION_MAJOR_TAG
    elif VERSION_MINOR_TAG in pr_label_list:
        return VERSION_MINOR_TAG
    elif VERSION_PATCH_TAG in pr_label_list:
        return VERSION_PATCH_TAG
    elif VERSION_PRE_TAG in pr_label_list:
        return VERSION_PRE_TAG
    else:
        return None


def add_suggest_header(comment_message):
    if block_pr == 1:
        comment_message.insert(0, "## :warning: Release Requirements")
    else:
        comment_message.insert(0, "## Release Suggestions")
    comment_message.insert(0, "Hi @" + pr_user)


def gen_history_comment_message(mod, mod_update_info, mod_message):
    if not mod_update_info["history_updated"]:
        mod_message.append(" - Please log updates into to `src/{0}/HISTORY.rst`".format(mod))


def gen_version_comment_message(mod, mod_update_info, mod_message):
    global block_pr
    if not mod_update_info.get("version_diff", None):
        if mod_update_info.get("version", None):
            mod_message.append(" - Update `VERSION` to `{0}` in `src/{1}/setup.py`".format(mod_update_info.get("version", "-"), mod))
    else:
        if mod_update_info.get("version", None):
            bot_version = parse(mod_update_info['version'])
            if mod_update_info.get("version_diff", None):
                diff_version = parse(mod_update_info['version_diff'])
                if diff_version != bot_version:
                    block_pr = 1
                    mod_message.append(" - :warning: Please update `VERSION` to be `{0}` in `src/{1}/setup.py`".format(mod_update_info.get("version", "-"), mod))
            else:
                mod_message.append(" - Update `VERSION` to `{0}` in `src/{1}/setup.py`".format(mod_update_info.get("version", "-"), mod))


def gen_preview_comment_message(mod, mod_update_info, mod_message):
    global block_pr
    if mod_update_info.get("preview_tag", "-") == mod_update_info.get("preview_tag_diff", "-"):
        return
    preview_comment_message = " - "
    if mod_update_info.get("version_diff", None):
        block_pr = 1
        preview_comment_message += ":warning: "
    if mod_update_info.get("preview_tag", None) and mod_update_info.get("preview_tag_diff", None):
        if mod_update_info["preview_tag"] == "add" and mod_update_info["preview_tag_diff"] == "remove":
            preview_comment_message += 'Set `azext.isPreview` to `true` in azext_metadata.json for {0}'.format(mod)
        elif mod_update_info["preview_tag"] == "remove" and mod_update_info["preview_tag_diff"] == "add":
            preview_comment_message += 'Remove `azext.isPreview: true` in azext_metadata.json for {0}'.format(mod)
    elif not mod_update_info.get("preview_tag", None) and mod_update_info.get("preview_tag_diff", None):
        if mod_update_info["preview_tag_diff"] == "add":
            preview_comment_message += 'Remove `azext.isPreview: true` in azext_metadata.json for {0}'.format(mod)
        elif mod_update_info["preview_tag_diff"] == "remove":
            preview_comment_message += 'Set `azext.isPreview` to `true` in azext_metadata.json for {0}'.format(mod)
    elif mod_update_info.get("preview_tag", None) and not mod_update_info.get("preview_tag_diff", None):
        if mod_update_info["preview_tag"] == "add":
            preview_comment_message += 'Set `azext.isPreview` to `true` in azext_metadata.json for {0}'.format(mod)
        elif mod_update_info["preview_tag"] == "remove":
            preview_comment_message += 'Remove `azext.isPreview: true` in azext_metadata.json for {0}'.format(mod)
    mod_message.append(preview_comment_message)


def gen_exp_comment_message(mod, mod_update_info, mod_message):
    global block_pr
    if mod_update_info.get("exp_tag", "-") == mod_update_info.get("exp_tag_diff", "-"):
        return
    exp_comment_message = " - "
    if mod_update_info.get("version_diff", None):
        block_pr = 1
        exp_comment_message += ":warning: "
    if mod_update_info.get("exp_tag", None) and mod_update_info.get("exp_tag_diff", None):
        if mod_update_info["exp_tag"] == "remove" and mod_update_info["exp_tag_diff"] == "add":
            exp_comment_message += 'Remove `azext.isExperimental: true` in azext_{0}/azext_metadata.json'.format(mod)
        if mod_update_info["exp_tag"] == "add" and mod_update_info["exp_tag_diff"] == "remove":
            exp_comment_message += 'Set `azext.isExperimental` to `true` in azext_metadata.json for {0}'.format(mod)
    elif not mod_update_info.get("exp_tag", None) and mod_update_info.get("exp_tag_diff", None):
        if mod_update_info["exp_tag_diff"] == "add":
            exp_comment_message += 'Remove `azext.isExperimental: true` in azext_{0}/azext_metadata.json'.format(mod)
        elif mod_update_info["exp_tag_diff"] == "remove":
            exp_comment_message += 'Set `azext.isExperimental` to `true` in azext_metadata.json for {0}'.format(mod)
    elif mod_update_info.get("exp_tag", None) and not mod_update_info.get("exp_tag_diff", None):
        if mod_update_info["exp_tag"] == "add":
            exp_comment_message += 'Set `azext.isExperimental` to `true` in azext_metadata.json for {0}'.format(mod)
        elif mod_update_info["exp_tag"] == "remove":
            exp_comment_message += 'Remove `azext.isExperimental: true` in azext_{0}/azext_metadata.json'.format(mod)
    mod_message.append(exp_comment_message)


def gen_comment_message(mod, mod_update_info, comment_message):
    mod_message = []
    gen_history_comment_message(mod, mod_update_info, mod_message)
    gen_version_comment_message(mod, mod_update_info, mod_message)
    gen_preview_comment_message(mod, mod_update_info, mod_message)
    gen_exp_comment_message(mod, mod_update_info, mod_message)
    if len(mod_message):
        comment_message.append("### Module: {0}".format(mod))
        comment_message += mod_message


def add_label_hint_message(comment_message):
    comment_message.append("#### Notes")
    # comment_message.append(" - Stable/preview tag is inherited from last release. "
    #                        "If needed, please add `stable`/`preview` label to modify it.")
    # comment_message.append(" - Major/minor/patch/pre increment of version number is calculated by pull request "
    #                        "code changes automatically. "
    #                        "If needed, please add `major`/`minor`/`patch`/`pre` label to adjust it.")
    comment_message.append(DEFAULT_MESSAGE)


def save_comment_message(comment_message):
    with open(result_path + "/" + output_file, "w") as f:
        for line in comment_message:
            f.write(line + "\n")


def save_label_output():
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'BlockPR={block_pr}', file=fh)
    add_label_dict = {
        "labels": ["release-version-block"]
    }
    removed_label = "release-version-block"
    if block_pr == 0:
        with open(result_path + "/" + remove_labels_file, "w") as f:
            f.write(removed_label + "\n")
    else:
        # add block label and empty release label file
        with open(result_path + "/" + add_labels_file, "w") as f:
            json.dump(add_label_dict, f)
        with open(result_path + "/" + remove_labels_file, "w") as f:
            pass


def main():
    print("Start calculate release version ...\n")
    print("base_meta_path: ", base_meta_path)
    print("diff_meta_path: ", diff_meta_path)
    print("output_file: ", output_file)
    print("changed_module_list: ", changed_module_list)
    print("pr_label_list: ", pr_label_list)
    comment_message = []
    modules_update_info = {}
    if len(changed_module_list) == 0:
        comment_message.append(DEFAULT_MESSAGE)
        save_comment_message(comment_message)
        save_label_output()
        return
    fill_module_update_info(modules_update_info)
    if len(modules_update_info) == 0:
        comment_message.append(DEFAULT_MESSAGE)
        save_comment_message(comment_message)
        save_label_output()
        return
    for mod, update_info in modules_update_info.items():
        gen_comment_message(mod, update_info, comment_message)
    if len(comment_message):
        add_suggest_header(comment_message)
        add_label_hint_message(comment_message)
    else:
        comment_message.append(DEFAULT_MESSAGE)
    print("comment_message:")
    print(comment_message)
    print("block_pr:", block_pr)
    save_comment_message(comment_message)
    save_label_output()


if __name__ == '__main__':
    main()
