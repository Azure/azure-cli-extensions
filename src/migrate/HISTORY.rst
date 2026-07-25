.. :changelog:

Release History
===============
3.0.0b5
+++++++++++++++
* Add ``az migrate runbook`` commands (generate, show, list, update,
  regenerate, delete, wait).
* Add ``az migrate runbook definition`` commands (show, download).
* Add ``az migrate runbook definition step`` commands (add, update,
  remove) and ``az migrate runbook definition workstream`` commands
  (split, merge).
* Add ``az migrate runbook execution`` commands (start, show, list,
  pause, resume, cancel).
* Add ``az migrate runbook execution step`` commands (retry, approve,
  complete).
* Add ``az migrate runbook parameter`` command (download).
* Add ``az migrate runbook definition visualize`` and
  ``az migrate runbook execution visualize`` commands (self-contained,
  offline HTML dependency graph).
* ``az migrate runbook execution show`` and ``execution visualize`` now
  retrieve the per-execution ``status.json`` via a generated SAS URL
  (``GenerateDownloadUrl``) instead of a direct ARM read.

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
