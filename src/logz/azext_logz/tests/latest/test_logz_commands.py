# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
from azure.cli.testsdk import (
    ResourceGroupPreparer,
    ScenarioTest
)
from azure.cli.testsdk.scenario_tests import (
    RecordingProcessor,
    live_only
)
from azure.cli.testsdk.scenario_tests.utilities import is_text_payload


class CredentialReplacer(RecordingProcessor):
    def process_response(self, response):
        import json
        fake_data = "hidden"
        sensitive_data = "apiKey"
        if is_text_payload(response) and response["body"]["string"]:
            try:
                props = json.loads(response["body"]["string"])
                if sensitive_data in props:
                    del props[sensitive_data]
                    props[fake_data] = fake_data
                response["body"]["string"] = json.dumps(props)
            except TypeError:
                pass
        return response


class LogzClientTest(ScenarioTest):
    def __init__(self, method_name):
        super(LogzClientTest, self).__init__(
            method_name,
            recording_processors=[CredentialReplacer()]
        )

    @live_only()
    @ResourceGroupPreparer(name_prefix="cli_test_logz_", location="westus2")
    def test_main_account_crud(self):
        self.kwargs.update({
            "name": "monitor",
            "date": "2021-08-31T15:14:33+02:00",
            "plan": "100gb14days", "email": "ethanyang@microsoft.com"  # set valid plan-data and user-info
        })
        # create main account
        self.cmd(
            "logz monitor create -n {name} -g {rg} \
            --plan-data billing-cycle=Monthly effective-date={date} plan-details={plan} usage-type=Committed \
            --user-info email-address={email} phone-number=01234567 first-name=Ethan last-name=Yang \
            --tags Environment=Dev",
            checks=[
                self.check("type", "microsoft.logz/monitors")
            ]
        )
        # validate list-related commands
        self.cmd(
            "logz monitor list -g {rg}",
            checks=[
                self.check("length(@)", 1)
            ]
        )
        role_obj = self.cmd(
            "logz monitor list-role -n {name} -g {rg} --email-address={email}"
        ).get_output_in_json()[0]
        assert role_obj["role"] == "Admin"
        resource_list = self.cmd(
            "logz monitor list-resource -n {name} -g {rg}"
        ).get_output_in_json()
        assert len(resource_list) >= 0
        # validate main account update
        self.cmd(
            "logz monitor update -n {name} -g {rg} \
            --monitoring-status Disabled --tags Environment=Dev"
        )
        self.cmd(
            "logz monitor show -n {name} -g {rg}",
            checks=[
                self.check("properties.monitoringStatus", "Disabled")
            ]
        )
        # delete main account
        self.cmd("logz monitor delete -n {name} -g {rg} --yes")

    @live_only()
    @ResourceGroupPreparer(name_prefix="cli_test_logz_", location="westus2")
    def test_main_account_vm(self):
        self.kwargs.update({
            "name": "monitor",
            "date": "2021-08-31T15:14:33+02:00",
            "plan": "100gb14days", "email": "ethanyang@microsoft.com",  # set valid plan-data and user-info
            "vm": "machine",
            "version": "1.0.*"

        })
        # create main account
        self.cmd(
            "logz monitor create -n {name} -g {rg} \
            --plan-data billing-cycle=Monthly effective-date={date} plan-details={plan} usage-type=Committed \
            --user-info email-address={email} phone-number=01234567 first-name=Ethan last-name=Yang \
            --tags Environment=Dev",
            checks=[
                self.check("type", "microsoft.logz/monitors")
            ]
        )
        # create virtual machine
        self.cmd(
            "vm create -n {vm} -g {rg} \
            --os-disk-name os-disk --image OpenLogic:CentOS:7.5:latest \
            --generate-ssh-keys --public-ip-sku standard",
            checks=[
                self.check("powerState", "VM running")
            ]
        )
        self.kwargs["id"] = self.cmd("vm show -n {vm} -g {rg}").get_output_in_json()["id"]
        # validate update and retrieval
        self.cmd(
            "logz monitor update-vm -n {name} -g {rg} \
            --state install \
            --vm-resource-ids id={id} agent-version={version}"
        )
        vm_obj = self.cmd("logz monitor list-vm -n {name} -g {rg}").get_output_in_json()[0]
        assert vm_obj["id"].lower() == self.kwargs["id"].lower()
        self.cmd(
            "logz monitor list-payload -n {name} -g {rg}",
            checks=[
                self.check("region", "westus2")
            ]
        )

    @live_only()
    @ResourceGroupPreparer(name_prefix="cli_test_logz_", location="westus2")
    def test_main_account_rule(self):
        self.kwargs.update({
            "name": "monitor",
            "date": "2021-08-31T15:14:33+02:00",
            "plan": "100gb14days", "email": "ethanyang@microsoft.com",  # set valid plan-data and user-info
            "rule": "default"
        })
        # create main account
        self.cmd(
            "logz monitor create -n {name} -g {rg} \
            --plan-data billing-cycle=Monthly effective-date={date} plan-details={plan} usage-type=Committed \
            --user-info email-address={email} phone-number=01234567 first-name=Ethan last-name=Yang \
            --tags Environment=Dev",
            checks=[
                self.check("type", "microsoft.logz/monitors")
            ]
        )
        # create tag rule
        self.cmd(
            "logz rule create --monitor-name {name} -g {rg} \
            --filtering-tag name=Environment action=Exclude value=Dev \
            --send-aad-logs false --send-activity-logs true --send-subscription-logs true \
            --rule-set-name {rule}",
            checks=[
                self.check("type", "microsoft.logz/monitors/tagrules")
            ]
        )
        # validate retrieval and update
        self.cmd(
            "logz rule list --monitor-name {name} -g {rg}",
            checks=[
                self.check("length(@)", 1)
            ]
        )
        self.cmd(
            "logz rule update --monitor-name {name} -g {rg} \
            --rule-set-name {rule} --send-aad-logs true"
        )
        self.cmd(
            "logz rule show --monitor-name {name} -g {rg} \
            --rule-set-name {rule}",
            checks=[
                self.check("properties.logRules.sendAadLogs", True)
            ]
        )
        # delete tag rule
        self.cmd(
            "logz rule delete --monitor-name {name} -g {rg} \
            --rule-set-name {rule} --yes"
        )

    @live_only()
    @ResourceGroupPreparer(name_prefix="cli_test_logz_", location="westus2")
    def test_sub_account_crud(self):
        self.kwargs.update({
            "name1": "monitor1",
            "name2": "monitor2",
            "date": "2021-08-31T15:14:33+02:00",
            "plan": "100gb14days", "email": "ethanyang@microsoft.com"  # set valid plan-data and user-info
        })
        # create main account
        self.cmd(
            "logz monitor create -n {name1} -g {rg} \
            --plan-data billing-cycle=Monthly effective-date={date} plan-details={plan} usage-type=Committed \
            --user-info email-address={email} phone-number=01234567 first-name=Ethan last-name=Yang \
            --tags Environment=Dev",
            checks=[
                self.check("type", "microsoft.logz/monitors")
            ]
        )
        # create sub account
        self.cmd(
            "logz sub-account create -n {name2} -g {rg} --monitor-name {name1} \
            --plan-data billing-cycle=Monthly effective-date={date} plan-details={plan} usage-type=Committed \
            --user-info email-address={email} phone-number=01234567 first-name=Ethan last-name=Yang \
            --tags Environment=Dev",
            checks=[
                self.check("type", "microsoft.logz/monitors/accounts")
            ]
        )
        # validate list-related commands
        self.cmd(
            "logz sub-account list -g {rg} --monitor-name {name1}",
            checks=[
                self.check("length(@)", 1)
            ]
        )
        resource_list = self.cmd(
            "logz sub-account list-resource -n {name2} -g {rg} --monitor-name {name1}"
        ).get_output_in_json()
        assert len(resource_list) >= 0
        # validate sub account update
        self.cmd(
            "logz sub-account update -n {name2} -g {rg} --monitor-name {name1} \
            --monitoring-status Disabled --tags Environment=Dev"
        )
        self.cmd(
            "logz sub-account show -n {name2} -g {rg} --monitor-name {name1}",
            checks=[
                self.check("properties.monitoringStatus", "Disabled")
            ]
        )
        # delete sub account
        self.cmd("logz sub-account delete -n {name2} -g {rg} --monitor-name {name1} --yes")

    @live_only()
    @ResourceGroupPreparer(name_prefix="cli_test_logz_", location="westus2")
    def test_sub_account_vm(self):
        self.kwargs.update({
            "name1": "monitor1",
            "name2": "monitor2",
            "date": "2021-08-31T15:14:33+02:00",
            "plan": "100gb14days", "email": "ethanyang@microsoft.com",  # set valid plan-data and user-info
            "vm": "machine",
            "version": "1.0.*"
        })
        # create main account
        self.cmd(
            "logz monitor create -n {name1} -g {rg} \
            --plan-data billing-cycle=Monthly effective-date={date} plan-details={plan} usage-type=Committed \
            --user-info email-address={email} phone-number=01234567 first-name=Ethan last-name=Yang \
            --tags Environment=Dev",
            checks=[
                self.check("type", "microsoft.logz/monitors")
            ]
        )
        # create sub account
        self.cmd(
            "logz sub-account create -n {name2} -g {rg} --monitor-name {name1} \
            --plan-data billing-cycle=Monthly effective-date={date} plan-details={plan} usage-type=Committed \
            --user-info email-address={email} phone-number=01234567 first-name=Ethan last-name=Yang \
            --tags Environment=Dev",
            checks=[
                self.check("type", "microsoft.logz/monitors/accounts")
            ]
        )
        # create virtual machine
        self.cmd(
            "vm create -n {vm} -g {rg} \
            --os-disk-name os-disk --image OpenLogic:CentOS:7.5:latest \
            --generate-ssh-keys --public-ip-sku standard",
            checks=[
                self.check("powerState", "VM running")
            ]
        )
        self.kwargs["id"] = self.cmd(
            "vm show -n {vm} -g {rg}"
        ).get_output_in_json()["id"]
        # validate update and retrieval
        self.cmd(
            "logz sub-account update-vm -n {name2} -g {rg} --monitor-name {name1} \
            --state install \
            --vm-resource-ids id={id} agent-version={version}"
        )
        vm_obj = self.cmd(
            "logz sub-account list-vm -n {name2} -g {rg} --monitor-name {name1}"
        ).get_output_in_json()[0]
        assert vm_obj["id"].lower() == self.kwargs["id"].lower()
        self.cmd(
            "logz sub-account list-payload -n {name2} -g {rg} --monitor-name {name1}",
            checks=[
                self.check("region", "westus2")
            ]
        )

    @live_only()
    @ResourceGroupPreparer(name_prefix="cli_test_logz_", location="westus2")
    def test_sub_account_rule(self):
        self.kwargs.update({
            "name1": "monitor1",
            "name2": "monitor2",
            "date": "2021-08-31T15:14:33+02:00",
            "plan": "100gb14days", "email": "ethanyang@microsoft.com",  # set valid plan-data and user-info
            "rule": "default"
        })
        # create main account
        self.cmd(
            "logz monitor create -n {name1} -g {rg} \
            --plan-data billing-cycle=Monthly effective-date={date} plan-details={plan} usage-type=Committed \
            --user-info email-address={email} phone-number=01234567 first-name=Ethan last-name=Yang \
            --tags Environment=Dev",
            checks=[
                self.check("type", "microsoft.logz/monitors")
            ]
        )
        # create sub account
        self.cmd(
            "logz sub-account create -n {name2} -g {rg} --monitor-name {name1} \
            --plan-data billing-cycle=Monthly effective-date={date} plan-details={plan} usage-type=Committed \
            --user-info email-address={email} phone-number=01234567 first-name=Ethan last-name=Yang \
            --tags Environment=Dev",
            checks=[
                self.check("type", "microsoft.logz/monitors/accounts")
            ]
        )
        # create tag rule of sub account
        self.cmd(
            "logz sub-rule create --monitor-name {name1} -g {rg} --sub-account-name {name2} \
            --filtering-tag name=Environment action=Exclude value=Dev \
            --send-aad-logs false --send-activity-logs true --send-subscription-logs true \
            --rule-set-name {rule}",
            checks=[
                self.check("type", "microsoft.logz/monitors/accounts/tagrules")
            ]
        )
        # validate retrieval and update
        self.cmd(
            "logz sub-rule list --monitor-name {name1} -g {rg} --sub-account-name {name2}",
            checks=[
                self.check("length(@)", 1)
            ]
        )
        self.cmd(
            "logz sub-rule update --monitor-name {name1} -g {rg} --sub-account-name {name2} \
            --rule-set-name {rule} --send-aad-logs true"
        )
        self.cmd(
            "logz sub-rule show --monitor-name {name1} -g {rg} --sub-account-name {name2} \
            --rule-set-name {rule}",
            checks=[
                self.check("properties.logRules.sendAadLogs", True)
            ]
        )
        # delete tag rule of sub account
        self.cmd(
            "logz sub-rule delete --monitor-name {name1} -g {rg} --sub-account-name {name2} \
            --rule-set-name {rule} --yes"
        )

    @live_only()
    @ResourceGroupPreparer(name_prefix="cli_test_logz_", location="westus2")
    def test_single_sign_on(self):
        self.kwargs.update({
            "name": "monitor",
            "date": "2021-08-31T15:14:33+02:00",
            "plan": "100gb14days", "email": "ethanyang@microsoft.com",  # set valid plan-data and user-info
            "id": "4c232741-efe7-4310-91cf-30c4c1adeb29",               # set valid enterprise-app-id
            "config": "default"
        })
        # create main account
        self.cmd(
            "logz monitor create -n {name} -g {rg} \
            --plan-data billing-cycle=Monthly effective-date={date} plan-details={plan} usage-type=Committed \
            --user-info email-address={email} phone-number=01234567 first-name=Ethan last-name=Yang \
            --tags Environment=Dev",
            checks=[
                self.check("type", "microsoft.logz/monitors")
            ]
        )
        # create single sign-on
        self.cmd(
            "logz sso create --monitor-name {name} -g {rg} \
            --properties enterprise-app-id={id} single-sign-on-state=Enable \
            --configuration-name {config}",
            checks=[
                self.check("type", "microsoft.logz/monitors/singlesignonconfigurations")
            ]
        )
        # validate single sign-on retrieval
        self.cmd(
            "logz sso list --monitor-name {name} -g {rg}",
            checks=[
                self.check("length(@)", 1)
            ]
        )
        self.cmd(
            "logz sso show --monitor-name {name} -g {rg} --configuration-name {config}",
            checks=[
                self.check("properties.singleSignOnState", "Existing")
            ]
        )
