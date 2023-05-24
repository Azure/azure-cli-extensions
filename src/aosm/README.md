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
https://github.com/jddarby/azure-cli-extensions/releases/download/aosm-extension/aosm-0.2.0-py2.py3-none-any.whl

To install, download this wheel and run:
`az extension add --source path/to/aosm-0.2.0-py2.py3-none-any.whl`

## Updating 

We are currently not bumping versions, so if you would like the most up to date version of the CLI. You should run:
'az extension remove --name aosm'

And then re-add with the new wheel, as detailed in Installation above. 

## Bug Reporting

Especially as this extension is still in development, you may encounter bugs or
usability issues as you try to use it in its current form. It would be much
appreciated if you could report these so that we're aware of them!

The (Microsoft internal) process for bug reporting during development is here:
https://eng.ms/docs/strategic-missions-and-technologies/strategic-missions-and-technologies-organization/azure-for-operators/aiops/aiops-orchestration/aosm-product-docs/processes/bug_process

CLI issues should be tagged and triaged as UX bugs.

## nfd and nsd commands

These commands help with the publishing of Network Function Definition and Network
Service Design resources.

## Overview of function
A generic workflow of using the tool would be:
- Find the pre-requisite items you require for your use-case
- Run a `generate-config` command to output an example JSON config file for subsequent commands
- Fill in the config file
- Run a `build` command to output one or more bicep templates for your Network Function Definition or Network Service Design
- Review the output of the build command, edit the output as necessary for your requirements
- Run a `publish` command to:
    * Create all pre-requisite resources such as Resource Group, Publisher, Artifact Stores, Groups
    * Deploy those bicep templates
    * Upload artifacts to the artifact stores

### Pre-requisites

#### VNFs

For VNFs, you will need a single ARM template which would create the Azure resources
for your VNF, for example a Virtual Machine, disks and NICs. You'll also need a VHD
image that would be used for the VNF Virtual Machine.

#### CNFs

For CNFs, you must provide helm packages with an associated schema. When filling in the input.json file, you must list helm packages in the order they are to be deployed. For example, if A must be deployed before B, your input.json should look something like this:

    "helm_packages": [
        {
            "name": "A",
            "path_to_chart": "Path to package A",
            "depends_on": [
                "Names of the Helm packages this package depends on"
            ]
        },
        {
            "name": "B",
            "path_to_chart": "Path to package B",
            "depends_on": [
                "Names of the Helm packages this package depends on"
            ]
        },

### Command examples

Get help on command arguments

`az aosm -h`
`az aosm nfd -h`
`az aosm nfd build -h`
etc...

All these commands take a `--definition-type` argument of `vnf` or `cnf`

Create an example config file for building a definition

`az aosm nfd generate-config`

This will output a file called `input.json` which must be filled in. 
Once the config file has been filled in the following commands can be run.

Build an nfd definition locally

`az aosm nfd build --config-file input.json`

Build and publish a definition

`az aosm nfd build --config-file input.json --publish`

Publish a pre-built definition

`az aosm nfd publish --config-file input.json`

Delete a published definition

`az aosm nfd delete --config-file input.json`

Delete a published definition and the publisher, artifact stores and NFD group

`az aosm nfd delete --config-file input.json --clean`

Coming soon:

`az aosm nsd build` and further nsd commands.
