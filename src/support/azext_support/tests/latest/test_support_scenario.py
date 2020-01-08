# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from datetime import date, timedelta

from azure.cli.testsdk import ScenarioTest
from azure_devtools.scenario_tests import AllowLargeResponse


class SupportScenarioTest(ScenarioTest):

    def test_support_services(self):

        # List
        list_services_result = self.cmd('support services list').get_output_in_json()
        self.assertTrue(list_services_result is not None)
        self.assertTrue(len(list_services_result) > 100)
        self.assertTrue("type" in list_services_result[0])
        self.assertTrue(list_services_result[0]["type"] == "Microsoft.Support/services")
        self.assertTrue("name" in list_services_result[0])
        self.assertTrue("id" in list_services_result[0])

        # Show
        show_services_result = self.cmd('support services show --service-name ' +
                                        list_services_result[0]["name"]).get_output_in_json()
        self.assertTrue(show_services_result is not None)
        self.assertTrue("type" in show_services_result)
        self.assertTrue(show_services_result["type"] == "Microsoft.Support/services")
        self.assertTrue("name" in show_services_result)
        self.assertTrue("id" in show_services_result)
        self.assertTrue(show_services_result["id"] ==
                        "/providers/Microsoft.Support/services/" + show_services_result["name"])

        # List problem classifications
        list_problem_classifications_result = self.cmd('az support services problem-classifications list --service-name ' +
                                                       list_services_result[0]["name"]).get_output_in_json()
        self.assertTrue(list_problem_classifications_result is not None)
        self.assertTrue(len(list_problem_classifications_result) > 0)
        self.assertTrue("type" in list_problem_classifications_result[0])
        self.assertTrue(list_problem_classifications_result[0]["type"] ==
                        "Microsoft.Support/problemClassifications")
        self.assertTrue("name" in list_problem_classifications_result[0])
        self.assertTrue("id" in list_problem_classifications_result[0])

        # Show problem classification
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

        # date_suffix = date.today().strftime("%m_%d_%y")
        # test_ticket_name = "test_ticket_" + date_suffix
        test_ticket_name = "support_api_demo_ticket_arm_template"
        # test_communication_name = "test_communication_" + date_suffix
        test_communication_name = "7f24f7e3-209e-431f-93ee-718d63e41042"
        service_name = "/providers/Microsoft.Support/services/06bfd9d3-516b-d5c6-5802-169c800dec89"
        problem_classification_name = "e12e3d1d-7fa0-af33-c6d0-3c50df9658a3"

        # Create
        base_cmd = "support tickets create "
        base_cmd += "--description 'test ticket from python cli test' "
        base_cmd += "--severity 'minimal' "
        base_cmd += "--ticket-name '" + test_ticket_name + "' "
        base_cmd += "--severity 'minimal' "
        base_cmd += "--title 'test ticket from python cli test' "
        base_cmd += "--contact-country 'USA' "
        base_cmd += "--contact-email 'azengcase@microsoft.com' "
        base_cmd += "--contact-first-name 'Foo' "
        base_cmd += "--contact-language 'en-US' "
        base_cmd += "--contact-last-name 'Bar' "
        base_cmd += "--contact-method 'email' "
        base_cmd += "--contact-timezone 'Pacific Standard Time' "

        quota_cmd = "--quota-change-payload \"{\"SKU\":\"DSv3 Series\",\"NewLimit\":100}" "{\"SKU\":\"DSv3 Series\",\"NewLimit\":100}\" "
        quota_cmd += "--quota-change-regions 'EastUS' 'EastUS2' "
        quota_cmd += "--quota-change-version '1.0' "

        # Failure scenario - invalid prefix service
        failure_cmd = str(base_cmd)
        failure_cmd += "--service 'abcd" + service_name + "' "
        failure_cmd += "--problem-classification '" + service_name
        failure_cmd += "'/problemClassifications/" + problem_classification_name + "' "
        self.cmd(base_cmd + failure_cmd, expect_failure=True)

        # Failure scenario - invalid guid service
        failure_cmd = str(base_cmd)
        failure_cmd += "--service '" + service_name + "-1234' "
        failure_cmd += "--problem-classification '" + service_name
        failure_cmd += "'/problemClassifications/" + problem_classification_name + "' "
        rsp = self.cmd(base_cmd + failure_cmd, expect_failure=True)

        # Failure scenario - invalid id service
        failure_cmd = str(base_cmd)
        failure_cmd += "--service '" + service_name.replace("af33", "0000") + "' "
        failure_cmd += "--problem-classification '" + service_name
        failure_cmd += "'/problemClassifications/" + problem_classification_name + "' "
        rsp = self.cmd(base_cmd + failure_cmd, expect_failure=True)

        # Failure scenario - invalid prefix problem classifications
        failure_cmd = str(base_cmd)
        failure_cmd += "--service 'abcd" + service_name + "' "
        failure_cmd += "--problem-classification 'abcd" + service_name
        failure_cmd += "'/problemClassifications/" + problem_classification_name + "' "
        rsp = self.cmd(base_cmd + failure_cmd, expect_failure=True)

        # Failure scenario - invalid guid problem classifications
        failure_cmd = str(base_cmd)
        failure_cmd += "--service '" + service_name + "' "
        failure_cmd += "--problem-classification '" + service_name
        failure_cmd += "'/problemClassifications/" + problem_classification_name + "-1234' "
        rsp = self.cmd(base_cmd + failure_cmd, expect_failure=True)

        # Failure scenario - invalid id problem classifications
        failure_cmd = str(base_cmd)
        failure_cmd += "--service '" + service_name + "' "
        failure_cmd += "--problem-classification '" + service_name
        failure_cmd += "'/problemClassifications/" + problem_classification_name.replace("c6d0", "0000") + "' "
        rsp = self.cmd(base_cmd + failure_cmd, expect_failure=True)

        # Success scenario:
        # validate 24x7, start time
        # show_tickets_result = self.cmd(base_cmd + quota_cmd).get_output_in_json()

        # List
        base_cmd = "support tickets list "
        base_cmd += "--filters \"CreatedDate ge " + str(date.today() - timedelta(days=7)) + "\" "
        # base_cmd += "--filters \"status eq 'Open' and CreatedDate ge " + str(date.today() - timedelta(7)) + "\" "
        rsp = self.cmd(base_cmd).get_output_in_json()
        self.assertTrue(rsp is not None)
        self.assertTrue(len(rsp) >= 1)
        self.assertTrue("type" in rsp[0])
        self.assertTrue(rsp[0]["type"] == "Microsoft.Support/supportTickets")
        self.assertTrue("name" in rsp[0])

        ticket_returned = False
        for ticket in rsp:
            if ticket["name"] == test_ticket_name:
                ticket_returned = True
                break
        self.assertTrue(ticket_returned is True)

        # Update

        # Show
        base_cmd = "support tickets show "
        base_cmd += "--ticket-name '" + test_ticket_name + "' "
        rsp = self.cmd(base_cmd).get_output_in_json()
        self.assertTrue(rsp is not None)
        self.assertTrue("type" in rsp)
        self.assertTrue(rsp["type"] == "Microsoft.Support/supportTickets")
        self.assertTrue("name" in rsp)
        self.assertTrue(rsp["name"] == test_ticket_name)

        # Create communication

        # List communications
        base_cmd = "support tickets communications list "
        base_cmd += "--ticket-name '" + test_ticket_name + "' "
        rsp = self.cmd(base_cmd).get_output_in_json()
        self.assertTrue(rsp is not None)
        self.assertTrue(len(rsp) >= 1)
        self.assertTrue("type" in rsp[0])
        self.assertTrue(rsp[0]["type"] == "Microsoft.Support/communications")
        self.assertTrue("name" in rsp[0])
        self.assertTrue("id" in rsp[0])

        # Show communication
        base_cmd = "support tickets communications show "
        base_cmd += "--ticket-name '" + test_ticket_name + "' "
        base_cmd += "--communication-name '" + test_communication_name + "' "
        rsp = self.cmd(base_cmd).get_output_in_json()
        self.assertTrue(rsp is not None)
        self.assertTrue("type" in rsp)
        self.assertTrue(rsp["type"] == "Microsoft.Support/communications")
        self.assertTrue("name" in rsp)
        self.assertTrue(rsp["name"] == test_communication_name)
