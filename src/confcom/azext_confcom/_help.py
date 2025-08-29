# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import
from azext_confcom.config import SUPPORTED_ALGOS

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

        - name: --virtual-node-yaml
          type: string
          short-summary: 'Input YAML file for Virtual Node policy generation'

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
          short-summary: 'When enabled, the generated security policy adds the ability to use /bin/sh or /bin/bash to debug the container. It also enabled stdio access, ability to dump stack traces, and enables runtime logging. It is recommended to only use this option for debugging purposes'

        - name: --approve-wildcards -y
          type: boolean
          short-summary: 'When enabled, all prompts for using wildcards in environment variables are automatically approved'

        - name: --disable-stdio
          type: boolean
          short-summary: 'When enabled, the containers in the container group do not have access to stdio'

        - name: --print-existing-policy
          type: boolean
          short-summary: 'When enabled, the existing security policy that is present in the ARM Template is printed to the command line, and no new security policy is generated'

        - name: --diff -d
          type: boolean
          short-summary: 'When combined with an input ARM Template file (or YAML file for Virtual Node policy generation), verifies the policy present in the ARM Template under "ccePolicy" and the containers within the file are compatible. If they are incompatible, a list of reasons is given and the exit status code will be 2'

        - name: --outraw
          type: boolean
          short-summary: 'Output policy in clear text compact JSON instead of default base64 format'

        - name: --outraw-pretty-print
          type: boolean
          short-summary: 'Output policy in clear text and pretty print format'

        - name: --save-to-file -s
          type: string
          short-summary: 'Save output policy to given file path'

        - name: --print-policy
          type: boolean
          short-summary: 'When enabled, the generated security policy is printed to the command line instead of injected into the input ARM Template'

        - name: --faster-hashing
          type: boolean
          short-summary: 'When enabled, the hashing algorithm used to generate the policy is faster but less memory efficient'

        - name: --omit-id
          type: boolean
          short-summary: 'When enabled, the generated policy will not contain the ID field. This will keep the policy from being tied to a specific image name and tag. This is helpful if the image being used will be present in multiple registries and used interchangeably'

        - name: --include-fragments -f
          type: boolean
          short-summary: 'When enabled, the path specified by --fragments-json will be used to pull fragments from an OCI registry or locally and include them in the generated policy'

        - name: --fragments-json -j
          type: string
          short-summary: 'Path to JSON file containing fragment information to use for generating a policy. This requires --include-fragments to be enabled'

        - name: --exclude-default-fragments -e
          type: boolean
          short-summary: 'When enabled, the default fragments are not included in the generated policy. This includes containers needed to mount azure files, mount secrets, mount git repos, and other common ACI features'

    examples:
        - name: Input an ARM Template file to inject a base64 encoded Confidential Container Security Policy into the ARM Template
          text: az confcom acipolicygen --template-file "./template.json"
        - name: Input an ARM Template file to create a human-readable Confidential Container Security Policy
          text: az confcom acipolicygen --template-file "./template.json" --outraw-pretty-print
        - name: Input an ARM Template file to save a Confidential Container Security Policy to a file as base64 encoded text
          text: az confcom acipolicygen --template-file "./template.json" -s "./output-file.txt" --print-policy
        - name: Input an ARM Template file and use a tar file as the image source instead of the Docker daemon
          text: az confcom acipolicygen --template-file "./template.json" --tar "./image.tar"
        - name: Input an ARM Template file and use a fragments JSON file to generate a policy
          text: az confcom acipolicygen --template-file "./template.json" --fragments-json "./fragments.json" --include-fragments
