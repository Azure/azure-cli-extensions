.. :changelog:

Release History
===============

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