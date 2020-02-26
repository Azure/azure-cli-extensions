# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['datafactory operations'] = """
    type: group
    short-summary: datafactory operations
"""

helps['datafactory operations list'] = """
    type: command
    short-summary: Lists the available Azure Data Factory API operations.
"""

helps['datafactory factories'] = """
    type: group
    short-summary: datafactory factories
"""

helps['datafactory factories list'] = """
    type: command
    short-summary: Lists factories under the specified subscription.
"""

helps['datafactory factories show'] = """
    type: command
    short-summary: Gets a factory.
"""

helps['datafactory factories create'] = """
    type: command
    short-summary: Creates or updates a factory.
"""

helps['datafactory factories update'] = """
    type: command
    short-summary: Updates a factory.
"""

helps['datafactory factories delete'] = """
    type: command
    short-summary: Deletes a factory.
"""

helps['datafactory factories configure-factory-repo'] = """
    type: command
    short-summary: Updates a factory's repo information.
"""

helps['datafactory factories get-data-plane-access'] = """
    type: command
    short-summary: Get Data Plane access.
"""

helps['datafactory factories get-git-hub-access-token'] = """
    type: command
    short-summary: Get GitHub Access Token.
"""

helps['datafactory exposure-control'] = """
    type: group
    short-summary: datafactory exposure-control
"""

helps['datafactory exposure-control get-feature-value-by-factory'] = """
    type: command
    short-summary: Get exposure control feature for specific factory.
"""

helps['datafactory exposure-control get-feature-value'] = """
    type: command
    short-summary: Get exposure control feature for specific location.
"""

helps['datafactory integration-runtimes'] = """
    type: group
    short-summary: datafactory integration-runtimes
"""

helps['datafactory integration-runtimes list'] = """
    type: command
    short-summary: Lists integration runtimes.
"""

helps['datafactory integration-runtimes show'] = """
    type: command
    short-summary: Gets an integration runtime.
"""

helps['datafactory integration-runtimes create'] = """
    type: command
    short-summary: Creates or updates an integration runtime.
"""

helps['datafactory integration-runtimes update'] = """
    type: command
    short-summary: Updates an integration runtime.
"""

helps['datafactory integration-runtimes delete'] = """
    type: command
    short-summary: Deletes an integration runtime.
"""

helps['datafactory integration-runtimes create-linked-integration-runtime'] = """
    type: command
    short-summary: Create a linked integration runtime entry in a shared integration runtime.
"""

helps['datafactory integration-runtimes regenerate-auth-key'] = """
    type: command
    short-summary: Regenerates the authentication key for an integration runtime.
"""

helps['datafactory integration-runtimes remove-links'] = """
    type: command
    short-summary: Remove all linked integration runtimes under specific data factory in a self-hosted integration runtime.
"""

helps['datafactory integration-runtimes get-status'] = """
    type: command
    short-summary: Gets detailed status information for an integration runtime.
"""

helps['datafactory integration-runtimes get-connection-info'] = """
    type: command
    short-summary: Gets the on-premises integration runtime connection information for encrypting the on-premises data source credentials.
"""

helps['datafactory integration-runtimes list-auth-keys'] = """
    type: command
    short-summary: Retrieves the authentication keys for an integration runtime.
"""

helps['datafactory integration-runtimes start'] = """
    type: command
    short-summary: Starts a ManagedReserved type integration runtime.
"""

helps['datafactory integration-runtimes stop'] = """
    type: command
    short-summary: Stops a ManagedReserved type integration runtime.
"""

helps['datafactory integration-runtimes sync-credentials'] = """
    type: command
    short-summary: Force the integration runtime to synchronize credentials across integration runtime nodes, and this will override the credentials across all worker nodes with those available on the dispatcher node. If you already have the latest credential backup file, you should manually import it (preferred) on any self-hosted integration runtime node than using this API directly.
"""

helps['datafactory integration-runtimes get-monitoring-data'] = """
    type: command
    short-summary: Get the integration runtime monitoring data, which includes the monitor data for all the nodes under this integration runtime.
"""

helps['datafactory integration-runtimes upgrade'] = """
    type: command
    short-summary: Upgrade self-hosted integration runtime to latest version if availability.
"""

helps['datafactory integration-runtime-object-metadata'] = """
    type: group
    short-summary: datafactory integration-runtime-object-metadata
"""

helps['datafactory integration-runtime-object-metadata get'] = """
    type: command
    short-summary: Get a SSIS integration runtime object metadata by specified path. The return is pageable metadata list.
"""

helps['datafactory integration-runtime-object-metadata refresh'] = """
    type: command
    short-summary: Refresh a SSIS integration runtime object metadata.
"""

helps['datafactory integration-runtime-nodes'] = """
    type: group
    short-summary: datafactory integration-runtime-nodes
"""

helps['datafactory integration-runtime-nodes show'] = """
    type: command
    short-summary: Gets a self-hosted integration runtime node.
"""

helps['datafactory integration-runtime-nodes update'] = """
    type: command
    short-summary: Updates a self-hosted integration runtime node.
"""

helps['datafactory integration-runtime-nodes delete'] = """
    type: command
    short-summary: Deletes a self-hosted integration runtime node.
"""

helps['datafactory integration-runtime-nodes get-ip-address'] = """
    type: command
    short-summary: Get the IP address of self-hosted integration runtime node.
"""

helps['datafactory linked-services'] = """
    type: group
    short-summary: datafactory linked-services
"""

helps['datafactory linked-services list'] = """
    type: command
    short-summary: Lists linked services.
