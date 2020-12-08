# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import json
from distutils import log as logger
from collections import OrderedDict
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import IdentityProperties, UserIdentityProperties


def create_identity_properties(user_assigned_identity_resource_id):
    if user_assigned_identity_resource_id is None:
        resource_identity_type = "SystemAssigned"
        user_assigned_identities = None

    else:
        resource_identity_type = "UserAssigned"
        user_identity_properties = UserIdentityProperties()
        user_assigned_identities = {user_assigned_identity_resource_id: user_identity_properties}

    return IdentityProperties(type=resource_identity_type, user_assigned_identities=user_assigned_identities)


def print_keyvault_policy_output(keyvault_secret_uri, user_assigned_identity_resource_id, raw_result):
    keyvault_name = keyvault_secret_uri.split("https://")[1].split('.')[0]

    if user_assigned_identity_resource_id is not None:
        # if user ended resource id with a '/', remove it
        if user_assigned_identity_resource_id[-1] == '/':
            user_assigned_identity_resource_id = user_assigned_identity_resource_id[:-1]

        # account for ARM bug where the identity user assigned identities dict key resource id has lowercase resourcegroup rather than resourceGroup
        user_assigned_identity_resource_id_list = user_assigned_identity_resource_id.split("/")
        user_assigned_identity_resource_id_list[3] = "resourcegroups"
        user_assigned_identity_resource_id = '/'.join(user_assigned_identity_resource_id_list)

    identity_object_id = raw_result.identity.principal_id if user_assigned_identity_resource_id is None else raw_result.identity.user_assigned_identities[user_assigned_identity_resource_id].principal_id

    logger.warn("***YOU MUST RUN THE FOLLOWING COMMAND PRIOR TO ATTEMPTING A PIPELINERUN OR EXPECTING SOURCETRIGGER TO SUCCESSFULLY IMPORT IMAGES***")
    logger.warn(f'az keyvault set-policy --name {keyvault_name} --secret-permissions get --object-id {identity_object_id}')


def print_pipeline_output(obj):
    is_importpipeline = "importPipelines" in obj.id
    is_exportpipeline = "exportPipelines" in obj.id
    is_pipelinerun = "pipelineRuns" in obj.id

    if is_pipelinerun:
        pipelinerun_type = "import" if "importPipelines" in obj.request.pipeline_resource_id else "export"

    # unroll the obj
    obj = json.loads(json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o))))
    d = OrderedDict()

    if is_pipelinerun and pipelinerun_type == "import":
        d["name"] = obj["name"]
        d["status"] = obj["response"]["status"]
        d["pipeline_resource_id"] = obj["request"]["pipeline_resource_id"]
        d["source_blob"] = obj["request"]["source"]["name"]
        d["imported_artifacts"] = obj["response"]["imported_artifacts"]
        d["progress_percentage"] = obj["response"]["progress"]["percentage"]
        d["start_time"] = obj["response"]["start_time"]
        d["duration"] = get_duration(d["start_time"], obj["response"]["finish_time"])
        d["catalog_digest"] = obj["response"]["catalog_digest"]
        d["pipeline_run_error"] = obj["response"]["pipeline_run_error_message"]

    elif is_pipelinerun and pipelinerun_type == "export":
        d["name"] = obj["name"]
        d["status"] = obj["response"]["status"]
        d["pipeline_resource_id"] = obj["request"]["pipeline_resource_id"]
        d["target_blob"] = obj["request"]["target"]["name"]
        d["exported_artifacts"] = obj["request"]["artifacts"]
        d["progress_percentage"] = obj["response"]["progress"]["percentage"]
        d["start_time"] = obj["response"]["start_time"]
        d["duration"] = get_duration(d["start_time"], obj["response"]["finish_time"])
        d["catalog_digest"] = obj["response"]["catalog_digest"]
        d["pipeline_run_error_message"] = obj["response"]["pipeline_run_error_message"]

    elif is_importpipeline:
        d["name"] = obj["name"]
        d["status"] = obj["provisioning_state"]
        d["id"] = obj["id"]
        d["storage_account_container_uri"] = obj["source"]["uri"]
        d["keyvault_secret_uri"] = obj["source"]["key_vault_uri"]
        d["source_trigger_status"] = obj["trigger"]["source_trigger"]["status"]
        d["options"] = obj["options"]
        d["identity_type"] = obj["identity"]["type"]

        if d["identity_type"] == "userAssigned":
            d["user_assigned_identities"] = obj["identity"]["user_assigned_identities"]
        else:
            d["principal_id"] = obj["identity"]["principal_id"]
            d["tenant_id"] = obj["identity"]["tenant_id"]

    elif is_exportpipeline:
        d["name"] = obj["name"]
        d["status"] = obj["provisioning_state"]
        d["id"] = obj["id"]
        d["storage_account_container_uri"] = obj["target"]["uri"]
        d["keyvault_secret_uri"] = obj["target"]["key_vault_uri"]
        d["options"] = obj["options"]
        d["identity_type"] = obj["identity"]["type"]

        if d["identity_type"] == "userAssigned":
            d["user_assigned_identities"] = obj["identity"]["user_assigned_identities"]
        else:
            d["principal_id"] = obj["identity"]["principal_id"]
            d["tenant_id"] = obj["identity"]["tenant_id"]

    return d


def print_lite_pipeline_output(obj):
    is_importpipeline = "importPipelines" in obj.id
    is_exportpipeline = "exportPipelines" in obj.id
    is_pipelinerun = "pipelineRuns" in obj.id

    if is_pipelinerun:
        pipelinerun_type = "import" if "importPipelines" in obj.request.pipeline_resource_id else "export"

    # unroll the obj
    obj = json.loads(json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o))))
    d = {}

    if is_pipelinerun and pipelinerun_type == "import":
        d["name"] = obj["name"]
        d["pipelinerun_type"] = pipelinerun_type
        d["status"] = obj["response"]["status"]
        d["start_time"] = obj["response"]["start_time"].split('.')[0]
        d["error_message"] = obj["response"]["pipeline_run_error_message"]

        return d

    elif is_pipelinerun and pipelinerun_type == "export":
        d["name"] = obj["name"]
        d["pipelinerun_type"] = pipelinerun_type
        d["status"] = obj["response"]["status"]
        d["start_time"] = obj["response"]["start_time"].split('.')[0]
        d["error_message"] = obj["response"]["pipeline_run_error_message"]
    elif is_importpipeline:
        d["name"] = obj["name"]
        d["status"] = obj["provisioning_state"]
        d["storage_uri"] = obj["source"]["uri"]

    elif is_exportpipeline:
        d["name"] = obj["name"]
        d["status"] = obj["provisioning_state"]
        d["storage_uri"] = obj["target"]["uri"]

    return d


def get_duration(start_time, finish_time):
    from dateutil.parser import parse
    try:
        duration = parse(finish_time) - parse(start_time)
        hours = "{0:02d}".format((24 * duration.days) + (duration.seconds // 3600))
        minutes = "{0:02d}".format((duration.seconds % 3600) // 60)
        seconds = "{0:02d}".format(duration.seconds % 60)
        return "{0}:{1}:{2}".format(hours, minutes, seconds)
    except:
        logger.debug("Unable to get duration with start_time '%s' and finish_time '%s'", start_time, finish_time)
        return ' '
