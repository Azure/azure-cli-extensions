Release History
===============
0.2.2
-----
* Validate that target machine exists before attempting to connect.
* ssh config accepts relative path for --file.
* Make --local-user mandatory for Windows target machines.
* For ssh config, relay information is stored under az_ssh_config folder.
* New optional parameter --arc-proxy-folder to determine where arc proxy is stored.
* Relay information lifetime is synced with certificate lifetime for AAD login.

0.2.1
-----
* SSHArc Private Preview 2

0.2.0
-----
* SSHArc Private Preview 1

0.1.9
-----
* Add support for connecting to Arc Servers using AAD issued certificates.
* Add support for connecting to local users on Azure VMs and Arc Server using certs-based, key-based, and password-based authentication
* Add --ssh-client-path, --resource-id, --local-user, --cert-file arguments.

0.1.8
-----
* Rollback from version 0.1.7 to 0.1.6 to remove preview features.

0.1.7
-----
* Introduced preview features.

0.1.6
-----
* Add support for direct MSAL usage in newer Azure CLI (beta currently)
* Add support for port option and ssh additional arguments option
* Remove directory creation as part of ssh_config creation
* Try .pub for public key if only private key is specified
* Add --hostname to --ip argument
* Add fallback to private IP with warning
* Add support for USGov and China clouds

0.1.5
-----
* Add public key error message
* Cleanup documentation

0.1.4
-----
* Change to use the first in the list of validprincipals as the default username
* Remove old paramiko dependency

0.1.3
-----
* Add support for using private IPs
* Add option alias `--name` for `--vm-name`
* Use lowercase username by default
* Fix various typos

0.1.2
-----
* Add support for hardware tokens (don't require the private key be passed in)
* Add support for cert signing only
* Add numerous short parameters
* Add support for and switch default behavior to ephemeral keypair generation when no public key is passed in
* Add support for Host * by not writing Hostname into ssh_config files

0.1.1
-----
* Fix bash not work problem.

0.1.0
-----
* Initial release.