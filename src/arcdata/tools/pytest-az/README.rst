# `pytest-az`


Py.test plugin for simplifying and speeding-up tests:
- `VCR.py <https://vcrpy.readthedocs.io/>`_ cassettes
- In-process `azure-cli` ArcData pytest fixture


Quick Start
===========

Install the plugin:

.. code-block:: sh

    pip install -e ./tools/pytest-az


Annotate your tests:

.. code-block:: python

    @pytest.mark.az_vcr()
    def test_some_command(az):
       res = az('arc <command> <action>', arg1='hello', arg2='v1')

       assert res.exit_code == 0
       assert res.output == {...}


A new file `cassettes/test_command_action.yaml` will be created next to your test
file on the first run. This file should be committed to a version control
for offline tests.
