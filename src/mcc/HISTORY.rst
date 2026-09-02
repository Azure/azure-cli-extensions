.. :changelog:

Release History
===============

1.0.0b4 (2026-09-01)
++++++
* Upgraded all ``az mcc ent`` commands to the ``2026-06-01`` API version.
* [BREAKING CHANGE] ``az mcc ent node update``: ``--auto-update-ring`` now accepts only ``Stable``
  and ``Beta``. The legacy ``Slow``, ``Fast`` and ``Preview`` rings are no longer selectable.
  ``Stable`` replaces ``Slow`` and ``Beta`` replaces ``Fast``; the ring is reported using the new
  names even though the service still stores the legacy values.
* [BREAKING CHANGE] ``az mcc ent node update``: ``--proxy`` now accepts only ``Enabled`` and
  ``Disabled``. The raw service values ``Required`` and ``None`` are no longer accepted; they were
  already rejected by validation and could never be used successfully.
* Fixed ``az mcc ent node update``: ``--proxy`` was unusable. Every allowed value failed, either at
  argument parsing or in validation.
* Fixed ``az mcc ent node update``: on a cache node that already had a proxy configured, changing
  only ``--proxy-host`` or ``--proxy-port`` failed, and disabling the proxy left the previous proxy
  URL on the resource.
* Fixed ``az mcc ent node update``: switching to ``Stable`` now correctly requires
  ``--auto-update-day``, ``--auto-update-week`` and ``--auto-update-time``, and switching to
  ``Beta`` correctly rejects them. The install schedule of the ``Beta`` ring is managed by Microsoft.
* Fixed ``az mcc ent node update``: after the update ring had been set, any later update that did
  not restate ``--auto-update-ring`` failed with ``InvalidAutoUpdateRingTypeForApiVersion``. The
  service stores the legacy ring name but rejects it on write, so the ring is now normalised on the
  instance before the request is sent.
* ``az mcc ent node update``: ``--auto-update-day`` now rejects ``0``; the allowed range is ``1-7``.
* ``az mcc ent node show/list``: the proxy state and update ring are reported using the customer
  facing values rather than the values stored by the service.
* Hid ``--bgp-network-interface``, ``--runtime-account-type`` and the ``--open-firewall-port*``
  arguments. They are reserved for an upcoming feature and are not ready for use.
* Improved help for ``--auto-update-ring``, ``--auto-update-day``, ``--auto-update-week``,
  ``--auto-update-time``, ``--cache-drive`` and ``--proxy`` so it matches the enforced behaviour.
* Added examples to every ``az mcc ent`` command.

1.0.0b3 (2025-06-17)
++++++
* Refactored commands to use new GA API version for MCC.

1.0.0b1 (2024-10-16)
++++++
* Initial release.