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
            'cluster': 'cluster1'
        })

        # check quote availability
        self.cmd('vmware location checkquotaavailability --location {loc}')

        # check trial availability
        self.cmd('vmware location checktrialavailability --location {loc}')

        # show should throw ResourceNotFound
        # with self.assertRaisesRegexp(CloudError, 'ResourceNotFound'):
        #     self.cmd('vmware private-cloud show -g {rg} -n {privatecloud}')

        count = len(self.cmd('vmware private-cloud list -g {rg}').get_output_in_json())
        self.assertEqual(count, 0, 'private cloud count expected to be 0')

        # create a private cloud
        self.cmd('vmware private-cloud create -g {rg} -n {privatecloud} --location {loc} --sku av20 --cluster-size 4 --network-block 192.168.48.0/22 --nsxt-password 5rqdLj4GF3cePUe6( --vcenter-password UpfBXae9ZquZSDXk( ')

        count = len(self.cmd('vmware private-cloud list -g {rg}').get_output_in_json())
        self.assertEqual(count, 1, 'private cloud count expected to be 1')

        # count at the subscription level
        # test passes, but commented out for privacy
        # count = len(self.cmd('vmware private-cloud list').get_output_in_json())
        # self.assertGreaterEqual(count, 1, 'subscription private cloud count expected to be more than 1')

        # get admin credentials
        # not currently supported in test environment
        # self.cmd('vmware private-cloud listadmincredentials -g {rg} -c {privatecloud}')

        # hcx-enterprise-site list should report 0
        count = len(self.cmd('vmware hcx-enterprise-site list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 0, 'hcx-enterprise-site count expected to be 0')

        # create authorization
        self.cmd('vmware hcx-enterprise-site create -g {rg} -c {privatecloud} -n myhcx')

        # hcx-enterprise-site list should report 1
        count = len(self.cmd('vmware hcx-enterprise-site list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'hcx-enterprise-site count expected to be 0')

        self.cmd('vmware hcx-enterprise-site show -g {rg} -c {privatecloud} -n myhcx')

        self.cmd('vmware hcx-enterprise-site delete -g {rg} -c {privatecloud} -n myhcx')

        # bug 7470537
        # hcx-enterprise-site list should report 0
        # count = len(self.cmd('vmware hcx-enterprise-site list -g {rg} -c {privatecloud}').get_output_in_json())
        # self.assertEqual(count, 0, 'hcx-enterprise-site count expected to be 0')

        # update private cloud to changed default cluster size
        self.cmd('vmware private-cloud update -g {rg} -n {privatecloud} --cluster-size 3')

        # update private cloud to enable internet
        self.cmd('vmware private-cloud update -g {rg} -n {privatecloud} --internet enabled')

        # create authorization
        self.cmd('vmware authorization create -g {rg} -c {privatecloud} -n myauthname')

        # delete authorization
        self.cmd('vmware authorization delete -g {rg} -c {privatecloud} -n myauthname')

        # add identity source
        self.cmd('vmware private-cloud addidentitysource -g {rg} -c {privatecloud} -n groupName --alias groupAlias --domain domain --base-user-dn "ou=baseUser" --base-group-dn "ou=baseGroup" --primary-server ldaps://1.1.1.1:636 --username someone --password something')

        # delete identity source
        self.cmd('vmware private-cloud deleteidentitysource -g {rg} -c {privatecloud} -n groupName --alias groupAlias --domain domain')

        # cluster list should report 0
        count = len(self.cmd('vmware cluster list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 0, 'cluster count expected to be 0')

        # cluster create
        self.cmd('vmware cluster create -g {rg} -c {privatecloud} -n {cluster} --sku av20 --size 3')

        # cluster list should report 1
        count = len(self.cmd('vmware cluster list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'cluster count expected to be 1')

        # cluster update
        self.cmd('vmware cluster update -g {rg} -c {privatecloud} -n {cluster} --size 4')

        # cluster delete
        self.cmd('vmware cluster delete -g {rg} -c {privatecloud} -n {cluster}')

        # delete the private cloud
        self.cmd('vmware private-cloud delete -g {rg} -n {privatecloud}')

        count = len(self.cmd('vmware private-cloud list -g {rg}').get_output_in_json())
        self.assertEqual(count, 0, 'private cloud count expected to be 0')
