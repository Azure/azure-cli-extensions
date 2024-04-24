Release History
===============
1.20.1
---
* Add command to show the configurations pulled by Application Configuration Service from upstream Git repositories. `az spring application-configuration-service config show`.

1.20.0
---
* Change default Application Configuration Service generation value to Gen2.

1.19.4
---
* Enhance managed component log streaming when `-i/--instance` and `--all-instances` parameters are not specified.

1.19.3
---
* Add arguments `--refresh-interval` in `spring application-configuration-service create` and `spring application-configuration-service update`.

1.19.2
---
* Add runtime version `Java_21`.

1.19.1
---
* Create workspace-based Application Insights instead, since classic Application Insights will be retired on 29 February 2024.

1.19.0
---
* Add new commands for managed component log streaming `az spring component list`, `az spring component instance list` and `az spring component logs`.

1.18.0
---
* Add arguments `--bind-service-registry` in `spring app create`.
* Add arguments `--bind-application-configuration-service` in `spring app create`.

1.17.0
---
* Add arguments `--enable-api-try-out` in `spring api-portal update`

1.16.0
---
* Add arguments `--enable-planned-maintenance`, `--planned-maintenance-day` and `--planned-maintenance-start-hour` in `az spring update` to support configuring Planned Maintenance.

1.15.1
---
* Add arguments `--apms` for Spring Cloud Gateway.

1.15.0
---
* Add arguments `--type` and `--git-sub-path` in `spring application-accelerator customized-accelerator create` and `spring application-accelerator customized-accelerator update` for accelerator fragment support.
* Add new argument `--server-version` in `az spring app deploy` and `az spring app deployment create` to support WAR file deployment in Standard tier. 
* Add argument `--enable-auto-sync` in `az spring certificate add`.
* Add new command `az spring certificate update` to update a certificate.
* Add new command `az spring list-support-server-versions` to list all supported server versions.
* Fix `list-marketplace-plan` command.

1.14.3
---
* Make error message for `az spring app logs` more readable.  

1.14.2
---
* Add new command `az spring flush-virtualnetwork-dns-settings` to flush virtual network DNS settings for the service instance.

1.14.1
---
* Support up to 1000 app instances in Enterprise tier.

1.14.0
---
* Add new command `az spring application-configuration-service create --generation` to support creating Application Configuration Service with different generation
* Add new command `az spring application-configuration-service update --generation` to support updating Application Configuration Service to different generation
* Add new command `az spring application-configuration-service git repo add --ca-cert-name` to support binding certificate to Application Configuration Service Gen2

1.13.3
---
* Add arguments `--allowed-origin-patterns`, `--addon-configs-json` and `--addon-configs-file` in `az spring gateway update`.
* Add new command `az spring gateway restart` to restart Spring Cloud Gateway.

1.13.2
---
* Add argument `--build-certificates` in `az spring app deploy`.

1.13.1
---
* Fix the parameter `--no-wait` of the command -- `az spring build-service update`.

1.13.0
---
* Add new command -- `az spring apm show` to show the APM resource.
* Add new command -- `az spring apm create` to create APM resource.
* Add new command -- `az spring apm update` to update APM resource.
* Add new command -- `az spring apm delete` to delete APM resource.
* Add new command -- `az spring apm enable-globally` to enable an APM globally.
* Add new command -- `az spring apm disable-globally` to disable an APM globally.
* Add new command -- `az spring apm list-support-types` to list all the supported APM types.
* Add new command -- `az spring apm list` to list all the APM resources.
* Add new command -- `az spring apm list-enabled-globally` to list all the APMs enabled globally.

1.12.2
---
* Add default `enabled_state` for `az spring config-server set` in Standard Counsumption tier.

1.12.1
---
* Add new command -- `az spring eureka-server show` to show the Eureka server resource in consumption tier.
* Add new command -- `az spring eureka-server enable` to enable the Eureka server resource in consumption tier.
* Add new command -- `az spring eureka-server disable` to disable the Eureka server resource in consumption tier.
* Add new command -- `az spring config-server enable` to enable the Config server resource in consumption tier.
* Add new command -- `az spring config-server disable` to disable the Config server resource in consumption tier.

1.12.0
---
* Add new command `az spring container-registry create` to craete container registry resource.
* Add new command `az spring container-registry delete` to delete container registry resource.
* Add new command `az spring container-registry list` to list all the container registry resources.
* Add new command `az spring build-service update` to update build service.
* Add new command `az spring build-service show` to show build service resource.
* Add new parameter `--workload-profile` for `az spring app create` and `az spring app update`.

1.11.3
---
* Fix `az spring create` command with `--container-registry-server`, `--container-registry-username` and `--container-registry-password`.
* Fix the help message for parameter `--sku` of `az spring create` and `az spring update` commands.

1.11.2
---
* Refine `az spring app create` command from 3 steps to 2 steps.

1.11.1
---
* Add argument `--ca-cert-name` in `az spring application-accelerator customized-accelerator update` and command `az spring application-accelerator customized-accelerator sync-cert`.
* Support client cert validation for customized accelerator with CA certificate.
* Add arguments `--enable-cert-verify` and `--certificate-names` in `az spring gateway update` and command `az spring gateway sync-cert`.
* Support client cert validation for Spring Cloud Gateway.

1.11.0
---
* Deprecate parameter `--enable-log-stream-public-endpoint` when creating/updating service 
* Add new parameter `--enable-dataplane-public-endpoint` when creating/updating service 

1.10.0
---
* Print more logs for app deployment

1.9.2
---
* Fix `ingress_read_timeout` and `session_max_age` validation error

1.9.1
---
* Support subPath for bring your own persistent storage feature.
* Add new parameter `--enable-sub-path` into `az spring append-persistent-storage` to enable subPath feature.

1.9.0
---
* Add new command -- `az spring build-service build create` to create the build resource when using your own container registry.
* Add new command -- `az spring build-service build update` to update the build resource when using your own container registry.
* Add new command -- `az spring build-service build show` to show the build resource.
* Add new command -- `az spring build-service build list` to list all build resource.
* Add new command -- `az spring build-service build delete` to delete the build resource.
* Add new command -- `az spring build-service build result show` to show the build result by build name and result name.
* Add new command -- `az spring build-service build result list` to list all build results of the build resource.
* Add new command -- `az spring container-registry update` to update container registry resource.
* Add new command -- `az spring container-registry show` to show the container registry resource.
* Add new parameters -- `--disable-build-service`, `--container-registry-server`, `--container-registry-username` and `--container-registry-password` when creating service.

1.8.0
---
* Add Azure Spring Apps StandardGen2 tier.

1.7.3
---
* Fix `subscription_id` AAZSimpleValue type error

1.7.2
---
* Support `--no-wait` in `az spring dev-tool`.
* [BREAKING CHANGE] Add delete confirmation in `az spring dev-tool` and `az spring application-live-view`.

1.7.1
---
* Remove dependency to NETWORK SDK

1.7.0
---
* Print application logs when create/update deployment
* Bypass jar check for enterprise tier
* Add java runtime check for jar file

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
