.. :changelog:

Release History
===============

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
* Register all hand-written commands (incl. ``ScenarioConfigCreate``) test injects subscription ID
  via ``self.get_subscription_id()`` in the ``ScenarioTest`` ``self.kwargs.update({...})`` setup
  helpers so ``{sub}`` substitutions in ``--scopes /subscriptions/{sub}/...`` resolve.
* Generated ``aaz/`` tree regenerated from spec commit ``f228b86c`` via the
  ``chaos-automation-codegen`` skill family (``aaz-dev cli generate-by-swagger-tag``).

0.1.0
+++++
* Initial scaffolding. Commands will be populated when aaz-dev codegen is complete (pending 2026-05-01-preview spec availability).
