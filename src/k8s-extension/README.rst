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

The partner installs into namespace ``chaos-infrastructure`` with automatic
upgrades disabled, and leaves the release train to the extension service default
(``stable``) unless ``--release-train`` is passed. ``--version`` is passed through
to the extension service; when it's omitted on create, the CLI asks the service
for the latest version registered for the cluster and release train. The CLI checks cluster/train registration
before workspace or extension writes, and update keeps the installed version
unless ``--version`` is passed. The chart must support the ``subscriber.enabled``
switch and platform Workload Identity. ``chaos-workspace-id`` is required.

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

Create and update assign the built-in ``Chaos Kubernetes Extension Operator``
role (``681440c1-3630-4424-a530-0305ac721cfd``) to the workspace identity at cluster
scope. They don't read, create or validate custom role definitions, and the
installer no longer needs role-definition write permission.
The built-in grants extension, managed-cluster and Deployment Safeguards reads,
plus ServiceAccount impersonation and pod reads.

Existing installations get a separate deterministic built-in assignment, including
when the same create command is rerun on an active installation. The CLI keeps its
owned legacy assignment until uninstall so migration doesn't remove working
authorization while the new assignment propagates. The old
``chaos-existing-role-definition-id`` setting no longer selects the assigned role;
its persisted value only identifies an older owned assignment for cleanup.
The value is validated before installation or updates and is immutable once
installed; updates cannot add it or replace the original cleanup ID. Invalid
persisted cleanup metadata stops uninstall before the connection or owned role
assignments are deleted. The CLI does not guess the original role; that state
requires owner-led repair from the installation record.
An active create rerun that waits for a pending operation reconciles the built-in
assignment after successful completion too; pending ``--no-wait`` calls and failed
operations do not add an assignment.
Updates retain existing configuration and reconcile prerequisites. Changing the
workspace or release namespace requires deleting and recreating the extension.
Delete removes the matching owned connection before both deterministic owned
workspace role assignments (built-in and legacy); it preserves all role definitions and resources that fail
ownership checks. Platform identity cleanup remains part of extension deletion.

Namespace ownership and retention
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before the first bootstrap, the CLI reads the release namespace from the target
AKS cluster using user credentials, not the current kube context. It passes
``namespaceLifecycle.createdByInstall=true`` only if that read confirms absence;
otherwise it passes ``false``. Resumed installs keep the persisted assertion,
and updates can't override it. The compatible chart writes
``chaosstudio.microsoft.com/namespace-created-by=<release-namespace>/<release-name>``
only on initial install. Older or pre-existing namespaces aren't adopted.

A synchronous delete confirms the ARM extension deletion operation and reports
that the release namespace and any remaining Kubernetes resources are retained.
The CLI does not inventory namespace contents, delete namespaces or wait for
namespace finalization during uninstall. ``--no-wait`` and ``--force`` do not
perform namespace cleanup either.

An installation marker proves creation ownership, not that every namespace
writer is stopped. An inventory followed by namespace DELETE cannot preserve a
customer object created between those operations, and namespace resourceVersion
does not protect child objects. This version therefore does not attempt automatic
namespace removal. It adds no admission drain, cleanup checkpoint or broader
cleanup authority.

An initial ARM 404 remains an idempotent result for the absent extension. It is
not evidence that the namespace is absent and does not trigger Kubernetes cleanup.
After confirmed extension removal, the CLI has no Kubernetes mutation or
finalization operation to resume. Automatic namespace removal and its verified
recovery contract remain deferred; this behavior is not full clean-namespace or
GA cleanup acceptance.

The installation ownership check still requires
``Microsoft.ContainerService/managedClusters/listClusterUserCredential/action``,
``kubelogin`` for Entra clusters, target-cluster network access and namespace GET
permission. It remains bounded by a 210-second API budget. Uninstall performs no
post-delete cluster credential request and needs no namespace DELETE or all-kind
LIST permission for such cleanup. Existing ARM permissions for the owned
connection and role assignments are unchanged.

