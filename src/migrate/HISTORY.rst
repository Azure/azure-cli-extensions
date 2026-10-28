.. :changelog:

Release History
===============
3.0.0b8
+++++++++++++++
* Evaluate conditional inputs independently for step inputs and each workload's
  overrides, preserving defined required and optional fields until a matching
  condition applies.
* Avoid duplicate required errors and preserve allowed inherited values when
  excluding conditional fields from saved parameters.

3.0.0b7
+++++++++++++++
* Support inline conditional input rules in runbook and execution parameter
  editors: const-based conditions select required inputs and exclude fields
  marked false from controls, validation, and saved parameters.
* Report conditional validation errors before preparing the upload command,
  while allowing incomplete parameters to be saved as a draft.

3.0.0b6
+++++++++++++++
* Add ``az migrate runbook`` command group to author, configure, and run
  Azure Migrate wave runbooks. Supported operations:

  * Runbook lifecycle: generate, view, update, regenerate, delete, and wait.
  * Definition authoring: view/visualize a runbook and edit its steps and
    step groups.
  * Parameter configuration: download, configure, and upload runbook and
    execution parameters.
  * Execution management: start, monitor/visualize, pause, resume, and
    cancel a run, plus per-step approve, retry, and complete.

3.0.0b5
+++++++++++++++
* Change migrate command parameter name.

3.0.0b4
+++++++++++++++
* Fix edge case bugs in az migrate local replication init & new commands.

3.0.0b3
+++++++++++++++
* Fix edge case bugs with az migrate get-discovered-server.

3.0.0b2
+++++++++++++++
* Added replication list, get and start migration commands.

3.0.0b1
+++++++++++++++
* Refactor codebase for improved readability and maintainability.

2.0.0
+++++++++++++++
* New version.

2.0.1b1
+++++++++++++++
* Switch to experimental version.

1.0.0
+++++++++++++++
* Initial release.
