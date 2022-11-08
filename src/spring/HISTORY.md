Release History
===============
1.2.0
---
* Add command `az spring list-marketplace-plan` to list all supported VMware product. For more detail, see https://learn.microsoft.com/en-us/azure/spring-apps/how-to-enterprise-marketplace-offer.
* Add argument `--marketplace-plan-id` in command `az spring create` to support purchasing different VMware product plan when creating Enterprise sku Spring resource.

1.1.14
---
* Add warn when update Config Server or Application Configuration Service with SSH auth.

1.1.13
---
* Stop execution and throw exception when operation status is `Failed`.

1.1.12
---
* Add warning logs when editing builders and buildpack bindings.

1.1.11
---
* Add command `az spring app deployment enable-remote-debugging`.
* Add command `az spring app deployment disable-remote-debugging`.
* Add command `az spring app deployment get-remote-debugging-config`.

1.1.10
---
* Remove `Preview` tag for user-assigned identities of apps.

1.1.9
---
* Fix the crash in windows.

1.1.8
---
* Add command `az spring app connect`.
* Add the parameter `language_framework` for deploying the customer image app.

1.1.7
---
* Update `minCliCoreVersion` requirement from `2.30.0` to `2.38.0`.
* Command `az spring create` and ` has new argument "--outboundType" to enable UDR for VNet instance.
* Command `az spring app create` and `az spring app update` has new argument "--ingress-read-timeout", "--ingress-send-timeout", "--session-affinity", "--session-max-age", "--backend-protocol" to customize the ingress settings of user applications.
* Add a new command `az spring build-service builder show-deployments` to list the deployments under a builder.

1.1.5
---
* Add service instance existance check before service creation

1.1.4
---
* Add warning that `az spring app-insights` don't support Enterprise tier.

1.1.3
---
* Enhance Application Insights settings when create service instance.

1.1.2
---
* Support configure Germination Grace Period Seconds for deployments.
* Fix the arguments parsing of the Command `az spring app create` with "--container-image".

1.1.1
---
* Support configure OpenAPI URI in Spring Cloud Gateway route configs.

1.1.0
---
* Command `az spring create` has new argument "--ingress-read-timeout" to set ingress read timeout when create Azure Spring Apps.
* Command `az spring update` has new argument "--ingress-read-timeout" to update ingress read timeout for Azure Spring Apps.
* Command `az spring create` and `az spring update` has new argument "--enable-log-stream-public-endpoint" to set whether assign public endpoint for log streaming in vnet injection instance.
* Command `az spring app create` and `az spring app update` has new argument "--assign-public-endpoint" to set whether assign endpoint URL which could be accessed out of virtual network for vnet injection instance app.
* Command `az spring app deploy` and `az spring app deployment create` has new argument "--build-cpu" and "--build-memory" to set cpu and memory during build process.
* Commands `az spring app create`, `az spring app update`, `az spring app deploy`, `spring app deployment create`
and `spring app deployment update` have new arguments "--enable-liveness-probe", "--enable-readiness-probe", "--enable-startup-probe", "--liveness-probe-config", "--readiness-probe-config", "--startup-probe-config" to customize the probe settings of user applications


1.0.0
---
* Initialize extension "Spring" to manage Azure Spring Apps resources.