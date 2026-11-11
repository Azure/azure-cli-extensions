.. :changelog:

Release History
===============

1.0.0b2
+++++++

* Create Azure managed API connections for local projects selected by path or
  saved context. Resolve Azure scope from local.settings.json with explicit
  command overrides, without changing the default account or context schema.
* Store seven-day development keys only in protected local settings and reference
  them from connections.json. Preserve deployed identity/access-policy behavior
  and the deployed-only legacy command. Keys are not automatically renewed.
* Guard local publication with bounded strict inputs, Git tracking/ignore checks,
  private staging, snapshot conflict detection and individual atomic replacements.
  Failures retain Azure state and can leave partial local updates; no multi-file
  transaction, unsafe rollback or automatic mutation retry is claimed.

1.0.0b1
+++++++

* Contribute the complete 59-command Logic Apps Standard preview to the official
  extension repository, retaining core app, settings and ZIP deployment commands.
* Relocate developer and contract guides under the extension and generate GA help
  controls with the same stock CLI in isolated configuration/extension directories.
* Adopt the upstream preview version scheme and declare Python 3.10 or newer and
  Azure CLI 2.67.0 or newer. Platform and live-cloud qualification remain separate.
* Preserve Rohitha's original extension and subsequent staging improvements;
  retain the read-only testing foundation alongside explicit native testing.
* Incorporate reviewed improvements through the historical 0.1.23 baseline,
  retaining the existing public preview version and historical report producers.
* Add genuine one-action run resubmission with completed-source, literal runtime
  eligibility and stable selected-evidence rechecks. Move trigger replay to
  trigger history resubmit; never substitute it for action-level recovery.
* Rename complete-document workflow replacement to workflow set. Share completed
  runtime-template validation and refuse unfinished or malformed receipts.
* Add connection managed create with distinct connection and site names, retaining
  deprecated legacy semantics and accurate OAuth resource-retention guidance.
* Isolate saved contexts by Azure CLI configuration, reject incompatible explicit
  cloud authoring targets and honor saved local runtime ports.
* Return 0 for successful planning and retain blocked exit 4 with --strict.
  Closed schema-2 reports record policy; supported schema-1 reports retain their
  historical exits. Neither mode executes business tests or clears SDK gates.
* Preserve execution bearer authentication against netrc substitution and reject
  every nonempty mutation acknowledgement before JSON decoding.
* Harden cloud coordinates, ACL collection completeness and duplicate-name
  ownership checks. Bind connection-file compensation to its completed write
  revision, retaining ambiguous or cross-scope state.
* Distinguish exited Windows process objects, exclude only verified pre-existing
  stale-parent subtrees and bound cleanup waits. Recover cleanup-pending receipts
  only on explicit, ownership-safe stop retries, with exact-snapshot locking.
* Keep Windows psutil below 7.1.2 so both x86 and x64 CLI installations use
  publisher wheels without requiring a C++ compiler; non-Windows resolution and
  all PID/birth-identity cleanup guards remain unchanged.
* Default test planning to a selected local context or current directory after
  explicit paths. Anchor relative report destinations to that project without
  implicit writes or SDK execution. Preserve exact historical report catalogs,
  including both schema-2 guidance variants of the unchanged public 1.0.0b1.
* Add source-only native SDK/MSTest scaffolding and explicit test execution with
  per-invocation SDK terms/project trust and separately opt-in restore. Preserve
  the ignored/inconclusive starter, identity-checked cleanup, retained-receipt
  retry hold, sensitive-artifact limits and explicit lack of sandbox/coverage
  attestation. No SDK binaries are redistributed.
* Inspect closed sanitized native reports without rerunning tests. Preserve
  historical 0.1.25/0.1.26 native/preflight producers and exact public historical
  finding catalogs, independent of later package versions.
* Exclude dedicated native test/state directories and raw TRX from deployment
  packages, refusing colocation with runtime content rather than omitting it.
* Normalize omitted context-create ports at the real CLI boundary to 7071,
  without weakening explicit-port or stored-context validation.
