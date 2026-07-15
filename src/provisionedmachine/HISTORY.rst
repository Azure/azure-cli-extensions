.. :changelog:

Release History
===============
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
