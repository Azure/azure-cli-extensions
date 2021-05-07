.. :changelog:

Release History
===============

0.1.17
++++++
* az webapp scale command

0.1.16
++++++
* Change k8se app sku to "K1" instead of "ANY", "ELASTICANY"

0.1.15
++++++
* Clean up az kube create parameters
* Update to 2020-12-01 SDK for k8se commands (removes --force parameter for az appservice kube delete)

0.1.14
++++++
* Stop using webapp list in creates - temporary fix for demo

0.1.13
++++++
* az webapp/functionapp create without --plan for k8se apps
* Change ASP "kind" back to "linux,kubernetes..." and detect k8se apps in webapp/functionapp create using customlocation/plan sku

0.1.12
++++++
* Allow specifying custom location by name as well, in appservice plan create
* az appservice kube create command
* Change ASP "kind" back to "K8SE", reserved to None so that "kind" is saved properly

0.1.11
++++++
* Oops broke AppService plan create for non-k8se 

0.1.10
++++++
* Functions should not pull docker image
* Functionapp deployment source config-zip command
* AppService plan create should drop --kube-environment and --kube-sku
* Change kind to 'linux,kubernetes'

0.1.9
++++++
* Fix webapp zipdeploy command
* Fix webapp config container set command

0.1.8
++++++
* Remove azure-cli-core dependency

0.1.7
++++++
* Update kube environments SDK
* Delete old parameters no longer in API

0.1.6
++++++
* Update SDK to fix appservice kube delete command

0.1.5
++++++
* Fix webapp show command

0.1.4
++++++
* Fix for including getfunctionsjson.sh in the extension package

0.1.3
++++++
* Add bring your own AKS cluster support

0.1.2
++++++
* Retrieve function triggers for kube function apps

0.1.1
++++++
* Add az webapp up support

0.1.0
++++++
* Initial release.