# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
import os
from .helper._constants import CSSCTaskTypes
from .helper._taskoperations import (
    create_continuous_patch_v1,
    update_continuous_patch_update_v1,
    delete_continuous_patch_v1,
    list_continuous_patch_v1,
    acr_cssc_dry_run
)
from ._validators import validate_inputs, validate_task_type, validate_cssc_update_input
from azext_acrcssc._client_factory import ( cf_acr_registries )

logger = get_logger(__name__)

def create_acrcssc(cmd, resource_group_name, registry_name, type, config, cadence, dryrun=False, defer_immediate_run=False):
    '''Create a continuous patch task in the registry.'''
    logger.debug("Entering create_acrcssc with parameters: %s %s %s %s %s", registry_name, type, config, cadence, dryrun)

    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)
    validate_inputs(cadence)
    if(dryrun is True):
        acr_cssc_dry_run(cmd, registry=registry, config_file_path=config)
    else:
        create_continuous_patch_v1(cmd, registry, config, cadence, dryrun, defer_immediate_run)

def update_acrcssc(cmd, resource_group_name, registry_name, type, config, cadence, dryrun=False, defer_immediate_run=False):
    '''Update a continuous patch task in the registry.'''
    logger.debug('Entering update_acrcssc with parameters: %s %s %s %s', registry_name, type, config, dryrun)
    validate_cssc_update_input(config, cadence)
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)
    validate_inputs(type, cadence, allow_null_cadence = (cadence == None))
    
    if config is None and cadence is None:
        raise ValueError("Please provide a configuration file path or cadence to update the workflow.")
    
    if(dryrun is True and config is not None):
        current_file_path = os.path.abspath(config)
        directory_path = os.path.dirname(current_file_path)
        acr_cssc_dry_run(cmd, registry=registry, config_file_path=directory_path)
    else:
        update_continuous_patch_update_v1(cmd, registry, config, cadence, dryrun, defer_immediate_run)

def delete_acrcssc(cmd, resource_group_name, registry_name, type):
    '''Delete a continuous patch task in the registry.'''
    logger.debug("Entering delete_acrcssc with parameters: %s %s", registry_name, type)
    
    validate_task_type(type)
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)
    
    from azure.cli.core.util import user_confirmation
    user_confirmation(f"Are you sure you want to delete the workflow {type} from registry {registry_name}?")
    
    delete_continuous_patch_v1(cmd, registry, False)
    logger.warning("Deleted workflow %s from registry %s", CSSCTaskTypes.ContinuousPatchV1.name, registry_name)

def show_acrcssc(cmd, resource_group_name, registry_name, type):
    '''Show a continuous patch task in the registry.'''
    logger.debug('Entering show_acrcssc with parameters: %s %s', registry_name, type)

    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)
    
    validate_task_type(type)
    return list_continuous_patch_v1(cmd, registry)


