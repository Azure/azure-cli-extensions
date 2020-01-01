# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from datetime import date, timedelta

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest

class SupportScenarioTest(ScenarioTest):

    def test_support_services(self):
        list_services_result = self.cmd('support services list').get_output_in_json()
        self.assertTrue(list_services_result is not None)
        self.assertTrue(len(list_services_result) > 100)
        self.assertTrue("type" in list_services_result[0])
        self.assertTrue(list_services_result[0]["type"] == "Microsoft.Support/services")
        self.assertTrue("name" in list_services_result[0])
        self.assertTrue("id" in list_services_result[0])

        show_services_result = self.cmd('support services show --service-name ' +
                                        list_services_result[0]["name"]).get_output_in_json()
        self.assertTrue(show_services_result is not None)
        self.assertTrue("type" in show_services_result)
        self.assertTrue(show_services_result["type"] == "Microsoft.Support/services")
        self.assertTrue("name" in show_services_result)
        self.assertTrue("id" in show_services_result)
        self.assertTrue(show_services_result["id"] ==
                        "/providers/Microsoft.Support/services/" + show_services_result["name"])

        list_problem_classifications_result = self.cmd('az support services problem-classifications list --service-name ' +
                                                       list_services_result[0]["name"]).get_output_in_json()
        self.assertTrue(list_problem_classifications_result is not None)
        self.assertTrue(len(list_problem_classifications_result) > 0)
        self.assertTrue("type" in list_problem_classifications_result[0])
        self.assertTrue(list_problem_classifications_result[0]["type"] ==
                        "Microsoft.Support/problemClassifications")
        self.assertTrue("name" in list_problem_classifications_result[0])
        self.assertTrue("id" in list_problem_classifications_result[0])

        show_problem_classifications_result = self.cmd('az support services problem-classifications show --service-name ' +
                                                       list_services_result[0]["name"] + ' --problem-classification-name ' +
                                                       list_problem_classifications_result[0]["name"]).get_output_in_json()
        self.assertTrue(show_problem_classifications_result is not None)
        self.assertTrue("type" in show_problem_classifications_result)
        self.assertTrue(show_problem_classifications_result["type"] ==
                        "Microsoft.Support/problemClassifications")
        self.assertTrue("name" in show_problem_classifications_result)
        self.assertTrue("id" in show_problem_classifications_result)
        self.assertTrue(show_problem_classifications_result["id"] ==
                        "/providers/Microsoft.Support/services/" + list_services_result[0]["name"] +
                        "/problemClassifications/" + list_problem_classifications_result[0]["name"])

    def test_support_tickets(self):
        '''
        dateFiler = "CreatedDate ge " + str(date.today() - timedelta(7))
        list_tickets_result = self.cmd('support tickets list --top 5 --filters "'+ dateFiler + ' "').get_output_in_json()
        self.assertTrue(list_tickets_result is not None)
        self.assertTrue(len(list_tickets_result) >= 5)
        self.assertTrue("type" in list_tickets_result[0])
        self.assertTrue(list_tickets_result[0]["type"] == "Microsoft.Support/supportTickets")
        self.assertTrue("name" in list_tickets_result[0])
        '''
        list_tickets_result = [{"name": "119120521000029"}]

        show_tickets_result = self.cmd('support tickets show --ticket-name ' +
                                       list_tickets_result[0]["name"]).get_output_in_json()
        self.assertTrue(show_tickets_result is not None)
        self.assertTrue("type" in show_tickets_result)
        self.assertTrue(show_tickets_result["type"] == "Microsoft.Support/supportTickets")
        self.assertTrue("name" in show_tickets_result)
        self.assertTrue(show_tickets_result["name"] == list_tickets_result[0]["name"])

        for ticket in list_tickets_result:
            list_tickets_communications_result = self.cmd('support tickets communications list --ticket-name ' +
                                                          ticket["name"]).get_output_in_json()
            self.assertTrue(list_tickets_communications_result is not None)
            self.assertTrue(len(list_tickets_communications_result) >= 0)
            
            if len(list_tickets_communications_result) > 0:
                self.assertTrue("type" in list_tickets_communications_result[0])
                self.assertTrue(list_tickets_communications_result[0]["type"] == "Microsoft.Support/communications")
                self.assertTrue("name" in list_tickets_communications_result[0])
                self.assertTrue("id" in list_tickets_communications_result[0])

                show_tickets_communications_result = self.cmd('support tickets communications show --ticket-name ' +
                                                              ticket["name"] + " --communication-name " +
                                                              list_tickets_communications_result[0]["name"]).get_output_in_json()
                self.assertTrue(show_tickets_communications_result is not None)
                self.assertTrue("type" in show_tickets_communications_result)
                self.assertTrue(show_tickets_communications_result["type"] == "Microsoft.Support/communications")
                self.assertTrue("name" in show_tickets_communications_result)
                self.assertTrue(show_tickets_communications_result["name"] == list_tickets_communications_result[0]["name"])
