# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import ResourceGroupPreparer, JMESPathCheck
from azure.cli.testsdk import ScenarioTest, record_only
from .afdx_scenario_mixin import CdnAfdScenarioMixin


class CdnAfdOriginGroupScenarioTest(CdnAfdScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(additional_tags={'owner': 'jingnanxu'})
    def test_afd_origin_group_disable_probe(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        self.afd_profile_create_cmd(resource_group, profile_name,
                                    options="--identity '{\"type\":\"SystemAssigned\"}'")

        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_origin_group_list_cmd(resource_group, profile_name, list_checks)

        origin_group_name = self.create_random_name(prefix='og', length=16)
        checks = [JMESPathCheck('name', origin_group_name),
                  JMESPathCheck('authentication.type', 'SystemAssignedIdentity'),
                  JMESPathCheck('authentication.scope', 'https://storage.azure.com/.default'),
                  JMESPathCheck('authentication.tokenDestinationHeader', 'X-Azure-Authorization'),
                  JMESPathCheck('loadBalancingSettings.sampleSize', 4),
                  JMESPathCheck('loadBalancingSettings.successfulSamplesRequired', 3),
                  JMESPathCheck('loadBalancingSettings.additionalLatencyInMilliseconds', 50),
                  JMESPathCheck('healthProbeSettings.probePath', "/test1/azure.txt"),
                  JMESPathCheck('healthProbeSettings.probeProtocol', "Https"),
                  JMESPathCheck('healthProbeSettings.probeIntervalInSeconds', 120),
                  JMESPathCheck('healthProbeSettings.probeRequestType', "GET"),
                  JMESPathCheck('provisioningState', 'Succeeded')]
        self.afd_origin_group_create_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         "--probe-request-type GET --probe-protocol Https --probe-interval-in-seconds 120 --probe-path /test1/azure.txt "
                                         "--sample-size 4 --successful-samples-required 3 "
                                         "--additional-latency-in-milliseconds 50 "
                                         "--authentication '{\"type\":\"SystemAssignedIdentity\",\"scope\":\"https://storage.azure.com/.default\",\"token-destination-header\":\"X-Azure-Authorization\"}'",
                                         checks=checks)

        update_checks = [JMESPathCheck('name', origin_group_name),
                         JMESPathCheck('authentication.type', 'SystemAssignedIdentity'),
                         JMESPathCheck('authentication.scope', 'https://storage.azure.com/.default'),
                         JMESPathCheck('authentication.tokenDestinationHeader', 'Authorization'),
                         JMESPathCheck('loadBalancingSettings.sampleSize', 4),
                         JMESPathCheck('loadBalancingSettings.successfulSamplesRequired', 3),
                         JMESPathCheck('loadBalancingSettings.additionalLatencyInMilliseconds', 50),
                         JMESPathCheck('healthProbeSettings.probePath', "/test1/azure.txt"),
                         JMESPathCheck('healthProbeSettings.probeProtocol', "Https"),
                         JMESPathCheck('healthProbeSettings.probeIntervalInSeconds', 120),
                         JMESPathCheck('healthProbeSettings.probeRequestType', "GET"),
                         JMESPathCheck('provisioningState', 'Succeeded')]
        options = "--probe-request-type GET --probe-protocol Https " \
                        "--authentication '{\"type\":\"SystemAssignedIdentity\",\"scope\":\"https://storage.azure.com/.default\",\"token-destination-header\":\"Authorization\"}'"
        self.afd_origin_group_update_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         options=options,
                                         checks=update_checks)

        update_checks = [JMESPathCheck('name', origin_group_name),
                         JMESPathCheck('loadBalancingSettings.sampleSize', 4),
                         JMESPathCheck('loadBalancingSettings.successfulSamplesRequired', 3),
                         JMESPathCheck('loadBalancingSettings.additionalLatencyInMilliseconds', 50),
                         JMESPathCheck('healthProbeSettings.probePath', None),
                         JMESPathCheck('healthProbeSettings.probeProtocol', None),
                         JMESPathCheck('healthProbeSettings.probeIntervalInSeconds', None),
                         JMESPathCheck('healthProbeSettings.probeRequestType', None),
                         JMESPathCheck('provisioningState', 'Succeeded')]
        options = '--health-probe-settings null'
        self.afd_origin_group_update_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         options=options,
                                         checks=update_checks)

        update_checks = [JMESPathCheck('name', origin_group_name),
                         JMESPathCheck('healthProbeSettings.probePath', "/test1/azure.txt"),
                         JMESPathCheck('healthProbeSettings.probeProtocol', "Https"),
                         JMESPathCheck('healthProbeSettings.probeIntervalInSeconds', 120),
                         JMESPathCheck('healthProbeSettings.probeRequestType', "GET"),
                         JMESPathCheck('provisioningState', 'Succeeded')]
        options = "--probe-request-type GET --probe-protocol Https --probe-interval-in-seconds 120 --probe-path /test1/azure.txt"
        self.afd_origin_group_update_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         options=options,
                                         checks=update_checks)

    @ResourceGroupPreparer(additional_tags={'owner': 'jingnanxu'})
    def test_afd_origin_group_crud(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        self.afd_profile_create_cmd(resource_group, profile_name)

        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_origin_group_list_cmd(resource_group, profile_name, list_checks)

        origin_group_name = self.create_random_name(prefix='og', length=16)
        checks = [JMESPathCheck('name', origin_group_name),
                  JMESPathCheck('loadBalancingSettings.capacityDistributionSettings.distributionType',
                                'DynamicWeights'),
                  JMESPathCheck('loadBalancingSettings.capacityDistributionSettings.capacityConsciousThreshold', 80),
                  JMESPathCheck('loadBalancingSettings.sampleSize', 4),
                  JMESPathCheck('loadBalancingSettings.successfulSamplesRequired', 3),
                  JMESPathCheck('loadBalancingSettings.additionalLatencyInMilliseconds', 50),
                  JMESPathCheck('healthProbeSettings.probePath', "/test1/azure.txt"),
                  JMESPathCheck('healthProbeSettings.probeProtocol', "Http"),
                  JMESPathCheck('healthProbeSettings.probeIntervalInSeconds', 120),
                  JMESPathCheck('healthProbeSettings.probeRequestType', "GET"),
                  JMESPathCheck('provisioningState', 'Succeeded')]
        self.afd_origin_group_create_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         "--probe-request-type GET --probe-protocol Http --probe-interval-in-seconds 120 --probe-path /test1/azure.txt "
                                         "--sample-size 4 --successful-samples-required 3 "
                                         "--additional-latency-in-milliseconds 50 "
                                         "--capacity-settings "
                                         "'{\"distribution-type\":\"DynamicWeights\",\"capacity-conscious-threshold\":80}'",
                                         checks=checks)
        self.afd_origin_group_show_cmd(resource_group, profile_name, origin_group_name, checks=checks)
        list_checks = [JMESPathCheck('length(@)', 1),
                       JMESPathCheck('@[0].loadBalancingSettings.capacityDistributionSettings.distributionType',
                                     'DynamicWeights'),
                       JMESPathCheck('@[0].loadBalancingSettings.capacityDistributionSettings.capacityConsciousThreshold',
                                     80),
                       JMESPathCheck('@[0].name', origin_group_name)]
        self.afd_origin_group_list_cmd(resource_group, profile_name, checks=list_checks)

        update_checks = [JMESPathCheck('name', origin_group_name),
                         JMESPathCheck('loadBalancingSettings.sampleSize', 4),
                         JMESPathCheck('loadBalancingSettings.successfulSamplesRequired', 3),
                         JMESPathCheck('loadBalancingSettings.additionalLatencyInMilliseconds', 50),
                         JMESPathCheck('healthProbeSettings.probePath', "/test1/azure.txt"),
                         JMESPathCheck('healthProbeSettings.probeProtocol', "Https"),
                         JMESPathCheck('healthProbeSettings.probeIntervalInSeconds', 120),
                         JMESPathCheck('healthProbeSettings.probeRequestType', "GET"),
                         JMESPathCheck('provisioningState', 'Succeeded')]
        options = "--probe-request-type GET --probe-protocol Https"
        self.afd_origin_group_update_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         options=options,
                                         checks=update_checks)

        update_checks = [JMESPathCheck('name', origin_group_name),
                         JMESPathCheck('loadBalancingSettings.sampleSize', 5),
                         JMESPathCheck('loadBalancingSettings.successfulSamplesRequired', 3),
                         JMESPathCheck('loadBalancingSettings.additionalLatencyInMilliseconds', 30),
                         JMESPathCheck('healthProbeSettings.probePath', "/test1/azure.txt"),
                         JMESPathCheck('healthProbeSettings.probeProtocol', "Https"),
                         JMESPathCheck('healthProbeSettings.probeIntervalInSeconds', 120),
                         JMESPathCheck('healthProbeSettings.probeRequestType', "GET"),
                         JMESPathCheck('provisioningState', 'Succeeded')]
        options = '--sample-size 5 --additional-latency-in-milliseconds 30'
        self.afd_origin_group_update_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         options=options,
                                         checks=update_checks)

        update_checks = [JMESPathCheck('name', origin_group_name),
                         JMESPathCheck('loadBalancingSettings.sampleSize', 4),
                         JMESPathCheck('loadBalancingSettings.successfulSamplesRequired', 3),
                         JMESPathCheck('loadBalancingSettings.additionalLatencyInMilliseconds', 30),
                         JMESPathCheck('healthProbeSettings.probePath', "/test1/azure.txt"),
                         JMESPathCheck('healthProbeSettings.probeProtocol', "Https"),
                         JMESPathCheck('healthProbeSettings.probeIntervalInSeconds', 120),
                         JMESPathCheck('healthProbeSettings.probeRequestType', "HEAD"),
                         JMESPathCheck('provisioningState', 'Succeeded')]
        options = "--sample-size 4 --additional-latency-in-milliseconds 30 --probe-request-type HEAD"
        self.afd_origin_group_update_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         options=options,
                                         checks=update_checks)

        distribution_checks = [
            JMESPathCheck('loadBalancingSettings.sampleSize', 4),
            JMESPathCheck('loadBalancingSettings.successfulSamplesRequired', 3),
            JMESPathCheck('loadBalancingSettings.additionalLatencyInMilliseconds', 30),
            JMESPathCheck('loadBalancingSettings.capacityDistributionSettings.distributionType', 'DynamicWeights'),
            JMESPathCheck('loadBalancingSettings.capacityDistributionSettings.capacityConsciousThreshold', 80),
            JMESPathCheck('healthProbeSettings.probeProtocol', 'Https'),
            JMESPathCheck('healthProbeSettings.probeRequestType', 'HEAD'),
        ]
        self.afd_origin_group_show_cmd(resource_group, profile_name, origin_group_name,
                                       checks=distribution_checks)
        distribution_checks = [
            JMESPathCheck('loadBalancingSettings.sampleSize', 4),
            JMESPathCheck('loadBalancingSettings.successfulSamplesRequired', 3),
            JMESPathCheck('loadBalancingSettings.additionalLatencyInMilliseconds', 30),
            JMESPathCheck('loadBalancingSettings.capacityDistributionSettings.distributionType', 'StaticWeights'),
            JMESPathCheck('loadBalancingSettings.capacityDistributionSettings.capacityConsciousThreshold', 100),
            JMESPathCheck('healthProbeSettings.probeProtocol', 'Https'),
            JMESPathCheck('healthProbeSettings.probeRequestType', 'HEAD'),
            JMESPathCheck('provisioningState', 'Succeeded'),
        ]
        self.afd_origin_group_update_cmd(
            resource_group, profile_name, origin_group_name,
            options='--capacity-distribution-settings '
                    '\'{"distribution-type":"StaticWeights","capacity-conscious-threshold":100}\'',
            checks=distribution_checks)
        self.afd_origin_group_show_cmd(resource_group, profile_name, origin_group_name,
                                       checks=distribution_checks)

        # This group has no origins: validate persistence without probing an HTTP-only backend.
        grpc_checks = [
            JMESPathCheck('healthProbeSettings.probeProtocol', 'Grpc'),
            JMESPathCheck('healthProbeSettings.probePath', '/'),
            JMESPathCheck('healthProbeSettings.probeIntervalInSeconds', 120),
            JMESPathCheck('loadBalancingSettings.sampleSize', 4),
            JMESPathCheck('loadBalancingSettings.successfulSamplesRequired', 3),
            JMESPathCheck('loadBalancingSettings.capacityDistributionSettings.distributionType', 'StaticWeights'),
            JMESPathCheck('loadBalancingSettings.capacityDistributionSettings.capacityConsciousThreshold', 100),
            JMESPathCheck('provisioningState', 'Succeeded'),
        ]
        self.afd_origin_group_update_cmd(
            resource_group, profile_name, origin_group_name,
            options='--probe-protocol Grpc --probe-path / --probe-request-type GET',
            checks=grpc_checks)
        self.afd_origin_group_show_cmd(resource_group, profile_name, origin_group_name, checks=grpc_checks)
        self.afd_origin_group_list_cmd(resource_group, profile_name, checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].healthProbeSettings.probeProtocol', 'Grpc'),
            JMESPathCheck('[0].loadBalancingSettings.capacityDistributionSettings.distributionType', 'StaticWeights'),
            JMESPathCheck('[0].loadBalancingSettings.capacityDistributionSettings.capacityConsciousThreshold', 100),
        ])

        self.afd_origin_group_delete_cmd(resource_group, profile_name, origin_group_name)

        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_origin_group_list_cmd(resource_group, profile_name, list_checks)
