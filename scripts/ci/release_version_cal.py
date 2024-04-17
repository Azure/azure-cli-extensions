#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
import os
from packaging.version import parse

from azdev.utilities.path import get_cli_repo_path, get_ext_repo_paths
from azdev.operations.extensions import cal_next_version
from azdev.operations.constant import (PREVIEW_INIT_SUFFIX, VERSION_MAJOR_TAG, VERSION_MINOR_TAG,
                                       VERSION_PATCH_TAG, VERSION_STABLE_TAG, VERSION_PREVIEW_TAG, VERSION_PRE_TAG)
from util import get_index_data


base_meta_path = os.environ.get('base_meta_path', None)
diff_meta_path = os.environ.get('diff_meta_path', None)
output_file = os.environ.get('output_file', None)

changed_module_list = os.environ.get('changed_module_list', "").split()
pr_label_list = os.environ.get('pr_label_list', "").split()
pr_label_list = [name.lower().strip().strip('"').strip("'") for name in pr_label_list]

DEFAULT_VERSION = "0.0.0"
INIT_RELEASE_VERSION = "1.0.0b1"


def get_module_metadata_of_max_version(mod):
    if mod not in get_index_data()['extensions']:
        print("No previous release for {0}".format(mod))
        return None
    pre_releases = get_index_data()['extensions'][mod]
    candidates_sorted = sorted(pre_releases, key=lambda c: parse(c['metadata']['version']), reverse=True)
    chosen = candidates_sorted[0]
    return chosen


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
        return pr_label_list
    elif VERSION_PATCH_TAG in pr_label_list:
        return VERSION_PATCH_TAG
    elif VERSION_PRE_TAG in pr_label_list:
        return VERSION_PRE_TAG
    else:
        return None


def add_suggest_header(comment_message):
    comment_message.append("## :warning: Release Suggestions")


def gen_comment_message(mod, next_version, comment_message):
    comment_message.append("### Module: {0}".format(mod))
    comment_message.append(" - Update version to `{0}` in setup.py".format(next_version.get("version", "-")))
    if next_version.get("preview_tag", None) == "add":
        comment_message.append(' - Set `azext.isPreview` to `true` in azext_{0}/azext_metadata.json'.format(mod))
    if next_version.get("preview_tag", None) == "remove":
        comment_message.append(' - Remove `azext.isPreview: true` in azext_{0}/azext_metadata.json'.format(mod))
    if next_version.get("exp_tag", None) == "remove":
        comment_message.append(' - Remove `azext.isExperimental: true` in azext_{0}/azext_metadata.json'.format(mod))


def add_label_hint_message(comment_message):
    comment_message.append("#### Notes")
    comment_message.append(" - Stable/preview tag is inherited from last release. "
                           "If needed, please add `stable`/`preview` label to modify it.")
    comment_message.append(" - Major/minor/patch/pre increment of version number is calculated by pull request "
                           "code changes automatically. "
                           "If needed, please add `major`/`minor`/`patch`/`pre` label to adjust it.")
    comment_message.append(" - For more info about extension versioning, please refer to [Extension version schema](https://github.com/Azure/azure-cli/blob/release/doc/extensions/versioning_guidelines.md)")


def save_comment_message(cli_ext_path, file_name, comment_message):
    with open(os.path.join(cli_ext_path, file_name), "w") as f:
        for line in comment_message:
            f.write(line + "\n")


def main():
    print("Start calculate release version ...\n")
    cli_ext_path = get_ext_repo_paths()[0]
    print("get_cli_repo_path: ", get_cli_repo_path())
    print("get_ext_repo_paths: ", cli_ext_path)
    print("base_meta_path: ", base_meta_path)
    print("diff_meta_path: ", diff_meta_path)
    print("output_file: ", output_file)
    print("changed_module_list: ", changed_module_list)
    print("pr_label_list: ", pr_label_list)
    comment_message = []
    if len(changed_module_list) == 0:
        comment_message.append("For more info about extension versioning, please refer to [Extension version schema](https://github.com/Azure/azure-cli/blob/release/doc/extensions/versioning_guidelines.md)")
        save_comment_message(cli_ext_path, output_file, comment_message)
        return
    next_version_pre_tag = get_next_version_pre_tag()
    next_version_segment_tag = get_next_version_segment_tag()
    print("next_version_pre_tag: ", next_version_pre_tag)
    print("next_version_segment_tag: ", next_version_segment_tag)
    add_suggest_header(comment_message)
    for mod in changed_module_list:
        base_meta_file = os.path.join(cli_ext_path, base_meta_path, "az_" + mod + "_meta.json")
        diff_meta_file = os.path.join(cli_ext_path, diff_meta_path, "az_" + mod + "_meta.json")
        if not os.path.exists(base_meta_file) and not os.path.exists(diff_meta_file):
            print("no base and diff meta file found for {0}".format(mod))
            continue
        elif not os.path.exists(base_meta_file) and os.path.exists(diff_meta_file):
            print("no base meta file found for {0}".format(mod))
            gen_comment_message(mod, {"version": INIT_RELEASE_VERSION}, comment_message)
            continue
        elif not os.path.exists(diff_meta_file):
            print("no diff meta file found for {0}".format(mod))
            continue

        pre_release = get_module_metadata_of_max_version(mod)
        if pre_release is None:
            next_version = cal_next_version(base_meta_file=base_meta_file, diff_meta_file=diff_meta_file,
                                            current_version=DEFAULT_VERSION,
                                            next_version_pre_tag=next_version_pre_tag,
                                            next_version_segment_tag=next_version_segment_tag
                                            )
        else:
            next_version = cal_next_version(base_meta_file=base_meta_file, diff_meta_file=diff_meta_file,
                                            current_version=pre_release['metadata']['version'],
                                            is_preview=pre_release['metadata'].get("azext.isPreview", None),
                                            is_experimental=pre_release['metadata'].get("azext.isExperimental", None),
                                            next_version_pre_tag=next_version_pre_tag,
                                            next_version_segment_tag=next_version_segment_tag
                                            )
        gen_comment_message(mod, next_version, comment_message)
    add_label_hint_message(comment_message)
    print(comment_message)
    save_comment_message(cli_ext_path, output_file, comment_message)


if __name__ == '__main__':
    main()
