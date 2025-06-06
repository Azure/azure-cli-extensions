# Testing

This file is used to organize what test cases are present and what they are specifically testing.
It could be replaced by having more descriptions inside each testing file.
The tests are split up into separate files depending on their input type:

## Coverage Report

To get line coverage from the tests run the following commands after installing `coverage` with `pip install coverage`.
`coverage run -m pytest <path-to-test-folder>`
then run
`coverage html`
to generate a report in html that can then be navigated using a browser by opening the file `htmlcov/index.html` in a browser tab.

## ARM Template [test file](test_confcom_arm.py)

This is arguably the easiest way to generate a CCE Policy.
It uses the ARM template used to deploy a ACI Container Group while taking into account environment variables and mounts that are present in the ARM template.

Test Name | Image Used | Purpose
---|---|---
test_arm_template_policy | mcr.microsoft.com/azurelinux/base/python:3.12 | Generate an ARM Template policy and policy.json policy and see if their outputs match
test_default_infrastructure_svn | mcr.microsoft.com/azurelinux/base/python:3.12 | See the default value of the minimum SVN for the infrastructure fragment
test_default_pause_container | mcr.microsoft.com/azurelinux/base/python:3.12 | See if the default pause containers match the config
test_arm_template_missing_image_name | N/A | Error condition if an image isn't specified
test_arm_template_missing_resources | N/A | Error condition where no resources are specified to deploy
test_arm_template_missing_aci | N/A | Error condition where ACI is not specified in resources
test_arm_template_missing_containers | N/A | Error condition where there are no containers in the ACI resource
test_arm_template_missing_definition | mcr.microsoft.com/azurelinux/base/python:3.12 | Error condition where image is specified in template.parameters.json but not in template.json
test_arm_template_with_parameter_file | mcr.microsoft.com/azure-functions/python:4-python3.8 | Condition where image in template.parameters.json overwrites image name in template.json
test_arm_template_with_parameter_file_injected_env_vars | mcr.microsoft.com/azure-functions/python:4-python3.8 | See if env vars from the image are injected into the policy. Also make sure the `concat` function in ARM template won't break the CLI if it's not in a required spot like image name
test_arm_template_with_parameter_file_arm_config | mcr.microsoft.com/azure-functions/python:4-python3.8 | Test valid case of using a parameter file with JSON output instead of Rego
test_arm_template_with_parameter_file_clean_room | mcr.microsoft.com/azure-functions/node:4 | Test clean room case where image specified does not exist remotely but does locally
test_policy_diff | mcr.microsoft.com/azurelinux/distroless/base:3.0 | See if the diff functionality outputs `True` when diffs match completely
test_incorrect_policy_diff | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Check output formatting and functionality of diff command
test_update_infrastructure_svn | mcr.microsoft.com/azurelinux/base/python:3.12 | Change the minimum SVN for the insfrastructure fragment
test_multiple_policies | mcr.microsoft.com/azurelinux/base/python:3.12 & mcr.microsoft.com/azurelinux/distroless/base:3.0 | See if two unique policies are generated from a single ARM Template container multiple container groups. Also have an extra resource that is untouched. Also has a secureValue for an environment variable.
test_arm_template_with_init_container | mcr.microsoft.com/azurelinux/base/python:3.12 & mcr.microsoft.com/azurelinux/distroless/base:3.0 | See if having an initContainer is picked up and added to the list of valid containers
test_arm_template_without_stdio_access | mcr.microsoft.com/azurelinux/distroless/base:3.0 | See if disabling container stdio access gets passed down to individual containers
test_arm_template_omit_id | mcr.microsoft.com/azurelinux/base/python:3.12 | Check that the id field is omitted from the policy
test_arm_template_allow_elevated_false | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Disabling allow_elevated via securityContext
test_arm_template_policy_regex | mcr.microsoft.com/azurelinux/base/python:3.12 | Make sure the regex generated from the ARM Template workflow matches that of the policy.json workflow
test_wildcard_env_var | mcr.microsoft.com/azurelinux/base/python:3.12 | Check that an "allow all" regex is created when a value for env var is not provided via a parameter value
test_wildcard_env_var_invalid | N/A | Make sure the process errors out if a value is not given for an env var or an undefined parameter is used for the name of an env var
test_arm_template_with_env_var | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Make sure that a value that looks similar to but is not an ARM parameter is treated as a string
test_arm_template_security_context_defaults | N/A | Make sure default values for securityContext are correct
test_arm_template_security_context_allow_privilege_escalation | N/A | See if changing the allowPrivilegeEscalation flag is working
test_arm_template_security_context_user | N/A | Set the user field manually to make sure it is reflected in the policy
test_arm_template_security_context_seccomp_profile | N/A | Make sure we have the correct seccomp profile hash
test_arm_template_capabilities_unprivileged | N/A | See if unprivileged capabilities are in the correct sets and have the right values. Using add and drop fields
test_arm_template_capabilities_privileged | N/A | See if privilileged capabilities are correct
test_arm_template_security_context_no_run_as_group | N/A | See if user is set correctly if run_as_group is not set in ARM template
test_arm_template_security_context_no_run_as_user | N/A | See if user is set correctly if run_as_user is not set in ARM template
test_arm_template_security_context_uid_gid | N/A | See if user is set correctly by getting the user field from the Docker image in the format uid:gid
test_arm_template_security_context_user_gid | N/A | See if user is set correctly by getting the user field from the Docker image in the format user:gid
test_arm_template_security_context_user_group | N/A | See if user is set correctly by getting the user field from the Docker image in the format user:group
test_arm_template_security_context_uid_group | N/A | See if user is set correctly by getting the user field from the Docker image in the format uid:group
test_arm_template_security_context_uid | N/A | See if user is set correctly by getting the user field from the Docker image in the format uid
test_arm_template_security_context_user_dockerfile | N/A | See if user is set correctly by getting the user field from the Docker image in the format user
test_zero_sidecar | mcr.microsoft.com/azurelinux/base/python:3.12 | Make sure the infrastructure fragment is taken out when the appropriate tag is present in an ARM template