* Escape OAuth callback details as HTML text and bound accepted-client reads
  by an absolute deadline as well as listener shutdown, including incomplete
  and trickled requests.
* Fail closed on invalid deployment exclusions, ambiguous test/runtime
  directories and aliased ZIP/manifest outputs. Exclude case-equivalent local
  settings while preserving ordinary runtime assemblies.
* Exclude positively identified triggers from action discovery. Recheck retained
  trigger histories using stable identity/execution/revision evidence without
  treating regenerated signed links as changes or relaxing fired-history checks.

0.1.19
++++++

* Require managed-deletion access policies to match the selected site's system
  principal and tenant, sharing the creation matcher. Retain missing/malformed
  tenant evidence and cross-tenant policies; never infer site ownership from login.
* Preserve proven pre-send deadline state in execution reports without erasing
  acknowledged cancellation or weakening post-send uncertainty. Validate the
  continuation-token Base64 alphabet before parsing its JSON offset.
* Distinguish credential acquisition failure before mutation submission from
  failed observation of an already acknowledged cancellation. Reject ambiguous
  doctor host-state JSON and conflicting inventory continuation sources.
* Preserve JSON scalar types in complete context snapshot rechecks and no-op
  detection, preventing type-only concurrent metadata changes from being
  overwritten while keeping object member order irrelevant.
* Preflight managed deletion's ARM ownership evidence before file unlink, then
  refresh cleanup evidence after verified unlink; early read failures preserve
  wiring while late failures retain ARM resources without unsafe file replay.
* Preserve JSON scalar types in connection publication/removal/recovery guards
  and workflow update no-op detection; reject malformed/noninteger paging offsets
  with CLI argument errors rather than unexpected overflow or recursion failures.
* Require existing managed access policies to match the selected principal type,
  object ID and tenant before forced connection update and again before ACL PUT.
* Bound workflow inventory traversal to 100 service pages and 10000 accumulated
  entries, failing without partial results independently of client-side paging.
* Reject ambiguous/nonfinite ARM identity and access-policy JSON before deriving
  destructive connection ownership. Runtime validation also strictly rereads
  authored workflow input before any POST rather than normalizing static failures.
* Decode shared site-runtime JSON receipts strictly so workflow discovery and
  mutation checks cannot authorize writes from already-collapsed metadata or
  validation fields. Preserve finite and empty-response receipt contracts.
* Strictly decode workflow-state metadata and app-settings snapshots/receipts
  before whole-map mutations or success claims. Accept ephemeral host keys for
  active local contexts, while preserving cloud-key and saved-port restrictions.
* Strictly decode connection-removal readback and refuse missing/ambiguous files
  before ARM cleanup. Acquire the selected CLI profile token for each execution
  request so long observations can refresh credentials without mutation retries.
* Reject duplicate JSON members and nonfinite/overflowing numbers before
  connection-file mutations, workflow authoring/validation/update, remote
  workflow snapshot use or execution-response interpretation. Share the strict
  decoder with testing preflight instead of silently normalizing ambiguous input.
* Buffer execution responses in bounded 64-KiB chunks while preserving raw
  receive deadlines, the 1-MiB payload cap and EOF/decode deadline checks.
* Bind connection-file publication, removal and restoration to the exact fresh
  strong VFS ETag. Revision conflicts never authorize ARM cleanup or wildcard
  retries. Require an existing strongly versioned connections.json before managed
  creation; unqualified missing-file creation is intentionally unsupported.
* Accept deployed site-qualified run references when verifying retained trigger
  history for resubmission, while rejecting other targets and rechecking the
  association after confirmation. Preserve local relative-reference behavior.
* Require completed connection-file write receipts and selected-entry readback
  before reporting wiring success or allowing destructive ARM cleanup.
* Reject unfinished asynchronous runtime-validation receipts before workflow
  update confirmation or publication; preserve existing POST payload contracts.
* Revalidate root identity and descendant ancestry before adopting child-process
  ownership; preserve unverified children as non-signaling cleanup/storage guards.
