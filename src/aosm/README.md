# Microsoft Azure CLI 'aosm' Extension
==========================================

This package is for the 'aosm' extension to support Azure Operator Service Manager 
functions.
i.e. `az aosm`

Install via `az extension add --name aosm`


# Background
The `az aosm` extension provides support for publishing Network Function Definitions
to use with Azure Operator Service Manager or Network Function Manager.

# Pre-requisites
## VNFs
For VNFs, you will need a single ARM template which would create the Azure resources
for your VNF, for example a Virtual Machine, disks and NICs. You'll also need a VHD
image that would be used for the VNF Virtual Machine.

# Command examples

Get help on command arguments

`az aosm -h` 
`az aosm definition -h`
`az aosm definition build -h`
etc...

All these commands take a `--definition-type` argument of `vnf`, `cnf` or (coming) `nsd`

Create an example config file for building a definition

`az aosm definition generate-config --config-file input.json`

This will output a file called `input.json` which must be filled in. 
Once the config file has been filled in the following commands can be run.

Build a definition locally

`az aosm definition build --config-file input.json`

Build and publish a definition

`az aosm definition build --config-file input.json --publish`

Publish a pre-built definition

`az aosm definition publish --config-file input.json`

Delete a published definition

`az aosm definition delete --config-file input.json`

Delete a published definition and the publisher, artifact stores and NFD group

`az aosm definition delete --config-file input.json --clean`
