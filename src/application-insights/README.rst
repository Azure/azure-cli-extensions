Commands for working with Azure Application Insights
==============================================

# Basic Usage

Query a Application Insights application for data over the last 12 hours:
.. code:: 
    az monitor app-insights query --app b8317023-66e4-4edc-8a5b-7c002b22f92f --analytics-query "availabilityResults | summarize count() by bin(timestamp, 15m), success" -t PT12H

Query multiple workspaces at once:
.. code::
    az monitor app-insights query --app b8317023-66e4-4edc-8a5b-7c002b22f92f f5b6ed22-4942-41c4-becd-1943e5a1b71f --analytics-query "requests | summarize count() by toint(resultCode)"
