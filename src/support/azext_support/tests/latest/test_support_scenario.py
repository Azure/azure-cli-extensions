# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import uuid
from datetime import date, timedelta

from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.testsdk import ScenarioTest
from azure_devtools.scenario_tests import AllowLargeResponse


class SupportScenarioTest(ScenarioTest):

    def cmd(self, command, checks=None, expect_failure=False):
        print("Runnig... {0}\n".format(command))
        rsp = super(SupportScenarioTest, self).cmd(command, checks=checks, expect_failure=expect_failure)

        try:
            rsp_json = rsp.get_output_in_json()
            print("Output... {0}\n".format(str(rsp_json)))
        except:
            pass

        return rsp

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

    def test_support_tickets_create_validations(self):
        test_ticket_name = self.create_random_name(prefix='test_ticket_from_cli_', length=30)
        service_name = "06bfd9d3-516b-d5c6-5802-169c800dec89"
        problem_classification_name = "e12e3d1d-7fa0-af33-c6d0-3c50df9658a3"
        invalid_arm_resource_id = "/subscriptions/1c4eecc5-46a8-4b7f-9a0a-fa0ba47240cd"
        invalid_arm_resource_id += "/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/testserver"
        base_cmd = self._build_base_support_tickets_create_command(test_ticket_name)

        # Failure scenario - invalid prefix problem classifications
        cmd = str(base_cmd)
        cmd += "--problem-classification '/providers/Microsoft.Support/services/0/{0}/".format(service_name)
        cmd += "problemClassifications/{0}' ".format(problem_classification_name)
        rsp = self.cmd(cmd, expect_failure=True)
        self._validate_failure_rsp(rsp, 1)

        # Failure scenario - invalid guid problem classifications
        cmd = str(base_cmd)
        cmd += "--problem-classification '/providers/Microsoft.Support/services/{0}/".format(service_name)
        cmd += "problemClassifications/{0}0' ".format(problem_classification_name)
        rsp = self.cmd(cmd, expect_failure=True)
        self._validate_failure_rsp(rsp, 1)

        # Failure scenario - invalid resource id
        cmd = str(base_cmd)
        cmd += "--problem-classification '/providers/Microsoft.Support/services/{0}/".format(service_name)
        cmd = cmd.replace(service_name, "cddd3eb5-1830-b494-44fd-782f691479dc")
        cmd += "problemClassifications/{0}' ".format("ef8b3865-0c5a-247b-dcaa-d70fd7611a3c")
        cmd += "--technical-resource '{0}' ".format(invalid_arm_resource_id)
        rsp = self.cmd(cmd, expect_failure=True)
        self._validate_failure_rsp(rsp, 1)

        # Failure scenario - invalid ticket name
        cmd = str(base_cmd)
        cmd = cmd.replace(test_ticket_name, "12345")
        cmd += "--problem-classification '/providers/Microsoft.Support/services/{0}/".format(service_name)
        cmd += "problemClassifications/{0}' ".format(problem_classification_name)
        rsp = self.cmd(cmd, expect_failure=True)
        self._validate_failure_rsp(rsp, 1)

    def test_support_tickets(self):
        random_guid = "12345678-1234-1234-1234-123412341234"
        test_ticket_name = self.create_random_name(prefix='test_ticket_from_cli_', length=30)
        test_communication_name = self.create_random_name(prefix='test_communication_from_cli_', length=40)

        # Create billing
        base_cmd = self._build_base_support_tickets_create_command(test_ticket_name)
        billing_cmd = self._build_support_tickets_create_billing_cmd()
        cmd = "{0} {1}".format(base_cmd, billing_cmd)
        rsp = self.cmd(cmd).get_output_in_json()
        self._validate_base_support_tickets_create_command(rsp, test_ticket_name)

        # Create communication 1 - invalid communication name
        cmd = self._build_support_tickets_communications_create_cmd(test_ticket_name, random_guid)
        rsp = self.cmd(cmd, expect_failure=True)
        self._validate_failure_rsp(rsp, 1)

        # Create communication 2
        cmd = self._build_support_tickets_communications_create_cmd(test_ticket_name, test_communication_name)
        rsp = self.cmd(cmd).get_output_in_json()
        self._validate_support_tickets_communications_create_cmd(rsp, test_ticket_name, test_communication_name)

        # List communications
        cmd = self._build_support_tickets_communications_list_cmd(test_ticket_name)
        rsp = self.cmd(cmd).get_output_in_json()
        self._validate_support_tickets_communications_list_cmd(rsp, test_ticket_name, test_communication_name)

        # Show communication
        cmd = self._build_support_tickets_communications_show_cmd(test_ticket_name, test_communication_name)
        rsp = self.cmd(cmd).get_output_in_json()
        self._validate_support_tickets_communications_show_cmd(rsp, test_ticket_name, test_communication_name)

        # List tickets
        cmd = self._build_support_tickets_list_cmd()
        rsp = self.cmd(cmd).get_output_in_json()
        self._validate_support_tickets_list_cmd(rsp, test_ticket_name)

        # Update severity/contact 1
        cmd = self._build_support_tickets_update_cmd1(test_ticket_name)
        rsp = self.cmd(cmd).get_output_in_json()
        self._validate_support_tickets_update_cmd1(rsp)

        # Update severity/contact 2
        cmd = self._build_support_tickets_update_cmd2(test_ticket_name)
        rsp = self.cmd(cmd).get_output_in_json()
        self._validate_support_tickets_update_cmd2(rsp)

        # Show
        cmd = self._build_support_tickets_show_cmd(test_ticket_name)
        rsp = self.cmd(cmd).get_output_in_json()
        self._validate_support_tickets_show_cmd(rsp, test_ticket_name)

    def _build_base_support_tickets_create_command(self, test_ticket_name):
        test_ticket_title = "test ticket from python cli test. Do not assign and close after a day."
        cmd = "support tickets create --debug "
        cmd += "--description '{0}' ".format(test_ticket_title)
        cmd += "--severity 'minimal' "
        cmd += "--ticket-name '{0}' ".format(test_ticket_name)
        cmd += "--severity 'minimal' "
        cmd += "--title '{0}' ".format(test_ticket_title)
        cmd += "--contact-country 'USA' "
        cmd += "--contact-email 'azengcase@microsoft.com' "
        cmd += "--contact-first-name 'Foo' "
        cmd += "--contact-language 'en-US' "
        cmd += "--contact-last-name 'Bar' "
        cmd += "--contact-method 'email' "
        cmd += "--contact-timezone 'Pacific Standard Time' "

        return cmd

    def _build_support_tickets_create_quota_cmd(self):
        service_name = "06bfd9d3-516b-d5c6-5802-169c800dec89"
        problem_classification_name = "e12e3d1d-7fa0-af33-c6d0-3c50df9658a3"
        cmd = "--problem-classification '/providers/Microsoft.Support/services/{0}/".format(service_name)
        cmd += "problemClassifications/{0}' ".format(problem_classification_name)

        quota_payload1 = '{"SKU": "DSv3 Series", "NewLimit": 100}'
        quota_payload2 = '{"SKU": "DSv3 Series", "NewLimit": 100}'
        cmd += "--quota-change-payload '{0}' '{1}' ".format(quota_payload1, quota_payload2)
        cmd += "--quota-change-regions 'EastUS' 'EastUS2' "
        cmd += "--quota-change-version '1.0' "

        return cmd

    def _build_support_tickets_create_technical_cmd(self):
        service_name = "cddd3eb5-1830-b494-44fd-782f691479dc"
        problem_classification_name = "6fb3a706-abe9-0693-1544-72e848334a9f"
        cmd = "--problem-classification '/providers/Microsoft.Support/services/{0}/".format(service_name)
        cmd += "problemClassifications/{0}' ".format(problem_classification_name)

        arm_resource_id = "/subscriptions/{0}".format(self.get_subscription_id())
        arm_resource_id += "/resourceGroups/AaronTest/providers/Microsoft.AppPlatform/Spring/springtest"
        cmd += "--technical-resource '{0}' ".format(arm_resource_id)

        return cmd

    def _build_support_tickets_create_billing_cmd(self):
        service_name = "517f2da6-78fd-0498-4e22-ad26996b1dfc"
        problem_classification_name = "44114011-6a66-e902-c00f-e419b6b4509f"
        cmd = "--problem-classification '/providers/Microsoft.Support/services/{0}/".format(service_name)
        cmd += "problemClassifications/{0}' ".format(problem_classification_name)

        return cmd

    def _build_support_tickets_create_submgmt_cmd(self):
        service_name = "f3dc5421-79ef-1efa-41a5-42bf3cbb52c6"
        problem_classification_name = "eefb3e6a-0243-9fc2-9197-d2798d71a74c"
        cmd = "--problem-classification '/providers/Microsoft.Support/services/{0}/".format(service_name)
        cmd += "problemClassifications/{0}' ".format(problem_classification_name)

        return cmd

    def _validate_base_support_tickets_create_command(self, rsp, test_ticket_name):
        self.assertTrue(rsp is not None)
        self.assertTrue("type" in rsp)
        self.assertTrue(rsp["type"] == "Microsoft.Support/supportTickets")
        self.assertTrue("name" in rsp)
        self.assertTrue(rsp["name"] == test_ticket_name)
        self.assertTrue("require24X7Response" in rsp)
        self.assertTrue(rsp["require24X7Response"] is False)

    def _build_support_tickets_communications_create_cmd(self, test_ticket_name, test_communication_name):
        cmd = "support tickets communications create --debug "
        cmd += "--ticket-name '{0}' ".format(test_ticket_name)
        cmd += "--communication-name '{0}' ".format(test_communication_name)
        cmd += "--communication-sender 'nichheda@microsoft.com' "
        cmd += "--communication-subject 'test subject for communication posted from azure python cli' "
        cmd += "--communication-body 'test body for communication posted from azure python cli' "

        return cmd

    def _validate_support_tickets_communications_create_cmd(self, rsp, test_ticket_name, test_communication_name):
        self.assertTrue(rsp is not None)
        self.assertTrue("type" in rsp)
        self.assertTrue(rsp["type"] == "Microsoft.Support/communications")
        self.assertTrue("name" in rsp)
        self.assertTrue(rsp["name"] == test_communication_name)

    def _build_support_tickets_communications_list_cmd(self, test_ticket_name):
        cmd = "support tickets communications list "
        cmd += "--ticket-name '{0}' ".format(test_ticket_name)

        return cmd

    def _validate_support_tickets_communications_list_cmd(self, rsp, test_ticket_name, test_communication_name):
        self.assertTrue(rsp is not None)
        self.assertTrue(len(rsp) >= 1)
        self.assertTrue("type" in rsp[0])
        self.assertTrue(rsp[0]["type"] == "Microsoft.Support/communications")
        self.assertTrue("name" in rsp[0])

        communication_returned = False
        for communication in rsp:
            if communication["name"] == test_communication_name:
                communication_returned = True
                break

        self.assertTrue(communication_returned is True)

    def _build_support_tickets_communications_show_cmd(self, test_ticket_name, test_communication_name):
        cmd = "support tickets communications show "
        cmd += "--ticket-name '{0}' ".format(test_ticket_name)
        cmd += "--communication-name '{0}' ".format(test_communication_name)

        return cmd

    def _validate_support_tickets_communications_show_cmd(self, rsp, test_ticket_name, test_communication_name):
        self.assertTrue(rsp is not None)
        self.assertTrue("type" in rsp)
        self.assertTrue(rsp["type"] == "Microsoft.Support/communications")
        self.assertTrue("name" in rsp)
        self.assertTrue(rsp["name"] == test_communication_name)

    def _build_support_tickets_list_cmd(self):
        cmd = "support tickets list "
        cmd += "--filters \"status eq 'Open'\" "

        return cmd

    def _validate_support_tickets_list_cmd(self, rsp, test_ticket_name):
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

    def _build_support_tickets_update_cmd1(self, test_ticket_name):
        cmd = "support tickets update "
        cmd += "--ticket-name '{0}' ".format(test_ticket_name)
        cmd += "--severity 'moderate' "
        cmd += "--contact-method 'phone' "
        cmd += "--contact-phone-number '123-456-7890' "

        return cmd

    def _validate_support_tickets_update_cmd1(self, rsp):
        self.assertTrue(rsp is not None)
        self.assertTrue("type" in rsp)
        self.assertTrue(rsp["type"] == "Microsoft.Support/supportTickets")
        self.assertTrue("severity" in rsp)
        self.assertTrue("Moderate" == rsp["severity"])
        self.assertTrue("contactDetails" in rsp)
        self.assertTrue("123-456-7890" == rsp["contactDetails"]["phoneNumber"])
        self.assertTrue("Phone" == rsp["contactDetails"]["preferredContactMethod"])

    def _build_support_tickets_update_cmd2(self, test_ticket_name):
        cmd = "support tickets update "
        cmd += "--ticket-name '{0}' ".format(test_ticket_name)
        cmd += "--severity 'minimal' "
        cmd += "--contact-method 'email' "

        return cmd

    def _validate_support_tickets_update_cmd2(self, rsp):
        self.assertTrue(rsp is not None)
        self.assertTrue("type" in rsp)
        self.assertTrue(rsp["type"] == "Microsoft.Support/supportTickets")
        self.assertTrue("severity" in rsp)
        self.assertTrue("Minimal" == rsp["severity"])
        self.assertTrue("contactDetails" in rsp)
        self.assertTrue("Email" == rsp["contactDetails"]["preferredContactMethod"])

    def _build_support_tickets_show_cmd(self, test_ticket_name):
        cmd = "support tickets show "
        cmd += "--ticket-name '{0}' ".format(test_ticket_name)

        return cmd

    def _validate_support_tickets_show_cmd(self, rsp, test_ticket_name):
        self.assertTrue(rsp is not None)
        self.assertTrue("type" in rsp)
        self.assertTrue(rsp["type"] == "Microsoft.Support/supportTickets")
        self.assertTrue("name" in rsp)
        self.assertTrue(rsp["name"] == test_ticket_name)

    def _validate_failure_rsp(self, rsp, exit_code):
        self.assertTrue(rsp is not None)
        self.assertTrue(rsp.exit_code is not None)
        self.assertTrue(rsp.exit_code == exit_code)
