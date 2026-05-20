.. :changelog:

Release History
===============

1.0.0b1
+++++++
* Initial release.
* Manage ChangeRecord, StageMap, and StageProgression resources (API version ``2026-01-01-preview``).
* Custom ``--targets`` parsing with key=value shorthand (e.g., ``resourceId=...,operation=DELETE``).
* ``--stagemap-name`` shortcut to reference a StageMap by name.
* Default scheduling: ``anticipatedStartTime`` defaults to now, ``anticipatedEndTime`` to +8 hours.
* Supports ``--acquire-policy-token`` and ``--change-reference`` for guarded resource operations.