.. :changelog:

Release History
===============
===============

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
