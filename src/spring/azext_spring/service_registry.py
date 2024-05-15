# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from azext_spring.jobs.job import (append_managed_component_ref, backfill_secret_envs,
                                   job_has_resource_id_ref_ignore_case, remove_managed_component_ref)
from azext_spring.vendored_sdks.appplatform.v2024_05_01_preview import models
from azext_spring._utils import (wait_till_end)
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from msrestazure.tools import resource_id

SERVICE_REGISTRY_NAME = "serviceRegistry"
RESOURCE_ID = "resourceId"

RESOURCE_TYPE = "serviceRegistries"
DEFAULT_NAME = "default"

logger = get_logger(__name__)


def service_registry_create(cmd, client, service, resource_group):
    return client.service_registries.begin_create_or_update(resource_group, service, DEFAULT_NAME)


def service_registry_delete(cmd, client, service, resource_group):
    return client.service_registries.begin_delete(resource_group, service, DEFAULT_NAME)


def service_registry_show(cmd, client, service, resource_group):
    return client.service_registries.get(resource_group, service, DEFAULT_NAME)


def service_registry_bind(cmd, client, service, resource_group, app=None, job=None):
    """app and job will be validated so that one and only one is not None.
    """
    if app is not None:
        return _service_registry_bind_or_unbind_app(cmd, client, service, resource_group, app, True)
    else:
        return _service_registry_bind_or_unbind_job(cmd, client, service, resource_group, job, True)


def service_registry_unbind(cmd, client, service, resource_group, app=None, job=None):
    """app and job will be validated so that one and only one is not None.
    """
    if app is not None:
        return _service_registry_bind_or_unbind_app(cmd, client, service, resource_group, app, False)
    else:
        return _service_registry_bind_or_unbind_job(cmd, client, service, resource_group, job, False)


def _service_registry_bind_or_unbind_app(cmd, client, service, resource_group, app_name, enabled):
    app = client.apps.get(resource_group, service, app_name)
    app.properties.addon_configs = _get_app_addon_configs_with_service_registry(app.properties.addon_configs)

    if (app.properties.addon_configs[SERVICE_REGISTRY_NAME][RESOURCE_ID] != "") == enabled:
        logger.warning('App "{}" has been {}binded'.format(app_name, '' if enabled else 'un'))
        return app

    service_registry_id = _get_service_registry_resource_id(cmd, resource_group, service)

    if enabled:
        app.properties.addon_configs[SERVICE_REGISTRY_NAME][RESOURCE_ID] = service_registry_id
    else:
        app.properties.addon_configs[SERVICE_REGISTRY_NAME][RESOURCE_ID] = ""
    return client.apps.begin_update(resource_group, service, app_name, app)


def _service_registry_bind_or_unbind_job(cmd, client, service, resource_group, job_name, enabled):
    job: models.JobResource = client.job.get(resource_group, service, job_name)
    job = backfill_secret_envs(client, resource_group, service, job_name, job)
    service_registry_id = _get_service_registry_resource_id(cmd, resource_group, service)
    is_job_already_binded = _is_job_already_binded_to_sr(job, service_registry_id)
    if is_job_already_binded == enabled:
        logger.warning(f'Job {job_name} has been {"" if enabled else "un"}binded.')
        return job

    if enabled:
        job = _append_service_registry_reference(job, service_registry_id)
    else:
        job = _remove_service_registry_reference(job, service_registry_id)
    """TODO(jiec): There seems to be issues in SDK if we directly return client.job.begin_create_or_update.
    """
    poller = client.job.begin_create_or_update(resource_group, service, job_name, job)
    wait_till_end(cmd, poller)
    return client.job.get(resource_group, service, job_name)


def _get_app_addon_configs_with_service_registry(addon_configs):
    if addon_configs is None:
        addon_configs = {}
    if addon_configs.get(SERVICE_REGISTRY_NAME) is None:
        addon_configs[SERVICE_REGISTRY_NAME] = {}
    if addon_configs[SERVICE_REGISTRY_NAME].get(RESOURCE_ID) is None:
        addon_configs[SERVICE_REGISTRY_NAME][RESOURCE_ID] = ""
    return addon_configs


def _get_service_registry_resource_id(cmd, resource_group, service):
    return resource_id(
        subscription=get_subscription_id(cmd.cli_ctx),
        resource_group=resource_group,
        namespace='Microsoft.AppPlatform',
        type='Spring',
        name=service,
        child_type_1=RESOURCE_TYPE,
        child_name_1=DEFAULT_NAME
    )


def _is_job_already_binded_to_sr(job: models.JobResource, service_registry_id: str):
    return job_has_resource_id_ref_ignore_case(job, service_registry_id)


def _append_service_registry_reference(job: models.JobResource, service_registry_id) -> models.JobResource:
    return append_managed_component_ref(job, service_registry_id)


def _remove_service_registry_reference(job: models.JobResource, service_registry_id) -> models.JobResource:
    return remove_managed_component_ref(job, service_registry_id)
