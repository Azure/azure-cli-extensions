.. :changelog:

Release History
===============

0.1.0
++++++
* Initial release.

0.2.0
++++++
* Bump version to 2021-07-12.
* Update: host_pool_name max length up to 64 characters long to Fix [19298](https://github.com/Azure/azure-cli/issues/19298)
* `az desktopvirtualization workspace create` Change: `--location` required to False
* `az desktopvirtualization applicationgroup create` Change: `--location` required to False
* `az desktopvirtualization hostpool create` Change `--preferred-app-group-type` required to True
* `az desktopvirtualization hostpool create` Change `--personal-desktop-assignment-type` required to False
* `az desktopvirtualization hostpool create` Change `--location` required to False
* `az desktopvirtualization hostpool create`  Add value `BYODesktop` to `--host-pool-type`
* `az desktopvirtualization hostpool create`  Deprecate parameter `-sso-context` in version 2020-11-10-preview
* `az desktopvirtualization hostpool create`  Add new parameter `--ssoadfs-authority` to support WVD SSO certificates
* `az desktopvirtualization hostpool create`  Add new parameter `--sso-client-id` to support WVD SSO certificates
* `az desktopvirtualization hostpool create`  Add new parameter `--sso-client-secret-key-vault-path` to support WVD SSO certificates
* `az desktopvirtualization hostpool create`  Add new parameter `--sso-secret-type` to support WVD SSO certificates
* `az desktopvirtualization hostpool create`  Add new parameter `--preferred-app-group-type` to support choosing the type of preferred application group type
* `az desktopvirtualization hostpool create`  Add new parameter `--start-vm-on-connect` to support turning on/off StartVMOnConnect feature
* `az desktopvirtualization hostpool update` Support parameter `--vm-template`
* `az desktopvirtualization hostpool update`  Deprecate parameter `-sso-context` in version 2020-11-10-preview
* `az desktopvirtualization hostpool update`  Add new parameter `--ssoadfs-authority` to support WVD SSO certificates
* `az desktopvirtualization hostpool update`  Add new parameter `--sso-client-id` to support WVD SSO certificates
* `az desktopvirtualization hostpool update`  Add new parameter `--sso-client-secret-key-vault-path` to support WVD SSO certificates
* `az desktopvirtualization hostpool update`  Add new parameter `--sso-secret-type` to support WVD SSO certificates
* `az desktopvirtualization hostpool update`  Add new parameter `--preferred-app-group-type` to support choosing the type of preferred application group type
* `az desktopvirtualization hostpool update`  Add new parameter `--start-vm-on-connect` to support turning on/off StartVMOnConnect feature
* `az desktopvirtualization hostpool` Add command `retrieve-registration-token` to retrieve registration token