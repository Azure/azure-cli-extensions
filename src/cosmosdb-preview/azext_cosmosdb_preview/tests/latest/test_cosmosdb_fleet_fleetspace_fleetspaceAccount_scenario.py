# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
import os
import json
import tempfile


class CosmosdbFleetScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_fleet', location='westus2')
    def test_cosmosdb_fleet_fleetspace_fleetspaceAccount(self, resource_group):
        # Names
        fleet_name = 'fleetTest'
        fleet_analytics_name = 'fleetAnalyticsTest'
        fleetspace_name = 'fleetspaceTest'
        account_name = self.create_random_name('acct', 15)

        # JSON
        fleetspace_body = self._write_temp_json({
            "properties": {
                "throughputPoolConfiguration": {
                    "minThroughput": 100000,
                    "maxThroughput": 400000,
                    "serviceTier": "GeneralPurpose",
                    "dataRegions": ["West US 2",]
                }
            }
        })

        fleetspace_update_body = self._write_temp_json({
            "properties": {
                "throughputPoolConfiguration": {
                    "minThroughput": 200000,
                    "maxThroughput": 600000,
                    "serviceTier": "GeneralPurpose",
                    "dataRegions": ["West US 2"]
                }
            }
        })

        fleetspace_account_body = self._write_temp_json({
            "properties": {
                "globalDatabaseAccountProperties": {
                    "resourceId": f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{resource_group}/providers/Microsoft.DocumentDb/databaseAccounts/{account_name}",
                    "armLocation": "westus2"
                }
            }
        })

        fleet_analytics_body = self._write_temp_json({
            "properties": {
                "storageLocationType": "StorageAccount",
                "storageLocationUri": f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/myStorageAccount",
            }
        })

        self.kwargs.update({
            'rg': resource_group,
            'acct': account_name,
            'fleet': fleet_name,
            'fanalytics': fleet_analytics_name,
            'fanalyticsbody': fleet_analytics_body,
            'fsp': fleetspace_name,
            'fspacct': account_name,
            'fspbody': fleetspace_body,
            'fspupdate': fleetspace_update_body,
            'fspacctbody': fleetspace_account_body
        })

        # Create Cosmos DB account dynamically
        self.cmd('az cosmosdb create -g {rg} -n {acct} --locations regionName=westus2 failoverPriority=0 isZoneRedundant=False')

        # Fleet
        self.cmd('az cosmosdb fleet create -g {rg} -n {fleet} -l westus2')
        self.cmd('az cosmosdb fleet show -g {rg} -n {fleet}')
        self.cmd('az cosmosdb fleet list -g {rg}')

        # Fleet Analytics
        self.cmd('az cosmosdb fleet analytics create -g {rg} --fleet-name {fleet} -n {fanalytics} --body @{fanalyticsbody}')
        self.cmd('az cosmosdb fleet analytics show -g {rg} --fleet-name {fleet} -n {fanalytics}')
        self.cmd('az cosmosdb fleet analytics list -g {rg} --fleet-name {fleet}')

        # Fleetspace
        self.cmd('az cosmosdb fleetspace create -g {rg} --fleet-name {fleet} -n {fsp} --body @{fspbody}')
        self.cmd('az cosmosdb fleetspace update -g {rg} --fleet-name {fleet} -n {fsp} --body @{fspupdate}')
        self.cmd('az cosmosdb fleetspace show -g {rg} --fleet-name {fleet} -n {fsp}')
        self.cmd('az cosmosdb fleetspace list -g {rg} --fleet-name {fleet}')

        # Fleetspace Account
        self.cmd('az cosmosdb fleetspace account create -g {rg} --fleet-name {fleet} --fleetspace-name {fsp} --fleetspace-account-name {fspacct} --body @{fspacctbody}')
        self.cmd('az cosmosdb fleetspace account show -g {rg} --fleet-name {fleet} --fleetspace-name {fsp} --fleetspace-account-name {fspacct}')
        self.cmd('az cosmosdb fleetspace account list -g {rg} --fleet-name {fleet} --fleetspace-name {fsp}')

        # Deletes
        self.cmd('az cosmosdb fleet analytics delete -g {rg} --fleet-name {fleet} -n {fanalytics} --yes')
        self.cmd('az cosmosdb fleetspace account delete -g {rg} --fleet-name {fleet} --fleetspace-name {fsp} --fleetspace-account-name {fspacct} --yes')
        self.cmd('az cosmosdb fleetspace delete -g {rg} --fleet-name {fleet} -n {fsp} --yes')
        self.cmd('az cosmosdb fleet delete -g {rg} -n {fleet} --yes')

    def _write_temp_json(self, data):
        fd, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)
        return os.path.abspath(path).replace('\\', '/')