* Budget doctor HTTP raw reads before header/body buffering, and accept host-state
  observations only from successful responses received within that budget.
* Request identity execution encoding and reject compressed responses before
  decoding so decompression cannot bypass streaming deadline checks. Budget raw
  HTTP/HTTPS and proxy CONNECT reads before header buffering using request-scoped
  connection pools; preserve TLS verification and unrelated Requests sessions.
* Add real loopback streaming, recycled-child adoption, incomplete/mismatched
  publication and unfinished-validation regression coverage. SDK execution
  remains gated; no commands or roadmap capabilities are added.

0.1.18
++++++

* Harden post-fork features without adding command surfaces or enabling the
  workflow test SDK. Retain connection resources when failed creation does not
  establish rollback ownership.
* Reject nonfinite/deeply nested context stores and ambiguous workflow metadata;
  sanitize malformed continuation URLs and preserve invalid saved state.
* Enforce execution deadlines at response EOF and after JSON decoding, without
  retrying mutations or accepting late receipts.
* Fail closed on malformed runtime ownership records, preserve uncertain cleanup
  and shared storage, and bind process termination to original creation identities.
* Clarify that report publication cleanup can fail after the destination exists.
  Add durable actual-CLI parser/output/exit-hook, offline wheel-content/metadata,
  concurrent publication, process-race and protocol regression coverage.

0.1.17
++++++

* Add explicit-local test plan with bounded read-only Standard authoring,
  literal reference and optional XML test-project declaration inspection.
* Add versioned sanitized preflight reports, stable finding rules, limited
  coverage and before/after input identity observations. Never execute tests.
* Preserve JSON/table/query output before authoring/input/policy/stale/artifact
  diagnostic exits; default stdout only, with explicitly guarded atomic saving.
* Add test results show for closed foundation preflight reports only, rejecting
  unknown/native/legacy schemas and arbitrary report text. Optional explicit
  workflow-file identity comparison never follows embedded report paths.
* Keep SDK adoption/restore/execution blocked and installed/resolved/platform/
  isolation evidence unknown. No SDK download/load, build/test discovery, native
  workflow run, test scaffold/generation or local-runtime integration was added.

0.1.16
++++++

* Add read-only, sorted context list and named/active show with stable target
  coordinates and active metadata, without creating a missing context store.
* Add validated partial update of existing shortcuts, with explicit complete
  local/cloud kind transitions and confirmation or --yes for active edits.
* Delete saved shortcuts only. Confirm active deletion and atomically clear
  selection without choosing a replacement; never delete projects or resources.
* Preserve original create/use behavior, unknown saved metadata and inherited
  Azure CLI authentication/subscription selection. Contexts do not bind tenants,
  subscriptions or slots and do not store credentials.
* Validate saved schema and fail explicitly on unreadable, malformed or
  unsupported stores rather than silently falling back to the current directory.
* Serialize cooperating create/use/update/delete writers with a bounded native
  advisory lock and snapshot recheck; publish complete JSON atomically. Document
  older/manual writer and filesystem limits instead of promising universal CAS.
* Aggregate Stateful execution controls with workflow discovery/mutations/state
  and read-only runtime doctor, retaining their existing safety boundaries.

0.1.15
++++++

* Add bounded Stateful run wait, confirmed cancellation, and confirmed resubmit
  through a verified retained trigger history association, for local/deployed
  Standard targets and existing contexts. Preserve existing run start responses.
* Distinguish acknowledged requests, observed terminal outcomes, pending/unknown
  state, workflow TimedOut, CLI wait timeout, and read/auth/provider failures.
  Preserve sanitized JSON/table/query reports before nonzero execution exits.
* Resubmission identifies a distinct new run only when the receipt provides it;
  do not substitute run IDs for history IDs, guess new IDs or retry mutations.
* Use a bounded execution-only transport with CLI profile authentication, no
  redirects, no automatic POST retries and no raw provider payloads/signed URLs.
  Reject Stateless and unsupported targets before mutations. Document limits,
  retained-history search bounds and cancellation/duplicate-side-effect risks.

0.1.14
++++++

