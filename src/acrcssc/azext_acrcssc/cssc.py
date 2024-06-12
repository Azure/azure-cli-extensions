# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from .helper._constants import CSSCTaskTypes, CONTINUOUS_PATCHING_WORKFLOW_NAME
from .helper._taskoperations import (
    create_update_continuous_patch_v1,
    delete_continuous_patch_v1,
    list_continuous_patch_v1,
    acr_cssc_dry_run
)
from ._validators import validate_inputs, validate_task_type, validate_cssc_optional_inputs
from azext_acrcssc._client_factory import ( cf_acr_registries )

logger = get_logger(__name__)

def _perform_continuous_patch_operation(cmd, resource_group_name, registry_name, type, config, cadence, dryrun=False, defer_immediate_run=False, is_create=True):
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)
    
    validate_inputs(cadence, config)

    if not is_create:
        validate_cssc_optional_inputs(config, cadence)
    
    logger.debug('validations completed successfully.')
    if dryrun:
        acr_cssc_dry_run(cmd, registry=registry, config_file_path=config)
    else:
        create_update_continuous_patch_v1(cmd, registry, config, cadence, dryrun, defer_immediate_run, is_create)

def create_acrcssc(cmd, resource_group_name, registry_name, type, config, cadence, dryrun=False, defer_immediate_run=False):
    '''Create a continuous patch task in the registry.'''
    logger.debug("Entering create_acrcssc with parameters: %s %s %s %s %s", registry_name, type, config, cadence, dryrun)
    _perform_continuous_patch_operation(cmd, resource_group_name, registry_name, type, config, cadence, dryrun, defer_immediate_run, is_create=True)

def update_acrcssc(cmd, resource_group_name, registry_name, type, config, cadence, dryrun=False, defer_immediate_run=False):
    '''Update a continuous patch task in the registry.'''
    logger.debug('Entering update_acrcssc with parameters: %s %s %s %s %s %s %s', registry_name, type, config, cadence, dryrun, defer_immediate_run)
    _perform_continuous_patch_operation(cmd, resource_group_name, registry_name, type, config, cadence, dryrun, defer_immediate_run, is_create=False)

def delete_acrcssc(cmd, resource_group_name, registry_name, type):
    '''Delete a continuous patch task in the registry.'''
    logger.debug("Entering delete_acrcssc with parameters: %s %s %s", resource_group_name, registry_name, type)
    
    validate_task_type(type)
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)
    
    from azure.cli.core.util import user_confirmation
    user_confirmation(f"Are you sure you want to delete the workflow {CONTINUOUS_PATCHING_WORKFLOW_NAME} from registry {registry_name}?")
    
    delete_continuous_patch_v1(cmd, registry, False)
    print(f"Deleted {CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow successfully from registry {registry_name}")

def show_acrcssc(cmd, resource_group_name, registry_name, type):
    '''Show a continuous patch task in the registry.'''
    logger.debug('Entering show_acrcssc with parameters: %s %s', registry_name, type)

    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)
    
    validate_task_type(type)
    return list_continuous_patch_v1(cmd, registry)
