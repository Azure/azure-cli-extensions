# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError
from ._deployment_uploadable_factory import FileUpload, FolderUpload
from azure.core.exceptions import HttpResponseError
from time import sleep
from ._stream_utils import stream_logs
from ._buildservices_factory import BuildService
from threading import Timer
from ._utils import (_get_file_ext)

logger = get_logger(__name__)


class EmptyDeployableBuilder():
    '''
    Construct the default relative path
    '''
    def __init__(self, cmd, client, resource_group, service, app, deployment, sku, **_):
        self.cmd = cmd
        self.client = client
        self.resource_group = resource_group
        self.service = service
        self.app = app
        self.deployment = deployment
        self.sku = sku

    def get_total_deploy_steps(self, **_):
        return 1

    def build_deployable_path(self, **_):
        return '<default>'

    def stream_log(self, **_):
        pass

    def get_source_type(self, runtime_version=None, artifact_path=None, **_):
        if self.sku.name == 'E0':
            return 'BuildResult'
        if runtime_version and runtime_version.lower() == 'netcore_31':
            return 'NetCoreZip'
        if _get_file_ext(artifact_path).lower() == ".war":
            return "War"
        return 'Jar'


class ContainerDeployable(EmptyDeployableBuilder):
    def get_source_type(self, **_):
        return 'Container'


class UploadDeployableBuilder(EmptyDeployableBuilder):
    '''
    Request the App's upload url, upload local file/folder to the given SaS URL and return the relative_path
    '''
    def get_total_deploy_steps(self, **_):
        return 3

    def build_deployable_path(self, **kwargs):
        logger.warning('[1/{}] Requesting for upload URL.'.format(kwargs['total_steps']))
        upload_info = self.client.apps.get_resource_upload_url(self.resource_group,
                                                               self.service,
                                                               self.app)
        if not upload_info.upload_url:
            raise InvalidArgumentValueError('Failed to get a SAS URL to upload context.')
        logger.warning('[2/{}] Uploading package to blob.'.format(kwargs['total_steps']))
        self._get_uploader(upload_url=upload_info.upload_url).upload_and_build(**kwargs)
        return upload_info.relative_path

    def _get_uploader(self, upload_url=None):
        return FileUpload(upload_url=upload_url, cli_ctx=self.cmd.cli_ctx)


class SourceBuildDeployableBuilder(UploadDeployableBuilder):
    def build_deployable_path(self, **kwargs):
        relative_path = super().build_deployable_path(**kwargs)
        if not kwargs.get('no_wait'):
            self.retrieve_log(**kwargs)
        return relative_path

    def _get_uploader(self, upload_url=None):
        return FolderUpload(upload_url=upload_url, cli_ctx=self.cmd.cli_ctx)

    def get_source_type(self, **_):
        return 'Source'

    def retrieve_log(self, client, resource_group, service, app, deployment, **_):
        def get_log_url():
            try:
                log_file_url_response = client.deployments.get_log_file_url(
                    resource_group_name=resource_group,
                    service_name=service,
                    app_name=app,
                    deployment_name=deployment)
                if not log_file_url_response:
                    return None
                return log_file_url_response.url
            except HttpResponseError:
                return None

        def get_logs_loop():
            log_url = None
            while not log_url or log_url == old_log_url:
                log_url = get_log_url()
                sleep(10)

            logger.warning("Trying to fetch build logs")
            stream_logs(client.deployments, resource_group, service,
                        app, deployment, logger_level_func=print)
        old_log_url = get_log_url()
        timer = Timer(3, get_logs_loop)
        timer.daemon = True
        timer.start()


class BuildServiceDeployableBuilder(EmptyDeployableBuilder):
    '''
    Call build service and get a successful build result
    '''
    def __init__(self, cmd, client, resource_group, service, app, deployment, sku, **_):
        super().__init__(cmd, client, resource_group, service, app, deployment, sku, **_)
        self.build_service = BuildService(cmd, client, resource_group, service)

    def get_total_deploy_steps(self, **_):
        return self.build_service.get_total_steps() + 1

    def get_source_type(self, **_):
        return 'BuildResult'

    def build_deployable_path(self, **kwargs):
        build_result = self.build_service.build_and_get_result(**kwargs)
        return build_result


def deployable_selector(**kwargs):
    if _is_custom_container(**kwargs):
        return ContainerDeployable(**kwargs)

    sku = kwargs.get('sku')
    source_path = kwargs.get('source_path')
    artifact_path = kwargs.get('artifact_path')

    if all(x is None for x in [source_path, artifact_path]):
        # Nothing will be deployed, just return the original deployable path
        return EmptyDeployableBuilder(**kwargs)

    if sku.name == 'E0':
        return BuildServiceDeployableBuilder(**kwargs)
    if source_path:
        return SourceBuildDeployableBuilder(**kwargs)
    return UploadDeployableBuilder(**kwargs)


def _is_custom_container(container_image=None,
                         **_):
    return container_image