* Add individual deployed Stateful/Stateless workflow enable/disable through the
  documented FlowState app setting, without whole-app stop/start or run cancellation.
* Require non-atomic acknowledgement and confirmation, preserve snapshot settings,
  check preflight/receipt/readback and distinguish configuration from observed
  runtime state. Do not retry uncertain writes or roll back unrelated settings.
* Reject unsupported live local state transitions without requests or file edits.
  Keep settings, signed URLs and provider error bodies out of results and REST
  debug logs. Document concurrency, propagation, backlog and hosting boundaries.
* Add read-only local runtime doctor for project/tool/bundle/reference/storage and
  verified runtime observations, without cloud calls or repair/start/stop behavior.
  Preserve JSON/table/query findings before nonzero diagnostic exits.
* Keep exact tool/bundle compatibility a required unknown: otherwise responsive
  projects normally exit 2, not a false healthy pass. Required failures exit 1;
  unknown and failed are distinct, and environment checks do not test workflows.

0.1.13
++++++

* Add guarded workflow update/delete for running local and deployed Standard apps.
  Require explicit non-atomic acknowledgement, exact ETag checks, confirmation,
  runtime definition preflight for updates, and verified file-plane outcomes.
* Expose source ETags in workflow show/export for optional editing-session guards.
* Preserve newer revisions during failure recovery; report ambiguous writes,
  unexpected creation and unverified deletion instead of returning success.
* Delete only the workflow definition, retaining sibling and shared app files.
* Correct local host-key and authorization behavior for raw VFS operations while
  preserving existing connection helpers' default write behavior.
* Preserve raw VFS upload bytes instead of allowing the Azure CLI request helper
  to reserialize JSON, so exact readback and conditional restoration work.
* Document the observed VFS concurrency/partial-write limits; do not promise
  transactional mutations, guaranteed rollback or completed runtime reload.

0.1.12
++++++

* Add read-only workflow list, show, and single-workflow export for running local
  and deployed Standard apps, including saved contexts and consistent paging.
* Read authored workflow.json through the authenticated file plane rather than
  reconstructing definitions from runtime metadata; preserve kind and configuration.
* Publish exports atomically, require force for replacement, and reject malformed
  service responses without creating a partial output file.
* Reject stray local ports on cloud targets and ignored port/host-key combinations
  on saved contexts.
* Document the capability investigation and incremental workflow-loop roadmap.

0.1.11
++++++

* Make managed connection creation and app-file wiring one transaction; unwind
  newly created state without deleting a pre-existing forced-update connection.
* Preserve shared user-assigned identity policies and resources during connection
  deletion, using the identity selected by the actual app connection entry.
* Verify local process ownership portably and fail closed for unknown or recycled
  process identities.
* Supply managed Node.js and other tool paths to child processes without changing
  the global PATH.
* Track foreground runtime consumers so stopping another host cannot release
  their shared CLI-owned Azurite.
* Report malformed workflow trigger shapes as structured validation findings.

0.1.10
++++++

* **Fixed ``startedByCli`` meaning two different things.** ``runtime start`` reported
  ``startedByCli: false`` for an emulator it had reused, while ``runtime show`` reported
  ``true`` for that same emulator -- so a developer reading ``start`` would conclude nothing
  would stop it, moments before ``runtime stop`` released it. The field now means one thing
  wherever it appears: this CLI owns the emulator and ``runtime stop`` may release it. It is
  read from the state record rather than from whatever the current invocation happened to do,
  which is already reported separately by ``state``. Found by running the command rather than
  its tests: every mocked test passed while the two commands contradicted each other.

* Documentation corrected: the getting-started guide still instructed the reader to start
  Azurite manually, and described the emulator as "never stopped by this CLI", both of which
  0.1.9 had made untrue.

0.1.9
+++++

* **``runtime start`` now starts the Azurite storage emulator instead of only warning about it.**
  A project whose ``local.settings.json`` sets ``AzureWebJobsStorage`` to
  ``UseDevelopmentStorage=true`` cannot run without the emulator, and the command previously
  printed a warning and started a host that could not work, leaving the developer to open a
  second terminal to satisfy a dependency the CLI already knows how to install. The emulator is
  now started on ports 10000-10002 and waited on until it answers. Pass ``--no-azurite`` to
  manage it yourself.

