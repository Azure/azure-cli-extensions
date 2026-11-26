# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import JMESPathCheck
from azure.cli.testsdk import ScenarioTest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azext_cdn.vendored_sdks.models import SkuName
from .scenario_mixin import CdnScenarioMixin


class CdnProfileScenarioTest(CdnScenarioMixin, ScenarioTest):
    def test_cdn_profile_crud(self):
        resource_group, profile_name = self.classic_cdn_profile()
        checks = [JMESPathCheck('name', profile_name),
                  JMESPathCheck('sku.name', SkuName.STANDARD_MICROSOFT),]
        profile = self.profile_show_cmd(resource_group, profile_name, checks=checks).get_output_in_json()

        list_checks = [JMESPathCheck(f"contains([].name, '{profile_name}')", True)]
        self.profile_list_cmd(resource_group, checks=list_checks)

        missing_name = self.create_random_name(prefix='missing', length=24)
        with self.assertRaises(ResourceNotFoundError):
            self.profile_show_cmd(resource_group, missing_name)
        with self.assertRaisesRegex(HttpResponseError, 'no longer support new profile creation'):
            self.profile_create_cmd(resource_group, missing_name)
            self.addCleanup(self.profile_delete_cmd, resource_group, missing_name)
        self.profile_delete_cmd(resource_group, missing_name)
        with self.assertRaises(ResourceNotFoundError):
            self.profile_show_cmd(resource_group, missing_name)

        original_tags = profile.get('tags') or {}
        self.addCleanup(self.profile_update_cmd, resource_group, profile_name, tags=original_tags)
        tags = dict(original_tags, foo='bar')
        checks.append(JMESPathCheck('tags.foo', 'bar'))
        self.profile_update_cmd(resource_group, profile_name, tags=tags, checks=checks)
