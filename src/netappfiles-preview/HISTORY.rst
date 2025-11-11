.. :changelog:

Release History
===============
1.0.0b4
++++++++
* Remove msrestazure dependency

1.0.0b3
+++++
Add new command `az netappfiles volume list-quota-report` 
Add new command `az netappfiles volume splitclonefromparent` 

1.0.0b2
+++++
Support for api-version 2024-03-01-preview
`az netappfiles account backup-vault backup update` removed parameter `use_existing_snapshot`
`az netappfiles volume create` removed parameter `backup-enabled`
`az netappfiles volume create` removed parameter `replication-id`
`az netappfiles volume create` update parameter `usage-threshold`: updated property default from 107374182400 to 100
`az netappfiles volume create` update parameter `usage-threshold`: updated property default from 107374182400 to 100
`az netappfiles volume update` removed parameter `backup-enabled`
`az netappfiles volume update` removed parameter `remote-volume-resource_id`
`az netappfiles volume update` removed parameter `replication-id`

0.4.2
+++++
Support for api-version 2022-11-01-preview
Add command groups `az netappfiles accounts backup-vaults`
Remove command groups `az netappfiles accounts` `az netappfiles pools` as those are now in Azure CLI NetApp Files main module 

0.3.2
+++++
Remove min profile version and max core version

0.3.1
+++++
Add cli max core version

0.3.0
+++++
R4 RP standard

0.2.0
+++++
R3.5 RP standard
Includes export policy for volumes and active directory for accounts

0.1.0
+++++
* Initial release
