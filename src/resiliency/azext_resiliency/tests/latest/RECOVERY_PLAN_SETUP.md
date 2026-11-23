# Native recovery-plan lifecycle setup

These scenarios use existing enrolled service groups and protected storage.
They do not provision service groups, RGs, Automation accounts, storage, runbooks,
ASR resources or VMs. Setup is outside HTTP recordings. Run one case at a time.

## Private manifest and authorization

Use a success fixture manifest containing `subscriptionId`, `tenantId`, `region`,
`resourceGroup`, `automationAccount`, `automationAccountId`, `storageAccountId`
and `noOpRunbookId`. An optional separate existing fixture adds
`intentionalFailureRunbookId` for Retry. All fixtures must share the caller's tenant.
The plan enrollment context is the success fixture subscription, not necessarily
the caller's default subscription.

With explicit authorization, run once:

```text
python setup_recovery_plan_fixture.py --az <native-az-path> \
  --success-fixture <private-success-manifest> \
  --failure-fixture <optional-existing-failure-manifest> \
  --identity-name <one-dedicated-validation-uai> --output <private-setup-journal>
```

Omit `--failure-fixture` during initial shared setup if unavailable; configure
the authorized runbook below before attempting Retry.
On Windows put the command on one line (the continuation above is illustrative).
The script validates existing fixtures before creating one UAI in the success
fixture RG and copying its policy tags. It grants Automation Job Operator
(`4fe576fe-1146-4730-92eb-48519fa6bf9f`) and Reader
(`acdd72a7-3385-48ef-bd42-f606fba81ae7`) at each existing Automation account,
plus Reader on the selected existing storage resources. It verifies each exact
new grant ID; there is no broad role listing. The caller needs UAI create/attach
rights and those narrow role-assignment write rights. A partial journal is
evidence: inspect it rather than rerunning setup or creating another identity.
Keep journals/logs outside git; they contain real IDs.

### Explicitly authorized failure-runbook provisioning

If separately authorized to create one failure runbook in the existing account,
use the existing shared-UAI journal; do not rerun identity/role setup:

```text
python setup_retry_runbook.py --az <native-az-path> --manifest <private-shared-uai-journal> --name ro-cli-drills-failure-<unique-suffix> --receipts <private-provisioning-journal>
```

This setup-only script uses native `az rest` to create one Python3 runbook,
upload the single `raise RuntimeError(...)` statement, publish it, and verify
exact content/state/type. It reads the **actual Automation account location**:
the selected storage/plan region is not necessarily the account region.
It never writes the success runbook or changes grants. Resume a successful
fixture with its same name/journal; do not create a second usable runbook.
The reusable failure runbook
is retained and not removed by plan cleanup.

The authorized setup is now **published and validated** in the actual parent
account region. An earlier zero-success create used the protected-resource
region and left an owned unpublished ARM reservation. Same-name repair failed;
the user explicitly authorized one fresh name in the correct parent region.
That new runbook is the **only usable new failure runbook**. The previous
reservation remains separate setup residue in private receipts; it is not
a RO product blocker and was not silently deleted. Do not loop its failed
repair or create additional fixture names. The private shared-UAI journal now
contains `failure.intentionalFailureRunbookId`, `failureRunbookId` and the
successful provisioning receipt path.

Set `RESILIENCY_DRILLS_FIXTURE` to the setup journal and
`RESILIENCY_SHARED_SERVICE_GROUP` to one existing enrolled SG. The tests attach
the shared UAI **and select it explicitly** in resource associated identity.
The runbooks do not authenticate internally; the UAI authorizes RO's account-level
Automation job start.

Before the shared lifecycles, prove a minimal UAI-backed readiness/Failover on
one fresh owned plan. Delete only that plan after terminal job proof. Outside
VCR, read the shared UAI and each exact setup grant ID. Service-side identity
cleanup may remove permissions: if any exact readback fails, block dependent
shared-UAI cases and report it. Do not silently regrant or fall back to SAI.

## Native scenario boundaries

