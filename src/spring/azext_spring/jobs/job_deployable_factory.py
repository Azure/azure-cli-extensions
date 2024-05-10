# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

from .._buildservices_factory import BuildService

logger = get_logger(__name__)


class EmptyDeployableBuilder():
    '''
    Construct the default relative path
    '''

    def __init__(self, cmd, client, resource_group, service, job, **_):
        self.cmd = cmd
        self.client = client
        self.resource_group = resource_group
        self.service = service
        self.job = job

    def get_total_deploy_steps(self, **_):
        return 1

    def build_deployable_path(self, **_):
        return '<default>'

    def stream_log(self, **_):
        pass

    def get_source_type(self, **_):
        return 'BuildResult'


class BuildServiceDeployableBuilder(EmptyDeployableBuilder):
    '''
    Call build service and get a successful build result
    '''

    def __init__(self, cmd, client, resource_group, service, job, **_):
        super().__init__(cmd, client, resource_group, service, job, **_)
        self.build_service = BuildService(cmd, client, resource_group, service)

    def get_total_deploy_steps(self, **_):
        return self.build_service.get_total_steps() + 1

    def get_source_type(self, **_):
        return 'BuildResult'

    def build_deployable_path(self, **kwargs):
        build_result = self.build_service.build_and_get_result(**kwargs)
        return build_result


def deployable_selector(**kwargs):
    source_path = kwargs.get('source_path')
    artifact_path = kwargs.get('artifact_path')

    if all(x is None for x in [source_path, artifact_path]):
        # Nothing will be deployed, just return the original deployable path
        return EmptyDeployableBuilder(**kwargs)

    return BuildServiceDeployableBuilder(**kwargs)
