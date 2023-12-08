# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, record_only)
from azure.cli.core.azclierror import ResourceNotFoundError


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
            'hosts': 'fakehost22.nyc1.kubernetes.center fakehost23.nyc1.kubernetes.center fakehost24.nyc1.kubernetes.center',
            'key_vault_key': 'vmwarekey',
            'vault_url': 'https://keyvault1-kmip-kvault.vault.azure.net/'
        })

        # check quote availability
        self.cmd('vmware location check-quota-availability --location {loc}')

        # check trial availability
        self.cmd('vmware location check-trial-availability --location {loc} --sku sku')

        count = len(self.cmd('vmware private-cloud list -g {rg}').get_output_in_json())
        self.assertEqual(count, 1, 'private cloud count expected to be 1')

        # create a private cloud
        self.cmd(
            'vmware private-cloud create -g {rg} -n {privatecloud} --location {loc} --sku av20 --cluster-size 3 --network-block 192.168.48.0/22 --nsxt-password 5rqdLj4GF3cePUe6( --vcenter-password UpfBXae9ZquZSDXk( --accept-eula')

        count = len(self.cmd('vmware private-cloud list -g {rg}').get_output_in_json())
        self.assertEqual(count, 1, 'private cloud count expected to be 1')

        # count at the subscription level
        count = len(self.cmd('vmware private-cloud list').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'subscription private cloud count expected to be more than 1')

        # get admin credentials
        creds = self.cmd('vmware private-cloud list-admin-credentials -g {rg} -c {privatecloud}').get_output_in_json()
        self.assertEqual("nsxtPassword" in creds, True)
        self.assertEqual("vcenterPassword" in creds, True)

        # rotate passwords
        self.cmd('vmware private-cloud rotate-vcenter-password -g {rg} -c {privatecloud} --yes')
        # self.cmd('vmware private-cloud rotate-nsxt-password')

        # update private cloud to changed default cluster size
        self.cmd('vmware private-cloud update -g {rg} -n {privatecloud} --cluster-size 4')

        # update private cloud to enable internet
        self.cmd('vmware private-cloud update -g {rg} -n {privatecloud} --internet Enabled')

        # create authorization
        self.cmd('vmware authorization create -g {rg} -c {privatecloud} -n myauthname --express-route-id id')

        # delete authorization
        self.cmd('vmware authorization delete -g {rg} -c {privatecloud} -n myauthname --yes')

        # add identity source
        self.cmd(
            'vmware private-cloud add-identity-source -g {rg} -c {privatecloud} -n group1 --alias groupAlias --domain domain1 --base-user-dn "ou=baseUser" --base-group-dn "ou=baseGroup" --primary-server ldaps://1.1.1.1:636 --username someone --password something')

        # delete identity source
        self.cmd(
            'vmware private-cloud delete-identity-source -g {rg} -c {privatecloud} -n group1 --alias groupAlias --domain domain1 --yes')

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

        # create extended network blocks
        self.cmd('vmware private-cloud update -g {rg} -n {privatecloud} --ext-nw-blocks 10.0.8.0/23 10.1.8.0/23 10.2.8.0/23')

        # delete all extended network blocks
        self.cmd('vmware private-cloud update -g {rg} -n {privatecloud} --ext-nw-blocks null')

        # set managed identity
        self.cmd('vmware private-cloud identity assign -g {rg} -c {privatecloud} --system-assigned')

        # enable cmk encryption
        self.cmd('vmware private-cloud enable-cmk-encryption -c {privatecloud} -g {rg} --enc-kv-key-name {key_vault_key} --enc-kv-url {vault_url}')

        # disable cmk encyrption
        self.cmd('vmware private-cloud disable-cmk-encryption -c {privatecloud} -g {rg} --yes')

        # remove managed identity
        self.cmd('vmware private-cloud identity remove -g {rg} -c {privatecloud}')

        # delete the private cloud
        self.cmd('vmware private-cloud delete -g {rg} -n {privatecloud} --yes')

        # cluster delete
        self.cmd('vmware cluster delete -g {rg} -c {privatecloud} -n {cluster} --yes')

        # cluster list zone
        self.cmd('vmware cluster list-zones -g {rg} -c {privatecloud} -n {cluster}')

        # delete the private cloud
        self.cmd('vmware private-cloud delete -g {rg} -n {privatecloud} --yes')
