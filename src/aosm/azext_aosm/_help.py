# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.help_files import helps

helps[
    "aosm"
] = """
    type: group
    short-summary: Commands to interact with Azure Operator Service Manager (AOSM).
    long-summary: |
      Azure Operator Service Manager (AOSM) is a service that enables you to manage and publish Network Function Definitions (NFD) and Network Service Definitions (NSD) to Azure. These commands allow you to build and publish NFDs and NSDs, including supporting infrastructure, from existing Helm charts and ARM templates.
"""

helps[
    "aosm nfd"
] = """
    type: group
    short-summary: Manage AOSM publisher Network Function Definitions.
    long-summary: |
      A Network Function Definition (NFD) is a collection of Helm charts or ARM templates that define a network function. This command group allows you to build and publish NFDs to Azure.
"""

helps[
    "aosm nfd generate-config"
] = """
    type: command
    short-summary: Generate configuration file for building an AOSM publisher Network Function Definition.
    long-summary: |
      Generates a configuration file that you can use to build an AOSM Network Function Definition (NFD). The configuration file is a JSONC file that contains the required parameters for building the NFD. You must complete the configuration file with your specific values before building the NFD.
    parameters:
      - name: --definition-type
        type: string
        short-summary: Required. Type of network function definition to be built.
        long-summary: |
          The type of AOSM definition to be built. The generate config file differs depending on type. This can be one of the following values:
          - cnf: Containerised Network Function
          - vnf: Virtual Network Function on Azure Core
          - vnf-nexus: Virtual Network Function on Nexus
      - name: --output-file
        type: string
        short-summary: Optional. The name of the output file to write the generated config text to.
    examples:
      - name: Generate a configuration file for a Containerised Network Function.
        text: az aosm nfd generate-config --definition-type cnf
      - name: Generate a configuration file for a Virtual Network Function.
        text: az aosm nfd generate-config --definition-type vnf
      - name: Generate a configuration file for a Virtual Network Function for use on Azure Nexus.
        text: az aosm nfd generate-config --definition-type vnf-nexus
      - name: Generate a configuration file for a Virtual Network Function and write to a specific file.
        text: az aosm nfd generate-config --definition-type vnf --output-file my-vnf-input-config.jsonc
"""

helps[
    "aosm nfd build"
] = """
    type: command
    short-summary: Build an AOSM Network Function Definition.
    long-summary: |
      Builds an AOSM Network Function Definition (NFD) based on the configuration file provided. The NFD is built from the Helm charts or ARM templates specified in the configuration file. The output is a directory which can either be published directly (using the aosm nfd publish command) or manually customized before publishing.
    parameters:
      - name: --definition-type
        type: string
        short-summary: Required. Type of network function definition to be built.
        long-summary: |
          The type of AOSM definition to be built. The generate config file differs depending on type. This can be one of the following values:
          - cnf: Containerised Network Function
          - vnf: Virtual Network Function on Azure Core
          - vnf-nexus: Virtual Network Function on Nexus
      - name: --config-file
        type: string
        short-summary: Required. The path to the configuration file.
        long-summary: |
          The path to the configuration file. This is a JSONC file that contains the required parameters for building the NFD.
    examples:
      - name: Build a Containerised Network Function.
        text: az aosm nfd build --definition-type cnf --config-file my-cnf-input-config.jsonc
      - name: Build a Virtual Network Function for use on Azure Core.
        text: az aosm nfd build --definition-type vnf --config-file my-vnf-input-config.jsonc
      - name: Build a Virtual Network Function for use on Azure Nexus.
        text: az aosm nfd build --definition-type vnf-nexus --config-file my-vnf-nexus-input-config.jsonc
"""

