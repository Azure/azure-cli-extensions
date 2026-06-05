.. :changelog:

Release History
===============

0.1.6
+++++
* Fix ``'NoneType' object is not callable`` crash on successful ``chaos workspace
  refresh-recommendation`` (and its alias ``evaluate-scenarios``). Root cause: the
  AAZ-generated inner operation passes ``None`` as the LRO success deserializer to
  ``build_lro_polling``; the framework later invokes that ``None`` from
  ``base_polling._parse_resource`` and raises ``TypeError``. Fixed in the
  ``WorkspaceRefreshRecommendation`` subclass by overriding ``_handler`` to provide
  a no-op deserializer (``lambda _: None``). ``post_operations`` (inner-LRO check)
  is unaffected and still runs.

0.1.5
+++++
* Refactor ``chaos workspace refresh-recommendation`` to use the AAZ-subclass + ``post_operations``
  pattern (``WorkspaceRefreshRecommendation`` overriding the AAZ-generated command). Inner-LRO
  failure detection (discoveries/latest + evaluations/latest with ``properties.status`` inspection,
  ARG-propagation-lag hint) preserved; ~30 lines of duplicated POST + outer-LRO polling removed
  (now handled by the AAZ framework).
* ``chaos workspace evaluate-scenarios`` re-implemented as a ``WorkspaceEvaluateScenarios`` subclass
  alias of the same handler. Behavior unchanged today; will become a true composite of
  ``/discover`` + ``/evaluate`` when those ARM ops land in ``2026-08-01-preview``.
* Command name changed from plural ``refresh-recommendations`` to singular ``refresh-recommendation``
  to match the aaz-dev convention for verb-noun command naming. The ``evaluate-scenarios`` alias
  retains its current name.
* Generated ``aaz/`` tree regenerated from spec commit ``f228b86c`` via the
  ``chaos-automation-codegen`` skill family (``aaz-dev cli generate-by-swagger-tag``).
* Test scaffolding: removed all ``@live_only()`` integration tests (workspace lifecycle,
  scenario CRUD, scenario_config CRUD, scenario_run, discovered-resource). Their value
  over the ~140 unit tests + ``azdev linter`` + spec-driven aaz-dev regen was marginal —
  they exercised service behavior (which Microsoft.Chaos owns) rather than extension
  behavior. Validation strategy is now: unit tests + ``azdev linter`` + ``azdev style`` +
  deterministic regen via the codegen skill + developer smoke before release. Matches how
  many other azure-cli-extensions packages validate (zero ScenarioTest coverage is a
  common, accepted pattern). No ``recordings/`` directory required.

0.1.0
+++++
* Initial scaffolding. Commands will be populated when aaz-dev codegen is complete (pending 2026-05-01-preview spec availability).
