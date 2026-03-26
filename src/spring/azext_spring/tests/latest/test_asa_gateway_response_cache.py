# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines


"""
Mark record_only to use the recording files as the mocked server to run the tests.
"""


@record_only()
class GatewayResponseCacheTest(ScenarioTest):
    def test_response_cache(self):
        self.kwargs.update({
            'serviceName': 'jiec-e-eastasia',
            'rg': 'jiec-rg',
        })

        # Disable response cache as a initial state and set to 1 instance to accelerate test speed
        self.cmd('spring gateway update -g {rg} -s {serviceName} --enable-response-cache false --instance-count 1',
                 self.check('properties.responseCacheProperties', None))

        self.cmd('spring gateway show -g {rg} -s {serviceName}',
                 self.check('properties.responseCacheProperties', None))

        # Update with nothing changed should be succeeded.
        self.cmd('spring gateway update -g {rg} -s {serviceName}',
                 self.check('properties.responseCacheProperties', None))

        # Must need to use --enable-response-cache when response cache is not enabled
        self.cmd('spring gateway update -g {rg} -s {serviceName} --response-cache-scope Route', expect_failure=True)

        self.cmd('spring gateway update -g {rg} -s {serviceName} --enable-response-cache --response-cache-scope Route',
                 checks=[
                     self.check('properties.responseCacheProperties.responseCacheType', 'LocalCachePerRoute'),
                     self.check('properties.responseCacheProperties.size', None),
                     self.check('properties.responseCacheProperties.timeToLive', None)])

        # After response cache enabled, not necessary to add --enable-response-caches
        self.cmd('spring gateway show -g {rg} -s {serviceName}', checks=[
            self.check('properties.responseCacheProperties.responseCacheType', 'LocalCachePerRoute'),
            self.check('properties.responseCacheProperties.size', None),
            self.check('properties.responseCacheProperties.timeToLive', None)])

        # After response cache enabled, still allowed to add --enable-response-cache
        self.cmd('spring gateway update -g {rg} -s {serviceName} --enable-response-cache --response-cache-ttl 10s',
                 checks=[
                     self.check('properties.responseCacheProperties.responseCacheType', 'LocalCachePerRoute'),
                     self.check('properties.responseCacheProperties.size', None),
                     self.check('properties.responseCacheProperties.timeToLive', '10s')])

        self.cmd('spring gateway show -g {rg} -s {serviceName}', checks=[
            self.check('properties.responseCacheProperties.responseCacheType', 'LocalCachePerRoute'),
            self.check('properties.responseCacheProperties.size', None),
            self.check('properties.responseCacheProperties.timeToLive', '10s')])

        # After response cache enabled, it's allowed to configure response cache without --enable-response-cache
        self.cmd(
            'spring gateway update -g {rg} -s {serviceName} --response-cache-size 10KB --response-cache-scope Instance',
            checks=[
                self.check('properties.responseCacheProperties.responseCacheType', 'LocalCachePerInstance'),
                self.check('properties.responseCacheProperties.size', '10KB'),
                self.check('properties.responseCacheProperties.timeToLive', '10s')])

        # Update with nothing changed
        self.cmd('spring gateway show -g {rg} -s {serviceName}', checks=[
            self.check('properties.responseCacheProperties.responseCacheType', 'LocalCachePerInstance'),
            self.check('properties.responseCacheProperties.size', '10KB'),
            self.check('properties.responseCacheProperties.timeToLive', '10s')])

        self.cmd(
            'spring gateway update -g {rg} -s {serviceName} --response-cache-ttl 11m --response-cache-scope Route',
            checks=[
                self.check('properties.responseCacheProperties.responseCacheType', 'LocalCachePerRoute'),
                self.check('properties.responseCacheProperties.size', '10KB'),
                self.check('properties.responseCacheProperties.timeToLive', '11m')])

        # Update with nothing changed should be succeeded.
        self.cmd('spring gateway update -g {rg} -s {serviceName}', checks=[
            self.check('properties.responseCacheProperties.responseCacheType', 'LocalCachePerRoute'),
            self.check('properties.responseCacheProperties.size', '10KB'),
            self.check('properties.responseCacheProperties.timeToLive', '11m')])

        self.cmd('spring gateway update -g {rg} -s {serviceName} --enable-response-cache false',
                 self.check('properties.responseCacheProperties', None))

        self.cmd('spring gateway show -g {rg} -s {serviceName}',
                 self.check('properties.responseCacheProperties', None))

        self.cmd(
            'spring gateway update -g {rg} -s {serviceName} --enable-response-cache --response-cache-ttl 11m --response-cache-scope Route',
            checks=[
                self.check('properties.responseCacheProperties.responseCacheType', 'LocalCachePerRoute'),
                self.check('properties.responseCacheProperties.size', None),
                self.check('properties.responseCacheProperties.timeToLive', '11m')])

        self.cmd(
            'spring gateway update -g {rg} -s {serviceName} --response-cache-size 13MB --response-cache-ttl default --response-cache-scope Instance',
            checks=[
                self.check('properties.responseCacheProperties.responseCacheType', 'LocalCachePerInstance'),
                self.check('properties.responseCacheProperties.size', '13MB'),
                self.check('properties.responseCacheProperties.timeToLive', None)])
