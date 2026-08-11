.. :changelog:

Release History
===============

1.1.0
++++++
* ``az aimanager``: Add ``get-credentials`` command to retrieve the AI Manager kubeconfig.
* ``az aimanager namespace``: Add ``get-credentials``, ``list-accesskeys`` and
  ``rotate-accesskeys`` commands.

1.0.0
++++++
* Initial release.
* ``az aimanager``: Add ``create``, ``update``, ``list``, ``show``, ``delete`` and
  ``namespace add/update/list/show/delete`` commands for AI Manager, backed by the vendored
  ``azure-mgmt-containerserviceaimanager`` SDK.
