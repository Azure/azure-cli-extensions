.. :changelog:

Release History
===============

0.2.0
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
