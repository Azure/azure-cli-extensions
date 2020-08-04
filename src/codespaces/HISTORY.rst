.. :changelog:

Release History
===============

0.3.0
++++++
* Switch to new Resource Provider - Microsoft.Codespaces

0.2.1
++++++
* Added 60 minute auto-suspend timeout option

0.2.0
++++++
* Update to latest resource provider API version, 2020-05-26.
* Plan creation: Set plan defaults (default sku, default suspend timeout).
* Plan creation: `--subnet` argument to create a plan with a vnet.
* Codespace creation: Plan defaults will be used for --instance-type and --suspend-after if available and you haven't specified to override the defaults.
* New `az codespace update` command (support for editing sku/suspend timeout of a Suspended codespace).
* `az codespace list` new behavior: By default, we now only show your codespaces. Add `--all` flag to `az codespace list` command to list codespaces of all users.
* Support Secrets Management.

0.1.0
++++++
* Initial release.