## policy.json [test file](test_confcom_scenario.py)

This was the initial way to input policy information into the confcom extension.
It is still used for generating sidecar CCE Policies.

Test Name | Image Used | Purpose
---|---|---
test_user_container_customized_mounts | mcr.microsoft.com/azurelinux/distroless/base:3.0 | See if mounts are translated correctly to the appropriate source and destination locations
test_user_container_mount_injected_dns | mcr.microsoft.com/azurelinux/base/python:3.12 | See if the resolvconf mount works properly
test_injected_sidecar_container_msi | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201203.1 | Make sure User mounts and env vars aren't added to sidecar containers, using JSON output format
test_debug_flags | mcr.microsoft.com/azurelinux/base/python:3.12 | Enable flags set via debug_mode
test_sidecar | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 | See if sidecar validation would pass policy created by given policy.json
test_sidecar_stdio_access_default | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 | Check that sidecar containers have std I/O access by default
test_incorrect_sidecar | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 | See what output format for failing sidecar validation would be
test_customized_workingdir | mcr.microsoft.com/azurelinux/base/python:3.12 | Using different working dir than specified in image metadata
test_allow_elevated | mcr.microsoft.com/azurelinux/base/python:3.12 | Using allow_elevated in container
test_image_layers_python | mcr.microsoft.com/azurelinux/base/python:3.12 | Make sure image layers are as expected
test_docker_pull | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Test pulling an image from docker client
test_infrastructure_svn | mcr.microsoft.com/azurelinux/distroless/base:3.0 | make sure the correct infrastructure_svn is present in the policy
test_stdio_access_default | mcr.microsoft.com/azurelinux/base/python:3.12 | Checking the default value for std I/O access
test_stdio_access_updated | mcr.microsoft.com/azurelinux/base/python:3.12 | Checking the value for std I/O when it's set
test_omit_id | mcr.microsoft.com/azurelinux/base/python:3.12 | Check that the id field is omitted from the policy
test_environment_variables_parsing | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Make sure env vars are output in the right format
test_get_layers_from_not_exists_image | notexists:1.0.0 | Fail out grabbing layers if image doesn't exist
test_incorrect_allow_elevated_data_type | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Making allow_elevated fail out if it's not a boolean
test_incorrect_workingdir_path | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Fail if working dir isn't an absolute path string
test_incorrect_workingdir_data_type | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Fail if working dir is an array
test_incorrect_command_data_type | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Fail if command is not array of strings
test_json_missing_containers | N/A | Fail if containers are not specified
test_json_missing_containerImage | N/A | Fail if container doesn't have an image specified
test_json_missing_environmentVariables | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Fail if there are no env vars defined
test_json_missing_command | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Fail if there is no command specified

## Image [test file](test_confcom_image.py)

This is a convenient way of generating a CCE Policy with no external files.
It accepts a string of the image name and tag and outputs a CCE Policy using the image's metadata.

Test Name | Image Used | Purpose
---|---|---
test_image_policy | mcr.microsoft.com/azurelinux/base/python:3.12 | Create a policy based on only an image name
test_sidecar_image_policy |mcr.microsoft.com/aci/atlas-mount-azure-file-volume:master_20201210.2| Create a policy based on a sidecar so no env vars are injected
test_invalid_image_policy | mcr.microsoft.com/aci/fake-image:master_20201210.2 | Fail out if the image doesn't exist locally or remotely
test_clean_room_policy | mcr.microsoft.com/aci/atlas-mount-azure-file-volume:master_20201210.2 | create a new tag of a sidecar locally and make sure it matches the original

## Startup Checks [test file](test_confcom_startup.py)

This does a series of checks to make sure the flag configuration that is attempted is valid

