.. :changelog:

Release History
===============
1.1.0
++++++
* az network front-door waf-policy create/update add: log scurbbing support

1.0.17
++++++
* az network front-door waf-policy managed-rules add: Fix managed-rule add issue for Microsoft_DefaultRuleSet with version 2.0 or higher.

1.0.16
++++++
* az network front-door routing-rule update: Fix unexpected configuration override when updating routing rule.

1.0.15
++++++
* Add az network front-door backend-pool backend update command: Update a backend to Front Door backend pool.
* Fix backend related bugs

1.0.14
++++++
* Migrate to Track2 SDK.

1.0.13
++++++
* az network front-door frontend-endpoint enable-https: allow secret-version to be optional to always use the 'Latest' version to support certificate auto-rotation.

1.0.12
++++++
* Add az network front-door check-name-availability command: Check the availability of a Front Door resource name.