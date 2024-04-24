# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import re
from datetime import datetime
from enum import Enum
import os
from time import sleep
import codecs
import requests
import tarfile
import tempfile
import uuid
from io import open
from re import (search, match, compile)
from json import dumps

from azure.cli.core._profile import Profile
from azure.cli.core.commands.client_factory import get_subscription_id, get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from knack.util import CLIError, todict
from knack.log import get_logger
from azure.cli.core.azclierror import ValidationError, CLIInternalError
from .vendored_sdks.appplatform.v2024_05_01_preview.models._app_platform_management_client_enums import SupportedRuntimeValue
from ._client_factory import cf_resource_groups


logger = get_logger(__name__)


def _get_upload_local_file(runtime_version, artifact_path=None, source_path=None, container_image=None):
    file_type = None
    file_path = None
    if artifact_path is not None:
        file_path = artifact_path
        file_type = "NetCoreZip" if runtime_version == SupportedRuntimeValue.NET_CORE31 else "Jar"
    elif source_path is not None:
        file_path = os.path.join(tempfile.gettempdir(
        ), 'build_archive_{}.tar.gz'.format(uuid.uuid4().hex))
        _pack_source_code(os.path.abspath(source_path), file_path)
        file_type = "Source"
    elif container_image is not None:
        file_type = 'Container'
    return file_type, file_path


def _get_file_ext(artifact_path):
    return os.path.splitext(artifact_path)[-1].lower() if artifact_path else ""


def _get_file_type(runtime_version, artifact_path=None):
    file_type = "Others"
    if _is_java(runtime_version):
        file_ext = _get_file_ext(artifact_path)
        if file_ext.lower() == ".jar":
            file_type = "Jar"
        elif file_ext.lower() == ".war":
            file_type = "War"
    if artifact_path is None:
        file_type = "Source"
    return file_type


def _is_java(runtime_version):
    if runtime_version is None:
        return False
    return runtime_version.casefold() == SupportedRuntimeValue.JAVA8.casefold() or \
        runtime_version.casefold() == SupportedRuntimeValue.JAVA11.casefold() or \
        runtime_version.casefold() == SupportedRuntimeValue.JAVA17.casefold()


def _java_runtime_in_number():
    return [8, 11, 17, 21]


def _pack_source_code(source_location, tar_file_path):
    logger.info("Packing source code into tar to upload...")

    ignore_list, ignore_list_size = _load_gitignore_file(source_location)
    common_vcs_ignore_list = {'.git', '.gitignore', 'bzrignore', '.hg',
                              '.hgignore', '.svn', '.circleci', 'target', 'docker', 'mvnw', 'mvnw.cmd'}

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
    """
    http(s)?://: Matches the beginning of the URL, which can start with either “http://” or “https://”.
    (?P<account_name>.*?): Matches the account name in the URL.
    The ?P<account_name> syntax creates a named group that can be referred to later in the expression.
    {re.escape(".")}: Escapes the period character so that it matches a literal period in the URL.
    {account_type}: Leverage f-string, to insert account_type into the string.
    {re.escape(".")}: Escapes the period character again.
    (?P<endpoint_suffix>.*?): Matches the endpoint suffix in the URL.
    /(?P<container_name>.*?): Matches the container name in the URL.
    /(?P<relative_path>.*?): Matches the relative path in the URL.
    {re.escape("?")}: The ? character is escaped so that it matches a literal question mark in the URL.
    (?P<sas_token>.*): Matches the SAS token in the URL.
    """
    regex = compile(f'http(s)?://(?P<account_name>.*?){re.escape(".")}{account_type}{re.escape(".")}(?P<endpoint_suffix>.*?)/(?P<container_name>.*?)/(?P<relative_path>.*?){re.escape("?")}(?P<sas_token>.*)')
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
    if tier == 'STANDARDGEN2':
        return 'S0'
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


def get_hostname(cli_ctx, client, resource_group, service_name):
    resource = client.services.get(resource_group, service_name)
    return get_proxy_api_endpoint(cli_ctx, resource)


def get_proxy_api_endpoint(cli_ctx, spring_resource):
    """Get the endpoint of the proxy api."""
    if not spring_resource.properties.fqdn:
        raise ValidationError('The property of the service "fqdn" is empty.')

    return spring_resource.properties.fqdn


def get_spring_sku(client, resource_group, name):
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
    while any(x for x in pollers if not x.done()):
        progress_bar.add(message='Running')
        sleep(5)
    progress_bar.end()


def handle_asc_exception(ex):
    try:
        raise CLIError(ex.inner_exception.error.message)
    except AttributeError:
        if hasattr(ex, 'response') and ex.response.internal_response.text:
            response_dict = json.loads(ex.response.internal_response.text)
            raise CLIError(response_dict["error"]["message"])
        else:
            raise CLIError(ex)


def register_provider_if_needed(cmd, rp_name):
    if not _is_resource_provider_registered(cmd, rp_name):
        _register_resource_provider(cmd, rp_name)


def _is_resource_provider_registered(cmd, resource_provider, subscription_id=None):
    registered = None
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)
    try:
        providers_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id).providers
        registration_state = getattr(providers_client.get(resource_provider), 'registration_state', "NotRegistered")

        registered = (registration_state and registration_state.lower() == 'registered')
    except Exception:  # pylint: disable=broad-except
        pass
    return registered


def _register_resource_provider(cmd, resource_provider):
    from azure.mgmt.resource.resources.models import ProviderRegistrationRequest, ProviderConsentDefinition

    logger.warning(f"Registering resource provider {resource_provider} ...")
    properties = ProviderRegistrationRequest(third_party_provider_consent=ProviderConsentDefinition(consent_to_authorization=True))

    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES).providers
    try:
        client.register(resource_provider, properties=properties)
        # wait for registration to finish
        timeout_secs = 120
        registration = _is_resource_provider_registered(cmd, resource_provider)
        start = datetime.utcnow()
        while not registration:
            registration = _is_resource_provider_registered(cmd, resource_provider)
            sleep(3)
            if (datetime.utcnow() - start).seconds >= timeout_secs:
                raise CLIInternalError(f"Timed out while waiting for the {resource_provider} resource provider to be registered.")

    except Exception as e:
        msg = ("This operation requires registering the resource provider {0}. "
               "We were unable to perform that registration on your behalf: "
               "Server responded with error message -- {1} . "
               "Please check with your admin on permissions, "
               "or try running registration manually with: az provider register --wait --namespace {0}")
        raise ValidationError(resource_provider, msg.format(e.args)) from e


def get_bearer_auth(cli_ctx):
    profile = Profile(cli_ctx=cli_ctx)
    creds, _, tenant = profile.get_raw_token()
    token = creds[1]
    return BearerAuth(token)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r
