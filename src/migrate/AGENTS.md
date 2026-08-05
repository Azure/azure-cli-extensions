# Principal Engineer Review Mode — migrate extension

This file is a standing instruction for **any** agent doing coding work anywhere under
`src/migrate/`. Treat every change as if you are the **principal engineer** who must approve
the pull request. Do not merely make code work — make it the code a principal engineer would
sign off on.

## Non-negotiable review discipline

Before finishing ANY migrate task, rigorously self-review against these criteria and reject
your own work if it fails:

1. **Simplicity** — Is this the simplest solution that fully solves the problem? Remove any
   complexity that does not earn its place.
2. **Reuse first** — Prefer existing helpers, patterns, and abstractions over new ones. Search
   before you write. (`shared/`, `runbook/`, existing `ArmClient`/`files` patterns.)
3. **Architecture fit** — The change must match the established structure (REST via `ArmClient`,
   `shared/files.py` for archive/IO, `runbook/cmds/*` for command logic, `transformers.py` for
   table shaping). No parallel or competing mechanisms.
4. **No speculative code** — Do not add constants, parameters, branches, or error handling for
   cases that cannot occur or are unproven. Validate only at real system boundaries.
5. **No duplicate logic** — Collapse repeated iterate/parse/classify/format loops into a single
   source of truth. Duplication is a defect.
6. **Root-cause fixes only** — Fix the underlying cause, never paper over a symptom. State the
   root cause explicitly in your summary.
7. **Net code growth** — Prefer changes that remove more than they add. Justify every new
   abstraction with a concrete, present-day need and a net-complexity benefit.
8. **Security by design** — Prefer designing hazards out (e.g. flatten to basename to eliminate
   zip-slip) over runtime guards. Keep the OWASP Top 10 in mind for every I/O boundary.
9. **Maintenance score** — Rate the resulting code 1–10 for maintainability. Do not ship below
   **9**. If below 9, keep simplifying.
10. **PR approval test** — Ask: "Would I approve this PR as principal engineer?" If not, revise.

## Mandatory concluding deliverable

Every non-trivial migrate change MUST end with a **10-point engineering review** covering:

1. Selected design and why it won.
2. Alternatives considered and why they were rejected.
3. What existing code was reused.
4. What was refactored/consolidated.
5. Duplicate logic removed.
6. New abstractions introduced and their justification.
7. Net lines added vs. removed.
8. Remaining technical debt (with explicit `TODO(confirm)` where behavior is unverified).
9. Maintenance score (1–10) with rationale.
10. Why this is the simplest correct solution.

## Verification gate (always run before declaring done)

- `python -m pytest migrate/azext_migrate/tests/latest/runbook/test_runbook_unit.py -q`
- `python -m azdev style migrate`
- `python -m azdev linter migrate` (the trailing `ERROR: invalid git repo: None` is harmless)

## Tests move with the code — never leave a reconciliation gap

Code and its tests are ONE change. A task is not done until the tests that cover the changed
behavior are updated in the SAME change and the suite is green.

- **Every code change updates its tests in lockstep.** If you change a contract (request body,
  command signature, transformer columns, file/archive handling, action verb, call kwargs), update
  the covering unit/scenario tests in the same edit. Never defer test updates to "later" or to a
  separate reconciliation pass.
- **Green-before-done.** Run the unit suite (see Verification gate) and confirm it passes before
  declaring any change complete. A change that leaves failing tests is an unfinished change.
- **Tests must load the source under `src/migrate/azext_migrate/`, not build artifacts.** Run
  pytest with `cwd = src/migrate`. A stale `build/lib/azext_migrate` copy can shadow/merge with the
  source package and mask source/test drift (a suite may appear to pass against the stale copy).
  If collection counts look inflated or failures vanish inexplicably, delete `src/migrate/build/`
  (a regenerable artifact) and clear `__pycache__`, then re-run against source.
- **Root cause of drift:** code advanced while its tests were not updated in the same change. Do not
  recreate that state. When source and tests disagree, the source is authoritative only because it
  was reviewed — still confirm the current behavior is intended before aligning the test to it.

## Domain facts to preserve

- Downloaded runbook archive members:
  - `runbook.json` → the **definition** (`{"runbookSpec": {...}}`).
  - `user-input(s).json` → the **parameters** (`{"runbookInputs": {...}}`). `definition download`
    writes this alongside the definition (per-step `configurationStatus` is derived from it), but
    table/CLI output (`show`, `visualize` grid) still renders the definition only.
  - `derived-input(s).json` → same shape as user-inputs; **never downloaded/rendered** by any CLI.
    It is distinguishable from user-inputs ONLY by filename, so it is excluded by name.
- Archive members are classified by **content**, not filename suffix (member naming varies across
  services, e.g. `rb-<name>-spec.json` vs `runbook.json`). See `shared/files.py::_classify_archive`
  as the single source of truth.
- **UpdateStep/AddStep `dependsOn` write contract (verified against live service):** each entry is a
  System.Text.Json polymorphic `RunbookStepDependency`. The discriminator property is the verbatim
  (non-camelCased) `"Mode"` whose value is the integer enum ordinal (`0` = step gate,
  `1` = migration-entity gate), and it must appear first. A `--depends-on <stepId>` maps to
  `{"Mode": 0, "stepId": "<id>"}`. See `models.py::_depends_on_refs`. NOTE: the GET (read) model
  differs — it emits `{"step": "<id>", "mode": "migrationEntity"}` (property `step`, string `mode`).
  Read/write are NOT symmetric; do not assume round-trip.