Stopped durable ChaosEngines remain in target namespaces as name reservations.
Their ``chaosengines.litmuschaos.io`` CRD therefore remains too. Shared/foreign
resources and unmarked namespaces remain, and role definitions are never deleted.
Engine-name reclamation needs the separate admission/commit drain protocol;
namespace cleanup doesn't implement or bypass it.

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
        --configuration-settings \
            "chaos-workspace-id=/subscriptions/<subscription-id>/resourceGroups/<workspace-group>/providers/Microsoft.Chaos/workspaces/<workspace-name>" \
            "experiments.stressToolsImage=PLACEHOLDER.invalid/never-pulled:0"

The chart requires ``experiments.stressToolsImage``. This inert placeholder was
used only for pod-delete validation, which doesn't pull a stress-tools image.
It isn't usable for CPU or memory faults; those require a supported, pullable
stress-tools image.

Pending live validation
^^^^^^^^^^^^^^^^^^^^^^^

The built-in role rollout is pending. Don't count an install against an empty
role definition as live authorization proof. Once the subscription's role readback
contains all five permissions, run this checklist with a locally built wheel:

* Confirm ``az role definition list --name 681440c1-3630-4424-a530-0305ac721cfd``
  returns Actions ``Microsoft.KubernetesConfiguration/extensions/read``,
  ``Microsoft.ContainerService/managedClusters/read`` and
  ``Microsoft.ContainerService/deploymentSafeguards/read``, and DataActions
  ``Microsoft.ContainerService/managedClusters/serviceaccounts/impersonate/action``
  and ``Microsoft.ContainerService/managedClusters/pods/read``.
* Use an enrolled test subscription and a new disposable resource group tagged
  ``purpose=cli-customization-test``. Don't reuse existing groups or DefaultWorkspace.
  Confirm the hidden extension's registration and approved chart/train coordinates.
  Create the AKS cluster with Workload Identity, OIDC and Azure RBAC, and a workspace
  scoped to that group. Build with ``azdev extension build k8s-extension`` and
  install that wheel using ``az extension add --source <wheel>`` in an isolated
  CLI extension directory.
* Run create and verify the active connection, workspace identity's built-in
  assignment, persisted namespace creation assertion and matching namespace marker.
  Prove the role's actual authorization using that workspace identity; the
  installer's successful ARM requests alone don't prove its permissions.
* On an existing legacy-role installation, run create and update. Verify the
  built-in assignment is added without removing the legacy assignment. Repeat
  to verify idempotence. Keep custom role definitions unchanged throughout.
* Run synchronous uninstall without ``--force`` or ``--no-wait``. Verify ARM
  extension deletion completes and both owned assignments disappear, while the
  release namespace is retained even when empty. Repeat with a customer object
  or retained ChaosEngine and verify the CLI does not modify it or the namespace.
  A pre-existing namespace must survive too. Record wheel version/hash and
  ARM/Kubernetes readbacks; do not record this as automatic namespace-removal proof.
* Delete the disposable resource group and confirm absence.

The 2026-10-21 disposable AKS attempt reached ``Succeeded`` with the local wheel
and registered ``dev`` chart ``0.1.12``. The namespace had both creation markers.
Uninstall removed the ARM extension, owned connection and built-in assignment.
It exposed the create-only ``bindings`` discovery gap fixed here. Retrying
namespace inspection preserved an unmarked ``durable-broker-learned-keys``
ConfigMap and Kubernetes Events rather than erasing them. AKS also returned a
pristine default ServiceAccount without managedFields, now covered by a regression.
This wasn't live proof of clean namespace removal. This CLI version now
intentionally retains namespaces; a chart release alone does not provide the
concurrent-writer fence or durable recovery contract required for automatic
removal. The compatible chart's learned-key owner marker and pre-delete cleanup
remain separate from that deferred capability. The CLI doesn't
special-case learned-key state; preserving the unmarked ConfigMap on 0.1.12 is
correct. Events no longer block namespace removal. The built-in role
readback still had empty Actions and DataActions, so this isn't live role
authorization proof either.

Historical evidence, not validation of staged installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installation and authorized data-plane polling succeeded with an earlier CLI
implementation and dev chart ``0.1.3``, which explicitly provisioned subscriber identity.
A five-minute pod-delete test passed in Litmus and the workload recovered to
2/2 replicas, but the ARM run failed/remained Stopping. This isn't a successful
ARM end-to-end result or proof of live update/delete behavior. The staged
platform-identity flow above has separate unit coverage and the bounded live
attempt described above; this older result isn't evidence for either.

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
