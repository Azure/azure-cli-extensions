# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import shlex
import time
from threading import Thread

import requests
from azure.cli.core.commands.client_factory import get_subscription_id
from azext_spring._clierror import (PermissionDenyError, JobExecutionInstanceNotFoundError)
from azext_spring._utils import (get_hostname, get_bearer_auth, wait_till_end, parallel_start_threads,
                                 sequential_start_threads, string_equals_ignore_case, get_service_instance_resource_id)
from azext_spring.jobs.job_deployable_factory import deployable_selector
from azext_spring.jobs.models.job_execution_instance import (JobExecutionInstanceCollection, JobExecutionInstance)
from azext_spring.log_stream.log_stream_operations import (attach_logs_query_options, log_stream_from_url,
                                                           LogStreamBaseQueryOptions)
from azext_spring.log_stream.log_stream_validators import validate_thread_number
from azext_spring.log_stream.writer import (DefaultWriter, PrefixWriter)
from azext_spring.vendored_sdks.appplatform.v2024_05_01_preview import models
from azure.cli.core.util import sdk_no_wait
from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)

LOG_RUNNING_PROMPT = "This command usually takes minutes to run. Add '--verbose' parameter if needed."
DEFAULT_BUILD_RESULT_ID = "<default>"
# Use this value to reset timeout for job
JOB_TIMEOUT_RESET_VALUE = -1
JOB_LOG_READER_ROLE_NAME = "Azure Spring Apps Job Log Reader Role"

#  Job's command usually operates an Spring/Job and the Spring/Job/Execution under the job.
# The general idea of these command is putting all input command in parameter dict and let the Resource factory to construct the payload.
# - A job must consume a path can be deployable, it can be custom container or build result resource id,
# - _job_deployable_factory determines the deployable type and upload necessary binary/code to the service when constructing the deployable_path.

def job_create(cmd, client, resource_group, service, name,
               parallelism=None,
               timeout=None,  # timeout in seconds
               retry_limit=None,
               cpu="1",
               memory="2Gi",
               envs=None,
               secret_envs=None,
               args=None,
               bind_service_registry=None,
               bind_config_server=None) -> models.JobResource:
    job_resource = models.JobResource(
        properties=models.JobResourceProperties(
            trigger_config=models.ManualJobTriggerConfig(
                parallelism=parallelism,
                timeout_in_seconds=timeout if timeout != JOB_TIMEOUT_RESET_VALUE else None,
                retry_limit=retry_limit
            ),
            source=None,
        )
    )

    job_resource.properties = _update_job_properties(job_resource.properties,
                                                     None,
                                                     envs,
                                                     secret_envs,
                                                     args,
                                                     cpu,
                                                     memory)

    # Bind service registry and config server is only avialable for job create and service-registry command group
    job_resource.properties.managed_component_references = []
    if bind_service_registry:
        sr_ref = models.ManagedComponentReference(resource_id=bind_service_registry)
        job_resource.properties.managed_component_references.append(sr_ref)

    if bind_config_server:
        cs_ref = models.ManagedComponentReference(resource_id=bind_config_server)
        job_resource.properties.managed_component_references.append(cs_ref)

    logger.warning(f"Start to create job '{name}'..")
    poller = client.job.begin_create_or_update(resource_group, service, name, job_resource)
    wait_till_end(cmd, poller)
    logger.warning(f"Job '{name}' is created successfully.")
    return job_get(client, resource_group, service, name)


def job_update(cmd, client, resource_group, service, name,
               parallelism=None,
               timeout=None,  # timeout in seconds
               retry_limit=None,
               cpu=None,
               memory=None,
               envs=None,
               secret_envs=None,
               args=None) -> models.JobResource:
    '''job_update
    Update job with configuration
    '''
    trigger_config = models.ManualJobTriggerConfig(
        parallelism=parallelism,
        timeout_in_seconds=timeout,
        retry_limit=retry_limit
    )
    job_resource = client.job.get(resource_group, service, name)
    job_resource = backfill_secret_envs(client, resource_group, service, name, job_resource)
    job_resource.properties = _update_job_properties(job_resource.properties, trigger_config, envs, secret_envs, args,
                                                     cpu, memory)

    logger.warning(f"Start to update job '{name}'..")
    poller = client.job.begin_create_or_update(resource_group, service, name, job_resource)
    wait_till_end(cmd, poller)
    logger.warning(f"Job '{name}' is updated successfully.")
    return job_get(client, resource_group, service, name)