| Scenario | Intended native coverage | Qualification |
| --- | --- | --- |
| `test_recovery_plan_crud_identity_lifecycle` | Create/Wait/Show/List/Update/Delete, identity Assign/Wait/Show/Remove | Existing SAI reassignment; exact principal/tenant completion predicate, not a prolonged transition or initial None→SAI |
| `test_recovery_plan_shared_uai_success_lifecycle` | UpdateResource, readiness job/resources, ValidateForOperation, ValidateForFailover, Failover, ValidateForReprotect, Reprotect, Finalize/Wait | Selected existing storage only; empty source-location list is valid; Finalize requires Ready beforehand, not Warning→Ready |
| `test_recovery_plan_shared_uai_resume_lifecycle` | Real manual pre-action Failover Paused→Resume→Completed, same job and selected resource | Ten-minute manual timeout and Unspecified consent; native void/error-free acknowledgment is not a substituted GET |
| `test_recovery_plan_shared_uai_retry_lifecycle` | Failed Reprotect→Retry→next numbered Failed attempt on the original job | Genuine shared-UAI Record; no repair or successful-recovery/exact-failure-cause claim; reusable failure runbook preconfigured |

Four replayable lifecycles are the consolidated suite. Retry is deliberately
independent because a manual-pause plan must not contaminate Retry prerequisites;
combining it with Resume would create artificial shared setup requirements.
An implemented case is **not** evidence of live validation; see local handoff
for the actual Record/Playback outcomes. The 14 superseded RO Python files and
12 per-operation recordings are retired from this candidate, including the
ownership ledger, custom metaclass, diagnostic patches and helper-only tests.
Drills, Goals, shared `test_resiliency.py` and product source are unchanged.
Historical recordings remain outside this candidate in the prior worktree
and frozen evidence, not as duplicate published tests.

### Coverage delta from the legacy suite

The twelve per-operation native tests are replaced by four replayable
lifecycles. All twelve original
command behaviors have genuine fresh Record evidence. Their independent
per-operation setup paths are now consolidated: ValidateForFailover precedes
Failover; ValidateForReprotect/Reprotect follow that Failover in one plan.
Non-identity operation recordings now exercise the configured shared UAI,
not the old disposable SAI permission-setup path. CRUD/identity retains SAI
reassignment and removal coverage. No initial None→SAI, prolonged pending
identity transition, regional/combined/replacement identity, non-selected
workload or Warning→Ready Finalize coverage is claimed.

The original **legacy Retry playback is retired** and replaced by genuine
fresh shared-UAI Retry recording. The live-only marker was removed only after
the reusable fixture and native Record succeeded. The expected failed seed and
next failed attempt are asserted on the exact same job/workload; they are not
failing tests, successful recovery, or evidence of a script-specific error cause.
The 42 helper-only offline tests were
retired with their obsolete scaffolding; private serial runner/isolation
controls remain session evidence, not published RO helper tests.

## Recording and replay

From the extension repository, use native azdev discovery and serial execution:

```text
azdev test test_recovery_plan_crud_identity_lifecycle --discover --series --xml-path <private-record.xml> --live
azdev test test_recovery_plan_crud_identity_lifecycle --discover --series --xml-path <private-playback.xml>
```

Repeat explicitly for each independent case. Do not run the entire extension
live: other Drills/Goals tests provision their own fixtures.
The RO endpoint is process-local Canary. Use current unmodified extension
source and normal testsdk HTTP Record/Playback. The recording processor
consistently redacts signed monitor query credentials, principal metadata and
fixture names; it never patches `Session.send` or `cli_ctx.invoke`.
Request bodies participate in VCR matching.
Retry has its own standard sanitized cassette and is replayable. Missing
failure-fixture prerequisites still fail live execution; they are not skipped.

Local execution policy (not committed test logic): initial attempt plus at most
five fresh-plan retries; inventory SG1–SG30 before each create, maximum five
current plans per SG, rotate when full. Leave preexisting plans untouched.
Preserve every attempt's source/cassette/JUnit/stdout/stderr privately. Stop
retrying local setup defects until corrected; block missing prerequisites.
Cleanup refuses paused/pending/unknown jobs and retains those owned plans;
there is no Azure Stop/Cancel or shared UAI/grant deletion.

Freeze final source, SDK and successful genuine recordings before isolated
socket-blocked Playback. No network fallback, fabricated recording, job-state
edits or signed-response stitching is permitted. Publish only sanitized VCR
inputs after that replay succeeds. No push/PR is implied by this setup.
