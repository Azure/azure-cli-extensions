.. :changelog:

Release History
===============

1.0.0
++++++
*Migrate to aaz commands

0.2.0
++++++
* Bump version to 2021-07-12.
* Fix #19298: `az desktopvirtualization hostPool show`: Support the maximum length of the host pool name to 64 characters
* `az desktopvirtualization workspace create` Change the argument `--location` from required to optional
* `az desktopvirtualization applicationgroup create` Change the argument `--location` from required to optional
* `az desktopvirtualization hostpool create` Change the argument `--preferred-app-group-type` from optional to required
* `az desktopvirtualization hostpool create` Change the argument `--personal-desktop-assignment-type` from required to optional
* `az desktopvirtualization hostpool create` Change the argument `--location` from required to optional
* `az desktopvirtualization hostpool create`  Add value `BYODesktop` to `--host-pool-type`
* `az desktopvirtualization hostpool create`  Deprecate argument `-sso-context` in version 2020-11-10-preview
* `az desktopvirtualization hostpool create`  Add new argument `--ssoadfs-authority` to support WVD SSO certificates
* `az desktopvirtualization hostpool create`  Add new argument `--sso-client-id` to support WVD SSO certificates
* `az desktopvirtualization hostpool create`  Add new argument `--sso-client-secret-key-vault-path` to support WVD SSO certificates
* `az desktopvirtualization hostpool create`  Add new argument `--sso-secret-type` to support WVD SSO certificates
* `az desktopvirtualization hostpool create`  Add new argument `--preferred-app-group-type` to support choosing the type of preferred application group type
* `az desktopvirtualization hostpool create`  Add new argument `--start-vm-on-connect` to support turning on/off StartVMOnConnect feature
* `az desktopvirtualization hostpool update` Support argument `--vm-template`
* `az desktopvirtualization hostpool update`  Deprecate argument `-sso-context` in version 2020-11-10-preview
* `az desktopvirtualization hostpool update`  Add new argument `--ssoadfs-authority` to support WVD SSO certificates
* `az desktopvirtualization hostpool update`  Add new argument `--sso-client-id` to support WVD SSO certificates
* `az desktopvirtualization hostpool update`  Add new argument `--sso-client-secret-key-vault-path` to support WVD SSO certificates
* `az desktopvirtualization hostpool update`  Add new argument `--sso-secret-type` to support WVD SSO certificates
* `az desktopvirtualization hostpool update`  Add new argument `--preferred-app-group-type` to support choosing the type of preferred application group type
* `az desktopvirtualization hostpool update`  Add new argument `--start-vm-on-connect` to support turning on/off StartVMOnConnect feature
* `az desktopvirtualization hostpool` Add command `retrieve-registration-token` to retrieve registration token

0.1.0
++++++
* Initial release.
