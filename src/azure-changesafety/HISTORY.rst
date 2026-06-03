.. :changelog:

Release History
===============

1.0.0b2
+++++++
* Fix ``--additional-data`` argument to accept free-form nested JSON (e.g., SafeFly payloads).
* Fix ``--change-definition`` details to accept free-form nested JSON (e.g., ApiOperations with operations array).
* Inject ``additionalData`` into request body via content override (AAZ builder workaround).
* Add content injection for ``additionalData`` in both Create and Update commands.

1.0.0b1
+++++++
* Initial release.
* Manage ChangeRecord, StageMap, and StageProgression resources (API version ``2026-01-01-preview``).
* Custom ``--targets`` parsing with key=value shorthand (e.g., ``resourceId=...,operation=DELETE``).
* ``--stagemap-name`` shortcut to reference a StageMap by name.
* Default scheduling: ``anticipatedStartTime`` defaults to now, ``anticipatedEndTime`` to +8 hours.
* Supports ``--acquire-policy-token`` and ``--change-reference`` for guarded resource operations.