.. :changelog:

Release History
===============

1.0.1b1
++++++
* Add comprehensive Neon PostgreSQL preview API commands with parameter mapping fixes
* Add 25 commands across 8 command groups: organization, project, branch, endpoint, neon-role, neon-database, and utility commands
* Fix parameter mapping for create commands using project_id with getattr/hasattr fallback pattern
* Add proper help examples and resolve linter compliance issues
* Remove unnecessary wait commands to reduce complexity
* Add linter exclusions for missing_command_example and require_wait_command_if_no_wait rules
* Comprehensive testing with real Azure resources validation
* Successfully tested endpoint, role, and database creation with live Azure subscription

1.0.0
++++++
* GA release.

1.0.0b1
++++++
* Initial release.

1.0.0b2
++++++
* Updated command descriptions.

1.0.0b3
++++++
* GA release of Neon CLI. Supports Change Plan, Project, Branches and Database Connection commands.

1.0.0b4
++++++
* Update the CLI command description to support AI related queries.
