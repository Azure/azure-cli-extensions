.. :changelog:

Release History
===============

Unreleased
++++++++++
* Prevent access-token JSON from being written to the SSH transport and verbose SSH logs for ``az ml compute connect-ssh`` and ``az ml job connect-ssh``.
* Improve SSH connection argument handling and endpoint validation for jobs and compute instances.
* Honor repeatable ``az ml job connect-ssh --ssh-args`` options.

2.39.0
++++++
* Fix a bug compute update which caused Enable SSO property to reset.
* Fix proxy endpoint path

2.38.0
++++++
* Fix a bug compute update which caused Enable SSO property to reset.