* **An emulator that is already serving is reused, never duplicated or hijacked.** Azurite binds
  fixed ports, so a second instance cannot start. The port is probed for a ``Server: Azurite-*``
  banner rather than merely for "something is listening", because an unrelated service holding
  port 10000 would otherwise be mistaken for the emulator and the runtime would then fail
  against an endpoint that is not storage at all. A reused emulator is recorded as not
  CLI-started, so ``runtime stop`` leaves it alone.

* **``runtime stop`` releases only an emulator this CLI started, and only once no CLI-started
  runtime is still using it.** The emulator is shared across every local runtime on the machine,
  so stopping it alongside the first runtime would have pulled storage out from under the
  others.

* **Fixed ``stop`` reporting success while the process it stopped was still serving.** On Windows
  the tools this CLI launches are ``.cmd`` shims; terminating the recorded process killed the
  shim and reparented the ``node``/host process that actually held the port, which then ran
  forever. Termination now stops the recorded process together with the descendants it spawned,
  and ``stop`` verifies the emulator has actually gone rather than trusting the kill. Observed
  live: an orphaned emulator survived a ``stop`` that returned success.

* ``runtime show`` now reports emulator state under ``azurite`` -- whether it is running, its
  server banner, and whether this CLI started it.

* Storage configuration that cannot be read is reported rather than guessed at: the emulator is
  started only when ``AzureWebJobsStorage`` is known to point at it, because spawning a
  background server process on a guess is a larger imposition than saying so.

0.1.8
+++++

* **``--auth-mode oauth`` now works instead of being refused.** Creating a connection to an
  OAuth managed connector (Office 365, SharePoint, Dataverse and similar) previously exited
  with "OAuth managed connector consent is not implemented by this CLI" and told the user to
  go create the connection in the designer or the portal. The interactive consent leg is now
  implemented end to end: the command creates the connection, asks the service for a consent
  link, opens it in a browser, and waits on a loopback listener for the redirect that signals
  consent finished. Verified live against ``office365``.

  The flow deliberately does not require an authorization code on the callback. The consent
  service registers its own ``redirect_uri`` with Entra ID and redeems the code server-side
  before bouncing the browser back, so the loopback request normally arrives with no query
  parameters at all -- that is the ordinary success path, not a failure. A ``code`` is
  confirmed with ``confirmConsentCode`` when one is present. Success is established by
  reading the connection back and requiring a connected status, not by assuming the redirect
  meant it worked.

  The consent link is requested as the **signed-in caller**, not as the app's managed
  identity. The service rejects anything else with ``InvalidConsentLinkParameter`` -- "The
  client can only request consent links for their own identity" -- because consent is granted
  by the human running the command. The access policy still names the app's managed identity,
  so the two principals are deliberately different and must not be unified.

* **A connection that fails to authorize is deleted, not left behind.** If consent is
  declined, times out, or the connection does not reach a connected state, the partially
  created ``Microsoft.Web/connections`` resource is removed before the command exits. A
  half-created connection is invisible in the designer's connection picker but still occupies
  the name, so the obvious retry used to fail with "already exists".

* **``--no-browser``** prints the consent URL instead of launching a browser, for headless
  and SSH sessions. **``--consent-timeout``** (default 300s) bounds the wait; the timeout
  message names the flag that extends it. Both are rejected with a specific error when the
  auth mode has no consent leg, rather than being silently ignored.

0.1.7
+++++

* **Breaking (preview):** pagination flags are now spelled the same way on every paged
  command. ``--next-token`` is primary and ``--continuation-token`` is accepted as an alias
  on all seven. Previously the extension shipped three different surfaces -- ``run list`` and
  ``run action list`` took only ``--continuation-token``; ``connection list``, ``connector
  managed list`` and ``connector managed operation list`` took only ``--next-token``; and
  ``connector list`` and ``connector operation list`` took both -- while every one of them
  returned the token under the same ``nextContinuationToken`` key. A token copied out of one
  command's output was rejected by the next command the user tried. Both flag spellings now
  work everywhere, so no existing command line breaks, and the flags are grouped under
  ``Pagination`` in ``--help`` to match the core ``logicapp`` commands.

