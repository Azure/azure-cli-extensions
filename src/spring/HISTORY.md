Release History
===============
1.1.0
---
* Command `az spring create` has new argument "--ingress-read-timeout" to set ingress read timeout when create Azure Spring Apps.
* Command `az spring update` has new argument "--ingress-read-timeout" to update ingress read timeout for Azure Spring Apps.
* Command `az spring create` has new argument "--marketplace-plan-id" to purchase SaaS resource against given plan for Azure Spring Apps.
* Command `az spring create` and `az spring update` has new argument "--enable-log-stream-public-endpoint" to set whether assign public endpoint for log streaming in vnet injection instance.
* Command `az spring app create` and `az spring app update` has new argument "--assign_public_endpoint" to set whether assign endpoint URL which could be accessed out of virtual network for vnet injection instance app.
* Command `az spring app deploy` and `az spring app deployment create` has new argument "--build-cpu" and "--build-memory" to set cpu and memory during build process.
* Commands `az spring app create`, `az spring app update`, `az spring app deploy`, `spring app deployment create`
and `spring app deployment update` have new arguments "--enable-liveness-probe", "--enable-readiness-probe", "--enable-startup-probe", "--liveness-probe-config", "--readiness-probe-config", "--startup-probe-config" to customize the probe settings of user applications


1.0.0
---
* Initialize extension "Spring" to manage Azure Spring Apps resources.