def job_delete(cmd, client, resource_group, service, name):
    client.job.get(resource_group, service, name)
    return client.job.begin_delete(resource_group, service, name)


def job_get(client, resource_group, service, name):
    return client.job.get(resource_group, service, name)


def job_list(cmd, client, resource_group, service):
    return client.jobs.list(resource_group, service)


def job_deploy(cmd, client, resource_group, service, name,
               parallelism=None,
               timeout=None,  # timeout in seconds
               retry_limit=None,
               # job.source
               build_env=None,
               builder=None,
               build_cpu=None,
               build_memory=None,
               source_path=None,
               artifact_path=None,
               version=None,
               cpu=None,
               memory=None,
               envs=None,
               secret_envs=None,
               args=None,
               # only used in validator
               disable_validation=None,
               no_wait=False):
    logger.warning(LOG_RUNNING_PROMPT)

    trigger_config = models.ManualJobTriggerConfig(
        parallelism=parallelism,
        timeout_in_seconds=timeout,
        retry_limit=retry_limit
    )
    job_resource = client.job.get(resource_group, service, name)
    job_resource = backfill_secret_envs(client, resource_group, service, name, job_resource)
    job_resource.properties = _update_job_properties(job_resource.properties, trigger_config, envs, secret_envs, args, cpu,
                                                     memory)

    kwargs = {
        'cmd': cmd,
        'client': client,
        'resource_group': resource_group,
        'service': service,
        'job': name,
        'source_path': source_path,
        'artifact_path': artifact_path,
        'build_env': build_env,
        'build_cpu': build_cpu,
        'build_memory': build_memory,
        'builder': builder,
        'no_wait': no_wait
    }

    deployable = deployable_selector(**kwargs)
    kwargs['source_type'] = deployable.get_source_type(**kwargs)
    kwargs['total_steps'] = deployable.get_total_deploy_steps(**kwargs)
    deployable_path = deployable.build_deployable_path(**kwargs)

    job_resource.properties = _update_source(job_resource.properties, deployable_path, version)

    poller = sdk_no_wait(no_wait, client.job.begin_create_or_update,
                         resource_group, service, name, job_resource)
    if "succeeded" != poller.status().lower():
        return poller
    return client.job.get(resource_group, service, name)


def job_start(cmd, client, resource_group, service, name,
              envs=None,
              secret_envs=None,
              cpu=None,
              memory=None,
              args=None,
              wait_until_finished=False):
    job_execution_template = models.JobExecutionTemplate(
        environment_variables=_update_envs(None, envs, secret_envs),
        args=_convert_args(args),
        resource_requests=_update_resource_requests(None, cpu, memory))

    if wait_until_finished is False:
        """TODO(jiec): There seems to be SDK issue when directly return client.job.begin_start
        """
        poller = client.job.begin_start(resource_group, service, name, job_execution_template)
        execution_name = poller.result().name
        wait_till_end(poller)
        return client.job_execution.get(resource_group, service, name, execution_name)
    else:
        poller = sdk_no_wait(False, client.job.begin_start,
                             resource_group, service, name, job_execution_template)
        execution_name = poller.result().name
        return _poll_until_job_end(client, resource_group, service, name, execution_name)


def job_execution_cancel(cmd, client,
                         resource_group,
                         service,
                         job,
                         name,  # execution name
                         no_wait=False):
    return sdk_no_wait(no_wait, client.job_execution.begin_cancel,
                       resource_group, service, job, name)


def job_execution_get(cmd, client, resource_group, service, job, name):
    return client.job_execution.get(resource_group, service, job, name)


def job_execution_list(cmd, client, resource_group, service, job):
    return client.job_executions.list(resource_group, service, job)


def job_log_stream(cmd, client, resource_group, service, name, execution, all_instances=None, instance=None,
                   follow=None, max_log_requests=5, lines=100, since=None, limit=2048):
    try:
        _job_log_stream(cmd, client, resource_group, service, name, execution, all_instances, instance,
                        follow, max_log_requests, lines, since, limit)
    except PermissionDenyError:
        operation_name = "read the job log stream"
        _handle_log_stream_permission_deny(cmd, resource_group, service, operation_name)
    except JobExecutionInstanceNotFoundError:
        _handle_log_stream_pod_not_found(cmd, resource_group, service, name, execution)


