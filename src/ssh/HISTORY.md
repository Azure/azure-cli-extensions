Release History
===============
2.0.3
-----
* [Bug Fix] Ensure that certificate validity value is always an integer when retrieving relay information for connecting to Arc Machines.
* Add support to ARM64 clients when connecting to Arc Machines. Connect proxy now available for ARM64 architecture.

2.0.2
-----
* [Bug Fix] Fix logic that checks for the OS of the target machine to avoid "cannot unpack non-iterable NoneType object" error

2.0.1
-----
* [Bug fix] For connections to arc resources, stop attempting to create new service configuration if user has no permission to read service configuration.

2.0.0
-----
* [BREAKING CHANGE] Update Microsoft.HybridConnectivity SDK to stable version, which adds functionality to enable SSH connections on specified ports in your Arc Server using an API, instead of enabling ports for connection locally in the Arc Agent running in the target machine. New connections might fail after updating the extension, since the port for connection will need to be enabled at the HybridConnectivity Resource Provider at the first connection attempt. This change doesn't affect those who use this extension to connect to Azure Virtual Machines.
* Move Microsoft.HybridCompute, Microsoft.HybridConnectivity, and Microsoft.ConnectedVMwarevSphere SDKs to AAZ
* Add support to update Service Configuration at runtime
* Add --yes-without-prompt parameter for updating Service Configuration in automation scenarios

1.1.6
-----
* Fix issue of getting `publicIPAddress` error for `az ssh vm` CLI command  

1.1.5
-----
* Fix issue of getting vm network interface `publicIPAddress` ref 

1.1.4
-----
* Remove dependency to NETWORK SDK

1.1.3
-----
* Add support to Microsoft.ConnectedVMwarevSphere/virtualMachines Resource Type.
* Correct the format of expected input for --resource-type parameter. From Resource Provider name (e.g. "Microsoft.HybridCompute") to Resource Type name (e.g. "Microsoft.HybridCompute/machines").
* [bug fix] SSH Banners are printed before authentication.

1.1.2
-----
* Remove dependency to cryptography (Az CLI core alredy has cryptography)
* New RDP over SSH feature

1.1.1
-----
* Undo changes to rely on PATH variable to find SSH executables on Windows. Look for executables under "C:\Windows\System32\OpenSSH"

1.1.0
-----
* SSHArc Public Preview
* Add support for connecting to Arc Servers using AAD Certificates or Local User credentials.
* New command az ssh arc.
* New parameters: --resource-type and --ssh-proxy-folder.
* Validate that target machine exists before attempting to connect.
* Stop looking for OpenSSH client executables under C:\Windows\System32\OpenSSH on Windows. Path variable must be set properly for pre-installed OpenSSH.
* Append username to host name on config files when using local user credentials.

1.0.1
-----
* Added --ssh-client-folder parameter.
* Fixed issues caused when there are spaces or non-english characters in paths provided by users.
* Ensure all paths provided by users are converted to absolute paths.
* Print OpenSSH error messages to console on "az ssh vm".
* Print level1 SSH client log messages when running "az ssh vm" in debug mode.
* Change "isPreview".
* Correctly find pre-installed OpenSSH binaries on Windows 32bit machines.

1.0.0
-----
* Delete all keys and certificates created during execution of ssh vm.
* Add --keys-destination-folder to ssh config
* Keys generated during ssh config are saved in az_ssh_config folder in the same directory as --file.
* Users no longer allowed to run ssh cert with no parameters. 
* When --public-key-file/-f is not provided to ssh cert, generated public and private keys are saved in the same folder as --file.
* Add support to connect to local users on local machines using key based, cert based, or password based authentication.

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
