.. :changelog:

Release History
===============
1.1.0
++++++
* Add: New command acr pipeline-run clean - Bulk deletes failed pipeline-runs.
* Add: New parameter to acr pipeline-run list --top - Displays only the n most recent pipeline-runs.
* Bug fix: ResourceNotFoundError will now be thrown if the resource does not exist when calling import-pipeline delete and export-pipeline delete.
* Bug fix: Help text typos fixed.

1.0.0
++++++
* Initial release.