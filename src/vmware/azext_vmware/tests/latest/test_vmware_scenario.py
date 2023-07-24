# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from msrestazure.azure_exceptions import CloudError


class VmwareScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware')
    def test_vmware(self):
        self.kwargs.update({
            'loc': 'centralus',
            'privatecloud': 'cloud1',
            'cluster': 'pycluster1',
            'hosts': 'fakehost22.nyc1.kubernetes.center fakehost23.nyc1.kubernetes.center fakehost24.nyc1.kubernetes.center'
        })

        # check quote availability
        self.cmd('vmware location check-quota-availability --location {loc}')

        # check trial availability
        self.cmd('vmware location check-trial-availability --location {loc} --sku sku')

        # show should throw ResourceNotFound
        # with self.assertRaisesRegexp(CloudError, 'ResourceNotFound'):
        #     self.cmd('vmware private-cloud show -g {rg} -n {privatecloud}')

        count = len(self.cmd('vmware private-cloud list -g {rg}').get_output_in_json())
        self.assertEqual(count, 1, 'private cloud count expected to be 1')

        # create a private cloud
        self.cmd('vmware private-cloud create -g {rg} -n {privatecloud} --location {loc} --sku av20 --cluster-size 3 --network-block 192.168.48.0/22 --nsxt-password 5rqdLj4GF3cePUe6( --vcenter-password UpfBXae9ZquZSDXk( --accept-eula')

        count = len(self.cmd('vmware private-cloud list -g {rg}').get_output_in_json())
        self.assertEqual(count, 1, 'private cloud count expected to be 1')

        # count at the subscription level
        # test passes, but commented out for privacy
        # count = len(self.cmd('vmware private-cloud list').get_output_in_json())
        # self.assertGreaterEqual(count, 1, 'subscription private cloud count expected to be more than 1')

        # get admin credentials
        # not currently supported in test environment
        # self.cmd('vmware private-cloud listadmincredentials -g {rg} -c {privatecloud}')

        # rotate passwords
        # self.cmd('vmware private-cloud rotate-vcenter-password -g {rg} -c {privatecloud}')
        # self.cmd('vmware private-cloud rotate-nsxt-password -g {rg} -c {privatecloud}')

        # update private cloud to changed default cluster size
        self.cmd('vmware private-cloud update -g {rg} -n {privatecloud} --cluster-size 4')

        # update private cloud to enable internet
        self.cmd('vmware private-cloud update -g {rg} -n {privatecloud} --internet Enabled')

        # create authorization
        self.cmd('vmware authorization create -g {rg} -c {privatecloud} -n myauthname --express-route-id id')

        # delete authorization
        self.cmd('vmware authorization delete -g {rg} -c {privatecloud} -n myauthname --yes')

        # add identity source
        self.cmd('vmware private-cloud add-identity-source -g {rg} -c {privatecloud} -n groupName --alias groupAlias --domain domain --base-user-dn "ou=baseUser" --base-group-dn "ou=baseGroup" --primary-server ldaps://1.1.1.1:636 --username someone --password something')

        # delete identity source
        self.cmd('vmware private-cloud delete-identity-source -g {rg} -c {privatecloud} -n groupName --alias groupAlias --domain domain --yes')

        # cluster list should report 0
        count = len(self.cmd('vmware cluster list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'cluster count expected to be 1')

        # cluster create
        self.cmd('vmware cluster create -g {rg} -c {privatecloud} -n {cluster} --sku av20 --size 3 --hosts {hosts}')

        # cluster create without --hosts
        self.cmd('vmware cluster create -g {rg} -c {privatecloud} -n {cluster} --sku av20 --size 3')

        # cluster list should report 1
        count = len(self.cmd('vmware cluster list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'cluster count expected to be 1')

        # cluster update
        self.cmd('vmware cluster update -g {rg} -c {privatecloud} -n {cluster} --size 4')

        # cluster delete
        self.cmd('vmware cluster delete -g {rg} -c {privatecloud} -n {cluster} --yes')

        # cluster list zone
        self.cmd('vmware cluster list-zones -g {rg} -c {privatecloud} -n {cluster}')

        # delete the private cloud
        self.cmd('vmware private-cloud delete -g {rg} -n {privatecloud} --yes')

        # enable cmk encryption
        self.cmd('az vmware private-cloud enable-cmk-encryption -c {privatecloud} -g {rg} --enc-kv-key-name test-key-name --enc-kv-key-version 1 --enc-kv-url test-url')

        # disable cmk encyrption
        self.cmd('az vmware private-cloud disable-cmk-encryption -c {privatecloud} -g {rg} --yes')

        # set managed identity
        self.cmd('vmware private-cloud identity assign -g {rg} -c {privatecloud} --system-assigned')

        # remove managed identity
        self.cmd('vmware private-cloud identity remove -g {rg} -c {privatecloud}')

        # show managed identity
        self.cmd('vmware private-cloud identity show -g {rg} -c {privatecloud}')

        count = len(self.cmd('vmware private-cloud list -g {rg}').get_output_in_json())
        self.assertEqual(count, 1, 'private cloud count expected to be 1')
