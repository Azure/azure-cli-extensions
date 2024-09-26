# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation
from knack.log import get_logger
from .helper._constants import CONTINUOUS_PATCHING_WORKFLOW_NAME
from .helper._taskoperations import (
    create_update_continuous_patch_v1,
    delete_continuous_patch_v1,
    list_continuous_patch_v1,
    acr_cssc_dry_run,
    cancel_continuous_patch_runs,
    track_scan_progress
)
from ._validators import (
    validate_inputs,
    validate_task_type,
    validate_cssc_optional_inputs
)
from azext_acrcssc._client_factory import cf_acr_registries

logger = get_logger(__name__)


def _perform_continuous_patch_operation(cmd,
                                        resource_group_name,
                                        registry_name,
                                        config,
                                        schedule,
                                        dryrun=False,
                                        run_immediately=False,
                                        is_create=True):
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)

    validate_inputs(schedule, config)

    if not is_create:
        validate_cssc_optional_inputs(config, schedule)

    logger.debug('validations completed successfully.')
    if dryrun:
        dryrun_output = acr_cssc_dry_run(cmd, registry=registry, config_file_path=config, is_create=is_create)
        print(dryrun_output)
    else:
        create_update_continuous_patch_v1(cmd, registry, config, schedule, dryrun, run_immediately, is_create)


def create_acrcssc(cmd,
                   resource_group_name,
                   registry_name,
                   workflow_type,
                   config,
                   schedule,
                   dryrun=False,
                   run_immediately=False):
    '''Create a continuous patch task in the registry.'''
    logger.debug(f"Entering create_acrcssc with parameters: {registry_name} {workflow_type} {config} {schedule} {dryrun}")
    _perform_continuous_patch_operation(cmd,
                                        resource_group_name,
                                        registry_name,
                                        config,
                                        schedule,
                                        dryrun,
                                        run_immediately,
                                        is_create=True)


def update_acrcssc(cmd,
                   resource_group_name,
                   registry_name,
                   workflow_type,
                   config,
                   schedule,
                   dryrun=False,
                   run_immediately=False):
    '''Update a continuous patch task in the registry.'''
    logger.debug(f'Entering update_acrcssc with parameters: {registry_name} {workflow_type} {config} {schedule} {dryrun} {run_immediately}')
    _perform_continuous_patch_operation(cmd,
                                        resource_group_name,
                                        registry_name,
                                        config,
                                        schedule,
                                        dryrun,
                                        run_immediately,
                                        is_create=False)


def delete_acrcssc(cmd,
                   resource_group_name,
                   registry_name,
                   workflow_type):
    '''Delete a continuous patch task in the registry.'''
    logger.debug(f"Entering delete_acrcssc with parameters: {resource_group_name} {registry_name} {workflow_type}")

    validate_task_type(workflow_type)
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)

    from azure.cli.core.util import user_confirmation
    user_confirmation(f"Are you sure you want to delete the workflow {CONTINUOUS_PATCHING_WORKFLOW_NAME} from registry {registry_name}?")

    delete_continuous_patch_v1(cmd, registry, False)
    print(f"Deleted {CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow successfully from registry {registry_name}")


def show_acrcssc(cmd,
                 resource_group_name,
                 registry_name,
                 workflow_type):
    '''Show a continuous patch task in the registry.'''
    logger.debug(f'Entering show_acrcssc with parameters: {registry_name} {workflow_type}')

    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)

    validate_task_type(workflow_type)
    return list_continuous_patch_v1(cmd, registry)


def cancel_runs(cmd,
                resource_group_name,
                registry_name,
                workflow_type):
    '''cancel all running scans in continuous patch in the registry.'''
    logger.debug('Entering cancel_runs with parameters:%s %s %s', resource_group_name, registry_name, workflow_type)
    validate_task_type(workflow_type)
    cancel_continuous_patch_runs(cmd, resource_group_name, registry_name)


def list_scan_status(cmd, registry_name, resource_group_name, status, workflow_type):
    '''track in continuous patch in the registry.'''
    logger.debug('Entering track_scan_status with parameters:%s %s %s', resource_group_name, registry_name, workflow_type)

    validate_task_type(workflow_type)
    acr_client_registries = cf_acr_registries(cmd.cli_ctx, None)
    registry = acr_client_registries.get(resource_group_name, registry_name)

    image_status = track_scan_progress(cmd, resource_group_name, registry, status)
    for image in image_status:
        print(image)

    print(f"Total images: {len(image_status)}")
