.. :changelog:

Release History
===============

1.0.0b7
++++++++
* Unpin cssc image version so that the latest cached image in task infra can be automatically picked for workflow runs. This allows us to push patch updates to cssc image without needing to update the task definition and release a new version of the extension.

1.0.0b6
++++++++
* Fix issue with DNL registry names when scheduling tasks

1.0.0b5
++++++++
* Update minCliCoreVersion

1.0.0b4
+++++++
* Fix resource SDK import error

1.0.0b3
+++++++
* Remove msrestazure dependency

1.0.0b2
++++++
* Bug fix: Updated to allow for az login when the account doesn't have any active subscriptions


1.0.0b1
++++++
* Release for Public Preview
* Added `list`and `cancel-run` commands for workflows
* `list` command provide output on the scan and patch status of the registry
* `cancel-run` command allows to canceling all running scan and patch tasks


0.1.0b1
++++++
* Initial release for Private Preview