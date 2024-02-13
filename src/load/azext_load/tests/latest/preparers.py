# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time

from azure.cli.testsdk.exceptions import CliTestError
from azure.cli.testsdk.preparers import NoTrafficRecordingPreparer
from azure.cli.testsdk.reverse_dependency import get_dummy_cli
from azure.cli.testsdk.scenario_tests import SingleValueReplacer

KEY_RESOURCE_GROUP = "rg"
KEY_LOAD_TEST_RESOURCE = "load"


class LoadTestResourcePreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(
        self,
        name_prefix="clitest-loadtest",
        parameter_name="load",
        resource_group_key=KEY_RESOURCE_GROUP,
        location="eastus",
        dev_setting_name="AZURE_CLI_TEST_DEV_LOAD_TEST_RESOURCE_NAME",
        random_name_length=20,
        subscription=None,
        key=KEY_LOAD_TEST_RESOURCE,
    ):
        if " " in name_prefix:
            raise CliTestError(
                "Error: Space character in name prefix '%s'" % name_prefix
            )
        super(LoadTestResourcePreparer, self).__init__(name_prefix, random_name_length)
        self.cli_ctx = get_dummy_cli()
        self.parameter_name = parameter_name
        self.key = key
        self.resource_group = [resource_group_key, None]
        self.dev_setting_name = os.environ.get(dev_setting_name, None)
        self.location = location
        self.subscription = subscription

    def create_resource(self, name, **_):
        if self.dev_setting_name:
            return {
                self.parameter_name: self.dev_setting_name,
            }

        if not self.resource_group[1]:
            self.resource_group[1] = self.test_class_instance.kwargs.get(
                self.resource_group[0]
            )
            if not self.resource_group[1]:
                raise CliTestError("Error: No resource group configured!")
        retries = 3
        while retries > 0:
            try:
                template = "az load create --resource-group {} --name {} --location {} "
                if self.subscription:
                    template += " --subscription {} ".format(self.subscription)
                self.live_only_execute(
                    self.cli_ctx,
                    template.format(self.resource_group[1], name, self.location),
                )

                self.test_class_instance.kwargs[self.key] = name
                return {self.parameter_name: name}
            except Exception:
                retries = retries - 1
                time.sleep(120)

    def remove_resource(self, name, **_):
        if not self.dev_setting_name:
            template = "az load delete --name {} --resource-group {} --yes --no-wait "
            if self.subscription:
                template += " --subscription {} ".format(self.subscription)
            self.live_only_execute(
                self.cli_ctx,
                template.format(name, self.resource_group[1]),
            )
