# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin
import sys
import requests
from time import sleep
from requests.auth import HTTPBasicAuth
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError, AzureInternalError, DeploymentError
from msrestazure.tools import parse_resource_id
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.azure_exceptions import CloudError
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from ._deployment_uploadable_factory import uploader_selector
from ._log_stream import LogStream

logger = get_logger(__name__)


class BuildService:
    def __init__(self, cmd, client, resource_group, service):
        self.cmd = cmd
        self.client = client
        self.resource_group = resource_group
        self.service = service
        self.name = 'default'
        self.log_stream = None
        self.progress_bar = None
        self.terminated_state = ['Succeeded', 'Failed', 'Deleting']

    def get_total_steps(self):
        return 4

    def build_and_get_result(self, total_steps, **kwargs):
        logger.warning("[1/{}] Requesting for upload URL.".format(total_steps))
        upload_info = self._get_upload_info()
        logger.warning("[2/{}] Uploading package to blob.".format(total_steps))
        uploader_selector(cli_ctx=self.cmd.cli_ctx, upload_url=upload_info.upload_url, **kwargs).upload_and_build(**kwargs)
        if 'app' in kwargs:
            build_name = kwargs['app']
        else:
            build_name = kwargs['build_name']
        logger.warning("[3/{}] Creating or Updating build '{}'.".format(total_steps, build_name))
        build_result_id = self._queue_build(upload_info.relative_path, **kwargs)
        logger.warning("[4/{}] Waiting for building container image to finish. This may take a few minutes.".format(total_steps))
        self._wait_build_finished(build_result_id)
        return build_result_id

    def _get_upload_info(self):
        try:
            response = self.client.build_service.get_resource_upload_url(self.resource_group, self.service, self.name)
            if not response.upload_url:
                raise AzureInternalError("Failed to get a SAS URL to upload context.")
            return response
        except CloudError as e:
            raise AzureInternalError("Failed to get a SAS URL to upload context. Error: {}".format(e.message))
        except AttributeError as e:
            raise AzureInternalError("Failed to get a SAS URL to upload context. Error: {}".format(e))

    def _queue_build(self, relative_path=None, builder=None, build_env=None, build_cpu=None, build_memory=None, app=None, deployment=None, build_name=None,
                     apms=None, certificates=None, build_certificates=None, **_):
        subscription = get_subscription_id(self.cmd.cli_ctx)
        service_resource_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}'.format(subscription, self.resource_group, self.service)
        build_resource_requests = models.BuildResourceRequests(
            cpu=build_cpu,
            memory=build_memory)
        properties = models.BuildProperties(
            builder='{}/buildservices/default/builders/{}'.format(service_resource_id, builder),
            agent_pool='{}/buildservices/default/agentPools/default'.format(service_resource_id),
            relative_path=relative_path,
            env=build_env if build_env else None,
            apms=apms,
            certificates=build_certificates if build_certificates is not None else certificates,
            resource_requests=build_resource_requests)
        build = models.Build(properties=properties)
        if build_name is None:
            build_name = app + '-' + deployment
        try:
            return self.client.build_service.create_or_update_build(self.resource_group,
                                                                    self.service,
                                                                    self.name,
                                                                    build_name,
                                                                    build).properties.triggered_build_result.id
        except (AttributeError, CloudError) as e:
            raise DeploymentError("Failed to create or update a build. Error: {}".format(e.message))

    def _wait_build_finished(self, build_result_id):
        '''
        Wait build result finished and stream the log during the waiting
        '''
        self.progress_bar = self.cmd.cli_ctx.get_progress_controller()
        result = self._get_build_result(build_result_id)

        build_log_streaming_available = True
        while result.properties.provisioning_state not in self.terminated_state:
            try:
                if build_log_streaming_available:
                    self._stream_build_logs(result)
            except Exception as e:
                build_log_streaming_available = False
                logger.debug('Failed to stream log out: {}'.format(str(e)))
                pass
            sleep(5)
            result = self._get_build_result(build_result_id)

        if not build_log_streaming_available:
            logger.warning("Cannot show real time build logs at this moment")
            self._try_print_build_logs(build_result_id)

        if result.properties.provisioning_state != "Succeeded":
            log_url = self._try_get_build_log_url(build_result_id)
            if hasattr(result.properties, "error") and result.properties.error:
                build_error = result.properties.error
                error_msg = "Failed to build container image, error code: {}, message: {}, check the build logs {} for more details and retry.".format(build_error.code, build_error.message, log_url)
            else:
                error_msg = "Failed to build container image, please check the build logs {} and retry.".format(log_url)
            raise DeploymentError(error_msg)

    def _get_build_result(self, id):
        resource_id = parse_resource_id(id)
        resource_group = resource_id['resource_group']
        service = resource_id['name']
        build_service = resource_id['child_name_1']
        build = resource_id['child_name_2']
        build_result_name = resource_id['resource_name']
        response = self.client.build_service.get_build_result(resource_group, service, build_service, build, build_result_name)
        self.progress_bar.add(message=response.properties.provisioning_state)
        return response

    def _stream_build_logs(self, result):
        pod = result.properties.build_pod_name
        stages = result.properties.build_stages
        if any(x is None for x in [pod, stages]):
            return
        for stage in stages:
            self._start_build_stage_log_with_retry(result, pod, stage.name)

    def _try_print_build_logs(self, build_result_id):
        blob_url = self._try_get_build_log_url(build_result_id)
        if blob_url:
            sys.stdout.write(requests.get(blob_url).text)

    def _try_get_build_log_url(self, build_result_id):
        resource_id = parse_resource_id(build_result_id)
        resource_group = resource_id['resource_group']
        service = resource_id['name']
        build_service = resource_id['child_name_1']
        build = resource_id['child_name_2']
        build_result_name = resource_id['resource_name']
        try:
            return self.client.build_service.get_build_result_log(resource_group,
                                                                  service,
                                                                  build_service,
                                                                  build,
                                                                  build_result_name).blob_url
        except Exception:
            logger.warning("Unfortunately we are not able to display offline build logs due to unknown errors.")

    def _start_build_stage_log_with_retry(self, result, pod, stage_name):
        while True:
            try:
                return self._start_build_stage_log(result, pod, stage_name)
            except InvalidArgumentValueError as e:
                logger.debug('Failed to stream log out for stage {}: {}'.format(stage_name, str(e)))
                sleep(5)
                pass

    def _start_build_stage_log(self, result, pod, stage_name):
        if result.properties.provisioning_state not in self.terminated_state:
            # refresh the build result
            result = self._get_build_result(result.id)
        if result.properties.provisioning_state in self.terminated_state:
            logger.info('The build result is already terminated, cannot stream the log out for stage {}.'.format(stage_name))
            return
        stage = next(iter(x for x in result.properties.build_stages if x.name == stage_name), None)
        if not stage:
            logger.debug('Not found the stage {} in latest response'.format(stage_name))
            raise 'Not found the stage {} in latest response'.format(stage_name)
        self._print_build_stage_log(pod, stage)

    def _print_build_stage_log(self, pod, stage):
        if stage.status == 'NotStarted':
            logger.debug('Build stage {} not started yet.'.format(stage.name))
            raise InvalidArgumentValueError('Build stage {} not started yet.'.format(stage.name))
        log_stream = self._get_log_stream()
        url = 'https://{}/api/logstream/buildpods/{}/stages/{}?follow=true'.format(log_stream.base_url, pod, stage.name)
        with requests.get(url, stream=True, auth=HTTPBasicAuth("primary", log_stream.primary_key)) as response:
            if response.status_code == 200:
                logger.debug('start to stream log for stage {}'.format(stage.name))
                self.progress_bar and self.progress_bar.end()
                std_encoding = sys.stdout.encoding
                for content in response.iter_content():
                    if content:
                        sys.stdout.write(content.decode(encoding='utf-8', errors='replace')
                                         .encode(std_encoding, errors='replace')
                                         .decode(std_encoding, errors='replace'))
                logger.debug('End to stream log for stage {}'.format(stage.name))
            elif response.status_code == 400:
                logger.debug('Failed to stream build log with response {}'.format(response.content))
                raise InvalidArgumentValueError(response.content)
            else:
                status_code = response.status_code if response else 'Unknown'
                content = response.content if response else 'Unknown'
                logger.debug('Failed to stream build log with response {}: {}'.format(status_code, content))
                raise "Failed to get build logs with status code '{}' and reason '{}'".format(
                      status_code, content)

    def _get_log_stream(self):
        if not self.log_stream:
            self.log_stream = LogStream(self.client, self.resource_group, self.service)
        return self.log_stream
