# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class Cosmosdb_throughputBucketingTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_sql_thoughput_bucketing', location='australiaeast')
    def test_cosmosdb_sql_throughput_bucketing(self, resource_group):
        col = self.create_random_name(prefix='cli', length=15)
        db_name = self.create_random_name(prefix='cli', length=15)
        throughput_buckets = '"[{\\"id\\": 1, \\"maxThroughputPercentage\\": 10 }, {\\"id\\": 2, \\"maxThroughputPercentage\\": 20 }]"'
        updated_throughput_buckets = '"[{\\"id\\": 1, \\"maxThroughputPercentage\\": 15 }, {\\"id\\": 2, \\"maxThroughputPercentage\\": 25, \\"isDefaultBucket\\": true }]"'
        empty_throughput_buckets = '"[]"'

        # This test needs to be run on the following account since it has the feature flag enabled
        self.kwargs.update({
            'rg': 'throughput-bucketing-rg',
            'acc': 'throughput-bucketing-rp-test',
            'db_name': db_name,
            'col': col,
            'throughput_buckets': throughput_buckets,
            'updated_throughput_buckets': updated_throughput_buckets,
            'empty_throughput_buckets': empty_throughput_buckets
        })

        # Create database
        self.cmd('az cosmosdb sql database create -g {rg} -a {acc} -n {db_name}')

        #Create container
        self.cmd('az cosmosdb sql container create -g {rg} -a {acc} -d {db_name} -n {col} -p /pk --throughput 3000').get_output_in_json()

        # update throughput buckets
        self.cmd('az cosmosdb sql container throughput update -g {rg} -a {acc} -d {db_name} -n {col} --throughput 3000 --throughput-buckets {throughput_buckets}')

        throughput_resource_json = self.cmd('az cosmosdb sql container throughput show -g {rg} -a {acc} -d {db_name} -n {col}').get_output_in_json()

        actual_throughput_buckets = throughput_resource_json["resource"]["throughputBuckets"]

        assert len(actual_throughput_buckets) == 2
        assert actual_throughput_buckets[0]["id"] == 1
        assert actual_throughput_buckets[0]["maxThroughputPercentage"] == 10
        assert actual_throughput_buckets[0].get("isDefaultBucket") is None
        assert actual_throughput_buckets[1]["id"] == 2
        assert actual_throughput_buckets[1]["maxThroughputPercentage"] == 20
        assert actual_throughput_buckets[1].get("isDefaultBucket") is None

        # Test: Change throughput without specifying throughput buckets - buckets should be retained
        self.cmd('az cosmosdb sql container throughput update -g {rg} -a {acc} -d {db_name} -n {col} --throughput 4000')

        throughput_resource_json = self.cmd('az cosmosdb sql container throughput show -g {rg} -a {acc} -d {db_name} -n {col}').get_output_in_json()
        retained_throughput_buckets = throughput_resource_json["resource"]["throughputBuckets"]

        # Verify throughput buckets are retained after throughput change
        assert len(retained_throughput_buckets) == 2
        assert retained_throughput_buckets[0]["id"] == 1
        assert retained_throughput_buckets[0]["maxThroughputPercentage"] == 10
        assert retained_throughput_buckets[0].get("isDefaultBucket") is None
        assert retained_throughput_buckets[1]["id"] == 2
        assert retained_throughput_buckets[1]["maxThroughputPercentage"] == 20
        assert retained_throughput_buckets[1].get("isDefaultBucket") is None

        # Verify throughput was actually updated
        assert throughput_resource_json["resource"]["throughput"] == 4000

        # Test: Update throughput buckets with new values and verify isDefaultBucket is correctly set
        self.cmd('az cosmosdb sql container throughput update -g {rg} -a {acc} -d {db_name} -n {col} --throughput 5000 --throughput-buckets {updated_throughput_buckets}')

        throughput_resource_json = self.cmd('az cosmosdb sql container throughput show -g {rg} -a {acc} -d {db_name} -n {col}').get_output_in_json()
        updated_buckets = throughput_resource_json["resource"]["throughputBuckets"]

        # Verify updated buckets have correct values and default bucket is set
        assert len(updated_buckets) == 2
        assert updated_buckets[0]["id"] == 1
        assert updated_buckets[0]["maxThroughputPercentage"] == 15
        assert updated_buckets[0].get("isDefaultBucket") is None
        assert updated_buckets[1]["id"] == 2
        assert updated_buckets[1]["maxThroughputPercentage"] == 25
        assert updated_buckets[1]["isDefaultBucket"] == True
        assert throughput_resource_json["resource"]["throughput"] == 5000

        # Test: Set throughput buckets to empty array - buckets should be removed
        self.cmd('az cosmosdb sql container throughput update -g {rg} -a {acc} -d {db_name} -n {col} --throughput 4000 --throughput-buckets {empty_throughput_buckets}')

        throughput_resource_json = self.cmd('az cosmosdb sql container throughput show -g {rg} -a {acc} -d {db_name} -n {col}').get_output_in_json()
        
        # Verify throughput buckets are removed when set to empty array
        assert len(throughput_resource_json["resource"]["throughputBuckets"]) == 0

        # delete container
        self.cmd('az cosmosdb sql container delete -g {rg} -a {acc} -d {db_name} -n {col} -y')

        # delete database
        self.cmd('az cosmosdb sql database delete -g {rg} -a {acc} -n {db_name} -y')