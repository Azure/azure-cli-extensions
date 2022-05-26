Release History
===============
1.1.0
---
* Command `az spring create` has new argument "--ingress-read-timeout" to set ingress read timeout when create Azure Spring App.
* Command `az spring update` has new argument "--ingress-read-timeout" to update ingress read timeout for Azure Spring App.
* Command `az spring create` has new argument "--enable-log-stream-public-endpoint" to set whether assign public endpoint for log streaming in vnet injection instance when create Azure Spring App.
* Command `az spring update` has new argument "--enable-log-stream-public-endpoint" to update whether assign public endpoint for log streaming in vnet injection instance for Azure Spring App.
* Command `az spring app create` has new argument "--assign_public_endpoint" to set whether assign endpoint URL which could be accessed out of virtual network for vnet injection instance app.
* Command `az spring app update` has new argument "--assign_public_endpoint" to update whether assign endpoint URL which could be accessed out of virtual network for vnet injection instance app.
* Command `az spring app deploy` and `az spring app deployment create` has new argument "--build-cpu" and "--build-memory" to set cpu and memory during build process.

1.0.0
---
* Initialize extension "Spring" to manage Azure Spring Apps resources.