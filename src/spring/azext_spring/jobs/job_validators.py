# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from re import match

from azext_spring._resource_quantity import (validate_cpu, validate_memory)
from azext_spring._util_enterprise import (get_client)
from azext_spring._validators_enterprise import (only_support_enterprise, validate_source_path, validate_artifact_path,
                                                 validate_build_env, _get_eactly_one_service_registry_resource_id)
from azext_spring.jobs.job import JOB_TIMEOUT_RESET_VALUE
from azext_spring.log_stream.log_stream_validators import (validate_log_limit, validate_log_lines, validate_log_since,
                                                           validate_max_log_requests,
                                                           validate_all_instances_and_instance_are_mutually_exclusive)
from azext_spring.vendored_sdks.appplatform.v2024_05_01_preview import models
from azure.cli.core.azclierror import (InvalidArgumentValueError, ClientRequestError, ValidationError)
from azure.cli.core.commands.validators import validate_tag


def validate_job_create(cmd, namespace):
    _validate_job_name(namespace.name)
    validate_cpu(namespace.cpu)
    validate_memory(namespace.memory)
    _validate_envs(namespace)
    _validate_secret_envs(namespace)
    _validate_parallelism(namespace)
    _validate_retry_limit(namespace)
    _validate_timeout(namespace)
    only_support_enterprise(cmd, namespace)
    _ensure_job_not_exist(cmd, namespace.resource_group, namespace.service, namespace.name)
    _validate_binding_default_service_registry(cmd, namespace)
    _validate_binding_default_config_server(cmd, namespace)


def validate_job_update(cmd, namespace):
    _validate_job_name(namespace.name)
    validate_cpu(namespace.cpu)
    validate_memory(namespace.memory)
    _validate_envs(namespace)
    _validate_secret_envs(namespace)
    _validate_parallelism(namespace)
    _validate_retry_limit(namespace)
    _validate_timeout(namespace)
    only_support_enterprise(cmd, namespace)


def validate_job_delete(cmd, namespace):
    _validate_job_name(namespace.name)
    only_support_enterprise(cmd, namespace)


def validate_job_get(cmd, namespace):
    _validate_job_name(namespace.name)
    only_support_enterprise(cmd, namespace)


def validate_job_list(cmd, namespace):
    only_support_enterprise(cmd, namespace)


def validate_job_deploy(cmd, namespace):
    _validate_job_name(namespace.name)
    validate_cpu(namespace.cpu)
    validate_memory(namespace.memory)
    _validate_envs(namespace)
    _validate_secret_envs(namespace)
    validate_source_path(namespace)
    validate_artifact_path(namespace)
    validate_build_env(cmd, namespace)
    _validate_parallelism(namespace)
    _validate_retry_limit(namespace)
    _validate_timeout(namespace)
    only_support_enterprise(cmd, namespace)


def validate_job_start(cmd, namespace):
    _validate_job_name(namespace.name)
    validate_cpu(namespace.cpu)
    validate_memory(namespace.memory)
    _validate_envs(namespace)
    _validate_secret_envs(namespace)
    validate_cpu(namespace.cpu)
    validate_memory(namespace.memory)
    only_support_enterprise(cmd, namespace)
    _validate_job_has_been_deployed(cmd, namespace)


def validate_job_execution_cancel(cmd, namespace):
    _validate_job_name(namespace.job)
    only_support_enterprise(cmd, namespace)


def validate_job_execution_get(cmd, namespace):
    _validate_job_name(namespace.job)
    only_support_enterprise(cmd, namespace)


def validate_job_execution_list(cmd, namespace):
    _validate_job_name(namespace.job)
    only_support_enterprise(cmd, namespace)


def validate_job_log_stream(cmd, namespace):
    _validate_mutual_exclusive_param(namespace)
    validate_log_lines(namespace)
    validate_log_since(namespace)
    validate_log_limit(namespace)
    validate_max_log_requests(namespace)
    only_support_enterprise(cmd, namespace)


def validate_job_execution_instance_list(cmd, namespace):
    _validate_job_name(namespace.job)
    only_support_enterprise(cmd, namespace)


def validate_job_name_for_oss_config_server_bind(namespace):
    if namespace.job is not None and namespace.app is not None:
        raise InvalidArgumentValueError(f"App name {namespace.app} and job name {namespace.job} cannot be both set.")
    if namespace.job is None and namespace.app is None:
        raise InvalidArgumentValueError("App name or job name is required.")
    if namespace.job is not None:
        _validate_job_name(namespace.job)


