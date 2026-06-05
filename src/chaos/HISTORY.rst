.. :changelog:

Release History
===============

1.0.0b1
+++++++
* Initial preview release of the ``chaos`` extension. Targets api-version
  ``2026-05-01-preview`` of ``Microsoft.Chaos``.

  Command surface:

  * ``az chaos workspace`` -- ``create``, ``show``, ``list``, ``update``,
    ``delete``, ``refresh-recommendation``, ``evaluate-scenarios``,
    ``show-discovery``, ``show-evaluation``, ``identity`` subgroup.
  * ``az chaos scenario`` -- ``create``, ``show``, ``list``, ``update``,
    ``delete``.
  * ``az chaos scenario config`` -- ``create``, ``show``, ``list``,
    ``update``, ``delete``, ``validate``, ``fix-permissions``, ``execute``,
    ``show-validation``, ``show-permission-fix``.
  * ``az chaos scenario run`` -- ``start``, ``show``, ``list``, ``cancel``,
    ``wait``.
  * ``az chaos discovered-resource`` -- ``show``, ``list``.

  Notable hand-written commands beyond the spec-derived surface:

  * ``scenario run start`` (porcelain composite of validate + execute with
    a satisfied evaluation gate).
  * ``workspace refresh-recommendation`` / ``evaluate-scenarios`` --
    AAZ subclass override that adds inner-LRO failure detection
    (``discoveries/latest`` + ``evaluations/latest`` ``properties.status``
    inspection) on top of the AAZ-generated outer-LRO polling. Surfaces
    the silent-failure case (e.g. Azure Resource Graph propagation lag
    after a fresh Reader role assignment) that the AAZ framework polling
    alone misses.
  * ``workspace show-discovery``, ``workspace show-evaluation``,
    ``scenario config show-validation``, ``scenario config show-permission-fix``
    -- singleton-latest GETs not exposed by the spec.
