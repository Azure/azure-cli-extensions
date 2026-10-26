.. :changelog:

Release History
===============
1.0.0b8
+++++++
* ``az provisionedmachine create`` - Fixed automatic AzureLinux OS image selection to use the architecture returned by ownership voucher validation before choosing the first compatible image. Architecture-aware lookups use ``2026-10-15-preview``; existing unfiltered callers retain ``2026-05-01-preview``. Explicit ``--os-image-version`` selection remains unchanged.
* ``az provisionedmachine install-os`` - Fixed automatic AzureLinux OS image selection to use ``reportedProperties.hardwareProfile.architecture``, defaulting to ``amd64`` when absent. The machine preflight GET uses ``2026-10-15-preview`` to retrieve architecture. Explicit versions, HCI selection and existing state checks remain unchanged.
* ``az provisionedmachine reset-os`` - Removed the fixed maintenance image URL so the resource provider selects its configured ROE image for the device architecture. Existing reset detection and state checks remain unchanged.
* Updated the package version, runtime ``__version__`` and README preview-version label to ``1.0.0b8``.

1.0.0b7
++++++
* ``az provisionedmachine os-image list`` - Added an optional ``--architecture`` filter (``amd64``/``arm64``) and a new ``Architecture`` column to the table output. The ``OsImageType`` column is now populated from the ``solutionType`` returned by the service.
* ``az provisionedmachine show`` / ``list`` / ``create`` - Moved to API version ``2026-10-15-preview``. Earlier versions omit ``architecture`` from the reported hardware profile and from the ownership voucher validation result, so those fields were being dropped before reaching the caller.

1.0.0b6
++++++
* ``az provisionedmachine create`` / ``install-os`` - Fixed AzureLinux OS provisioning: the resolved OS image version is now mapped to ``vsrVersion`` (previously ``osVersion``).

1.0.0b5
++++++
* ``az provisionedmachine ssh-cert-create`` - Create a short-lived SSH certificate for authenticating to a provisioned machine via Key Vault-signed certificates.

1.0.0b4
++++++
* ``az provisionedmachine show-status`` - Show lifecycle status of a provisioned machine with hierarchical table view.
* ``az provisionedmachine os-image list`` - List available OS images by location and type (HCI/AzureLinux).
* ``az provisionedmachine install-os`` - Renamed ``--os-image`` to ``--os-image-type`` and ``--version`` to ``--os-image-version``. Auto-resolves latest available version when not specified.
* ``az provisionedmachine create`` - Renamed ``--os-image`` to ``--os-image-type`` and ``--version`` to ``--os-image-version``. Auto-resolves latest available version when not specified.
* Updated all commands to API version ``2026-05-01-preview``.

1.0.0b3
++++++
* ``az provisionedmachine create`` - Create a provisioned machine resource with ownership voucher validation.
* ``az provisionedmachine install-os`` - Install OS on a provisioned machine.
* ``az provisionedmachine reset-os`` - Reset OS on a provisioned machine.

1.0.0b1
++++++
* Initial preview release.
* ``az provisionedmachine list`` - List edge machines by subscription or resource group.
* ``az provisionedmachine show`` - Get details of a specific edge machine.
* ``az provisionedmachine delete`` - Delete an edge machine.