* **Malformed paging input no longer produces a traceback.** ``--next-token garbage`` on the
  site-runtime commands raised a bare ``ValueError``, which the CLI reports as "The command
  failed with an unexpected error" with a full traceback and a link to file an azure-cli bug.
  The managed-catalog commands already raised ``InvalidArgumentValueError`` for the identical
  input. All paging validation now raises the CLI error type, as does a bad ``--max-items``
  and a malformed local runtime address or site resource id.

* **``--kind`` means the same thing on both operation list commands.** When the kind filter
  matched nothing, ``connector managed operation list`` fell back to returning the *unfiltered*
  list, so ``--kind trigger`` answered with actions; ``connector operation list`` returned an
  empty page for the same request. The fallback is removed -- a filter that silently disables
  itself is worse than an empty result.

* **``connector managed list --query-text`` is now ``--search``**, matching the two operation
  list commands, which already used ``--search`` for the same client-side text filter.
  ``--query-text`` is kept as an alias.

* ``connector operation list`` now returns an explicit ``{connector, kind, value,
  nextContinuationToken}`` document instead of copying the upstream runtime payload, which was
  leaking unrelated fields (an always-null ``skipToken``, among others) and would have silently
  grown new keys as the runtime evolved.

* Internal: the client-side paging token codec existed in three copies -- ``_runtime_client``,
  ``_managed_api``, and ``_connection`` reaching across a module boundary into ``_managed_api``'s
  private ``_encode_token``/``_decode_token``. All three used the same base64url ``{"offset": N}``
  envelope but raised different exception types, which is what produced the traceback above.
  They are now one implementation in ``azext_logicapp/_paging.py``, shared with the ``--kind``
  value validation that ``custom`` and ``_managed_api`` also each carried a copy of.

0.1.6
+++++

* New commands ``az logicapp connector operation list`` and ``az logicapp connector operation
  show`` report the operations exposed by a built-in (service provider) connector. Only the
  connectors themselves were listable before; the ARM managed catalog already had
  ``connector managed operation list/show``, but the built-in catalog the runtime actually
  serves had no equivalent, so there was no way to discover an operation name to author against
  without reading the connector manifest by hand.

  Notable behaviour:

  * ``--kind trigger`` and ``--kind action`` classify using the runtime's own ``trigger``
    field on each operation, which is an explicit discriminator. This is deliberately not the
    multi-field heuristic that ``connector managed operation list`` has to use, because the ARM
    catalog carries no such field. Verified against a deployed app: ``serviceBus`` returns 41
    operations, of which 10 are triggers and 31 are actions, and every one of the 41 reports the
    same ``operationType``, so the managed heuristic could not have separated them.
  * The trigger value arrives PascalCase on the wire -- ``Batch`` and ``Single``, not the
    lowercase the enum members suggest -- and actions omit the field entirely rather than
    sending a sentinel. Comparison folds case, so all forms classify correctly; absent, null and
    ``notSpecified`` are all actions.
  * The runtime returns the whole operation list in one response and emits no continuation
    token, so ``--kind``, ``--search``, ``--max-items`` and ``--continuation-token`` are all
    applied by the CLI. Filtering is applied before paging, so a filtered page is not cut out of
    operations the caller excluded.
  * ``--connector`` accepts the id, unrooted and bare-name forms, as ``connector show`` does.
    ``--operation`` likewise accepts the full operation id that ``connector operation list``
    reports as well as the bare name, so the output of one command feeds the next. Both are
    still escaped as a single route segment.

* The 0.1.4 entry below claimed ``connector operation list/show`` accepted normalized connector
  ids. Those commands did not exist until this release; only ``connector show`` was fixed. The
  entry has been corrected.

