.. :changelog:

Release History
===============

1.2.6
++++++
* bugfix making it so the fields in the --input format are case-insensitive

1.2.5
++++++
* consolidating functions for --input policygen
* bugfix for "scenario" field in json input
* updating tests and examples to use azurelinux
* "name" field is required when using --input

1.2.4
++++++
* rolling back genpolicy version for Azure Linux V2 support instead of V3

1.2.3
++++++
* adding fragment support for VN2
* bugfix for vn2 workload identities
* no longer encouraged to have multiple images in the same tar file

1.2.2
++++++
* support for pure OCI v1 schema 2 formatted images
* adding debug logging
* changing where parameters and variables are filled in for arm templates
* updating documentation about fragments
* bugfix for exec processes in fragment generation
* bugfix for custom mount options in fragment generation

1.2.1
++++++
* updating genpolicy to version 3.2.0.azl3.genpolicy3

1.2.0
++++++
* fixing metadata for uploaded fragments
* fixing support for non-image feed names and attaching fragments to an image
* bug fixes for image-attached fragments
* adding ability to generate a fragment import from an image name using the remote attached fragments
* updating stdout import statement to look more like the file output
* adding `--omit-id` to the `acifragmentgen` command
* updating genpolicy to version 3.2.0.azl3.genpolicy2

1.1.1
++++++
* updating dmverity-vhd version with bugfix for empty image layers

1.1.0
++++++
* adding support for image-attached fragments via `acifragmentgen`
* adding workload identity support for VN2
* adding `--exclude-default-fragments` to disallow sidecars from policy
* adding `--omit-id` for policy stability across multiple image registries
* better handle broken base64 policies in templates
* improve error handling structure
* make some mount types in VN2 required readonly
* prompt users if they want to overwrite their policy in VN2
* changing where dmverity-vhd and sign1util binaries are fetched from. This includes a significant speedup in dmverity-vhd hashing

1.0.1
++++++
* getting rid of msrestazure dependency in _validators.py

1.0.0
++++++
* adding support for Virtual Node
* updating genpolicy version up through 3.2.0.azl1.genpolicy1

0.3.6
++++++
* updating genpolicy version up through 3.2.0.azl1.genpolicy0. Please note that this is a breaking change for deploying older policies. With the new node image, 0.3.6 or newer will be required.
* changing genpolicy flags to give full path to config files instead of path as a flag
* adding genpolicy flags for --containerd-pull, --containerd-socket-path, --rules-file-name, and --print-version
* `-c` flag for katapolicygen now supports persistent volume claims

0.3.5
++++++
* making diff mode more robust
* bugfix for arm template regex
* updating genpolicy version up through 3.2.0.azl0.genpolicy1
* adding configmap sidecar
* bugfix for seccompProfile missing after injecting policy
* adding cs2 support

0.3.4
++++++
* adding faster hashing flag to use buffered reader in dmverity-vhd

0.3.3
++++++
* improving testing standards from pytest recommendations
* updating genpolicy version up through genpolicy-0.6.2-5

0.3.2
++++++
* updating genpolicy version to allow for topologySpreadConstraints, version genpolicy-0.6.2-2

0.3.1
++++++
* removing unneeded print statement

0.3.0
++++++
* adding katapolicygen as a subcommand

0.2.18
++++++
* adding warning if printing to stdout

0.2.17
++++++
* updating dmverity-vhd version to allow for larger images with better memory efficiency

0.2.16
++++++
* adding stop signals as a field that is picked up from image manifest and placed into policy
* updating --print-existing-policy to print the whole policy
* refactoring tests to be more portable across releases

0.2.15
++++++
* updating dmverity-vhd interface to be more flexible with output formats
* bugfix for --print-existing-policy flag with parameter values

0.2.14
++++++
* changing the name of api_svn and framework_svn to api_version and framework_version
* changing fragment versions to an integer instead of semver
* bugfix for allowing 32bit python on a 64bit OS

0.2.13
++++++
* fixing bug where you could not pull by sha value if a tag was not specified
* fixing error message when attempting to use sha value with tar files
* making image caching template-wide instead of container group-wide

0.2.12
++++++
* adding ability for mixed-mode OCI image pulling, e.g. using tar files and remote registries in the same template
* adding option to use allow-all regex for environment variables
* tar file bug fixes

0.2.11
++++++
* bug fix for clean room scenario where non-existent docker client connection attempted to be closed
* adding ability for ARM Template workflows to use regex for environment variables
* fixing linux permissions for dmverity-vhd tool

0.2.10
++++++
* dmverity-vhd tool fixes
* changing startup checks to errors rather than warnings
* can specify image name in arm template by its SHA256 hash
* disabling stdio in pause container
* adding another README.md with more descriptive information

0.2.9
++++++
* adding support for exec_processes for non-arm template input
* adding --disable-stdio flag to disable stdio for containers
* changing print behavior by not needing both --print-policy in conjunction with --outraw or --outraw-pretty-print
* adding flag for --print-existing-policy that decodes and pretty prints the base64 encoded policy in the ARM template

0.2.8
++++++
* adding secureValue as a valid input for environment variables

0.2.7
++++++
* adding default mounts field for sidecars

0.2.6
++++++
* updating secretSource mount source to "plan9://" and adding vkMetrics and scKubeProxy to sidecar list

0.2.5
++++++
* removing default mounts and updating mount type to "bind"

0.2.4
++++++
* updating sidecar package name and svn

0.2.3
++++++
* added ability to use tarball as input for layer hashes and container manifests
* added initContainers as container source in ARM Template
* update dealing with liveness and readiness probes

0.2.2
++++++
* added pause container to customer container groups
* added caching for dm-verity calculation when using the same image multiple times in a container group
* added new rego variables
* made injecting security policies into ARM template the default behavior

0.2.1
++++++
* update rego format
* allow users to update the infrastructure fragment minimum svn value from command line arguments
* add check for arm64 architecture
* add policy diff feature
* add ability to generate policy based on image name
* add debug mode for rego policy
* add ability to inject policy into ARM template

0.2.0
++++++
* update to remove hardcoded side-cars
* update to create CCE Policy with ARM Template
* update to make rego the default output format

0.1.2
++++++
* update for enable restart field

0.1.1
++++++
* update for private preview

0.1.0
++++++
* Initial release.
