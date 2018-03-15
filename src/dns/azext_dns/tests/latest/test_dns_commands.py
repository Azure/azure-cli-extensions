# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
import os
import unittest

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DnsScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_dns')
    def test_dns(self, resource_group):  # pylint: disable=unused-argument

        self.kwargs['zone'] = 'myzone.com'

        self.cmd('network dns zone list')  # just verify is works (no Exception raised)
        self.cmd('network dns zone create -n {zone} -g {rg}')
        self.cmd('network dns zone list -g {rg}',
                 checks=self.check('length(@)', 1))

        base_record_sets = 2
        self.cmd('network dns zone show -n {zone} -g {rg}',
                 checks=self.check('numberOfRecordSets', base_record_sets))

        args = {
            'a': '--ipv4-address 10.0.0.10',
            'aaaa': '--ipv6-address 2001:db8:0:1:1:1:1:1',
            'caa': '--flags 0 --tag foo --value "my value"',
            'cname': '--cname mycname',
            'mx': '--exchange 12 --preference 13',
            'ns': '--nsdname foobar.com',
            'ptr': '--ptrdname foobar.com',
            'soa': '--email foo.com --expire-time 30 --minimum-ttl 20 --refresh-time 60 --retry-time 90 --serial-number 123',
            'srv': '--port 1234 --priority 1 --target target.com --weight 50',
            'txt': '--value some_text'
        }

        record_types = ['a', 'aaaa', 'caa', 'cname', 'mx', 'ns', 'ptr', 'srv', 'txt']

        for t in record_types:
            # test creating the record set and then adding records
            self.cmd('network dns record-set {0} create -n myrs{0} -g {{rg}} --zone-name {{zone}}'.format(t))
            add_command = 'set-record' if t == 'cname' else 'add-record'
            self.cmd('network dns record-set {0} {2} -g {{rg}} --zone-name {{zone}} --record-set-name myrs{0} {1}'.format(t, args[t], add_command))
            # test creating the record set at the same time you add records
            self.cmd('network dns record-set {0} {2} -g {{rg}} --zone-name {{zone}} --record-set-name myrs{0}alt {1}'.format(t, args[t], add_command))

        self.cmd('network dns record-set a add-record -g {rg} --zone-name {zone} --record-set-name myrsa --ipv4-address 10.0.0.11')
        self.cmd('network dns record-set soa update -g {{rg}} --zone-name {{zone}} {0}'.format(args['soa']))

        long_value = '0123456789' * 50
        self.cmd('network dns record-set txt add-record -g {{rg}} -z {{zone}} -n longtxt -v {0}'.format(long_value))

        typed_record_sets = 2 * len(record_types) + 1
        self.cmd('network dns zone show -n {zone} -g {rg}',
                 checks=self.check('numberOfRecordSets', base_record_sets + typed_record_sets))
        self.cmd('network dns record-set a show -n myrsa -g {rg} --zone-name {zone}',
                 checks=self.check('length(arecords)', 2))

        # test list vs. list type
        self.cmd('network dns record-set list -g {rg} -z {zone}',
                 checks=self.check('length(@)', base_record_sets + typed_record_sets))

        self.cmd('network dns record-set txt list -g {rg} -z {zone}',
                 checks=self.check('length(@)', 3))

        for t in record_types:
            self.cmd('network dns record-set {0} remove-record -g {{rg}} --zone-name {{zone}} --record-set-name myrs{0} {1}'.format(t, args[t]))

        self.cmd('network dns record-set a show -n myrsa -g {rg} --zone-name {zone}',
                 checks=self.check('length(arecords)', 1))

        self.cmd('network dns record-set a remove-record -g {rg} --zone-name {zone} --record-set-name myrsa --ipv4-address 10.0.0.11')

        self.cmd('network dns record-set a show -n myrsa -g {rg} --zone-name {zone}',
                 checks=self.is_empty())

        self.cmd('network dns record-set a delete -n myrsa -g {rg} --zone-name {zone} -y')
        self.cmd('network dns record-set a show -n myrsa -g {rg} --zone-name {zone}')

        self.cmd('network dns zone delete -g {rg} -n {zone} -y',
                 checks=self.is_empty())

    @ResourceGroupPreparer(name_prefix='cli_test_dns')
    def test_private_dns(self, resource_group):  # pylint: disable=unused-argument

        self.kwargs['zone'] = 'myprivatezone.com'
        self.kwargs['regvnet'] = 'regvnet'
        self.kwargs['resvnet'] = 'resvnet'

        self.cmd('network vnet create -n {regvnet} -g {rg}')
        self.cmd('network vnet create -n {resvnet} -g {rg}')

        self.cmd('network dns zone list')  # just verify is works (no Exception raised)
        self.cmd('network dns zone create -n {zone} -g {rg} --zone-type Private --registration-vnets {regvnet} --resolution-vnets {resvnet}')
        self.cmd('network dns zone list -g {rg}',
                 checks=self.check('length(@)', 1))

        self.cmd('network dns zone update -n {zone} -g {rg} --zone-type Private --registration-vnets "" --resolution-vnets ""')
        self.cmd('network dns zone update -n {zone} -g {rg} --zone-type Private --registration-vnets {regvnet} --resolution-vnets {resvnet}')

        base_record_sets = 1
        self.cmd('network dns zone show -n {zone} -g {rg}',
                 checks=self.check('numberOfRecordSets', base_record_sets))

        args = {
            'a': '--ipv4-address 10.0.0.10',
            'aaaa': '--ipv6-address 2001:db8:0:1:1:1:1:1',
            'caa': '--flags 0 --tag foo --value "my value"',
            'cname': '--cname mycname',
            'mx': '--exchange 12 --preference 13',
            'ptr': '--ptrdname foobar.com',
            'soa': '--email foo.com --expire-time 30 --minimum-ttl 20 --refresh-time 60 --retry-time 90 --serial-number 123',
            'srv': '--port 1234 --priority 1 --target target.com --weight 50',
            'txt': '--value some_text'
        }

        # Private Zones do NOT support delegation through NS records
        record_types = ['a', 'aaaa', 'caa', 'cname', 'mx', 'ptr', 'srv', 'txt']

        for t in record_types:
            # test creating the record set and then adding records
            self.cmd('network dns record-set {0} create -n myrs{0} -g {{rg}} --zone-name {{zone}}'.format(t))
            add_command = 'set-record' if t == 'cname' else 'add-record'
            self.cmd('network dns record-set {0} {2} -g {{rg}} --zone-name {{zone}} --record-set-name myrs{0} {1}'.format(t, args[t], add_command))
            # test creating the record set at the same time you add records
            self.cmd('network dns record-set {0} {2} -g {{rg}} --zone-name {{zone}} --record-set-name myrs{0}alt {1}'.format(t, args[t], add_command))

        self.cmd('network dns record-set a add-record -g {rg} --zone-name {zone} --record-set-name myrsa --ipv4-address 10.0.0.11')
        self.cmd('network dns record-set soa update -g {{rg}} --zone-name {{zone}} {0}'.format(args['soa']))

        long_value = '0123456789' * 50
        self.cmd('network dns record-set txt add-record -g {{rg}} -z {{zone}} -n longtxt -v {0}'.format(long_value))

        typed_record_sets = 2 * len(record_types) + 1
        self.cmd('network dns zone show -n {zone} -g {rg}',
                 checks=self.check('numberOfRecordSets', base_record_sets + typed_record_sets))
        self.cmd('network dns record-set a show -n myrsa -g {rg} --zone-name {zone}',
                 checks=self.check('length(arecords)', 2))

        # test list vs. list type
        self.cmd('network dns record-set list -g {rg} -z {zone}',
                 checks=self.check('length(@)', base_record_sets + typed_record_sets))

        self.cmd('network dns record-set txt list -g {rg} -z {zone}',
                 checks=self.check('length(@)', 3))

        for t in record_types:
            self.cmd('network dns record-set {0} remove-record -g {{rg}} --zone-name {{zone}} --record-set-name myrs{0} {1}'.format(t, args[t]))

        self.cmd('network dns record-set a show -n myrsa -g {rg} --zone-name {zone}',
                 checks=self.check('length(arecords)', 1))

        self.cmd('network dns record-set a remove-record -g {rg} --zone-name {zone} --record-set-name myrsa --ipv4-address 10.0.0.11')

        self.cmd('network dns record-set a show -n myrsa -g {rg} --zone-name {zone}',
                 checks=self.is_empty())

        self.cmd('network dns record-set a delete -n myrsa -g {rg} --zone-name {zone} -y')
        self.cmd('network dns record-set a show -n myrsa -g {rg} --zone-name {zone}')

        self.cmd('network dns zone delete -g {rg} -n {zone} -y',
                 checks=self.is_empty())


if __name__ == '__main__':
    unittest.main()
