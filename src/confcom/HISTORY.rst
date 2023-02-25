.. :changelog:

Release History
===============
0.2.11
* bug fix for clean room scenario where non-existent docker client connection attempted to be closed
* adding ability for ARM Template workflows to use regex for environment variables
* fixing linux permissions for dmverity-vhd tool

0.2.10
* dmverity-vhd tool fixes
* changing startup checks to errors rather than warnings
* can specify image name in arm template by its SHA256 hash
* disabling stdio in pause container
* adding another README.md with omre descriptive information

0.2.9
* adding support for exec_processes for non-arm template input
* adding --disable-stdio flag to disable stdio for containers
* changing print behavior by not needing both --print-policy in conjunction with --outraw or --outraw-pretty-print
* adding flag for --print-existing-policy that decodes and pretty prints the base64 encoded policy in the ARM template

0.2.8
* adding secureValue as a valid input for environment variables

0.2.7
* adding default mounts field for sidecars

0.2.6
* updating secretSource mount source to "plan9://" and adding vkMetrics and scKubeProxy to sidecar list

0.2.5
* removing default mounts and updating mount type to "bind"

0.2.4
* updating sidecar package name and svn

0.2.3
* added ability to use tarball as input for layer hashes and container manifests
* added initContainers as container source in ARM Template
* update dealing with liveness and readiness probes
* update

0.2.2
* added pause container to customer container groups
* added caching for dm-verity calculation when using the same image multiple times in a container group
* added new rego variables
* made injecting security policies into ARM template the default behavior

0.2.1
* update rego format
* allow users to update the infrastructure fragment minimum svn value from command line arguments
* add check for arm64 architecture
* add policy diff feature
* add ability to generate policy based on image name
* add debug mode for rego policy
* add ability to inject policy into ARM template

0.2.0
* update to remove hardcoded side-cars
* update to create CCE Policy with ARM Template
* update to make rego the default output format

0.1.2
* update for enable restart field

0.1.1
* update for private preview

0.1.0
++++++
* Initial release.