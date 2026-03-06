# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import time
from knack.log import get_logger
from azure.cli.core.azclierror import ResourceNotFoundError, RequiredArgumentMissingError, ClientRequestError, AzureConnectionError, AzureResponseError, AzureInternalError
from .vendored_sdks.containerregistry.v2025_06_01_preview.models._models_py3 import PipelineRun, PipelineRunRequest, PipelineRunSourceProperties, PipelineRunTargetProperties

logger = get_logger(__name__)


def create_pipelinerun(client, resource_group_name, registry_name, pipeline_name, pipeline_run_name, pipeline_type, storage_blob_name, artifacts=None, force_update_tag=False):
    '''Create a pipeline run.'''

    if pipeline_type == "import":
        try:
            raw_result = client.import_pipelines.get(resource_group_name=resource_group_name,
                                                     registry_name=registry_name,
                                                     import_pipeline_name=pipeline_name)
        except Exception as e:
            raise ResourceNotFoundError(f'Import pipeline {pipeline_name} not found on registry {registry_name} in the {resource_group_name} resource group.') from e

        # Display authentication method
        storage_access_mode = raw_result.source.storage_access_mode if raw_result.source else None
        if storage_access_mode == 'ManagedIdentity':
            logger.warning("Authenticating to Storage Account using Entra Managed Identity.")
        elif storage_access_mode == 'SasToken':
            logger.warning("Authenticating to Storage Account using Storage SAS Token.")

        pipeline_resource_id = raw_result.id
        pipeline_run_source = PipelineRunSourceProperties(name=storage_blob_name)
        pipeline_run_request = PipelineRunRequest(pipeline_resource_id=pipeline_resource_id, source=pipeline_run_source)

    else:
        try:
            raw_result = client.export_pipelines.get(resource_group_name=resource_group_name,
                                                     registry_name=registry_name,
                                                     export_pipeline_name=pipeline_name)
        except Exception as e:
            raise ResourceNotFoundError(f'Export pipeline {pipeline_name} not found on registry {registry_name} in the {resource_group_name} resource group.') from e

        # Display authentication method
        storage_access_mode = raw_result.target.storage_access_mode if raw_result.target else None
        if storage_access_mode == 'ManagedIdentity':
            logger.warning("Authenticating to Storage Account using Entra Managed Identity.")
        elif storage_access_mode == 'SasToken':
            logger.warning("Authenticating to Storage Account using Storage SAS Token.")

        pipeline_resource_id = raw_result.id
        if artifacts is None:
            raise RequiredArgumentMissingError("artifacts cannot be null for Export PipelineRuns. Please provide a space-separated list of container images to be exported in the form REPOSITORY:TAG or REPOSITORY@sha256:90659bf80b44ce6be8234e6ff90a1ac34acbeb826903b02cfa0da11c82cbc042.")

        # add tag ":latest" if a tag is not present
        artifacts = [artifact + ":latest" if ":" not in artifact and "@" not in artifact else artifact for artifact in artifacts]

        pipeline_run_target = PipelineRunTargetProperties(name=storage_blob_name)
        pipeline_run_request = PipelineRunRequest(pipeline_resource_id=pipeline_resource_id,
                                                  target=pipeline_run_target,
                                                  artifacts=artifacts)

    force_update_tag_str = str(time.time()) if force_update_tag else None
    pipeline_run = PipelineRun(request=pipeline_run_request, force_update_tag=force_update_tag_str)

    return client.pipeline_runs.begin_create(resource_group_name=resource_group_name,
                                             registry_name=registry_name,
                                             pipeline_run_name=pipeline_run_name,
                                             pipeline_run_create_parameters=pipeline_run)


def get_pipelinerun(client, resource_group_name, registry_name, pipeline_run_name):
    '''Get a pipeline run.'''

    result = client.pipeline_runs.get(resource_group_name=resource_group_name,
                                      registry_name=registry_name,
                                      pipeline_run_name=pipeline_run_name)
    
    # Display authentication method used during pipeline run
    if result.request and result.request.pipeline_resource_id:
        try:
            pipeline_resource_id = result.request.pipeline_resource_id
            storage_access_mode = None
            
            # Parse resource ID and fetch pipeline based on type
            if '/exportPipelines/' in pipeline_resource_id:
                pipeline_name = pipeline_resource_id.split('/exportPipelines/')[-1]
                pipeline = client.export_pipelines.get(resource_group_name, registry_name, pipeline_name)
                storage_access_mode = pipeline.target.storage_access_mode if pipeline.target else None
            elif '/importPipelines/' in pipeline_resource_id:
                pipeline_name = pipeline_resource_id.split('/importPipelines/')[-1]
                pipeline = client.import_pipelines.get(resource_group_name, registry_name, pipeline_name)
                storage_access_mode = pipeline.source.storage_access_mode if pipeline.source else None
            
            # Display diagnostic messages
            if storage_access_mode == 'ManagedIdentity':
                logger.warning("Authenticating to Storage Account using Entra Managed Identity.")
            elif storage_access_mode == 'SasToken':
                logger.warning("Authenticating to Storage Account using Storage SAS Token.")
        except Exception:
            pass
    
    return result


def delete_pipelinerun(client, resource_group_name, registry_name, pipeline_run_name):
    '''Delete a pipeline run.'''

    try:
        client.pipeline_runs.get(resource_group_name=resource_group_name,
                                 registry_name=registry_name,
                                 pipeline_run_name=pipeline_run_name)

    except Exception as e:
        raise ResourceNotFoundError(f'Pipeline-run {pipeline_run_name} not found on registry {registry_name} in the {resource_group_name} resource group.') from e

    return client.pipeline_runs.begin_delete(resource_group_name=resource_group_name,
                                             registry_name=registry_name,
                                             pipeline_run_name=pipeline_run_name)


def list_pipelinerun(client, resource_group_name, registry_name, top=None):
    '''List pipeline runs on a registry.'''

    pipelineruns = client.pipeline_runs.list(resource_group_name=resource_group_name, registry_name=registry_name)

    if top is None:
        return pipelineruns

    top_int = int(top)

    return list(pipelineruns)[-top_int:]


def clean_pipelinerun(client, resource_group_name, registry_name, dry_run=False):
    pipelineruns = client.pipeline_runs.list(resource_group_name=resource_group_name, registry_name=registry_name)

    failed_pipelineruns = list(filter(lambda x: (x.provisioning_state == 'Failed'), pipelineruns))
    num_failed_pipelineruns = len(failed_pipelineruns)

    logger.warning('Found %s failed pipeline-runs to delete.', num_failed_pipelineruns)

    if dry_run:
        logger.warning('The following failed pipeline-runs would have been deleted:')
        return failed_pipelineruns

    succ_count = 0
    failed_count = 0
    for pipelinerun in failed_pipelineruns:
        try:
            client.pipeline_runs.begin_delete(resource_group_name=resource_group_name,
                                              registry_name=registry_name,
                                              pipeline_run_name=pipelinerun.name)

            succ_count += 1

        except (ClientRequestError, AzureConnectionError, AzureResponseError, AzureInternalError, ResourceNotFoundError):
            failed_count += 1

        if succ_count % 100 == 0:
            logger.warning('Deletion in progress: Deleted %s/%s failed pipeline-runs. %s deletions failed.', succ_count, num_failed_pipelineruns, failed_count)

    logger.warning('Deletion complete: Deleted %s failed pipeline-runs.', succ_count)
    logger.warning('%s deletions failed.', failed_count)

    return None