"""

helps['datafactory linked-services show'] = """
    type: command
    short-summary: Gets a linked service.
"""

helps['datafactory linked-services create'] = """
    type: command
    short-summary: Creates or updates a linked service.
"""

helps['datafactory linked-services update'] = """
    type: command
    short-summary: Creates or updates a linked service.
"""

helps['datafactory linked-services delete'] = """
    type: command
    short-summary: Deletes a linked service.
"""

helps['datafactory datasets'] = """
    type: group
    short-summary: datafactory datasets
"""

helps['datafactory datasets list'] = """
    type: command
    short-summary: Lists datasets.
"""

helps['datafactory datasets show'] = """
    type: command
    short-summary: Gets a dataset.
"""

helps['datafactory datasets create'] = """
    type: command
    short-summary: Creates or updates a dataset.
"""

helps['datafactory datasets update'] = """
    type: command
    short-summary: Creates or updates a dataset.
"""

helps['datafactory datasets delete'] = """
    type: command
    short-summary: Deletes a dataset.
"""

helps['datafactory pipelines'] = """
    type: group
    short-summary: datafactory pipelines
"""

helps['datafactory pipelines list'] = """
    type: command
    short-summary: Lists pipelines.
"""

helps['datafactory pipelines show'] = """
    type: command
    short-summary: Gets a pipeline.
"""

helps['datafactory pipelines create'] = """
    type: command
    short-summary: Creates or updates a pipeline.
"""

helps['datafactory pipelines update'] = """
    type: command
    short-summary: Creates or updates a pipeline.
"""

helps['datafactory pipelines delete'] = """
    type: command
    short-summary: Deletes a pipeline.
"""

helps['datafactory pipelines create-run'] = """
    type: command
    short-summary: Creates a run of a pipeline.
"""

helps['datafactory pipeline-runs'] = """
    type: group
    short-summary: datafactory pipeline-runs
"""

helps['datafactory pipeline-runs show'] = """
    type: command
    short-summary: Get a pipeline run by its run ID.
"""

helps['datafactory pipeline-runs query-by-factory'] = """
    type: command
    short-summary: Query pipeline runs in the factory based on input filter conditions.
"""

helps['datafactory pipeline-runs cancel'] = """
    type: command
    short-summary: Cancel a pipeline run by its run ID.
"""

helps['datafactory activity-runs'] = """
    type: group
    short-summary: datafactory activity-runs
"""

helps['datafactory activity-runs query-by-pipeline-run'] = """
    type: command
    short-summary: Query activity runs based on input filter conditions.
"""

helps['datafactory triggers'] = """
    type: group
    short-summary: datafactory triggers
"""

helps['datafactory triggers list'] = """
    type: command
    short-summary: Lists triggers.
"""

helps['datafactory triggers show'] = """
    type: command
    short-summary: Gets a trigger.
"""

helps['datafactory triggers create'] = """
    type: command
    short-summary: Creates or updates a trigger.
"""

helps['datafactory triggers update'] = """
    type: command
    short-summary: Creates or updates a trigger.
"""

helps['datafactory triggers delete'] = """
    type: command
    short-summary: Deletes a trigger.
"""

helps['datafactory triggers query-by-factory'] = """
    type: command
    short-summary: Query triggers.
"""

helps['datafactory triggers subscribe-to-events'] = """
    type: command
    short-summary: Subscribe event trigger to events.
"""

helps['datafactory triggers get-event-subscription-status'] = """
    type: command
    short-summary: Get a trigger's event subscription status.
"""

helps['datafactory triggers unsubscribe-from-events'] = """
    type: command
    short-summary: Unsubscribe event trigger from events.
"""

helps['datafactory triggers start'] = """
    type: command
    short-summary: Starts a trigger.
"""

helps['datafactory triggers stop'] = """
    type: command
    short-summary: Stops a trigger.
"""

helps['datafactory trigger-runs'] = """
    type: group
    short-summary: datafactory trigger-runs
"""

helps['datafactory trigger-runs query-by-factory'] = """
    type: command
    short-summary: Query trigger runs.
"""

helps['datafactory trigger-runs rerun'] = """
    type: command
    short-summary: Rerun single trigger instance by runId.
"""

helps['datafactory data-flows'] = """
    type: group
    short-summary: datafactory data-flows
"""

helps['datafactory data-flows list'] = """
    type: command
    short-summary: Lists data flows.
"""

helps['datafactory data-flows show'] = """
    type: command
    short-summary: Gets a data flow.
"""

helps['datafactory data-flows create'] = """
    type: command
    short-summary: Creates or updates a data flow.
"""

helps['datafactory data-flows update'] = """
    type: command
    short-summary: Creates or updates a data flow.
"""

helps['datafactory data-flows delete'] = """
    type: command
    short-summary: Deletes a data flow.
"""

helps['datafactory data-flow-debug-session'] = """
    type: group
    short-summary: datafactory data-flow-debug-session
"""

helps['datafactory data-flow-debug-session create'] = """
    type: command
    short-summary: Creates a data flow debug session.
"""

helps['datafactory data-flow-debug-session delete'] = """
    type: command
    short-summary: Deletes a data flow debug session.
"""

helps['datafactory data-flow-debug-session add-data-flow'] = """
    type: command
    short-summary: Add a data flow into debug session.
"""

helps['datafactory data-flow-debug-session execute-command'] = """
    type: command
    short-summary: Execute a data flow debug command.
"""

helps['datafactory data-flow-debug-session query-by-factory'] = """
    type: command
    short-summary: Query all active data flow debug sessions.
"""
