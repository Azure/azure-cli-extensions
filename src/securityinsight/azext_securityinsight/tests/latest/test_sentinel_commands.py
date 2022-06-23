# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import json
from azure.cli.testsdk import (
    ResourceGroupPreparer,
    ScenarioTest
)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class SentinelClientTest(ScenarioTest):
    def __init__(self, method_name):
        super().__init__(method_name)

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
            "--ms-security-incident "
            "\"{{product-filter:'Microsoft Cloud App Security',display-name:testing,enabled:true}}\"",
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
    def test_sentinel_analytics_setting_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "setting_name": "f209187f-1d17-4431-94af-c141bf5f23db",
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        settings_props = {
            "etag": "'260090e2-0000-0d00-0000-5d6fb8670000'",
            "kind": "Anomaly",
            "properties": {
                "description": "When account logs from a source region that has rarely been logged in from during the last 14 days, an anomaly is triggered.",
                "anomalySettingsVersion": 0,
                "anomalyVersion": "1.0.5",
                "customizableObservations": {
                    "multiSelectObservations": None,
                    "prioritizeExcludeObservat": None,
                    "singleSelectObservations": [{
                        "name": "Device vendor",
                        "description": "Choose device vendor of network connection logs from CommonSecurityLog",
                        "rerun": "RerunAlways",
                        "sequenceNumber": 1,
                        "supportedValues": ["Palo Alto Networks", "Fortinet", "Check Point"],
                        "supportedValuesKql": None,
                        "value": ["Palo Alto Networks"],
                        "valuesKql": None
                    }],
                    "singleValueObservations": None,
                    "thresholdObservations": [
                        {
                            "name": "Daily data transfer threshold in MB",
                            "description": "Suppress anomalies when daily data transfered (in MB) per hour is less than the chosen value",
                            "maximum": "100",
                            "minimum": "1",
                            "rerun": "RerunAlways",
                            "sequenceNumber": 1,
                            "value": "25",
                        },
                        {
                            "name": "Number of standard deviations",
                            "description": "Triggers anomalies when number of standard deviations is greater than the chosen value",
                            "maximum": "10",
                            "minimum": "2",
                            "rerun": "RerunAlways",
                            "sequenceNumber": 2,
                            "value": "3"
                        }
                    ]
                },
                "displayName": "Login from unusual region",
                "enabled": True,
                "frequency": "PT1H",
                "isDefaultSettings": True,
                "requiredDataConnectors": [{
                    "connectorId": "AWS",
                    "dataTypes": ["AWSCloudTrail"]
                }],
                "settingsDefinitionId": "f209187f-1d17-4431-94af-c141bf5f23db",
                "settingsStatus": "Production",
                "tactics": ["Exfiltration", "CommandAndControl"],
                "techniques": ["T1037", "T1021"]
            }
        }
        self.kwargs["settings"] = json.dumps(settings_props)

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_bookmark_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "bookmark_id": "73e01a99-5cd7-4139-a149-9f2736ff2ab5",
            "query_content": "SecurityEvent | where TimeGenerated > ago(1d) and TimeGenerated < ago(2d)",
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        entity_mappings_props = [{
            "entity_type": "Account",
            "fieldMappings": [{
                "identifier": "Fullname",
                "value": "johndoe@microsoft.com"
            }]
        }]
        self.kwargs["entity_mappings"] = json.dumps(entity_mappings_props)
        self.cmd(
            "sentinel bookmark create -g {rg} --bookmark-id {bookmark_id} --workspace-name {workspace_name} "
            "--query-content '{query_content}' --query-result 'Security Event query result' "
            "--etag '0300bf09-0000-0000-0000-5c37296e0000' --display-name 'My Bookmark' --entity-mappings '{entity_mappings}' "
            "--labels Tag1 Tag2 --notes 'Found a suspicious activity' --tactics Execution --techniques T1609",
            checks=[
                self.check("name", "{bookmark_id}"),
                self.check("query", "{query_content}")
            ]
        )

        self.cmd(
            "sentinel bookmark list -g {rg} --workspace-name {workspace_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{bookmark_id}")
            ]
        )

        self.cmd(
            "sentinel bookmark show -g {rg} --bookmark-id {bookmark_id} --workspace-name {workspace_name}",
            checks=[
                self.check("name", "{bookmark_id}"),
                self.check("query", "{query_content}")
            ]
        )

        self.cmd("sentinel bookmark delete -g {rg} --bookmark-id {bookmark_id} --workspace-name {workspace_name} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_incident_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "incident_id": "73e01a99-5cd7-4139-a149-9f2736ff2ab5",
            "comment_id": "4bb36b7b-26ff-4d1c-9cbe-0d8ab3da0014"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.cmd(
            "sentinel incident create -g {rg} --incident-id {incident_id} --workspace-name {workspace_name} "
            "--classification FalsePositive --classification-reason IncorrectAlertLogic --classification-comment 'Not a malicious activity' "
            "--owner object-id=2046feea-040d-4a46-9e2b-91c2941bfa70 --first-activity-time-utc 2019-01-01T13:00:30Z --last-activity-time-utc 2019-01-01T13:05:30Z "
            "--etag '0300bf09-0000-0000-0000-5c37296e0000' --severity High --status Closed --title 'My incident' --description 'This is a demo incident'",
            checks=[
                self.check("name", "{incident_id}"),
                self.check("classification", "FalsePositive")
            ]
        )

        self.cmd(
            "sentinel incident list -g {rg} --orderby 'properties/createdTimeUtc desc' --top 1 --workspace-name {workspace_name}",
            checks=[
                self.check("length(@)", "1"),
                self.check("[0].name", "{incident_id}")
            ]
        )

        self.cmd(
            "sentinel incident show -g {rg} --incident-id {incident_id} --workspace-name {workspace_name}",
            checks=[
                self.check("name", "{incident_id}"),
                self.check("classification", "FalsePositive")
            ]
        )

        self.cmd(
            "sentinel incident comment create -g {rg} --incident-comment-id {comment_id} --message 'Some message' --incident-id {incident_id} --workspace-name {workspace_name}",
            checks=[
                self.check("name", "{comment_id}"),
                self.check("message", "Some message")
            ]
        )

        self.cmd(
            "sentinel incident comment list -g {rg} --incident-id {incident_id} --workspace-name {workspace_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{comment_id}")
            ]
        )

        self.cmd(
            "sentinel incident comment show -g {rg} --incident-comment-id {comment_id} --incident-id {incident_id} --workspace-name {workspace_name}",
            checks=[
                self.check("name", "{comment_id}"),
                self.check("message", "Some message")
            ]
        )

        self.cmd("sentinel incident delete -g {rg} --incident-id {incident_id} --workspace-name {workspace_name} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_automation_rule_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "rule_id": "73e01a99-5cd7-4139-a149-9f2736ff2ab5"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.cmd(
            "sentinel automation-rule create -g {rg} --automation-rule-id {rule_id} --workspace-name {workspace_name} "
            "--actions action-type=ModifyProperties order=1 severity=High --is-enabled true --triggers-when Created "
            "--etag 0300bf09-0000-0000-0000-5c37296e0000 --order 1 --display-name 'High severity incidents escalation'",
            checks=[
                self.check("name", "{rule_id}"),
                self.check("type", "Microsoft.SecurityInsights/AutomationRules")
            ]
        )

        self.cmd(
            "sentinel automation-rule list -g {rg} --workspace-name {workspace_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{rule_id}")
            ]
        )

        self.cmd(
            "sentinel automation-rule show -g {rg} --automation-rule-id {rule_id} --workspace-name {workspace_name}",
            checks=[
                self.check("name", "{rule_id}"),
                self.check("type", "Microsoft.SecurityInsights/AutomationRules")
            ]
        )

        self.cmd("sentinel automation-rule delete -g {rg} --automation-rule-id {rule_id} --workspace-name {workspace_name} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_data_connector_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "connector_id": "73e01a99-5cd7-4139-a149-9f2736ff2ab5"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        data_connector_props = {
            "kind": "ThreatIntelligence",
            "properties": {
                "dataTypes": {
                    "indicators": {
                        "state": "Enabled"
                    }
                },
                "tenantId": "54826b22-38d6-4fb2-bad9-b7b93a3e9c5a",
                "tipLookbackPeriod": "2020-01-01T13:00:30.123Z"
            }
        }
        self.kwargs["data_connector"] = json.dumps(data_connector_props)

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_domain_whois_crud(self):
        self.kwargs.update({
            "domain": "microsoft.com",
        })

        self.cmd(
            "sentinel domain-whois show -g {rg} --domain {domain}",
            checks=[
                self.check("domain", "{domain}")
            ]
        )

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_ip_geodata_crud(self):
        self.kwargs.update({
            "ip_address": "1.2.3.4"
        })

        self.cmd(
            "sentinel ip-geodata show -g {rg} --ip-address {ip_address}",
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

        alert_rule_props = {
            "etag": "260097e0-0000-0d00-0000-5d6fa88f0000",
            "kind": "MicrosoftSecurityIncidentCreation",
            "properties": {
                "displayName": "testing displayname",
                "enabled": True,
                "productFilter": "Microsoft Cloud App Security"
            }
        }
        self.kwargs["alert_rule"] = json.dumps(alert_rule_props)
        self.kwargs["parent_id"] = self.cmd("sentinel alert-rule create -g {rg} --alert-rule '{alert_rule}' --rule-id {alert_rule_name} --workspace-name {workspace_name}").get_output_in_json()["id"]
        self.cmd(
            "sentinel metadata create -n {metadata_name} -g {rg} --content-id {content_id} --workspace-name {workspace_name} "
            "--kind AnalyticsRule --parent-id {parent_id}",
            checks=[
                self.check("name", "{metadata_name}"),
                self.check("contentId", "{content_id}")
            ]
        )

        self.cmd(
            "sentinel metadata list -g {rg} --workspace-name {workspace_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{metadata_name}")
            ]
        )

        self.cmd("sentinel metadata update -n {metadata_name} -g {rg} --workspace-name {workspace_name} --author name=cli email=cli@microsoft.com")
        self.cmd(
            "sentinel metadata show -n {metadata_name} -g {rg} --workspace-name {workspace_name}",
            checks=[
                self.check("name", "{metadata_name}"),
                self.check("author.name", "cli"),
                self.check("author.email", "cli@microsoft.com")
            ]
        )

        self.cmd("sentinel metadata delete -n {metadata_name} -g {rg} --workspace-name {workspace_name} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_onboarding_state_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16)
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.cmd(
            "sentinel onboarding-state create -n default -g {rg} --workspace-name {workspace_name} --customer-managed-key false",
            checks=[
                self.check("name", "default"),
                self.check("type", "Microsoft.SecurityInsights/onboardingStates")
            ]
        )

        self.cmd(
            "sentinel onboarding-state list -g {rg} --workspace-name {workspace_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("value[0].name", "default")
            ]
        )

        self.cmd(
            "sentinel onboarding-state show -n default -g {rg} --workspace-name {workspace_name}",
            checks=[
                self.check("name", "default"),
                self.check("type", "Microsoft.SecurityInsights/onboardingStates")
            ]
        )

        self.cmd("sentinel onboarding-state delete -n default -g {rg} --workspace-name {workspace_name} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_sentinel_", location="eastus2")
    def test_sentinel_threat_indicator_crud(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("workspace-", 16),
            "reference": "contoso@contoso.com"
        })

        self.cmd("monitor log-analytics workspace create -n {workspace_name} -g {rg}")
        self.cmd("monitor log-analytics solution create -t SecurityInsights -w {workspace_name} -g {rg}")

        self.kwargs["indicator_id"] = self.cmd(
            "sentinel threat-indicator create -g {rg} --workspace-name {workspace_name} "
            "--source 'Microsoft Sentinel' --threat-tags 'new schema' --threat-types 'compromised' "
            "--display-name 'new schema' --confidence 78 --created-by-ref {reference} --external-references [] "
            "--modified '' --pattern '[url:value = 'https://www.contoso.com']' --pattern-type url --revoked false "
            "--valid-from 2021-09-15T17:44:00.114052Z --valid-until '' --description 'debugging indicators'",
            checks=[
                self.check("createdByRef", "{reference}"),
                self.check("type", "Microsoft.SecurityInsights/threatIntelligence")
            ]
        ).get_output_in_json()["name"]

        self.cmd(
            "sentinel threat-indicator list -g {rg} --workspace-name {workspace_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].createdByRef", "{reference}")
            ]
        )

        self.cmd(
            "sentinel threat-indicator show --name {indicator_id} -g {rg} --workspace-name {workspace_name}",
            checks=[
                self.check("name", "{indicator_id}"),
                self.check("confidence", 78)
            ]
        )

        self.cmd("sentinel threat-indicator delete -g {rg} --name {indicator_id} --workspace-name {workspace_name} --yes")
