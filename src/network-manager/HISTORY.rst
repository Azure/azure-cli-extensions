.. :changelog:

Release History
===============
0.4.1
+++++
* 'az network manager connect-config update': update parameter '--connectivity-topology'
* 'az network manager group create': update parameter '--member-type' and remove parameters `--group-members` and '--conditional-membership'
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