def job_execution_instance_list(cmd, client, resource_group, service, job, execution):
    try:
        return _list_job_execution_instances(cmd, client, resource_group, service, job, execution)
    except PermissionDenyError:
        operation_name = "perform action 'Microsoft.AppPlatform/Spring/jobs/executions/listInstances/action'"
        _handle_log_stream_permission_deny(cmd, resource_group, service, operation_name)
    except JobExecutionInstanceNotFoundError:
        _handle_log_stream_pod_not_found(cmd, resource_group, service, job, execution)


def job_has_resource_id_ref_ignore_case(job: models.JobResource, resource_id: str):
    if job.properties.managed_component_references is None:
        return False

    if len(job.properties.managed_component_references) == 0:
        return False

    for ref in job.properties.managed_component_references:
        if string_equals_ignore_case(ref.resource_id, resource_id):
            return True

    return False


def append_managed_component_ref(job: models.JobResource, component_id: str):
    ref = models.ManagedComponentReference(resource_id=component_id)
    if job.properties.managed_component_references is None:
        job.properties.managed_component_references = [ref]
    else:
        job.properties.managed_component_references.append(ref)
    return job


def remove_managed_component_ref(job: models.JobResource, component_id: str):
    target_ref_list = []
    if job.properties.managed_component_references is not None:
        for ref in job.properties.managed_component_references:
            if not string_equals_ignore_case(ref.resource_id, component_id):
                target_ref_list.append(ref)
    job.properties.managed_component_references = target_ref_list
    return job


def _update_job_properties(properties: models.JobResourceProperties,
                           trigger_config: models.ManualJobTriggerConfig,
                           envs: dict,
                           secret_envs: dict,
                           args: str,
                           cpu: str,
                           memory: str):
    if not any([trigger_config, envs, secret_envs, args, cpu, memory]):
        return properties
    if properties is None:
        properties = models.JobResourceProperties()
    properties.template = _update_job_properties_template(properties.template, envs, secret_envs, args, cpu, memory)
    properties.trigger_config = _patch_job_trigger_config(properties.trigger_config, trigger_config)
    return properties


def _update_source(properties, deployable_path, version):
    if properties is None:
        properties = models.JobResourceProperties()
    properties.source = models.BuildResultUserSourceInfo(
        build_result_id=deployable_path,
        version=version
    )
    return properties


def _update_job_properties_template(template, envs, secret_envs, args, cpu, memory):
    if (template is None):
        template = models.JobExecutionTemplate()
    template.environment_variables = _update_envs(template.environment_variables, envs, secret_envs)
    template.args = _update_args(template.args, args)
    template.resource_requests = _update_resource_requests(template.resource_requests, cpu, memory)
    return template


def _update_envs(envs: [models.EnvVar], envs_dict: dict, secrets_dict: dict):
    if envs is None:
        envs = []
    existed_properties = [env for env in envs if env.value is not None]
    existed_secrets = [env for env in envs if
                       ((env.secret_value is not None) or (env.secret_value is None and env.value is None))]
    target_properties = existed_properties
    target_secrets = existed_secrets
    if envs_dict is not None and isinstance(envs_dict, dict):
        target_properties = [models.EnvVar(name=key, value=envs_dict[key]) for key in envs_dict.keys()]
    if secrets_dict is not None and isinstance(secrets_dict, dict):
        target_secrets = [models.EnvVar(name=key, secret_value=secrets_dict[key]) for key in secrets_dict.keys()]
    return target_properties + target_secrets


def _update_secrets(envs: [models.EnvVar], secrets: [models.Secret]):
    if envs is None:
        envs = []
    target_properties = [env for env in envs if env.value is not None]
    target_secrets = []
    if secrets is not None:
        target_secrets = [models.EnvVar(name=secret.name, secret_value=secret.value) for secret in secrets]
    return target_properties + target_secrets


def _update_resource_requests(existing, cpu, memory):
    existing = existing if existing is not None else models.ResourceRequests()
    resource_requests = models.ResourceRequests(
        cpu=cpu or existing.cpu,
        memory=memory or existing.memory
    )
    return resource_requests


def _update_args(existing, args):
    args = _convert_args(args)
    if args is not None:
        return args
    return existing


def _convert_args(args):
    if args is None:
        return args

    return shlex.split(args)


