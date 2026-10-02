Azure CLI ml extension
==============================================================================

.. contents::
    :depth: 1
    :local:

Overview
------------------------------------------------------------------------------
This is the extension for ml


Get started with Azure CLI ml extension
------------------------------------------------------------------------------

Install this extension using the below CLI command:

    .. code-block:: bash

        az extension add --name ml


Packaging compatibility
------------------------------------------------------------------------------

The wheel build writes the package name and version into the bundled
``azext_metadata.json`` using the package definition in ``setup.py``. This lets
older Azure CLI metadata readers identify the installed extension even when
they cannot parse the wheel's newer metadata format. The source metadata file
is not modified, and build-tool downgrades are not required.

Run the packaging regression tests from the repository root:

.. code-block:: bash

    python -m pytest tests/e2e/packaging/test_packaging_lifecycle.py -k ml_metadata
