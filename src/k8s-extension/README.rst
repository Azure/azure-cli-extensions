Microsoft Azure CLI 'k8s-extension' Extension
=============================================

This package is for the 'k8s-extension' extension.
i.e. 'az k8s-extension'

This package includes the 'extension-types' subgroup.
i.e. 'az k8s-extension extension-types'

How to use
----------

Install this extension using the below CLI command:

.. code-block:: bash

    az extension add --name k8s-extension

Included Features
-----------------

Chaos Studio (private preview)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Microsoft.ChaosStudio`` supports cluster-scoped AKS installations. Pass
``chaos-workspace-id=<workspace-resource-id>`` in ``--configuration-settings`` to
validate AKS Workload Identity, OIDC and Azure RBAC prerequisites and configure
the workspace identity role assignment and workspace connection. The workspace
must have a system-assigned identity or exactly one user-assigned identity.
The extension platform owns the subscriber identity and federation; the CLI
never creates, modifies or deletes them.

The partner targets the ``dev`` train, chart candidate ``0.1.6``, namespace
``chaos-infrastructure``, with automatic upgrades disabled. This source requires
the coordinated chart's ``subscriber.enabled`` switch and platform Workload
Identity support. Publication and extension-type registration of that chart
remain release dependencies; a version number alone doesn't establish support.
The CLI checks cluster/train registration before workspace or extension writes.
Older charts aren't supported by this staged flow. ``chaos-workspace-id`` is required.

One create command installs with the subscriber stopped, waits for completion,
reads ``aksAssignedIdentity.principalId`` and ``tenantId``, and reconciles the workspace
connection. A normal extension update then enables the subscriber with the
connection's returned ``dataPlaneEndpoint``, unchanged. No endpoint, region or
identity override is needed or accepted. ``--no-wait`` still waits for bootstrap;
it skips only the final activation wait.

Rerun the same create command after an interruption. The CLI observes an existing
pending operation rather than submitting a changed PUT, resumes a completed
bootstrap, and leaves an already active installation unchanged. Failures retain
the extension, connection and workspace permissions for diagnosis and retry.
Older manually provisioned identity installations aren't automatically migrated.

``chaos-existing-role-definition-id=<role-resource-id>`` explicitly reuses a
compatible custom role in the cluster subscription without modifying it.
Updates retain existing configuration and reconcile prerequisites. Changing the
workspace or release namespace requires deleting and recreating the extension.
Delete removes the matching owned connection before the owned workspace role
assignment; it preserves shared role definitions and resources that fail
ownership checks. Platform identity cleanup remains part of extension deletion.

Staged installation (pending chart release)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use a CLI build containing this partner customization and an existing workspace.
After the compatible chart is published and registered, use the following
configuration, replacing resource placeholders with your own values:

.. code-block:: bash

    az k8s-extension create \
        --resource-group groupName \
        --cluster-name clusterName \
        --cluster-type managedClusters \
        --name chaos-studio \
        --extension-type Microsoft.ChaosStudio \
        --scope cluster \
        --release-namespace chaos-infrastructure \
        --release-train dev \
        --version 0.1.6 \
        --configuration-settings \
            "chaos-workspace-id=/subscriptions/<subscription-id>/resourceGroups/<workspace-group>/providers/Microsoft.Chaos/workspaces/<workspace-name>" \
            "experiments.stressToolsImage=PLACEHOLDER.invalid/never-pulled:0"

The chart requires ``experiments.stressToolsImage``. This inert placeholder was
used only for pod-delete validation, which doesn't pull a stress-tools image.
It isn't usable for CPU or memory faults; those require a supported, pullable
stress-tools image. If reusing a compatible custom role, also include
``"chaos-existing-role-definition-id=/subscriptions/<subscription-id>/providers/Microsoft.Authorization/roleDefinitions/<role-definition-id>"``
in the configuration settings.

Historical evidence, not validation of staged installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installation and authorized data-plane polling succeeded with an earlier CLI
implementation and dev chart ``0.1.3``, which explicitly provisioned subscriber identity.
A five-minute pod-delete test passed in Litmus and the workload recovered to
2/2 replicas, but the ARM run failed/remained Stopping. This isn't a successful
ARM end-to-end result or proof of live update/delete behavior. The staged
platform-identity flow above has unit coverage, not live installation evidence.

Kubernetes Extensions
~~~~~~~~~~~~~~~~~~~~~

`More information <https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/extensions>`_

*Examples:*

Create a KubernetesExtension
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    az k8s-extension create \
        --resource-group groupName \
        --cluster-name clusterName \
        --cluster-type clusterType \
        --name extensionName \
        --extension-type extensionType \
        --scope scopeType \
        --release-train releaseTrain \
        --version versionNumber \
        --auto-upgrade-minor-version autoUpgrade \
        --configuration-settings exampleSetting=exampleValue \
        --plan-name examplePlanName \
        --plan-publisher examplePublisher \
        --plan-product exampleOfferId

Get a KubernetesExtension
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    az k8s-extension show \
        --resource-group groupName \
        --cluster-name clusterName \
        --cluster-type clusterType \
        --name extensionName

Delete a KubernetesExtension
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    az k8s-extension delete \
        --resource-group groupName \
        --cluster-name clusterName \
        --cluster-type clusterType \
        --name extensionName

List all KubernetesExtension of a cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    az k8s-extension list \
        --resource-group groupName \
        --cluster-name clusterName \
        --cluster-type clusterType

Update an existing KubernetesExtension of a cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    az k8s-extension update \
        --resource-group groupName \
        --cluster-name clusterName \
        --cluster-type clusterType \
        --name extensionName \
        --auto-upgrade true/false \
        --version extensionVersion \
        --release-train releaseTrain \
        --configuration-settings settingsKey=settingsValue \
        --configuration-protected-settings protectedSettingsKey=protectedValue \
        --configuration-settings-file configSettingsFile \
        --configuration-protected-settings-file protectedSettingsFile

List available extension types of a cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    az k8s-extension extension-types list \
        --resource-group groupName \
        --cluster-name clusterName \
        --cluster-type clusterType

List available extension types by location
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    az k8s-extension extension-types list-by-location \
        --location location

Show an extension types of a cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    az k8s-extension extension-types show \
        --resource-group groupName \
        --cluster-name clusterName \
        --cluster-type clusterType \
        --name extensionName

List all versions of an extension type by release train
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    az k8s-extension extension-types list-versions \
        --location location \
        --name extensionName
