.. :changelog:

Release History
===============

2.44.1
++++++
* Make ``azureml-registry-tools`` (used by ``modelpublisher model-card`` commands) install only on Python < 3.14, so the extension installs on Azure CLI builds bundling Python 3.14.

2.44.0
++++++
* Add ``az ml modelpublisher`` command group (preview) for Models-as-a-Service self-serve publishing: ``gpu-config``, ``plan``, ``model``, ``release-candidate``, ``model-card``, and ``registry`` subgroups.

2.39.0
++++++
* Fix a bug compute update which caused Enable SSO property to reset.
* Fix proxy endpoint path

2.38.0
++++++
* Fix a bug compute update which caused Enable SSO property to reset.