.. :changelog:

Release History
===============
0.1.0b3
+++++++
* Updated Context and Solution Template operations to API version ``2026-06-01``.
* Deprecated ``--capabilities`` for context creation. Existing values remain supported for backward compatibility while capabilities move to automatic Target management.
* Deprecated ``context add-capability`` and ``context remove-capability`` while preserving their legacy ``2025-08-01`` capability PATCH behavior.

0.1.0b2
++++++
* Renamed the command group from ``workload-orchestration`` to ``workload-orchestration-preview``
  so the preview extension no longer collides with the GA ``workload-orchestration`` extension.
  Preview commands are now invoked as ``az workload-orchestration-preview ...``.

0.1.0b1
++++++
* Initial preview release.
* Added ``az workload-orchestration-preview solution-deployment create`` command
* Added ``az workload-orchestration-preview solution-deployment show`` command
* Added ``az workload-orchestration-preview solution-deployment list`` command
* Added ``az workload-orchestration-preview solution-deployment delete`` command
* Multi-target deployment support
* Configuration accepts string or JSON