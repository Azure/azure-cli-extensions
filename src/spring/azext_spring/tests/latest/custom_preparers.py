# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
from datetime import datetime
from azure.cli.testsdk.preparers import (
    NoTrafficRecordingPreparer,
    ResourceGroupPreparer,
)
from azure.cli.testsdk.scenario_tests import (
    SingleValueReplacer,
)
from azure.cli.testsdk.exceptions import (
    CliTestError,
)
from azure.cli.testsdk.reverse_dependency import (
    get_dummy_cli,
)
from .custom_recording_processor import RegexSingleValueReplacer
from knack.log import get_logger

logger = get_logger(__name__)


class SpringSubResourceWrapper(NoTrafficRecordingPreparer):
    def __init__(self, *args, **kwargs):
        if not args:
            args = ['fake', 10]
        super(SpringSubResourceWrapper, self).__init__(*args, **kwargs)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a Spring a resource group is required. Please add ' \
                       'decorator @{} in front of this Spring preparer.'
            raise CliTestError(template.format(SpringResourceGroupPreparer.__name__))

    def _get_spring(self, **kwargs):
        try:
            return kwargs.get(self.spring_parameter_name)
        except KeyError:
            template = 'To get a Spring app, a Spring resource is required. Please add ' \
                       'decorator @{} in front of this Spring preparer.'
            raise CliTestError(template.format(SpringPreparer.__name__))

    def _safe_exec(self, cmd):
        try:
            self.live_only_execute(self.cli_ctx, cmd, expect_failure=True)
        except Exception:
            pass


class SpringSingleValueReplacer(RegexSingleValueReplacer):
    def __init__(self, dev_setting_name, moniker):
        super(SpringSingleValueReplacer, self).__init__(re.compile(f'(?<![a-zA-Z0-9-]){dev_setting_name}(?![a-zA-Z0-9-])', re.IGNORECASE),
                                                        anchor=dev_setting_name, moniker=moniker)


class SpringResourceGroupPreparer(ResourceGroupPreparer):
    def __init__(self, location='uksouth', **kwargs):
        super(SpringResourceGroupPreparer, self).__init__(location=location, **kwargs)

    def create_resource(self, name, **kwargs):
        response = super().create_resource(name, **kwargs)
        is_live = self.live_test or self.test_class_instance.in_recording
        if self.dev_setting_name and is_live:
            self.test_class_instance.recording_processors.append(SpringSingleValueReplacer(self.dev_setting_name, self.moniker))
            return response
        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name, self.parameter_name_for_location: self.location}


class SpringPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    """
    Prepare a Spring instance before testing and distroy it when finishing.
    It runs `az spring create -n {} -g {} {addtional_params}` to create the instance
    """
    def __init__(self, name_prefix='clitest',
                 parameter_name='spring',
                 dev_setting_name='AZURE_CLI_TEST_DEV_SPRING_NAME',
                 resource_group_parameter_name='resource_group',
                 location='uksouth',
                 random_name_length=15, key='asa', additional_params=None):
        if ' ' in name_prefix:
            raise CliTestError('Error: Space character in Spring name prefix \'%s\'' % name_prefix)
        super(SpringPreparer, self).__init__(name_prefix, random_name_length)
        self.cli_ctx = get_dummy_cli()
        self.parameter_name = parameter_name
        self.key = key
        self.additional_params = additional_params
        self.location = location
        self.resource_group_parameter_name = resource_group_parameter_name

        self.dev_setting_name = os.environ.get(dev_setting_name, None)

    def create_resource(self, name, **kwargs):
        is_live = self.live_test or self.test_class_instance.in_recording
        if self.dev_setting_name and is_live:
            self.test_class_instance.kwargs[self.key] = self.dev_setting_name
            self.test_class_instance.recording_processors.append(SpringSingleValueReplacer(self.dev_setting_name, self.moniker))
            return {self.parameter_name: self.dev_setting_name}
        group = self._get_resource_group(**kwargs)
        template = 'az spring create -n {} -g {} -l {} {}'.format(name, group, self.location, self.additional_params)
        self.live_only_execute(self.cli_ctx, template)
        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        if not self.dev_setting_name:
            group = self._get_resource_group(**kwargs)
            template = 'az spring delete -n {} -g {}'.format(name, group)
            self.live_only_execute(self.cli_ctx, template)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a Spring a resource group is required. Please add ' \
                       'decorator @{} in front of this Spring preparer.'
            raise CliTestError(template.format(SpringResourceGroupPreparer.__name__))


class SpringAppNamePreparer(SpringSubResourceWrapper, SingleValueReplacer):
    """
    Prepare a Spring instance before testing and distroy it when finishing.
    It runs `az spring create -n {} -g {} {addtional_params}` to create the instance
    """
    def __init__(self, name_prefix='clitest',
                 parameter_name='app',
                 dev_setting_name='AZURE_CLI_TEST_DEV_APP_NAME',
                 resource_group_parameter_name='resource_group',
                 spring_parameter_name='spring',
                 skip_delete=False,
                 random_name_length=15, key='spring_app'):
        if ' ' in name_prefix:
            raise CliTestError('Error: Space character in Spring App name prefix \'%s\'' % name_prefix)
        super(SpringAppNamePreparer, self).__init__(name_prefix, random_name_length)
        self.cli_ctx = get_dummy_cli()
        self.parameter_name = parameter_name
        self.resource_group_parameter_name = resource_group_parameter_name
        self.spring_parameter_name = spring_parameter_name
        self.key = key
        self.skip_delete = skip_delete

        self.dev_setting_name = os.environ.get(dev_setting_name, None)

    def create_resource(self, name, **kwargs):
        is_live = self.live_test or self.test_class_instance.in_recording
        if self.dev_setting_name and is_live:
            self.test_class_instance.kwargs[self.key] = self.dev_setting_name
            self.test_class_instance.recording_processors.append(SpringSingleValueReplacer(self.dev_setting_name, self.moniker))
            return {self.parameter_name: self.dev_setting_name}
        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        if self.dev_setting_name or self.skip_delete:
            return
        group = self._get_resource_group(**kwargs)
        spring = self._get_spring(**kwargs)
        try:
            self.live_only_execute(self.cli_ctx, 'spring app delete -n {} -g {} -s {}'.format(name, group, spring))
        except:
            pass