.. :changelog:

Release History
===============

1.1.0b1
+++++++
* Add support for service version ``2026-10-01-preview``.
* Add ``--capabilities`` to ``az storage-discovery workspace create`` and ``update`` for Azure Blob Storage capacity-details status and prefix configurations.
* Include capability settings in workspace create, update, show, and list responses.
* Preserve omitted capability settings during partial updates while retaining the existing GET-and-PUT update strategy.
* Add preview command ``az storage-discovery workspace query`` to execute queries directly against a workspace.
* Add preview commands ``az storage-discovery workspace report list`` and ``show`` to retrieve named report resources.
* Add preview command ``az storage-discovery workspace report generate-report`` to execute queries against a named report.
* Support ``--no-wait`` for workspace query and named-report generation.

1.0.0
++++++
* Stable version release upon api version 2025-09-01.

1.0.0b1
++++++
* Initial release.