helps[
    "aosm nfd publish"
] = """
    type: command
    short-summary: Publish a pre-built AOSM Network Function definition.
    long-summary: |
      Publishes a pre-built AOSM Network Function Definition (NFD) to Azure. The NFD must be built using the aosm nfd build command before it can be published. The NFD and other required resources (publisher resource, artifact manifest(s), storage account(s) etc.) is published to the specified resource group in the currently active Azure subscription.
    parameters:
      - name: --definition-type
        type: string
        short-summary: Required. Type of network function definition to be built.
        long-summary: |
          The type of AOSM definition to be built. The generate config file differs depending on type. This can be one of the following values:
          - cnf: Containerised Network Function
          - vnf: Virtual Network Function on Azure Core
          - vnf-nexus: Virtual Network Function on Nexus
      - name: --build-output-folder
        type: string
        short-summary: Required. Path to the folder to publish, created by the build command.
      - name: --no-subscription-permissions
        type: flag
        short-summary: Optional. Pass this flag if you do not have permission to import to the Publisher subscription.
        long-summary: |
          Applies only when publishing CNFs - ignored for VNF. Pass this flag if you do not have permission to import to the Publisher subscription (Contributor role + AcrPush role, or a custom role that allows the importImage action and AcrPush over the whole subscription). Using this flag causes image artifacts to be pulled to your local machine and then pushed to the Artifact Store. This is slower than a copy entirely within Azure, but is an alterative if you do not have the required permissions.
    examples:
      - name: Publish a Containerised Network Function.
        text: az aosm nfd publish --definition-type cnf --build-output-folder my-cnf-output-folder
      - name: Publish a Virtual Network Function for use on Azure Core.
        text: az aosm nfd publish --definition-type vnf --build-output-folder my-vnf-output-folder
      - name: Publish a Virtual Network Function for use on Azure Nexus.
        text: az aosm nfd publish --definition-type vnf-nexus --build-output-folder my-vnf-nexus-output-folder
      - name: Publish a Containerised Network Function when you do not have the required import permissions.
        text: az aosm nfd publish --definition-type cnf --build-output-folder my-cnf-output-folder --no-subscription-permissions
"""

helps[
    "aosm nsd"
] = """
    type: group
    short-summary: Manage AOSM publisher Network Service Designs.
    long-summary: |
      A Network Service Design (NSD) is a collection of Network Function Definitions (NFD) and any supporting infrastructure that define a network service. This command group allows you to build and publish NSDs to Azure.
"""

helps[
    "aosm nsd generate-config"
] = """
    type: command
    short-summary: Generate configuration file for building an AOSM publisher Network Service Design.
    long-summary: |
      Generates a configuration file that you can use to build an AOSM Network Service Design (NSD). The configuration file is a JSONC file that contains the required parameters for building the NSD. You must complete the configuration file with your specific values before building the NSD.
    parameters:
      - name: --output-file
        type: string
        short-summary: Optional. The name of the output file to write the generated config text to.
    examples:
      - name: Generate a configuration file for a Network Service Design.
        text: az aosm nsd generate-config
      - name: Generate a configuration file for a Network Service Design and write to a specific file.
        text: az aosm nsd generate-config --output-file my-nsd-input-config.jsonc
"""

helps[
    "aosm nsd build"
] = """
    type: command
    short-summary: Build an AOSM Network Service Design.
    long-summary: |
      Builds an AOSM Network Service Design (NSD) based on the configuration file provided. The NSD is built from the Network Function Definitions (NFD) and ARM templates specifying supporting infrastructure, as specified in the configuration file. The output is a directory which can either be published directly (using the aosm nsd publish command) or manually customized before publishing.
    parameters:
      - name: --config-file
        type: string
        short-summary: Required. The path to the configuration file.
        long-summary: |
          The path to the configuration file. This is a JSONC file that contains the required parameters for building the NFD.
    examples:
      - name: Build a Network Service Design.
        text: az aosm nsd build --config-file my-nsd-input-config.jsonc
"""

helps[
    "aosm nsd publish"
] = """
    type: command
    short-summary: Publish a pre-built AOSM Network Service Design.
    long-summary: |
      Publishes a pre-built AOSM Network Service Design (NSD) to Azure. The NSD must be built using the aosm nsd build command before it can be published. The NSD and other required resources (publisher resource, artifact manifest(s), storage account(s) etc.) is published to the specified resource group in the currently active Azure subscription.
    parameters:
      - name: --build-output-folder
        type: string
        short-summary: Required. Path to the folder to publish, created by the build command.
    examples:
      - name: Publish a Network Service Design.
        text: az aosm nsd publish --build-output-folder my-nsd-output-folder
"""
