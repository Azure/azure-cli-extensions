# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger
import logging
import os
from .helper._constants import CSSCTaskTypes
from .helper._constants import ERROR_MESSAGE_INVALID_TASK
from .helper._taskoperations import (
    create_continuous_patch_v1,
    update_continuous_patch_update_v1,
    delete_continuous_patch_v1,
    list_continuous_patch_v1,
    acr_cssc_dry_run
)

from azext_acrcssc._client_factory import (
    cf_acr_registries
)

logger = get_logger(__name__)

def create_acrcssc(cmd, resource_group_name, registry_name, type, config, cadence, dryrun=False, defer_immediate_run=False):
    logger.debug("Entering create_acrcssc %s %s %s %s %s", registry_name, type, config, cadence, dryrun)
    logger.info('Creating task type %s in registry %s', type, registry_name)
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)

    if(_validate_task_type(type)):
        if(dryrun is True):
            current_file_path = os.path.abspath(config)
            directory_path = os.path.dirname(current_file_path)
            acr_cssc_dry_run(cmd, registry=registry, config_file_path=directory_path)
        else:
            create_continuous_patch_v1(cmd, registry, config, cadence, dryrun, defer_immediate_run)
    else:
        raise CLIError(ERROR_MESSAGE_INVALID_TASK)

def update_acrcssc(cmd, resource_group_name, registry_name, type, config, cadence, dryrun=False, defer_immediate_run=False):
    logger.debug('Entering update_acrcssc %s %s %s %s', registry_name, type, config, dryrun)
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)
    if(_validate_task_type(type)):
        if(dryrun is True):
            current_file_path = os.path.abspath(config)
            directory_path = os.path.dirname(current_file_path)
            acr_cssc_dry_run(cmd, registry=registry, config_file_path=directory_path)
        else:
            update_continuous_patch_update_v1(cmd, registry, config, cadence, dryrun, defer_immediate_run)
    else:
        raise CLIError(ERROR_MESSAGE_INVALID_TASK)

def delete_acrcssc(cmd, resource_group_name, registry_name, type):
    logger.debug("Entering delete_acrcssc %s %s", registry_name, type)
    logger.info('Deleting task type %s from registry %s', type, registry_name)
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)

    if(_validate_task_type(type)):
        delete_continuous_patch_v1(cmd, registry, False)
    else:
        raise CLIError(ERROR_MESSAGE_INVALID_TASK)

def show_acrcssc(cmd, resource_group_name, registry_name, type):
    logger.debug('Entering show_acrcssc %s %s', registry_name, type)
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)
    
    if(_validate_task_type(type)):
        return list_continuous_patch_v1(cmd, registry)
    raise CLIError(ERROR_MESSAGE_INVALID_TASK)

def _validate_task_type(task_type):
    if task_type in CSSCTaskTypes._value2member_map_:
        return task_type == CSSCTaskTypes.ContinuousPatchV1.value
    return False
