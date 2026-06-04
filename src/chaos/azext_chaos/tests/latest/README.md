# Chaos CLI Extension — Integration Tests

Tests in this directory use the Azure CLI `ScenarioTest` framework
(`azure.cli.testsdk`) and are runnable in both **live** and **playback** modes.

## Running Tests

```bash
# Playback mode (from recordings — no Azure subscription needed)
azdev test chaos

# Live mode (requires Azure subscription + ARM Gateway deployed)
azdev test chaos --live

# Single test class
azdev test chaos -t test_chaos_workspace
```

## Command Coverage

Run `azdev cmdcov chaos` to verify 100 % command-path coverage.
The report should enumerate **27 command paths** (26 unique commands + the
`workspace evaluate-scenarios` alias) with all of them covered. The count
includes `fix-permissions`, `show-permission-fix`, `show-discovery`, and
`show-evaluation` which were added during plan revisions.

## Test Files

| File | Epic Task | Commands Covered |
|------|-----------|-----------------|
| `test_chaos_workspace.py` | E5-T1 | `workspace create`, `show`, `list`, `update`, `refresh-recommendation`, `evaluate-scenarios`, `show-discovery`, `show-evaluation`, `delete` |
| `test_chaos_scenario.py` | E5-T2 | `scenario create`, `show`, `list`, `delete` |
| `test_chaos_scenario_config.py` | E5-T3 | `scenario config create`, `show`, `list`, `validate`, `show-validation`, `fix-permissions`, `show-permission-fix`, `delete` |
| `test_chaos_scenario_run.py` | E5-T3a/b/T4 | `scenario run start` (5 modes), `list`, `show`, `cancel` |
| `test_chaos_discovered_resource.py` | E5-T5 | `discovered-resource list`, `show` |
| `test_custom_commands.py` | E3-T6 | Unit tests for `custom.py` (mocked — no recording) |
| `test_command_registration.py` | E2 | Unit tests for command & help registration |
| `test_table_format.py` | E4 | Unit tests for table formatters |
| `test_validators.py` | E2 | Unit tests for argument validators |

## When to Re-record

Re-record (`azdev test chaos --live`) when **either** condition is true:

1. **Playback failures** — a test that used to pass in playback mode now
   fails (typically because the request/response shape has changed).
2. **Spec change** — a change merges to `azure-rest-api-specs[-pr]` under
   `Microsoft.Chaos` that touches a covered operation.  The agentic
   spec-change cross-links emitted from `az-chaos-codegen` (companion
   skill codification plan E1-T10) propagate this trigger automatically.

After re-recording, commit the updated `recordings/*.yaml` files.
