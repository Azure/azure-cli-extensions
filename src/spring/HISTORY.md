Release History
===============
1.1.0
---
* Command `az spring create` has new argument "--ingress-read-timeout" to set ingress read timeout when create Azure Spring Apps.
* Command `az spring update` has new argument "--ingress-read-timeout" to update ingress read timeout for Azure Spring Apps.
* Command `az spring create` has new argument "--marketplace-plan-id" to purchase SaaS resource against given plan for Azure Spring Apps.
* Command `az spring app deploy` and `az spring app deployment create` has new argument "--build-cpu" and "--build-memory" to set cpu and memory during build process.

1.0.0
---
* Initialize extension "Spring" to manage Azure Spring Apps resources.