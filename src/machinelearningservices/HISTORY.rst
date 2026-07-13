.. :changelog:

Release History
===============

2.44.1
++++++
* Pin ``azureml-registry-tools`` to 0.1.0a64 (adds Python 3.14 support) and gate it to Python < 3.15, so the extension installs and all ``modelpublisher`` commands — including ``model-card`` — work on Azure CLI builds bundling Python 3.14 (e.g. az 2.88).

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