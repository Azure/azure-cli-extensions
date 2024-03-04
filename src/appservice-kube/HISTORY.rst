.. :changelog:

Release History
===============
0.1.10
++++++
* Add command `az webapp list-runtimes --is-kube` for arc enabled app service
* Fix language version unsupported issue on `az webapp create`

0.1.9
++++++
* `az webapp scale`: Add validation to reject non-arc enabled app service

0.1.8
++++++
* Fix appservice kube - No module named 'azure.mgmt.web.v2021_01_01'

0.1.7
++++++
* Allow creating Azure Arc-hosted Function Apps without storage accounts

0.1.6
++++++
* Fix TypeError on 'az webapp create'

0.1.5
++++++
* SSL bind bug fix
* Fix compatibility issue with CLI version 2.34.1

0.1.4
++++++
* Ensure compatibility of 'az webapp create' and 'az functionapp create' with CLI version 2.34.0

0.1.3
++++++
* Update functionapp runtimes and support v4 functionapps

0.1.2
++++++
* Allow passing custom locations by name if in the same resource group as the app/plan
* Add App Service Environment V3 SKUs to 'az appservice plan create' help text
* Fix bug causing App Service Kube Environment "resourceGroup" value to be null in command responses

0.1.1
++++++
* Fix ssl binding for web apps in kubernetes environments

0.1.0
++++++
* Initial public preview release.
