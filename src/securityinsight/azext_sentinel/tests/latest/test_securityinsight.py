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
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class SentinelClientTest(ScenarioTest):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.cmd("extension add -n log-analytics-solution")

    @AllowLargeResponse(size_kb=2048)
    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_alert_rule_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "alert_rule_name": self.create_random_name("alert-rule-", 16),
            "template_id": "65360bb0-8986-4ade-a89d-af3cf44d28aa"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.cmd(
            "sentinel alert-rule create -n {alert_rule_name} -w {workspace_name} -g {rg} "
            "--ms-security-incident \"{{product-filter:'Microsoft Cloud App Security',display-name:testing,enabled:true}}\"",
            checks=[
                self.check("name", "{alert_rule_name}"),
                self.check("type", "Microsoft.SecurityInsights/alertRules")
            ]
        )

        self.cmd(
            "sentinel alert-rule list -w {workspace_name} -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].name", "{alert_rule_name}")
            ]
        )

        self.cmd("sentinel alert-rule update -n {alert_rule_name} -w {workspace_name} -g {rg} --ms-security-incident display-name=tested")
        self.cmd(
            "sentinel alert-rule show -n {alert_rule_name} -w {workspace_name} -g {rg}",
            checks=[
                self.check("name", "{alert_rule_name}"),
                self.check("displayName", "tested")
            ]
        )

        self.cmd("sentinel alert-rule delete -n {alert_rule_name} --workspace-name {workspace_name} -g {rg} --yes")

        self.cmd("sentinel alert-rule template list -w {workspace_name} -g {rg}")
        self.cmd(
            "sentinel alert-rule template show -n {template_id} -w {workspace_name} -g {rg}",
            checks=[
                self.check("name", "{template_id}"),
                self.check("kind", "Scheduled")
            ]
        )

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_automation_rule_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "rule_name": self.create_random_name("rule-", 12)
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.cmd(
            "sentinel automation-rule create -n {rule_name} -w {workspace_name} -g {rg} "
            "--display-name 'High severity incidents escalation' --order 1 "
            "--actions \"[{{order:1,modify-properties:{{action-configuration:{{severity:High}}}}}}]\" "
            "--triggering-logic \"{{is-enabled:true,triggers-on:Incidents,triggers-when:Created}}\"",
            checks=[
                self.check("name", "{rule_name}"),
                self.check("type", "Microsoft.SecurityInsights/AutomationRules")
            ]
        )

        self.cmd(
            "sentinel automation-rule list -w {workspace_name} -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{rule_name}")
            ]
        )

        self.cmd("sentinel automation-rule update -n {rule_name} -w {workspace_name} -g {rg} --display-name 'New name'")
        self.cmd(
            "sentinel automation-rule show -n {rule_name} -w {workspace_name} -g {rg}",
            checks=[
                self.check("name", "{rule_name}"),
                self.check("displayName", "New name"),
                self.check("type", "Microsoft.SecurityInsights/AutomationRules")
            ]
        )

        self.cmd("sentinel automation-rule delete -n {rule_name} -w {workspace_name} -g {rg} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_bookmark_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "bookmark_id": "73e01a99-5cd7-4139-a149-9f2736ff2ab5",
            "query": "SecurityEvent | where TimeGenerated > ago(1d) and TimeGenerated < ago(2d)",
            "expand_id": "27f76e63-c41b-480f-bb18-12ad2e011d49",
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.cmd(
            "sentinel bookmark create -n {bookmark_id} -w {workspace_name} -g {rg} "
            "--query-content '{query}' --query-result 'Security Event query result' "
            "--display-name 'My bookmark' --notes 'Found a suspicious activity' "
            "--entity-mappings \"[{{entity-type:Account,field-mappings:[{{identifier:Fullname,value:johndoe@microsoft.com}}]}}]\" "
            "--tactics \"[Execution]\" "
            "--techniques \"[T1609]\" "
            "--labels \"[Tag1,Tag2]\"",
            checks=[
                self.check("name", "{bookmark_id}"),
                self.check("query", "{query}")
            ]
        )

        self.cmd(
            "sentinel bookmark list -w {workspace_name} -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{bookmark_id}")
            ]
        )

        self.cmd(
            "sentinel bookmark show -n {bookmark_id} -w {workspace_name} -g {rg}",
            checks=[
                self.check("name", "{bookmark_id}"),
                self.check("displayName", "My bookmark")
            ]
        )

        self.cmd("sentinel bookmark delete -n {bookmark_id} -w {workspace_name} -g {rg} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_incident_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "incident_id": "73e01a99-5cd7-4139-a149-9f2736ff2ab5"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.cmd(
            "sentinel incident create -n {incident_id} -w {workspace_name} -g {rg} "
            "--classification FalsePositive --classification-reason IncorrectAlertLogic --classification-comment 'Not a malicious activity' "
            "--first-activity-time-utc 2019-01-01T13:00:30Z --last-activity-time-utc 2019-01-01T13:05:30Z "
            "--severity High --status Closed --title 'My incident' --description 'This is a demo incident' "
            "--owner \"{{object-id:2046feea-040d-4a46-9e2b-91c2941bfa70}}\"",
            checks=[
                self.check("name", "{incident_id}"),
                self.check("classification", "FalsePositive")
            ]
        )

        self.cmd(
            "sentinel incident list -w {workspace_name} -g {rg} --orderby 'properties/createdTimeUtc desc' --top 1",
            checks=[
                self.check("length(@)", "1"),
                self.check("[0].name", "{incident_id}")
            ]
        )

        self.cmd(
            "sentinel incident show -n {incident_id} -w {workspace_name} -g {rg}",
            checks=[
                self.check("name", "{incident_id}"),
                self.check("classification", "FalsePositive")
            ]
        )

        self.cmd("sentinel incident delete -n {incident_id} -w {workspace_name} -g {rg} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_incident_comment_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "incident_id": "73e01a99-5cd7-4139-a149-9f2736ff2ab5",
            "comment_id": "4bb36b7b-26ff-4d1c-9cbe-0d8ab3da0014"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")
        self.cmd(
            "sentinel incident create -n {incident_id} -w {workspace_name} -g {rg} "
            "--classification FalsePositive --classification-reason IncorrectAlertLogic --classification-comment 'Not a malicious activity' "
            "--first-activity-time-utc 2019-01-01T13:00:30Z --last-activity-time-utc 2019-01-01T13:05:30Z "
            "--severity High --status Closed --title 'My incident' --description 'This is a demo incident' "
            "--owner \"{{object-id:2046feea-040d-4a46-9e2b-91c2941bfa70}}\""
        )

        self.cmd(
            "sentinel incident comment create -n {comment_id} -w {workspace_name} -g {rg} --incident-id {incident_id} --message 'Some message'",
            checks=[
                self.check("name", "{comment_id}"),
                self.check("message", "Some message")
            ]
        )

        self.cmd(
            "sentinel incident comment list -w {workspace_name} -g {rg} --incident-id {incident_id}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{comment_id}")
            ]
        )

        self.cmd("sentinel incident comment update -n {comment_id} -w {workspace_name} -g {rg} --incident-id {incident_id} --message 'Some messages'")
        self.cmd(
            "sentinel incident comment show -n {comment_id} -w {workspace_name} -g {rg} --incident-id {incident_id}",
            checks=[
                self.check("name", "{comment_id}"),
                self.check("message", "Some messages")
            ]
        )

        self.cmd("sentinel incident comment delete -n {comment_id} -w {workspace_name} -g {rg} --incident-id {incident_id} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_bookmark_relation_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "relation_name": self.create_random_name("relation-", 16),
            "bookmark_id": "2216d0e1-91e3-4902-89fd-d2df8c535096",
            "incident_id": "afbd324f-6c48-459c-8710-8d1e1cd03812",
            "query": "SecurityEvent | where TimeGenerated > ago(1d) and TimeGenerated < ago(2d)"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")
        self.cmd(
            "sentinel bookmark create -n {bookmark_id} -w {workspace_name} -g {rg} "
            "--query-content '{query}' --query-result 'Security Event query result' "
            "--display-name 'My bookmark' --notes 'Found a suspicious activity' "
            "--entity-mappings \"[{{entity-type:Account,field-mappings:[{{identifier:Fullname,value:johndoe@microsoft.com}}]}}]\" "
            "--tactics \"[Execution]\" "
            "--techniques \"[T1609]\" "
            "--labels \"[Tag1,Tag2]\""
        )
        self.kwargs["resource_id"] = self.cmd(
            "sentinel incident create -n {incident_id} -w {workspace_name} -g {rg} "
            "--classification FalsePositive --classification-reason IncorrectAlertLogic --classification-comment 'Not a malicious activity' "
            "--first-activity-time-utc 2019-01-01T13:00:30Z --last-activity-time-utc 2019-01-01T13:05:30Z "
            "--severity High --status Closed --title 'My incident' --description 'This is a demo incident' "
            "--owner \"{{object-id:2046feea-040d-4a46-9e2b-91c2941bfa70}}\""
        ).get_output_in_json()["id"]

        self.cmd(
            "sentinel bookmark relation create -n {relation_name} -w {workspace_name} -g {rg} --bookmark-id {bookmark_id} --related-resource-id {resource_id}",
            checks=[
                self.check("name", "{relation_name}"),
                self.check("type", "Microsoft.SecurityInsights/Bookmarks/relations")
            ]
        )

        self.cmd(
            "sentinel bookmark relation list -w {workspace_name} -g {rg} --bookmark-id {bookmark_id}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{relation_name}")
            ]
        )

        self.cmd(
            "sentinel bookmark relation show -n {relation_name} -w {workspace_name} -g {rg} --bookmark-id {bookmark_id}",
            checks=[
                self.check("name", "{relation_name}"),
                self.check("type", "Microsoft.SecurityInsights/Bookmarks/relations")
            ]
        )

        self.cmd("sentinel bookmark relation delete -n {relation_name} -w {workspace_name} -g {rg} --bookmark-id {bookmark_id} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_incident_relation_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "relation_name": self.create_random_name("relation-", 16),
            "bookmark_id": "2216d0e1-91e3-4902-89fd-d2df8c535096",
            "incident_id": "afbd324f-6c48-459c-8710-8d1e1cd03812",
            "query": "SecurityEvent | where TimeGenerated > ago(1d) and TimeGenerated < ago(2d)"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")
        self.cmd(
            "sentinel incident create -n {incident_id} -w {workspace_name} -g {rg} "
            "--classification FalsePositive --classification-reason IncorrectAlertLogic --classification-comment 'Not a malicious activity' "
            "--first-activity-time-utc 2019-01-01T13:00:30Z --last-activity-time-utc 2019-01-01T13:05:30Z "
            "--severity High --status Closed --title 'My incident' --description 'This is a demo incident' "
            "--owner \"{{object-id:2046feea-040d-4a46-9e2b-91c2941bfa70}}\""
        )
        self.kwargs["resource_id"] = self.cmd(
            "sentinel bookmark create -n {bookmark_id} -w {workspace_name} -g {rg} "
            "--query-content '{query}' --query-result 'Security Event query result' "
            "--display-name 'My bookmark' --notes 'Found a suspicious activity' "
            "--entity-mappings \"[{{entity-type:Account,field-mappings:[{{identifier:Fullname,value:johndoe@microsoft.com}}]}}]\" "
            "--tactics \"[Execution]\" "
            "--techniques \"[T1609]\" "
            "--labels \"[Tag1,Tag2]\""
        ).get_output_in_json()["id"]

        self.cmd(
            "sentinel incident relation create -n {relation_name} -w {workspace_name} -g {rg} --incident-id {incident_id} --related-resource-id {resource_id}",
            checks=[
                self.check("name", "{relation_name}"),
                self.check("type", "Microsoft.SecurityInsights/Incidents/relations")
            ]
        )

        self.cmd(
            "sentinel incident relation list -w {workspace_name} -g {rg} --incident-id {incident_id}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{relation_name}")
            ]
        )

        self.cmd(
            "sentinel incident relation show -n {relation_name} -w {workspace_name} -g {rg} --incident-id {incident_id}",
            checks=[
                self.check("name", "{relation_name}"),
                self.check("type", "Microsoft.SecurityInsights/Incidents/relations")
            ]
        )

        self.cmd("sentinel incident relation delete -n {relation_name} -w {workspace_name} -g {rg} --incident-id {incident_id} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_enrichment_crud(self):
        self.kwargs.update({
            "domain": "microsoft.com",
            "ip_address": "1.2.3.4"
        })

        self.cmd(
            "sentinel enrichment domain-whois show -g {rg} --domain {domain}",
            checks=[
                self.check("domain", "{domain}")
            ]
        )

        self.cmd(
            "sentinel enrichment ip-geodata show -g {rg} --ip-address {ip_address}",
            checks=[
                self.check("ipAddr", "{ip_address}")
            ]
        )

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_metadata_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "alert_rule_name": self.create_random_name("alert-rule-", 16),
            "metadata_name": self.create_random_name("metadata-", 16),
            "content_id": "c00ee137-7475-47c8-9cce-ec6f0f1bedd0"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")
        self.kwargs["parent_id"] = self.cmd(
            "sentinel alert-rule create -n {alert_rule_name} -w {workspace_name} -g {rg} "
            "--ms-security-incident \"{{product-filter:'Microsoft Cloud App Security',display-name:testing,enabled:true}}\""
        ).get_output_in_json()["id"]

        self.cmd(
            "sentinel metadata create -n {metadata_name} -w {workspace_name} -g {rg} "
            "--content-id {content_id} --parent-id {parent_id} --kind AnalyticsRule",
            checks=[
                self.check("name", "{metadata_name}"),
                self.check("contentId", "{content_id}")
            ]
        )

        self.cmd(
            "sentinel metadata list -w {workspace_name} -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{metadata_name}")
            ]
        )

        self.cmd("sentinel metadata update -n {metadata_name} -w {workspace_name} -g {rg} --author \"{{name:cli,email:cli@microsoft.com}}\"")
        self.cmd(
            "sentinel metadata show -n {metadata_name} -w {workspace_name} -g {rg}",
            checks=[
                self.check("name", "{metadata_name}"),
                self.check("author.name", "cli"),
                self.check("author.email", "cli@microsoft.com")
            ]
        )

        self.cmd("sentinel metadata delete -n {metadata_name} -w {workspace_name} -g {rg} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_onboarding_state_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16)
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.cmd(
            "sentinel onboarding-state create -n default -w {workspace_name} -g {rg} --customer-managed-key false",
            checks=[
                self.check("name", "default"),
                self.check("type", "Microsoft.SecurityInsights/onboardingStates")
            ]
        )

        self.cmd(
            "sentinel onboarding-state list -w {workspace_name} -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("value[0].name", "default")
            ]
        )

        self.cmd(
            "sentinel onboarding-state show -n default -w {workspace_name} -g {rg}",
            checks=[
                self.check("name", "default"),
                self.check("type", "Microsoft.SecurityInsights/onboardingStates")
            ]
        )

        self.cmd("sentinel onboarding-state delete -n default -w {workspace_name} -g {rg} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_threat_indicator_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "reference": "contoso@contoso.com"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.kwargs["indicator_name"] = self.cmd(
            "sentinel threat-indicator create -w {workspace_name} -g {rg} "
            "--source 'Microsoft Sentinel' --display-name 'new schema' --confidence 78 --created-by-ref {reference} "
            "--modified '' --pattern '[url:value = 'https://www.contoso.com']' --pattern-type url --revoked false "
            "--valid-from 2022-06-15T17:44:00.114052Z --valid-until '' --description 'debugging indicators' "
            "--threat-tags \"['new schema']\" "
            "--threat-types \"[compromised]\" "
            "--external-references \"[]\"",
            checks=[
                self.check("createdByRef", "{reference}"),
                self.check("type", "Microsoft.SecurityInsights/threatIntelligence")
            ]
        ).get_output_in_json()["name"]

        self.cmd(
            "sentinel threat-indicator list -w {workspace_name} -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].createdByRef", "{reference}")
            ]
        )

        self.cmd(
            "sentinel threat-indicator show -n {indicator_name} -w {workspace_name} -g {rg}",
            checks=[
                self.check("name", "{indicator_name}"),
                self.check("confidence", "78")
            ]
        )

        self.cmd("sentinel threat-indicator delete -n {indicator_name} -w {workspace_name} -g {rg} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_watchlist_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "watchlist_name": self.create_random_name("watchlist-", 16)
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.cmd(
            "sentinel watchlist create -n {watchlist_name} -w {workspace_name} -g {rg} "
            "--description 'Watchlist from CSV content' --display-name 'High Value Assets Watchlist' "
            "--provider Microsoft --items-search-key header1",
            checks=[
                self.check("name", "{watchlist_name}"),
                self.check("type", "Microsoft.SecurityInsights/Watchlists")
            ]
        )

        self.cmd(
            "sentinel watchlist list -w {workspace_name} -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{watchlist_name}")
            ]
        )

        self.cmd("sentinel watchlist update -n {watchlist_name} -w {workspace_name} -g {rg} --display-name 'New name'")
        self.cmd(
            "sentinel watchlist show -n {watchlist_name} -w {workspace_name} -g {rg}",
            checks=[
                self.check("name", "{watchlist_name}"),
                self.check("displayName", "New name"),
                self.check("type", "Microsoft.SecurityInsights/Watchlists")
            ]
        )

        self.cmd("sentinel watchlist delete -n {watchlist_name} -w {workspace_name} -g {rg} --yes")