0.1.5
+++++

* ``dependency install --kind azurite`` now installs the Azurite storage emulator. It was
  previously refused with a pointer to ``npm install -g azurite``, on the reasoning that Visual
  Studio Code's Azure Logic Apps extension supplies Azurite. A CLI user has no such extension, so
  a local run that needs the storage emulator had nothing to fall back on.

  Azurite is published only through npm and declares twenty runtime dependencies, so unlike
  Node.js and Core Tools there is no self-contained archive to unpack -- the dependency tree has
  to be resolved. It is installed with the npm that ships alongside Node.js, confined to the
  managed dependency folder with ``--global --prefix``, and records the same
  ``.logicapps-integrity.json`` manifest as every other install, so ``dependency uninstall``
  continues to remove only what this CLI put there.

  Notable behaviour:

  * It installs from the public npm registry rather than whatever registry the machine's npm is
    configured for. An internal mirror that does not carry ``azurite`` is the usual reason the
    previously documented ``npm install -g azurite`` route fails with a 401. ``--source-url``
    takes another registry.
  * Installing every kind installs Node.js before Azurite, because Azurite is installed with the
    npm that comes with it. When npm cannot be found, the error names
    ``az logicapp dependency install --kind node``.
  * Azurite requires Node.js 22 or later, which npm enforces only as a warning. A too-old
    Node.js is refused up front rather than producing an install that fails on first run.
  * npm exiting zero is not treated as success on its own. The install is confirmed by finding a
    runnable launcher where ``dependency check`` looks for one, and the version recorded is the
    one in the installed ``package.json`` rather than the one requested.
  * npm writes to a staging folder first, so a failed install leaves nothing behind.

* ``dependency check`` now suggests ``az logicapp dependency install --kind azurite`` for a
  missing Azurite instead of ``npm install -g azurite``.

0.1.4
+++++

Fixes for defects found by running 0.1.3 end to end on a clean machine.

* ``connector show`` now accepts the connector ``id`` that ``connector list`` itself reports
  (``/serviceProviders/serviceBus``), as well as the unrooted and bare-name forms. The id form
  was previously percent-encoded whole into ``%2FserviceProviders%2FserviceBus`` and the runtime
  answered ``ApiNotFound``, so the output of one command could not be fed into the next. Names
  are still escaped as a single route segment.
* ``dependency check`` no longer reports Azurite as flatly optional. It reads
  ``AzureWebJobsStorage`` from the project's ``local.settings.json`` and reports Azurite as
  required only when storage resolves to the emulator, along with a ``requiredWhen`` explanation
  and the ``usesDevelopmentStorage`` finding. A project it cannot read is reported as unknown
  rather than guessed either way. Pass ``--path`` to name the project, or ``--context`` to use a
  saved one.
* ``runtime start`` only warns about a missing Azurite when the project actually uses development
  storage, instead of warning purely because the binary was absent.
* ``runtime start`` waits for the host to answer before reporting success, and distinguishes
  ``running``, ``starting`` and ``failed``. A start that never becomes ready now says so and
  points at the log rather than reporting ``running``. Tune or disable the wait with
  ``--ready-timeout`` (default 30 seconds; ``0`` returns immediately).
* ``runtime show``'s ``managementEndpointReachable`` is now the result of actually calling the
  management endpoint. It was previously an alias for "something is bound to the port", so an
  unrelated process holding the port, or a host that had bound but was not yet serving, reported
  as ready. A new ``lastProbeError`` reports why a probe failed.
* ``runtime show`` no longer reports ``stopped`` for a runtime that is up. The port check
  decided by binding with ``SO_REUSEADDR``, which on Windows means "bind even though this
  address is taken" -- the opposite of its Unix meaning -- so a host that also set the option
  read as absent. The check now connects to the port, which is the claim being made.
* ``connection test`` reports HTTP 401/403 as ``authorizationFailed`` rather than a flat
  ``failed``, and explains that a connector's generic test operation routinely needs broader
  rights than the operations a workflow calls. A service provider connection answering 400 gets
  the same explanation. The command still exits non-zero, because the connection was not verified.
