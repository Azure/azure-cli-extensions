Commands for working with Azure Application Insights
==============================================

# Basic Usage

Query a Application Insights application for data over the last 12 hours:
.. code:: 
    az monitor app-insights query --app b8317023-66e4-4edc-8a5b-7c002b22f92f --analytics-query "availabilityResults | summarize count() by bin(timestamp, 15m), success" -t PT12H

Query multiple workspaces at once:
.. code::
    az monitor app-insights query --app b8317023-66e4-4edc-8a5b-7c002b22f92f f5b6ed22-4942-41c4-becd-1943e5a1b71f --analytics-query "requests | summarize count() by toint(resultCode)"

Distributed trace preview
-------------------------

Requires Azure CLI 2.75.0 or later and the ``2026-09-03-preview`` Azure Monitor APIs
in the target subscription and region. All commands below ship in this extension:

.. code-block:: console

    az extension add --name application-insights --upgrade

Onboard a new or existing Application Insights component:

.. code-block:: console

    az monitor app-insights component create -g myRg -a myAi -l eastus --workspace <log-analytics-id> --enable-traces --trace-workspace <amw-id>
    az monitor app-insights component update -g myRg -a myAi --enable-traces --trace-workspace <amw-id>

``--workspace`` remains the Log Analytics workspace. ``--trace-workspace`` is an
Azure Monitor workspace name or resource ID. A name resolves in the component's
resource group and subscription; cross-subscription workspaces require a full ID.
Trace-enabled commands need read access to the component, applicable associations
and target container, plus write access for the resources they create.

Omit the workspace to keep existing routing. Only a component with no applicable
association gets a default workspace, following the managed Prometheus naming
convention:

.. code-block:: console

    az monitor app-insights component update -g myRg -a myAi --enable-traces

Onboard a resource group or subscription using its full resource ID. Future
components in that scope are covered as well:

.. code-block:: console

    az monitor trace-association create --resource-uri <scope-id> --azure-monitor-workspace <amw-id>

Onboarding creates the trace container first and waits for it before writing the
association. A new container defaults to 30 days retention, a 600-second trace
duration window and Enabled trace metrics. Trace-derived metrics are billed.
``--trace-retention-days`` and ``--trace-metrics`` apply only when onboarding
creates a container. An existing container is never modified by onboarding;
conflicting explicit settings are rejected.

The workspace owner can pre-provision a container or change its shared settings:

.. code-block:: console

    az monitor account trace-container create -g obsRg -w myAmw --retention-days 30 --trace-duration-window 600 --trace-metrics Enabled
    az monitor account trace-container update -g obsRg -w myAmw --retention-days 90
    az monitor account trace-container show -g obsRg -w myAmw
    az monitor account trace-container wait -g obsRg -w myAmw --created

Retention is 4-730 days and the duration window is 120-600 seconds. Omitted
settings are preserved on an existing container. Only container create/update
support ``--no-wait``. Include ``--subscription`` for a workspace outside the
active subscription.

Retarget a component's own association to another workspace:

.. code-block:: console

    az monitor app-insights component update -g myRg -a myAi --trace-workspace <other-amw-id>

Associations are additive: component, resource group and subscription
associations can all contribute destinations. Retargeting a component does not
remove inherited destinations. ``show`` reads only the association at the exact
scope; ``list`` includes its ancestors, but does not enumerate descendants:

.. code-block:: console

    az monitor trace-association show --resource-uri <scope-id>
    az monitor trace-association list --resource-uri <scope-id>

Offboard a component or a broader scope:

.. code-block:: console

    az monitor app-insights component update -g myRg -a myAi --disable-traces
    az monitor trace-association delete --resource-uri <scope-id>

These commands remove only the selected scope's association and report any
remaining inherited routing. They do not delete trace containers or stored data.
If provisioning fails partway through, completed resources are retained for
reuse and the error explains how to retry.
