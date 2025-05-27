.. :changelog:

Release History
===============
===============

##### 1.0.0
++++++
New commands added:
* perimeter associable-resource-type: list
* perimeter logging-configuration: list

Existing commands updated:
* perimeter delete: added --force-deletion parameter.
* Flattened output reponse for all commands.

Removed commands:
* perimeter onboarded-resources: list

##### 1.0.0b3
++++++
New commands added:
* perimeter logging-configuration: create, delete, show, update

##### 1.0.0b2
++++++
No new commands added. Flatten false the properties of the command output.


##### 1.0.0b1
++++++
No new commands added.
Commands for new api version 2023-08-01-preview added.

Existing commands updated:
* perimeter profile access-rule: create, show, update (added servicetag based rules).

##### 0.3.0
++++++
No new commands added or updated.
Commands for new api version 2023-07-01-preview added.

##### 0.2.1
++++++
No new commands added.

Existing commands updated:
* perimeter profile access-rule: create, update (remove existing "--nsp" paramter from request. Now access rule doesn't support creation/updation of perimeter based rules.

##### 0.2.0
++++++
New commands added:
* perimeter link: create, delete, list, show, update
* perimeter link-reference: delete, list, show

Existing commands updated:
* perimeter profile access-rule: create, delete, list, show, update (introduced new keys [--phone-numbers, --email-addresses] in request and response. Now access rule supports email/sms based outbound connections.

===============
##### 0.1.0
++++++
New commands added:
* perimeter: create, delete, list, show
* perimeter profile: create, delete, list, show 
* perimeter association: create, delete, list, show, update
* perimeter profile access-rule: create, delete, list, show, update
* perimeter onboarded-resources: list