Test Name | Purpose
---|---
test_invalid_output_flags | Makes sure that the policy fails if we specify more than one output format at a time
test_invalid_many_input_types | Makes sure we're only getting input from one source i.e. ARM Template, policy.json, or image name
test_diff_wrong_input_type | Makes sure we're only doing the diff command if we're using a ARM Template as the input type
test_parameters_without_template | Makes sure we error out if a parameter file is getting passed in without an ARM Template
test_input_and_virtual_node | Error out if both input and virtual node are specified
test_workload_identity | Make sure env vars are injected if workload identity is used

## Tar File [test file](test_confcom_tar.py)

This is a way to generate a CCE policy without the use of the docker daemon. The tar file that gets passed in is either from the `docker save` command or doing `image.save(named=True)` with the Docker python SDK. It accepts either a path to a tar file or the path to a JSON file with keys being the name of the image and value being the path to that file relative to the JSON file.

Test Name | Image Used | Purpose
---|---|---
test_arm_template_with_parameter_file_clean_room_tar | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Create a policy from a tar file and compare it to a policy generated from an ARM template
test_arm_template_mixed_mode_tar | mcr.microsoft.com/azurelinux/base/python:3.12 & mcr.microsoft.com/azurelinux/distroless/base:3.0 | Create a policy with one image from a tar file and one image that must be downloaded or used locally from the daemon
test_arm_template_with_parameter_file_clean_room_tar_invalid | N/A | Fail out if searching for an image in a tar file that does not include it
test_clean_room_fake_tar_invalid | N/A | Fail out if the path to the tar file doesn't exist

## Kata Containers File [test file](test_confcom_kata.py)

This is how to generate security policies for Confidential Containers on AKS

Test Name | Image Used | Purpose
---|---|---
test_invalid_input_path | mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64 | Input a path that does not exist for the pod.yaml file
test_invalid_config_map_path | mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64 | Input a path that does not exist for the config-map.yaml file
test_valid_settings | mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64 | Input a valid path for the pod.yaml with the default config file
test_print_version | N/A | Print the version of the extension
test_invalid_settings | mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64 | Input an invalid name for a custom settings file

## Virtual Node File [test file](test_confcom_virtual_node.py)

This is how to generate security policies for Virtual Nodes on AKS

Test Name | Image Used | Purpose
---|---|---
test_compare_policy_sources | mcr.microsoft.com/azurelinux/base/python:3.12 | Compare the output of a policy generated from a Virtual Node file and a policy generated from an input json
test_configmaps | mcr.microsoft.com/azurelinux/base/python:3.12 | Check that the configmaps are being added to the policy in env var and mount form
test_secrets | mcr.microsoft.com/azurelinux/base/python:3.12 | Check that the secrets are being added to the policy in env var and mount form

## Fragment File [test file](test_confcom_fragment.py)

This is how to generate a policy fragment to be included in a CCE Policy for Confidential ACI

Test Name | Image Used | Purpose
---|---|---
test_fragment_user_container_customized_mounts | mcr.microsoft.com/azurelinux/distroless/base:3.0 | See if mounts are translated correctly to the appropriate source and destination locations
test_fragment_user_container_mount_injected_dns | mcr.microsoft.com/azurelinux/distroless/base:3.0 | See if the resolvconf mount works properly
test_fragment_omit_id | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201203.1 | Check that the id field is omitted from the policy
test_fragment_injected_sidecar_container_msi | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201203.1 | Make sure User mounts and env vars aren't added to sidecar containers, using JSON output format
test_debug_processes | mcr.microsoft.com/azurelinux/distroless/base:3.0 | Enable exec_processes via debug_mode
test_fragment_sidecar | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 | See if sidecar fragments can be created by a given policy.json
test_fragment_sidecar_stdio_access_default | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 | Check that sidecar containers have std I/O access by default
test_fragment_incorrect_sidecar | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 | See what output format for failing sidecar validation would be
test_signing | mcr.microsoft.com/acc/samples/aci/helloworld:2.9 | Sign a fragment with a key and chain file
test_generate_import | mcr.microsoft.com/acc/samples/aci/helloworld:2.9 | Generate an import statement for the signed fragment file
test_local_fragment_references | mcr.microsoft.com/acc/samples/aci/helloworld:2.9 | Make sure the fragment references are correct when the fragment is local
test_invalid_input | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 | Fail out under various invalid input circumstances

## Policy Conversion File [test file](test_confcom_policy_conversion.py)

Test Name | Image Used | Purpose
---|---|---
test_detect_old_format | N/A | Verify that old and new format configurations are correctly identified
test_top_level_fields_propagated | N/A | Check that top-level fields like version and fragments are preserved during conversion
test_container_count_preserved | N/A | Ensure the number of containers remains unchanged after conversion
test_env_strategy_to_regex_flag | N/A | Verify environment variable strategy is correctly translated to regex flags in v1 format
test_exec_processes_built_correctly | N/A | Check command and probe commands are correctly aggregated into execProcesses
test_volume_mount_basic_fields | N/A | Test volume mount properties are correctly translated to the new format
test_workingdir_and_allow_elevated_migrated | N/A | Verify workingDir and allow_elevated are correctly moved to security context
test_already_v1_returns_same_object | N/A | Confirm conversion is idempotent - v1 format input remains unchanged
