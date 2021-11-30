from azure.cli.testsdk import ScenarioTest
import time

class ManagementGroupTests(ScenarioTest):
    '''def test_list_managementgroup(self):
        managementgroups_list = self.cmd(
            'az managementgroup management-group list').get_output_in_json()
        self.assertIsNotNone(managementgroups_list)
        self.assertTrue(len(managementgroups_list) > 0)
        self.assertIsNotNone(managementgroups_list[0]["displayName"])
        self.assertTrue(managementgroups_list[0]["id"].startswith(
            "/providers/Microsoft.Management/managementGroups/"))
        self.assertIsNotNone(managementgroups_list[0]["name"])
        self.assertIsNotNone(managementgroups_list[0]["tenantId"])
        self.assertEqual(
            managementgroups_list[0]["type"],
            "Microsoft.Management/managementGroups")'''

    def test_tenant_backfill(self):
        backfill_result = self.cmd('az managementgroup start-tenant-backfill').get_output_in_json()
        self.assertIsNotNone(backfill_result)
        self.assertEqual(backfill_result["status"], "Completed")
        backfill_status = self.cmd('az managementgroup tenant-backfill-status').get_output_in_json()
        self.assertIsNotNone(backfill_status)
        self.assertEqual(backfill_status["status"], "Completed")
        
    def test_show_managementgroup(self):
        self.cmd('az managementgroup management-group create --group-id "thomasSubs"')
        self.cmd('az managementgroup management-group create --group-id "thomasSubs1" --id "/providers/Microsoft.Management/managementGroups/thomasSubs"')
        self.cmd('az managementgroup management-group create --group-id "thomasSubs2" --id "/providers/Microsoft.Management/managementGroups/thomasSubs1"')
        self.cmd('az managementgroup management-group-subscription create --group-id "thomasSubs1" --subscription-id "5602fbd9-fb0d-4fbb-98b3-10c8ea20b6de"')
        managementgroup_get = self.cmd('az managementgroup management-group show --group-id "thomasSubs1"').get_output_in_json()
        managementgroup_show_sub = self.cmd('az managementgroup management-group-subscription show-subscription --group-id "thomasSubs1" --subscription-id "5602fbd9-fb0d-4fbb-98b3-10c8ea20b6de"').get_output_in_json()
        show_sub_under_mg = self.cmd('az managementgroup management-group-subscription show-subscription-under-management-group --group-id "thomasSubs1"').get_output_in_json()
        '''self.cmd('az managementgroup management-group delete --group-id "testcligetgroup2" --yes')
        self.cmd('az managementgroup management-group delete --group-id "testcligetgroup1" --yes')'''
        self.assertIsNotNone(managementgroup_get)
        self.assertIsNone(managementgroup_get["children"])
        self.assertIsNotNone(managementgroup_get["details"])
        self.assertEqual(
            managementgroup_get["id"],
            "/providers/Microsoft.Management/managementGroups/thomasSubs1")
        self.assertEqual(managementgroup_get["name"], "thomasSubs1")
        self.assertEqual(
            managementgroup_get["displayName"],
            "thomasSubs1")
        self.assertEqual(
            managementgroup_get["details"]["parent"]["displayName"],
            "thomasSubs")
        self.assertEqual(
            managementgroup_get["details"]["parent"]["id"],
            "/providers/Microsoft.Management/managementGroups/thomasSubs")
        self.assertEqual(
            managementgroup_get["details"]["parent"]["name"],
            "thomasSubs")
        self.assertIsNotNone(managementgroup_get["tenantId"])
        self.assertEqual(
            managementgroup_get["type"],
            "Microsoft.Management/managementGroups")
        self.assertIsNotNone(managementgroup_show_sub)
        self.assertEqual(managementgroup_show_sub["displayName"], 
            "Visual Studio Enterprise Subscription")
        self.assertEqual(managementgroup_show_sub["name"], 
            "5602fbd9-fb0d-4fbb-98b3-10c8ea20b6de")
        self.assertEqual(managementgroup_show_sub["parent"]["id"], 
            "/providers/Microsoft.Management/managementGroups/thomasSubs1")
        self.assertEqual(managementgroup_show_sub["state"], 
            "Active")
        self.assertEqual(managementgroup_show_sub["type"], 
            "Microsoft.Management/managementGroups/subscriptions")
        self.assertIsNotNone(show_sub_under_mg)
        self.assertEqual(managementgroup_show_sub["name"], show_sub_under_mg[0]["name"])
        self.cmd('az managementgroup management-group update --group-id "thomasSubs1" --display-name "dolanSubs1"')
        managementgroup_get = self.cmd('az managementgroup management-group show --group-id "thomasSubs1"').get_output_in_json()
        self.assertIsNotNone(managementgroup_get)
        self.assertEqual(managementgroup_get["displayName"], "dolanSubs1")
        self.cmd('az managementgroup management-group-subscription delete --group-id "thomasSubs1" --subscription-id "5602fbd9-fb0d-4fbb-98b3-10c8ea20b6de" --yes')
        self.cmd('az managementgroup management-group delete --group-id "thomasSubs2" --yes')
        self.cmd('az managementgroup management-group delete --group-id "thomasSubs1" --yes')
        self.cmd('az managementgroup management-group delete --group-id "thomasSubs" --yes')



    