def validate_job_name_for_service_registry_bind(namespace):
    if namespace.job is not None and namespace.app is not None:
        raise InvalidArgumentValueError(f"App name {namespace.app} and job name {namespace.job} cannot be both set.")
    if namespace.job is None and namespace.app is None:
        raise InvalidArgumentValueError("App name or job name is required.")
    if namespace.job is not None:
        _validate_job_name(namespace.job)


def _validate_mutual_exclusive_param(namespace):
    validate_all_instances_and_instance_are_mutually_exclusive(namespace)


def _validate_job_name(job_name):
    matchObj = match(r'^[a-z][a-z0-9-]{2,30}[a-z0-9]$', job_name)
    if matchObj is None:
        raise InvalidArgumentValueError(
            'The job name is invalid. It can contain only lowercase letters, numbers and hyphens. The first character must be a letter. The last character must be a letter or number. The value must be between 4 and 32 characters long.')


def _validate_envs(namespace):
    """ Extracts multiple space-separated properties in key[=value] format """
    if isinstance(namespace.envs, list):
        properties_dict = {}
        for item in namespace.envs:
            properties_dict.update(validate_tag(item))
        namespace.envs = properties_dict


def _validate_secret_envs(namespace):
    """ Extracts multiple space-separated secrets in key[=value] format """
    if isinstance(namespace.secret_envs, list):
        secrets_dict = {}
        for item in namespace.secret_envs:
            secrets_dict.update(validate_tag(item))
        namespace.secret_envs = secrets_dict


def _ensure_job_not_exist(cmd, resource_group, service, job_name):
    job = None
    client = get_client(cmd)
    try:
        job = client.job.get(resource_group, service, job_name)
    except Exception:
        # ignore
        return
    if job:
        raise ValidationError('Job {} already exist, cannot create.'.format(job.id))


def _validate_binding_default_service_registry(cmd, namespace):
    if namespace.bind_service_registry:
        namespace.bind_service_registry = _get_eactly_one_service_registry_resource_id(cmd,
                                                                                       namespace.resource_group,
                                                                                       namespace.service)


def _validate_binding_default_config_server(cmd, namespace):
    if namespace.bind_config_server:
        namespace.bind_config_server = _get_eactly_one_config_server_resource_id(cmd,
                                                                                 namespace.resource_group,
                                                                                 namespace.service)


def _get_eactly_one_service_registry_resource_id(cmd, resource_group, service):
    client = get_client(cmd)
    service_registry_resources = list(client.service_registries.list(resource_group, service))
    if len(service_registry_resources) == 0:
        raise ClientRequestError('Job cannot bind to service registry because it is not configured.')
    if len(service_registry_resources) > 1:
        raise ClientRequestError('Job cannot bind to multiple service registries.')
    return service_registry_resources[0].id


def _get_eactly_one_config_server_resource_id(cmd, resource_group, service):
    client = get_client(cmd)
    cs_resources = list(client.config_servers.list(resource_group, service))
    if len(cs_resources) == 0:
        raise ClientRequestError('Job cannot bind to config server because it is not configured.')
    if len(cs_resources) > 1:
        raise ClientRequestError('Job cannot bind to multiple config servers.')
    return cs_resources[0].id


def _validate_timeout(namespace):
    if namespace.timeout is not None:
        if not (namespace.timeout == -1 or namespace.timeout >= 1):
            raise InvalidArgumentValueError(
                "Invalid value: timeout should greater than or equal to 1. You can use {} to reset timeout.".format(
                    JOB_TIMEOUT_RESET_VALUE))


def _validate_retry_limit(namespace):
    if namespace.retry_limit is not None:
        if not (namespace.retry_limit >= 0):
            raise InvalidArgumentValueError("Invalid value: retry-limit should be greater than or equal to 0.")


def _validate_parallelism(namespace):
    if namespace.parallelism is not None:
        if not (namespace.parallelism >= 1):
            raise InvalidArgumentValueError("Invalid value: parallelism should be greater than or equal to 1.")


def _validate_job_has_been_deployed(cmd, namespace):
    client = get_client(cmd)
    job: models.JobResource = client.job.get(namespace.resource_group, namespace.service, namespace.name)
    if job.properties.source is None:
        raise ClientRequestError(
            'Please deploy to your job before starting it. You can deploy with following exmaple command and learn more from `az spring job deploy --help`.\n'
            'Example: `az spring job deploy --name {} --service {} --resource-group {} --source-path /path/to/source/code/folder`'.format(
                namespace.name, namespace.service, namespace.resource_group))
