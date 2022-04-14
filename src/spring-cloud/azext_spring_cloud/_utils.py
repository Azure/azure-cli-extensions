# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from enum import Enum
import os
from time import sleep
import codecs
import tarfile
import tempfile
import uuid
from io import open
from re import (search, match, compile)
from json import dumps
from knack.util import CLIError, todict
from knack.log import get_logger
from .vendored_sdks.appplatform.v2020_07_01.models import _app_platform_management_client_enums as AppPlatformEnums
from ._client_factory import cf_resource_groups


logger = get_logger(__name__)


def _get_upload_local_file(runtime_version, artifact_path=None, source_path=None, container_image=None):
    file_type = None
    file_path = None
    if artifact_path is not None:
        file_path = artifact_path
        file_type = "NetCoreZip" if runtime_version == AppPlatformEnums.RuntimeVersion.NET_CORE31 else "Jar"
    elif source_path is not None:
        file_path = os.path.join(tempfile.gettempdir(
        ), 'build_archive_{}.tar.gz'.format(uuid.uuid4().hex))
        _pack_source_code(os.path.abspath(source_path), file_path)
        file_type = "Source"
    elif container_image is not None:
        file_type = 'Container'
    return file_type, file_path


def _get_file_type(runtime_version, artifact_path=None):
    file_type = "NetCoreZip" if runtime_version == AppPlatformEnums.RuntimeVersion.NET_CORE31 else "Jar"

    if artifact_path is None:
        file_type = "Source"
    return file_type


def _pack_source_code(source_location, tar_file_path):
    logger.info("Packing source code into tar to upload...")

    ignore_list, ignore_list_size = _load_gitignore_file(source_location)
    common_vcs_ignore_list = {'.git', '.gitignore', 'bzrignore', '.hg',
                              '.hgignore', '.svn', '.circleci', 'target', 'docker'}

    def _ignore_check(tarinfo, parent_ignored, parent_matching_rule_index):
        # ignore common vcs dir or file
        if tarinfo.name in common_vcs_ignore_list:
            logger.info(
                "Excluding '%s' based on default ignore rules", tarinfo.name)
            return True, parent_matching_rule_index

        if ignore_list is None:
            # if .dockerignore doesn't exists, inherit from parent
            # eg, it will ignore the files under .git folder.
            return parent_ignored, parent_matching_rule_index

        for index, item in enumerate(ignore_list):
            # stop checking the remaining rules whose priorities are lower than the parent matching rule
            # at this point, current item should just inherit from parent
            if index >= parent_matching_rule_index:
                break
            if match(item.pattern, tarinfo.name):
                logger.debug(".gitignore: rule '%s' matches '%s'.",
                             item.rule, tarinfo.name)
                return item.ignore, index

        logger.debug(".gitignore: no rule for '%s'. parent ignore '%s'",
                     tarinfo.name, parent_ignored)
        # inherit from parent
        return parent_ignored, parent_matching_rule_index

    with tarfile.open(tar_file_path, "w:gz") as tar:
        # need to set arcname to empty string as the archive root path
        _archive_file_recursively(tar,
                                  source_location,
                                  arcname="",
                                  parent_ignored=False,
                                  parent_matching_rule_index=ignore_list_size,
                                  ignore_check=_ignore_check)


class IgnoreRule(object):  # pylint: disable=too-few-public-methods
    def __init__(self, rule):

        self.rule = rule
        self.ignore = True
        # ! makes exceptions to exclusions
        if rule.startswith('!'):
            self.ignore = False
            rule = rule[1:]  # remove !

        self.pattern = "^"
        tokens = rule.split('/')
        token_length = len(tokens)
        for index, token in enumerate(tokens, 1):
            # ** matches any number of directories
            if token == "**":
                self.pattern += ".*"  # treat **/ as **
            else:
                # * matches any sequence of non-seperator characters
                # ? matches any single non-seperator character
                # . matches dot character
                self.pattern += token.replace(
                    "*", "[^/]*").replace("?", "[^/]").replace(".", "\\.")
                if index < token_length:
                    self.pattern += "/"  # add back / if it's not the last
        self.pattern += "$"


def _load_gitignore_file(source_location):
    # reference: https://git-scm.com/docs/gitignore
    git_ignore_file = os.path.join(source_location, ".gitignore")
    if not os.path.exists(git_ignore_file):
        return None, 0

    encoding = "utf-8"
    header = open(git_ignore_file, "rb").read(len(codecs.BOM_UTF8))
    if header.startswith(codecs.BOM_UTF8):
        encoding = "utf-8-sig"

    ignore_list = []

    for line in open(git_ignore_file, 'r', encoding=encoding).readlines():
        rule = line.rstrip()

        # skip empty line and comment
        if not rule or rule.startswith('#'):
            continue

        # the ignore rule at the end has higher priority
        ignore_list = [IgnoreRule(rule)] + ignore_list

    return ignore_list, len(ignore_list)


