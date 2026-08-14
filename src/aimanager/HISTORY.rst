.. :changelog:

Release History
===============

1.2.1b1
+++++++
* Add ``az aimanager model`` commands to list and show AI models in a region, and to
  ``calculate-cost`` for deploying a model.

1.2.0
++++++
* Add ``az aimanager namespace modeldeployment`` commands to add, update, list, show, delete,
  and wait for model deployments.

1.1.0
++++++
* ``az aimanager``: Add ``get-credentials`` command to retrieve the AI Manager kubeconfig.
* ``az aimanager namespace``: Add ``get-credentials`` command to retrieve the namespace kubeconfig.

1.0.0
++++++
* Initial release.
* ``az aimanager``: Add ``create``, ``update``, ``list``, ``show``, ``delete`` and
  ``namespace add/update/list/show/delete`` commands for AI Manager, backed by the vendored
  ``azure-mgmt-containerserviceaimanager`` SDK.
