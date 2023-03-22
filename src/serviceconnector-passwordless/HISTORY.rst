.. :changelog:

Release History
===============
0.2.2
++++++
* Update dependency psycopg2 to psycopg2-binary.

0.2.1
++++++
* Use the client ip in SQL connection output to update firewall rule.

0.2.0
++++++
* Remove firewall rule to avoid security issue. Prompt confirmation before open all IPs. Add param `--yes` to skip the confirmation. 

0.1.0
++++++
* Initial release.