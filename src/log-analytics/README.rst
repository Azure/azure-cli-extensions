Commands for working with Azure Log Analytics
==============================================

# Basic Usage

Query a Log Analytics workspace for data over the last 12 hours:
.. code:: 
    az monitor log-analytics query -w b8317023-66e4-4edc-8a5b-7c002b22f92f --analytics-query -t PT12H

Query multiple workspaces at once:
.. code::
    az monitor log-analytics query -w b8317023-66e4-4edc-8a5b-7c002b22f92f f5b6ed22-4942-41c4-becd-1943e5a1b71f