def _poll_until_job_end(client, resource_group, service, job_name, job_execution_name):
    while True:
        execution = client.job_execution.get(resource_group, service, job_name, job_execution_name)
        status = execution.status
        if _is_job_execution_in_final_state(status):
            logger.warning(
                f"Job execution '{job_execution_name}' is in final status '{status}'. Exiting polling loop.")
            return execution
        else:
            logger.warning(
                f"Job execution '{job_execution_name}' is in status '{status}'. Polling again in 10 second...")
        time.sleep(10)


def _is_job_execution_in_final_state(status):
    return status is not None and status in (
        models.JobExecutionRunningState.COMPLETED,
        models.JobExecutionRunningState.FAILED,
        models.JobExecutionRunningState.CANCELED)


def backfill_secret_envs(client, resource_group, service, job_name, job_resource: models.JobResource):
    existing_secret_collection = client.job.list_env_secrets(resource_group, service, job_name)
    if existing_secret_collection is not None and existing_secret_collection.value is not None:
        target_env_list = _update_secrets(job_resource.properties.template.environment_variables,
                                          existing_secret_collection.value)
        job_resource.properties.template.environment_variables = target_env_list
    return job_resource


def _patch_job_trigger_config(existed: models.ManualJobTriggerConfig,
                              patch: models.ManualJobTriggerConfig) -> models.ManualJobTriggerConfig:
    if patch is None:
        return existed

    if existed is None:
        existed = models.ManualJobTriggerConfig()

    result = existed
    if patch.parallelism is not None:
        result.parallelism = patch.parallelism
    if patch.timeout_in_seconds is not None:
        # Handle the timeout reset
        if patch.timeout_in_seconds == JOB_TIMEOUT_RESET_VALUE:
            result.timeout_in_seconds = None
        else:
            result.timeout_in_seconds = patch.timeout_in_seconds
    if patch.retry_limit is not None:
        result.retry_limit = patch.retry_limit

    return result


def _get_log_stream_urls(cmd, client, resource_group, service, job_name, execution_name,
                         all_instances, instance, queryOptions: LogStreamBaseQueryOptions):
    hostname = get_hostname(cmd.cli_ctx, client, resource_group, service)
    url_dict = {}

    if not all_instances and not instance:
        logger.warning("No `-i/--instance` or `--all-instances` parameters specified.")
        instances: [JobExecutionInstance] = _list_job_execution_instances(cmd, client, resource_group, service,
                                                                          job_name, execution_name)
        if instances is None or len(instances) == 0:
            logger.warning(f"No instances found for job execution: '{job_name}/{execution_name}'.")
            return url_dict
        elif instances is not None and len(instances) > 1:
            logger.warning("Multiple instances found:")
            for temp_instance in instances:
                logger.warning("{}".format(temp_instance.name))
            logger.warning("Please use '-i/--instance' parameter to specify the instance name, "
                           "or use `--all-instance` parameter to get logs for all instances.")
            return url_dict
        elif instances is not None and len(instances) == 1:
            logger.warning("Exact one instance found, will get logs for it:")
            logger.warning('{}'.format(instances[0].name))
            # Make it as if user has specified exact instance name
            instance = instances[0].name

    if all_instances is True:
        instances: [JobExecutionInstance] = _list_job_execution_instances(cmd, client, resource_group, service,
                                                                          job_name, execution_name)
        if instances is None or len(instances) == 0:
            logger.warning(f"No instances found for job execution: '{job_name}/{execution_name}'.")
            return url_dict
        for i in instances:
            url = _get_log_stream_url(hostname, job_name, execution_name, i.name, queryOptions)
            url_dict[url] = JobExecutionInstance(name=i.name)
    elif instance:
        url = _get_log_stream_url(hostname, job_name, execution_name, instance, queryOptions)
        url_dict[url] = JobExecutionInstance(name=instance)

    return url_dict


def _get_log_stream_url(hostname, job_name, execution_name, job_execution_instance_name,
                        queryOptions: LogStreamBaseQueryOptions):
    url_template = "https://{}/api/jobs/{}/executions/{}/instances/{}/logstream"
    url = url_template.format(hostname, job_name, execution_name, job_execution_instance_name)
    url = attach_logs_query_options(url, queryOptions)
    return url