"""

helps[
    "confcom acifragmentgen"
] = f"""
    type: command
    short-summary: Create a Confidential Container Policy Fragment for ACI.

    parameters:
        - name: --image
          type: string
          short-summary: 'Image to use for the generated policy fragment'

        - name: --input -i
          type: string
          short-summary: 'Path to a JSON file containing the configuration for the generated policy fragment'

        - name: --tar
          type: string
          short-summary: 'Path to either a tarball containing image layers or a JSON file containing paths to tarballs of image layers'

        - name: --namespace -n
          type: string
          short-summary: 'Namespace to use for the generated policy fragment'

        - name: --svn
          type: string
          short-summary: 'Minimum Allowed Software Version Number for the generated policy fragment. This should be a monotonically increasing integer'

        - name: --feed -f
          type: string
          short-summary: 'Feed to use for the generated policy fragment. This is typically the same as the image name when using image-attached fragments. It is the location in the remote repository where the fragment will be stored'

        - name: --key -k
          type: string
          short-summary: 'Path to .pem formatted key file to use for signing the generated policy fragment. This must be used with --chain'

        - name: --chain
          type: string
          short-summary: 'Path to .pem formatted certificate chain file to use for signing the generated policy fragment. This must be used with --key'

        - name: --algo
          type: string
          short-summary: |
            Algorithm used for signing the generated policy fragment. This must be used with --key and --chain.
            Supported algorithms are {SUPPORTED_ALGOS}

        - name: --fragment-path -p
          type: string
          short-summary: 'Path to an existing signed policy fragment file to be used with --generate-import. This option allows you to create import statements for the specified fragment without needing to explicitly pull it from an OCI registry. This can either be a local path or an OCI registry reference. For local fragments, the file will remain in the same location. For remote fragments, the file will be downloaded and cleaned up after processing'

        - name: --omit-id
          type: boolean
          short-summary: 'When enabled, the generated policy will not contain the ID field. This will keep the policy from being tied to a specific image name and tag. This is helpful if the image being used will be present in multiple registries and used interchangeably'

        - name: --generate-import -g
          type: boolean
          short-summary: 'Generate an import statement for a policy fragment'

        - name: --disable-stdio
          type: boolean
          short-summary: 'When enabled, the containers in the container group do not have access to stdio'

        - name: --debug-mode
          type: boolean
          short-summary: 'When enabled, the generated security policy adds the ability to use /bin/sh or /bin/bash to debug the container. It also enabled stdio access, ability to dump stack traces, and enables runtime logging. It is recommended to only use this option for debugging purposes'

        - name: --output-filename
          type: string
          short-summary: 'Save output policy to given file path'

        - name: --outraw
          type: boolean
          short-summary: 'Output policy in clear text compact JSON instead of default pretty print format'

        - name: --upload-fragment -u
          type: boolean
          short-summary: 'When enabled, the generated policy fragment will be uploaded to the registry of the image being used'

        - name: --fragments-json -j
          type: string
          short-summary: 'Path to a JSON file that will store the fragment import information generated when using --generate-import. This file can later be fed into the policy generation command (acipolicygen) to include the fragment in a new or existing policy. If not specified, the import statement will be printed to the console instead of being saved to a file'

    examples:
        - name: Input an image name to generate a simple fragment
          text: az confcom acifragmentgen --image mcr.microsoft.com/azuredocs/aci-helloworld
        - name: Input a config file to generate a fragment with a custom namespace and debug mode enabled
          text: az confcom acifragmentgen --input "./config.json" --namespace "my-namespace" --debug-mode
        - name: Generate an import statement for a signed local fragment
          text: az confcom acifragmentgen --fragment-path "./fragment.rego.cose" --generate-import --minimum-svn 1
        - name: Generate a fragment and COSE sign it with a key and chain
          text: az confcom acifragmentgen --input "./config.json" --key "./key.pem" --chain "./chain.pem" --svn 1 --namespace contoso --no-print
        - name: Generate a fragment import from an image name
          text: az confcom acifragmentgen --image <my-image> --generate-import --minimum-svn 1
        - name: Attach a fragment to a specified image
          text: az confcom acifragmentgen --input "./config.json" --key "./key.pem" --chain "./chain.pem" --svn 1 --namespace contoso --upload-fragment --image-target <my-image>


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

        - name: --rules-file-name -p
          type: bool
          short-summary: 'Path to custom rules file'

        - name: --print-version -v
          type: bool
          short-summary: 'Print the version of genpolicy tooling'

        - name: --containerd-pull -d
          type: string
          short-summary: 'Use containerd to pull the image. This option is only supported on Linux'

        - name: --containerd-socket-path
          type: string
          short-summary: 'Path to the containerd socket. This option is only supported on Linux'


    examples:
        - name: Input a Kubernetes YAML file to inject a base64 encoded Confidential Container Security Policy into the YAML file
          text: az confcom katapolicygen --yaml "./pod.json"
        - name: Input a Kubernetes YAML file to print a base64 encoded Confidential Container Security Policy to stdout
          text: az confcom katapolicygen --yaml "./pod.json" --print-policy
        - name: Input a Kubernetes YAML file and custom settings file to inject a base64 encoded Confidential Container Security Policy into the YAML file
          text: az confcom katapolicygen --yaml "./pod.json" -j "./settings.json"
        - name: Input a Kubernetes YAML file and external config map file
          text: az confcom katapolicygen --yaml "./pod.json" --config-map-file "./configmap.json"
        - name: Input a Kubernetes YAML file and custom rules file
          text: az confcom katapolicygen --yaml "./pod.json" -p "./rules.rego"
        - name: Input a Kubernetes YAML file with a custom containerd socket path
          text: az confcom katapolicygen --yaml "./pod.json" --containerd-pull --containerd-socket-path "/my/custom/containerd.sock"
"""
