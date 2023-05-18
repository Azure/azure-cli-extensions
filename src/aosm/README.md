# Microsoft Azure CLI 'aosm' Extension

This package is for the 'aosm' extension to support Azure Operator Service Manager 
functions.
i.e. `az aosm`

## Background

The `az aosm` extension is intended to provide support for working with AOSM
resources and definitions. Currently it only implements commands which aid the
process of publishing Network Function Definitions and Network Service Designs to
use with Azure Operator Service Manager or Network Function Manager.

## Installation

Eventually the extension will be published through the usual process and it will be
installed as usual, via `az extension add --name aosm`

Until then, the latest development version can be found here:
https://github.com/jddarby/azure-cli-extensions/releases/download/aosm-extension/aosm-0.1.0-py2.py3-none-any.whl

To install, download this wheel and run:
`az extension add --source path/to/aosm-0.1.0-py2.py3-none-any.whl`

## Bug Reporting

Especially as this extension is still in development, you may encounter bugs or
usability issues as you try to use it in its current form. It would be much
appreciated if you could report these so that we're aware of them!

The (Microsoft internal) process for bug reporting during development is here:
https://eng.ms/docs/strategic-missions-and-technologies/strategic-missions-and-technologies-organization/azure-for-operators/aiops/aiops-orchestration/aosm-product-docs/processes/bug_process

CLI issues should be tagged and triaged as UX bugs.

## Definitions

These commands help with the publishing of Network Function Definition and Network
Service Design resources.

### Pre-requisites

#### VNFs

For VNFs, you will need a single ARM template which would create the Azure resources
for your VNF, for example a Virtual Machine, disks and NICs. You'll also need a VHD
image that would be used for the VNF Virtual Machine.

### Command examples

Get help on command arguments

`az aosm -h`  
`az aosm definition -h`  
`az aosm definition build -h`  
etc...

All these commands take a `--definition-type` argument of `vnf`, `cnf` or `nsd`

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
