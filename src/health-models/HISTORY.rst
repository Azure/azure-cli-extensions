.. :changelog:

Release History
===============

1.0.0b1
++++++
* Initial preview release. Supports the ``Microsoft.CloudHealth`` resource provider at API version ``2026-05-01-preview``.
* Commands are registered under the ``az monitor health-models`` namespace.
* Adds ``monitor health-models`` commands for the health model itself: ``create``, ``show``, ``list``, ``update``, ``delete``, ``wait``.
* Adds ``monitor health-models entity`` commands for entities (nodes in the graph): ``create``, ``show``, ``list``, ``update``, ``delete``, ``wait``, plus ``get-history``, ``get-signal-history``, ``ingest-health-report``, ``add-data-annotation``, ``get-data-annotations``, and ``get-signal-recommendations``.
* Adds dynamic-threshold signal evaluation shapes and Azure Resource Health availability signal schema support.
* Adds ``monitor health-models signal-definition`` commands for health signals: ``create``, ``show``, ``list``, ``update``, ``delete``, ``wait``.
* Adds ``monitor health-models relationship`` commands for parent-child edges between entities: ``create``, ``show``, ``list``, ``update``, ``delete``, ``wait``.
* Adds ``monitor health-models authentication-setting`` commands for managed-identity-backed authentication used by signals and discovery rules: ``create``, ``show``, ``list``, ``update``, ``delete``, ``wait``.
* Adds ``monitor health-models discovery-rule`` commands for rules that auto-populate the model: ``create``, ``show``, ``list``, ``update``, ``delete``, ``wait``.
* Adds ``monitor health-models identity`` commands for system- and user-assigned managed identities on a health model: ``assign``, ``remove``, ``show``, ``wait``.