* ``dependency install`` no longer downloads a second copy of a tool that is already on ``PATH``.
  It reports ``skipped``/``alreadyPresent`` with the path it found; ``--force`` or an explicit
  ``--version`` still installs a CLI-managed copy.
* ``workflow package`` excludes repository metadata files (``.gitignore``, ``.gitattributes``,
  ``.hgignore``, ``.dockerignore``, ``.funcignore``) and honours ``.funcignore`` patterns.
  Previously every unrecognized file was packaged, so the only way to keep a scratch payload out
  of a deployment was to move it out of the project.

0.1.3
+++++

* Add ``connection delete``, the inverse of both ``connection create`` modes. For a managed API
  connection it removes the ``connections.json`` entry, the access policy naming this app's
  identity, and the ARM connection resource; for a service provider connection it removes the
  ``connections.json`` entry. The ``connections.json`` entry is always written before anything is
  deleted in ARM, so a partial failure leaves an orphaned resource rather than an app pointing at
  a connection that no longer exists.
* ``connection delete`` refuses to delete a *shared* managed connection. A managed API connection
  can serve several apps, each through its own access policy, so an access policy naming a
  principal outside this app is treated as evidence that something else is using it. The resource
  is kept, only this app's access policy and ``connections.json`` entry are removed, and the
  reason is reported along with the exact command to finish the job. ``--keep-resource`` requests
  that outcome deliberately.
* ``connection delete`` never deletes app settings. Settings a service provider connection
  referenced are reported as ``orphanedAppSettings`` and left in place, because other connections
  or workflows may still read them.
* ``connection delete`` refuses a connection name that exists in both connection classes rather
  than guessing which one was meant; pass ``--class`` to disambiguate.

0.1.2
+++++

* Add ``connection create --managed-api``, which creates an Azure managed API connection for a
  deployed Logic App. It creates the three coupled things the app actually needs: the ARM
  ``Microsoft.Web/connections`` resource, an access policy naming the app's managed identity, and
  a ``managedApiConnections`` entry in the app's ``connections.json``. Connections are always
  created with ``kind: V2``; a V1 connection rejects every access policy and its kind cannot be
  changed afterwards. Supports ``--auth-mode`` ``managed-identity``, ``raw`` and
  ``service-principal``; the managed-identity parameter set is read from the connector's own
  metadata rather than assumed. ``--auth-mode oauth`` is refused with guidance, because browser
  consent is not implemented and a partial attempt would orphan a connection.
* Add ``connection acl list|show|add|remove`` for access policies on managed API connections.
  ``acl add`` refuses V1 connections, and refuses a second policy for a principal that already
  has one -- a collision the service otherwise reports as an opaque ``InternalServerError``.
* ``connection create`` now accepts ``-n`` as an alias for ``--name``.

0.1.1
+++++

* Fix ``workflow validate --with-runtime``, which rejected every workflow. The request posted the
  workflow file as-is; the runtime expects it wrapped in a ``properties`` envelope.
* Fix ``workflow validate --workflow NAME`` reporting findings against the current directory
  instead of the workflow file.
* Fix ``coverage.checks.runtimeTemplate`` always reporting ``false`` even when the runtime
  template check had run.
* Report a missing Logic App as exit 3 from ``identity assign`` and ``identity remove``. Only
  ``identity show`` did so before, despite the identical ARM 404.
* Emit matching field names from ``runtime start`` and ``runtime show`` (``state``/``status``,
  top-level ``listening`` and ``managementEndpoint``, and the nested ``readiness`` equivalents),
  so a script can start the runtime and then poll it without changing how it reads the payload.
  Additive: no previously emitted field was removed or renamed.
* Stop redacting connection parameter values that are exactly an app setting reference such as
  ``@appsetting('NAME')``. The reference names a setting rather than carrying its value, and
  hiding it removed the main way to tell that the referenced setting does not exist.

0.1.0
+++++

* Add preview Logic Apps Standard project, context, workflow, deployment, dependency, connector, runtime, and run commands.
