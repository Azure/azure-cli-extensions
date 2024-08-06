.. :changelog:

Release History
===============

1.2.1
++++++++++++++++++
* `az monitor app-insights component connect-webapp/connect-function`: Add `connection_string` auto setting for webapp/function.

1.2.0
++++++++++++++++++
* `az monitor app-insights`: Add new command group `workbook` to support managing workbook.

1.1.0
++++++++++++++++++
* `az monitor app-insights component`: Add new command group `favorite` to support managing favorite.
* `az monitor app-insights component`: Add new command group `quotastatus` to support managing quotastatus.
* `az monitor app-insights`: Add new command group `my-workbook` to support managing my-workbook.
* `az monitor app-insights`: Add new command group `workbook revision` to support managing workbook revision.
* `az monitor app-insights`: Add new command `migrate-to-new-pricing-model` to support migrating to new pricing model.

1.0.0
++++++++++++++++++
* Migrate manual code to automatic code by aaz tool.


0.1.19
++++++++++++++++++
* `az monitor app-insights web-test`: Upgrade api-version to 2022-06-15.

0.1.18
++++++++++++++++++
* `az monitor app-insights web-test`: Fix issue for header property create and display.

0.1.17
++++++++++++++++++
* `az monitor app-insights component connect-webapp`: Support cross resource groups.
* `az monitor app-insights component connect-function`: Support cross resource groups.

0.1.16
++++++++++++++++++
* `az monitor app-insights query`: Fix application could not be found.

0.1.15
++++++++++++++++++
* `az monitor app-insights web-test`: Create/list/update/show/delete Application Insights Web Test.

0.1.14
++++++++++++++++++

* `az monitor app-insights events show`: Add enum values for `--type`.

0.1.13
++++++++++++++++++

* `az monitor app-insights component connect-function`: Enable application insights on Azure function.

0.1.12
++++++++++++++++++

* `az monitor app-insights component connect-webapp`: Enable application insights on web app.

0.1.11
++++++++++++++++++

* `az monitor app-insights component update`: Update consent message.

0.1.10
++++++++++++++++++

* `az monitor app-insights component update`: Prompt consent when migrating to workspace-centric workspace.

0.1.9
++++++++++++++++++

* Argument `--cap` in `az monitor app-insights component billing update` supports float value.
* [Incoming Breaking Change] Default write permission would be removed for `az monitor app-insights api-key` in the future.

0.1.8
++++++++++++++++++

* Argument `--offset` in `az monitor app-insights query` supports iso8601 format.

0.1.7
++++++++++++++++++

* support linked storage account for application insights component.
* support link one log analytics workspace to application insights component.
* support setting public network access for application insights component.
* one fix for api-key creation.

0.1.6
++++++++++++++++++

* Typo fixes

0.1.5
++++++++++++++++++

* Small fixes for help messages and error messages

0.1.4
++++++++++++++++++

* Support managing billing features of application insights component.

0.1.3
++++++++++++++++++

* Set min azure cli core version to 2.0.79

0.1.2
++++++++++++++++++

* Support the usage in Azure China Cloud.

0.1.0
++++++++++++++++++

* Initial release.