def _list_job_execution_instances(cmd, client, resource_group, service, job, execution) -> [JobExecutionInstance]:
    auth = get_bearer_auth(cmd.cli_ctx)
    url = _get_list_job_execution_instances_url(cmd, client, resource_group, service, job, execution)
    connect_timeout_in_seconds = 30
    read_timeout_in_seconds = 60
    timeout = (connect_timeout_in_seconds, read_timeout_in_seconds)
    with requests.get(url, stream=False, auth=auth, timeout=timeout) as response:
        if response.status_code != 200:
            _handle_and_raise_list_job_execution_instance_error(url, response)
        return _parse_job_execution_instances(response.json())


def _get_list_job_execution_instances_url(cmd, client, resource_group, service, job, execution):
    hostname = get_hostname(cmd, client, resource_group, service)
    return f"https://{hostname}/api/jobs/{job}/executions/{execution}/instances"


def _handle_and_raise_list_job_execution_instance_error(url, response):
    failure_reason = response.reason
    if response.content:
        if isinstance(response.content, bytes):
            failure_reason = f"{failure_reason}:{response.content.decode('utf-8')}"
        else:
            failure_reason = f"{failure_reason}:{response.content}"
    msg = f"Failed to access the url '{url}' with status code '{response.status_code}' and reason '{failure_reason}'"
    if response.status_code == 401:
        raise PermissionDenyError(msg)
    if response.status_code == 404 and "No pod found for job execution" in failure_reason:
        raise JobExecutionInstanceNotFoundError(msg)
    else:
        raise CLIError(msg)


def _parse_job_execution_instances(response_json) -> [JobExecutionInstance]:
    p = JobExecutionInstanceCollection.deserialize(response_json)
    if p.value is None:
        raise CLIError("Failed to parse the response '{}'".format(response_json))

    return p.value


def _get_log_threads(all_instances, url_dict, auth, exceptions):
    threads = []
    need_prefix = all_instances is True
    for url in url_dict.keys():
        writer = _get_default_writer()
        if need_prefix:
            instance_info = url_dict[url]
            prefix = "[{}]".format(instance_info.name)
            writer = _get_prefix_writer(prefix)
        threads.append(Thread(target=log_stream_from_url, args=(url, auth, None, exceptions, writer)))
    return threads


def _get_prefix_writer(prefix):
    """
    Define this method, so that we can mock this method in scenario test to test output
    """
    return PrefixWriter(prefix)


def _get_default_writer():
    """
    Define this method, so that we can mock this method in scenario test to test output
    """
    return DefaultWriter()


def _job_log_stream(cmd, client, resource_group, service, name, execution, all_instances=None, instance=None,
                    follow=None, max_log_requests=5, lines=100, since=None, limit=2048):
    queryOptions = LogStreamBaseQueryOptions(follow=follow, lines=lines, since=since, limit=limit)
    url_dict = _get_log_stream_urls(cmd, client, resource_group, service, name, execution, all_instances,
                                    instance, queryOptions)
    validate_thread_number(follow, len(url_dict), max_log_requests)
    auth = get_bearer_auth(cmd.cli_ctx)
    exceptions = []
    threads = _get_log_threads(all_instances, url_dict, auth, exceptions)

    if follow and len(threads) > 1:
        parallel_start_threads(threads)
    else:
        sequential_start_threads(threads)

    if exceptions:
        raise exceptions[0]


def _handle_log_stream_permission_deny(cmd, resource_group, service, operation_name):
    sub_id = get_subscription_id(cmd.cli_ctx)
    resource_id = get_service_instance_resource_id(sub_id=sub_id, group=resource_group, service=service)
    msg = f"(AuthorizationFailed) You do not have authorization to {operation_name} over the scope '{resource_id}' . " \
          f"Please check if you have the Azure role '{JOB_LOG_READER_ROLE_NAME}' ." \
          " If access was recently granted, please refresh your credentials."
    raise PermissionDenyError(msg)


def _handle_log_stream_pod_not_found(cmd, resource_group, service, job, execution):
    sub_id = get_subscription_id(cmd.cli_ctx)
    resource_id = get_service_instance_resource_id(sub_id=sub_id, group=resource_group, service=service)
    execution_resource_id = f"{resource_id}/jobs/{job}/executions/{execution}"
    msg = f"No instance found for job execution '{execution_resource_id}' ."
    raise JobExecutionInstanceNotFoundError(msg)
