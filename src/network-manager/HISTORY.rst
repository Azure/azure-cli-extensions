.. :changelog:

Release History
===============
1.0.1
+++++
* `az network manager connect-config`: Fix cross-tenant resource id for `--hubs`

1.0.0
+++++
* Fix example and help info (Fix #6788)
* BREAKING CHANGE: Make params required and remove non-updatable params (Fix #6786)
* Fix `az network manager security-admin-config rule-collection rule update`: Fix to respect params provided. (Fix #6787)

1.0.0b2
+++++
* `az network manager group static-member create`: Fix cross-tenant --resource-id
* `az network manager post-commit`: Fix when no response body is returned

1.0.0b1
+++++
* Migrate to CodeGen V2

0.6.0
+++++
* `az network manager security-admin-config`: Upgrade API version from 2022-01-01 to 2022-05-01.
* Deprecate parameter `--display-name`.

0.5.3
+++++
* Fix force delete behavior.

0.5.2
+++++
* 'az network manager connection management-group': reopen the set of commands.

0.5.1
+++++
* 'az network manager group': remove parameters '--member-type' and '--display-name'
* 'az network manager security-user-config': hide this command
* 'az network manager group list-effect-vnet': hide this command
* 'az network manager delete': add parameter 'force'
* 'az network manager connect-config delete': add parameter 'force'
* 'az network manager security-admin-config rule-collection delete': add parameter 'force'
* 'az network manager security-admin-config rule-collection rule delete': add parameter 'force'

0.5.0
+++++
* 'az network manager list-effect-vnet': hide this command
* 'az network manager security-user-config rule-collection': hide this command
* 'az network manager security-user-config rule-collection rule ': hide this command
* 'az network manager group static-member update': hide this command
* 'az network manager list-active-security-user-rule': hide this command
* 'az network manager connect-config create': rename parameter '--hub'
* Bump up azure-mgmt-network SDK to 2022_02_01_preview

0.4.1
+++++
* 'az network manager connect-config update': update parameter '--connectivity-topology'
* 'az network manager group create': update parameter '--member-type' and remove parameters '--group-members' and '--conditional-membership'
* 'az network manager security-admin-config create': add parameter '--apply-on'

0.4.0
+++++
* Add new cmd `az network manager connection`
* Add new cmd `az network manager connection management-group`
* Add new cmd `az network manager scope connection`
* Add new cmd `az network manager group static-member`
* `az network manager group delete`: add parameter `force`
* `az network manager security-admin-config delete`: add parameter `force` and add parameter `recursive`
* Bump up azure-mgmt-network SDK to 2021_05_01_preview

0.3.0
+++++
* `az network manager list-active-connectivity-config`: rename parameter `region` to `regions`
* `az network manager security-user-config create`: remove parameter `security-type`
* `az network manager security-admin-config create`: remove parameter `security-type`
* Fix some mistakes on help messages.

0.2.0
+++++
* Rename `az network manager admin-rule collection` to `az network manager security-admin-config rule-collection`
* Rename `az network manager user-rule collection` to `az network manager security-user-config rule-collection`
* Rename `az network manager admin-rule` to `az network manager security-admin-config rule-collection rule`
* Rename `az network manager user-rule` to `az network manager security-user-config rule-collection rule`
* Add new cmd `az network manager list-effective-security-admin-rule`
* `network manager connect-config`: rename `--delete-peering` to `--delete-existing-peering`

0.1.0
++++++
* Initial release.
