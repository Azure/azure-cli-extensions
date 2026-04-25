# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['cloud-health'] = """
type: group
short-summary: Manage CloudHealth resources (Microsoft.CloudHealth).
"""

helps['cloud-health health-model'] = """
type: group
short-summary: Manage health models.
"""

helps['cloud-health health-model create'] = """
type: command
short-summary: Create a health model.
examples:
  - name: Create a health model in a resource group.
    text: az cloud-health health-model create -g myRG -n myModel --location eastus
"""

helps['cloud-health health-model show'] = """
type: command
short-summary: Get a health model.
"""

helps['cloud-health health-model list'] = """
type: command
short-summary: List health models.
examples:
  - name: List health models in a resource group.
    text: az cloud-health health-model list -g myRG
  - name: List all health models in the subscription.
    text: az cloud-health health-model list
"""

helps['cloud-health health-model update'] = """
type: command
short-summary: Update a health model.
"""

helps['cloud-health health-model delete'] = """
type: command
short-summary: Delete a health model.
"""

helps['cloud-health entity'] = """
type: group
short-summary: Manage entities within a health model.
"""

helps['cloud-health entity create'] = """
type: command
short-summary: Create an entity in a health model.
examples:
  - name: Create an entity.
    text: az cloud-health entity create -g myRG --model myModel -n myEntity --display-name "My Entity"
"""

helps['cloud-health entity show'] = """
type: command
short-summary: Get an entity.
"""

helps['cloud-health entity list'] = """
type: command
short-summary: List entities in a health model.
"""

helps['cloud-health entity delete'] = """
type: command
short-summary: Delete an entity.
"""

helps['cloud-health entity get-history'] = """
type: command
short-summary: Get health state history of an entity.
"""

helps['cloud-health entity get-signal-history'] = """
type: command
short-summary: Get signal history for an entity.
"""

helps['cloud-health entity ingest'] = """
type: command
short-summary: Ingest an external health report for an entity signal.
examples:
  - name: Report healthy state for a signal.
    text: >
        az cloud-health entity ingest -g myRG --model myModel -n myEntity
        --signal-name mySig --health-state Healthy --value 99.5
"""

helps['cloud-health signal-definition'] = """
type: group
short-summary: Manage signal definitions within a health model.
"""

helps['cloud-health signal-definition create'] = """
type: command
short-summary: Create a signal definition.
long-summary: >
    Use --body to pass the full signal definition properties as JSON.
    The JSON structure varies by signal-kind (AzureResourceMetric, LogAnalyticsQuery, PrometheusMetricsQuery).
examples:
  - name: Create a PromQL signal definition.
    text: >
        az cloud-health signal-definition create -g myRG --model myModel -n mySig
        --body '{\"signalKind\":\"PrometheusMetricsQuery\",\"queryText\":\"up{job=\\\"api\\\"}\",
        \"evaluationRules\":{\"unhealthyRule\":{\"operator\":\"LessThan\",\"threshold\":1}}}'
"""

helps['cloud-health signal-definition show'] = """
type: command
short-summary: Get a signal definition.
"""

helps['cloud-health signal-definition list'] = """
type: command
short-summary: List signal definitions in a health model.
"""

helps['cloud-health signal-definition delete'] = """
type: command
short-summary: Delete a signal definition.
"""

helps['cloud-health relationship'] = """
type: group
short-summary: Manage relationships between entities in a health model.
"""

helps['cloud-health relationship create'] = """
type: command
short-summary: Create a relationship between two entities.
examples:
  - name: Create a parent-child relationship.
    text: >
        az cloud-health relationship create -g myRG --model myModel -n myRel
        --parent-entity-name parentEntity --child-entity-name childEntity
"""

helps['cloud-health relationship show'] = """
type: command
short-summary: Get a relationship.
"""

helps['cloud-health relationship list'] = """
type: command
short-summary: List relationships in a health model.
"""

helps['cloud-health relationship delete'] = """
type: command
short-summary: Delete a relationship.
"""

helps['cloud-health auth-setting'] = """
type: group
short-summary: Manage authentication settings for a health model.
"""

helps['cloud-health auth-setting create'] = """
type: command
short-summary: Create an authentication setting.
examples:
  - name: Create a managed-identity auth setting.
    text: >
        az cloud-health auth-setting create -g myRG --model myModel -n myAuth
        --authentication-kind ManagedIdentity --managed-identity-name SystemAssigned
"""

helps['cloud-health auth-setting show'] = """
type: command
short-summary: Get an authentication setting.
"""

helps['cloud-health auth-setting list'] = """
type: command
short-summary: List authentication settings in a health model.
"""

helps['cloud-health auth-setting delete'] = """
type: command
short-summary: Delete an authentication setting.
"""

helps['cloud-health discovery-rule'] = """
type: group
short-summary: Manage discovery rules for a health model.
"""

helps['cloud-health discovery-rule create'] = """
type: command
short-summary: Create a discovery rule.
examples:
  - name: Create a Resource Graph discovery rule.
    text: >
        az cloud-health discovery-rule create -g myRG --model myModel -n myRule
        --authentication-setting myAuth --discover-relationships Enabled
        --add-recommended-signals Enabled --specification-kind ResourceGraphQuery
        --resource-graph-query "resources | where type == 'microsoft.compute/virtualmachines'"
"""

helps['cloud-health discovery-rule show'] = """
type: command
short-summary: Get a discovery rule.
"""

helps['cloud-health discovery-rule list'] = """
type: command
short-summary: List discovery rules in a health model.
"""

helps['cloud-health discovery-rule delete'] = """
type: command
short-summary: Delete a discovery rule.
"""
