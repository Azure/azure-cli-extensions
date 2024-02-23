.. :changelog:

Release History
===============
1.0.1
++++++
* Normalization module name in setup

1.0.0
++++++
* Enable all of the facilities of `data-collection` in stable version `2022-06-01`
* Remove `id_part` of subcommands `data-flow`, `log-analytics`, `performance-counter`, `windows-event-log` and `syslog` for `az monitor data-collection rule`

0.4.1
++++++
* `az monitor data-collection rule association create/update`: Add parameter --endpoint-id.

0.4.0
++++++
* Bump api version to `2022-06-01`

0.3.1
++++++
* `az monitor data-collection rule create`: Add json file example for parameter --rule-file.

0.3.0
++++++
* `az monitor data-collection rule create`: Add parameter --rule-file.
* `az monitor data-collection rule create`: Remove parameters --data-flows, --log-analytics, --monitor-metrics, --performance-counters, --windows-event-logs, --syslog and --extensions.
* `az monitor data-collection rule association list`: Add parameter --data-collection-endpoint-name.
* Bump api version from 2021-04-01 to 2021_09_01_preview.

0.2.0
++++++
* GA release.
* Add `az monitor data-collection endpoint` command group.

0.1.0
++++++
* Initial release.
