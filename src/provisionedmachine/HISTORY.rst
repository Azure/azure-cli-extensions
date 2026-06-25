.. :changelog:

Release History
===============
1.0.0b4
++++++
* ``az provisionedmachine show-status`` - Show lifecycle status of a provisioned machine with hierarchical table view.
* ``az provisionedmachine os-image list`` - List available OS images by location and type (HCI/AzureLinux).
* ``az provisionedmachine install-os`` - Renamed ``--os-image`` to ``--os-image-type`` and ``--version`` to ``--os-image-version``. Auto-resolves latest available version when not specified.
* ``az provisionedmachine create`` - Renamed ``--os-image`` to ``--os-image-type`` and ``--version`` to ``--os-image-version``. Auto-resolves latest available version when not specified.
* Updated all commands to API version ``2026-05-01-preview``.

1.0.0b1
++++++
* Initial preview release.
* ``az provisionedmachine list`` - List edge machines by subscription or resource group.
* ``az provisionedmachine show`` - Get details of a specific edge machine.
* ``az provisionedmachine delete`` - Delete an edge machine.
