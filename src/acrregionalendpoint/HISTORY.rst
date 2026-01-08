.. :changelog:

Release History
===============

1.0.0b1
+++++++
* Initial preview release for Azure Container Registry regional endpoints support.
* Add: `--enable-regional-endpoints` parameter to `az acr create` and `az acr update` commands to enable regional endpoint functionality.
* Add: `--all-endpoints` parameter to `az acr login` command to authenticate against all available regional endpoints.
* Add: Enhanced `az acr show` command to display `regionalEndpointEnabled` and `regionalEndpointHostNames` properties in registry information.
* Add: Enhanced `az acr show-endpoints` command to display comprehensive endpoint information including registry login server, data endpoints, and regional endpoints.
* Add: Enhanced `az acr import` command to automatically detect and handle regional endpoint URIs in source image specifications.