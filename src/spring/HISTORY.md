Release History
===============
1.6.8
---
* Add detail description to Default for argument `--backend-protocol`.

1.6.7
---
* Change all Azure Spring Apps API version to 2022-11-01-preview.

1.6.6
---
* Modify help text of name in command `az spring create` and `az spring app create`

1.6.5
---
* Add argument `--deployment-name` in command `az spring app create`.

1.6.4
---
* Add new commands `az spring application-configuration-service create` and `az spring application-configuration-service delete`.
* Add new commands `az spring service-registry create` and `az spring service-registry delete`.
* Add new commands `az spring gateway create` and `az spring gateway delete`.
* Add new commands `az spring api-portal create` and `az spring api-portal delete`.

1.6.3
---
* Deprecate the subcommand 'spring app binding'.

1.6.2
---
* Add new arguments `--apm-types`, `--properties` and `--secrets` for command `az spring gateway update`.

1.6.1
---
* Add type check for argument `--artifact-path`.

1.6.0
---
* Add argument `--client-auth-certs` in command `az spring app create` and `az spring app update`.

1.5.0
---
* Add the validator for `--build-env`.

1.4.2
---
* Fix the missing echo in `bash` after exiting from `az spring app connect`.

1.4.1
---
* Fix enabling dev tool failed when creating Azure Spring Apps Enterprise in command `az spring create --sku Enterprise --enable-application-live-view --enable-application-accelerator`.

1.4.0
---
* Show help link when `az spring app deploy` failed.

1.3.0
---
* Add new command group `az spring application-live-view` to manage Application Live View.
* Support route to app level in command `az spring gateway route-config create` and `az spring gateway route-config create`.
* Add new command group `az spring dev-tool` to manage Dev Tools.
* Add argument `--enable-application-live-view` in command `az spring create` to support enable application live view when creating Enterprise sku Spring resource.
* Add new command group `az spring application-accelerator customized-accelerator` to manage Customized Accelerator.
* Add new command group `az spring application-accelerator predefined-accelerator` to manage Predefined Accelerator.
* Add argument `--enable-application-accelerator` in command `az spring create` to support enable application accelerator when creating Enterprise sku Spring resource.

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