def _archive_file_recursively(tar, name, arcname, parent_ignored, parent_matching_rule_index, ignore_check):
    # create a TarInfo object from the file
    tarinfo = tar.gettarinfo(name, arcname)

    if tarinfo is None:
        raise CLIError("tarfile: unsupported type {}".format(name))

    # check if the file/dir is ignored
    ignored, matching_rule_index = ignore_check(
        tarinfo, parent_ignored, parent_matching_rule_index)

    if not ignored:
        # append the tar header and data to the archive
        if tarinfo.isreg():
            with open(name, "rb") as f:
                tar.addfile(tarinfo, f)
        else:
            tar.addfile(tarinfo)

    # even the dir is ignored, its child items can still be included, so continue to scan
    if tarinfo.isdir():
        for f in os.listdir(name):
            _archive_file_recursively(tar, os.path.join(name, f), os.path.join(arcname, f),
                                      parent_ignored=ignored, parent_matching_rule_index=matching_rule_index,
                                      ignore_check=ignore_check)


def get_blob_info(blob_sas_url):
    return _get_azure_storage_client_info('blob', blob_sas_url)


def get_azure_files_info(file_sas_url):
    return _get_azure_storage_client_info('file', file_sas_url)


def _get_azure_storage_client_info(account_type, sas_url):
    regex = compile("http(s)?://(?P<account_name>.*?)\.{0}\.(?P<endpoint_suffix>.*?)/(?P<container_name>.*?)/(?P<relative_path>.*?)\?(?P<sas_token>.*)".format(account_type))
    matchObj = search(regex, sas_url)
    account_name = matchObj.group('account_name')
    endpoint_suffix = matchObj.group('endpoint_suffix')
    container_name = matchObj.group('container_name')
    relative_path = matchObj.group('relative_path')
    sas_token = matchObj.group('sas_token')

    if not account_name or not container_name or not relative_path or not sas_token:
        raise CLIError(
            "Failed to parse the SAS URL: '{!s}'.".format(sas_url))

    return account_name, endpoint_suffix, container_name, relative_path, sas_token


class ApiType(Enum):
    mongo = "mongo"
    sql = "sql"
    cassandra = 'cassandra'
    gremlin = 'gremlin'
    table = 'table'


def dump(obj):
    input_dict = todict(obj)
    json_object = dumps(input_dict, ensure_ascii=False,
                        indent=2, sort_keys=True, separators=(',', ': ')) + '\n'
    logger.info(json_object)


def _get_rg_location(ctx, resource_group_name, subscription_id=None):
    groups = cf_resource_groups(ctx, subscription_id=subscription_id)
    # Just do the get, we don't need the result, it will error out if the group doesn't exist.
    rg = groups.get(resource_group_name)
    return rg.location


def _get_sku_name(tier):  # pylint: disable=too-many-return-statements
    tier = tier.upper()
    if tier == 'BASIC':
        return 'B0'
    if tier == 'STANDARD':
        return 'S0'
    if tier == 'ENTERPRISE':
        return 'E0'
    raise CLIError("Invalid sku(pricing tier), please refer to command help for valid values")


def _get_persistent_disk_size(tier):  # pylint: disable=too-many-return-statements
    tier = tier.upper()
    if tier == 'BASIC':
        return 1
    if tier == 'STANDARD':
        return 50
    if tier == 'ENTERPRISE':
        return 50
    return 50


def get_portal_uri(cli_ctx):
    """Get the Azure Portal URL in the current cloud."""
    try:
        return cli_ctx.cloud.endpoints.portal
    except Exception as e:
        logger.debug("Could not get Azure Portal endpoint. Exception: %s", str(e))
        return 'https://portal.azure.com'


def get_spring_cloud_sku(client, resource_group, name):
    return client.services.get(resource_group, name).sku


def convert_argument_to_parameter_list(args):
    return ', '.join([convert_argument_to_parameter(x) for x in args])


def convert_argument_to_parameter(arg):
    return '--{}'.format(arg.replace('_', '-'))


def wait_till_end(cmd, *pollers):
    if not pollers:
        return
    progress_bar = cmd.cli_ctx.get_progress_controller()
    progress_bar.add(message='Running')
    progress_bar.begin()
    while any(x and not x.done() for x in pollers):
        progress_bar.add(message='Running')
        sleep(5)


def handle_asc_exception(ex):
    try:
        raise CLIError(ex.inner_exception.error.message)
    except AttributeError:
        if hasattr(ex, 'response') and ex.response.internal_response.text:
            response_dict = json.loads(ex.response.internal_response.text)
            raise CLIError(response_dict["error"]["message"])
        else:
            raise CLIError(ex)
