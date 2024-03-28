# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps[
    "confcom"
] = """
    type: group
    short-summary: Commands to generate security policies for confidential containers in Azure.
"""

helps[
    "confcom acipolicygen"
] = """
    type: command
    short-summary: Create a Confidential Container Security Policy for ACI.

    parameters:
        - name: --input -i
          type: string
          short-summary: 'Input JSON config file'

        - name: --template-file -a
          type: string
          short-summary: 'Input ARM Template file'

        - name: --parameters -p
          type: string
          short-summary: 'Input parameters file to optionally accompany an ARM Template'

        - name: --image
          type: string
          short-summary: 'Input image name'

        - name: --tar
          type: string
          short-summary: 'Path to either a tarball containing image layers or a JSON file containing paths to tarballs of image layers'

        - name: --infrastructure-svn
          type: string
          short-summary: 'Minimum Allowed Software Version Number for Infrastructure Fragment'

        - name: --debug-mode
          type: boolean
          short-summary: 'When enabled, the generated security policy adds the ability to use /bin/sh or /bin/bash to debug the container. It also enabled stdio access, ability to dump stack traces, and enables runtime logging. It is recommended to only use this option for debugging purposes.'

        - name: --approve-wildcards -y
          type: boolean
          short-summary: 'When enabled, all prompts for using wildcards in environment variables are automatically approved.'

        - name: --disable-stdio
          type: boolean
          short-summary: 'When enabled, the containers in the container group do not have access to stdio.'

        - name: --print-existing-policy
          type: boolean
          short-summary: 'When enabled, the existing security policy that is present in the ARM Template is printed to the command line, and no new security policy is generated.'

        - name: --diff -d
          type: boolean
          short-summary: 'When combined with an input ARM Template, verifies the policy present in the ARM Template under "ccePolicy" and the containers within the ARM Template are compatible. If they are incompatible, a list of reasons is given and the exit status code will be 2.'

        - name: --outraw
          type: boolean
          short-summary: 'Output policy in clear text compact JSON instead of default base64 format'

        - name: --outraw-pretty-print
          type: boolean
          short-summary: 'Output policy in clear text and pretty print format'

        - name: --save-to-file -s
          type: string
          short-summary: 'Save output policy to given file path.'

        - name: --print-policy
          type: boolean
          short-summary: 'When enabled, the generated security policy is printed to the command line instead of injected into the input ARM Template'

        - name: --faster-hashing
          type: boolean
          short-summary: 'When enabled, the hashing algorithm used to generate the policy is faster but less memory efficient'

    examples:
        - name: Input an ARM Template file to inject a base64 encoded Confidential Container Security Policy into the ARM Template
          text: az confcom acipolicygen --template-file "./template.json"
        - name: Input an ARM Template file to create a human-readable Confidential Container Security Policy
          text: az confcom acipolicygen --template-file "./template.json" --outraw-pretty-print
        - name: Input an ARM Template file to save a Confidential Container Security Policy to a file as base64 encoded text
          text: az confcom acipolicygen --template-file "./template.json" -s "./output-file.txt" --print-policy
        - name: Input an ARM Template file and use a tar file as the image source instead of the Docker daemon
          text: az confcom acipolicygen --template-file "./template.json" --tar "./image.tar"
"""

helps[
    "confcom katapolicygen"
] = """
    type: command
    short-summary: Create a Confidential Container Security Policy for AKS.

    parameters:
        - name: --yaml -y
          type: string
          short-summary: 'Input YAML Kubernetes file'

        - name: --outraw
          type: boolean
          short-summary: 'Output policy in clear text compact JSON instead of default base64 format'

        - name: --print-policy
          type: boolean
          short-summary: 'Print the base64 encoded generated policy in the terminal'

        - name: --config-map-file -c
          type: string
          short-summary: 'Path to config map file'

        - name: --use-cached-files -u
          type: bool
          short-summary: 'Use cached files to save on computation time'

        - name: --settings-file-name -j
          type: bool
          short-summary: 'Path to custom settings file'

    examples:
        - name: Input a Kubernetes YAML file to inject a base64 encoded Confidential Container Security Policy into the YAML file
          text: az confcom katapolicygen --yaml "./pod.json"
        - name: Input a Kubernetes YAML file to print a base64 encoded Confidential Container Security Policy to stdout
          text: az confcom katapolicygen --yaml "./pod.json" --print-policy
        - name: Input a Kubernetes YAML file and custom settings file to inject a base64 encoded Confidential Container Security Policy into the YAML file
          text: az confcom katapolicygen --yaml "./pod.json" -j "./settings.json"
        - name: Input a Kubernetes YAML file and external config map file
          text: az confcom katapolicygen --yaml "./pod.json" --config-map-file "./configmap.json"
"""
