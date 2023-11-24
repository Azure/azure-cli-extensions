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
test_arm_template_policy | python:3.6.14-slim-buster | Generate an ARM Template policy and policy.json policy and see if their outputs match
test_default_infrastructure_svn | python:3.6.14-slim-buster | See the default value of the minimum SVN for the infrastructure fragment
test_default_pause_container | python:3.6.14-slim-buster | See if the default pause containers match the config
test_arm_template_missing_image_name | N/A | Error condition if an image isn't specified
test_arm_template_missing_resources | N/A | Error condition where no resources are specified to deploy
test_arm_template_missing_aci | N/A | Error condition where ACI is not specified in resources
test_arm_template_missing_containers | N/A | Error condition where there are no containers in the ACI resource
test_arm_template_missing_definition | python:3.6.14-slim-buster | Error condition where image is specified in template.parameters.json but not in template.json
test_arm_template_with_parameter_file | mcr.microsoft.com/azure-functions/python:4-python3.8 | Condition where image in template.parameters.json overwrites image name in template.json
test_arm_template_with_parameter_file_injected_env_vars | mcr.microsoft.com/azure-functions/python:4-python3.8 | See if env vars from the image are injected into the policy. Also make sure the `concat` function in ARM template won't break the CLI if it's not in a required spot like image name
test_arm_template_with_parameter_file_arm_config | mcr.microsoft.com/azure-functions/python:4-python3.8 | Test valid case of using a parameter file with JSON output instead of Rego
test_arm_template_with_parameter_file_clean_room | mcr.microsoft.com/azure-functions/node:4 | Test clean room case where image specified does not exist remotely but does locally
test_policy_diff | alpine:3.16 | See if the diff functionality outputs `True` when diffs match completely
test_incorrect_policy_diff | alpine:3.16 | Check output formatting and functionality of diff command
test_update_infrastructure_svn | python:3.6.14-slim-buster | Change the minimum SVN for the insfrastructure fragment
test_multiple_policies | python:3.6.14-slim-buster & alpine:3.16 | See if two unique policies are generated from a single ARM Template container multiple container groups. Also have an extra resource that is untouched. Also has a secureValue for an environment variable.
test_arm_template_with_init_container | python:3.6.14-slim-buster & alpine:3.16 | See if having an initContainer is picked up and added to the list of valid containers
test_arm_template_without_stdio_access | alpine:3.16 | See if disabling container stdio access gets passed down to individual containers
test_arm_template_allow_elevated_false | alpine:3.16 | Disabling allow_elevated via securityContext
test_arm_template_policy_regex | python:3.6.14-slim-buster | Make sure the regex generated from the ARM Template workflow matches that of the policy.json workflow
test_wildcard_env_var | python:3.6.14-slim-buster | Check that an "allow all" regex is created when a value for env var is not provided via a parameter value
test_wildcard_env_var_invalid | N/A | Make sure the process errors out if a value is not given for an env var or an undefined parameter is used for the name of an env var
test_arm_template_with_env_var | alpine:3.16 | Make sure that a value that looks similar to but is not an ARM parameter is treated as a string
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

## policy.json [test file](test_confcom_scenario.py)

This was the initial way to input policy information into the confcom extension.
It is still used for generating sidecar CCE Policies.

Test Name | Image Used | Purpose
---|---|---
test_user_container_customized_mounts | alpine:3.16 | See if mounts are translated correctly to the appropriate source and destination locations
test_user_container_mount_injected_dns | python:3.6.14-slim-buster | See if the resolvconf mount works properly
test_injected_sidecar_container_msi | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201203.1 | Make sure User mounts and env vars aren't added to sidecar containers, using JSON output format
test_debug_flags | python:3.6.14-slim-buster | Enable flags set via debug_mode
test_sidecar | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 | See if sidecar validation would pass policy created by given policy.json
test_sidecar_stdio_access_default | Check that sidecar containers have std I/O access by default
test_incorrect_sidecar | mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 | See what output format for failing sidecar validation would be
test_customized_workingdir | python:3.6.14-slim-buster | Using different working dir than specified in image metadata
test_allow_elevated | python:3.6.14-slim-buster | Using allow_elevated in container
test_image_layers_python | python:3.6.14-slim-buster | Make sure image layers are as expected
test_image_layers_nginx | nginx:1.22 | Make sure image layers are as expected with different image
test_docker_pull | alpine:3.16 | Test pulling an image from docker client
test_infrastructure_svn | alpine:3.16 | make sure the correct infrastructure_svn is present in the policy
test_stdio_access_default | python:3.6.14-slim-buster | Checking the default value for std I/O access
test_stdio_access_updated | python:3.6.14-slim-buster | Checking the value for std I/O when it's set
test_environment_variables_parsing | mcr.microsoft.com/azuredocs/aci-dataprocessing-cc:v1 | Make sure env vars are output in the right format
test_get_layers_from_not_exists_image | notexists:1.0.0 | Fail out grabbing layers if image doesn't exist
test_incorrect_allow_elevated_data_type | alpine:3.16 | Making allow_elevated fail out if it's not a boolean
test_incorrect_workingdir_path | alpine:3.16 | Fail if working dir isn't an absolute path string
test_incorrect_workingdir_data_type | alpine:3.16 | Fail if working dir is an array
test_incorrect_command_data_type | alpine:3.16 | Fail if command is not array of strings
test_json_missing_containers | N/A | Fail if containers are not specified
test_json_missing_version | mcr.microsoft.com/azuredocs/aci-dataprocessing-cc:v1 | Fail if version is not included in policy.json
test_json_missing_containerImage | N/A | Fail if container doesn't have an image specified
test_json_missing_environmentVariables | mcr.microsoft.com/azuredocs/aci-dataprocessing-cc:v1 | Fail if there are no env vars defined
test_json_missing_command | mcr.microsoft.com/azuredocs/aci-dataprocessing-cc:v1 | Fail if there is no command specified

## Image [test file](test_confcom_image.py)

This is a convenient way of generating a CCE Policy with no external files.
It accepts a string of the image name and tag and outputs a CCE Policy using the image's metadata.

Test Name | Image Used | Purpose
---|---|---
test_image_policy | python:3.6.14-slim-buster | Create a policy based on only an image name
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

## Tar File [test file](test_confcom_tar.py)

This is a way to generate a CCE policy without the use of the docker daemon. The tar file that gets passed in is either from the `docker save` command or doing `image.save(named=True)` with the Docker python SDK. It accepts either a path to a tar file or the path to a JSON file with keys being the name of the image and value being the path to that file relative to the JSON file.

Test Name | Image Used | Purpose
---|---|---
test_arm_template_with_parameter_file_clean_room_tar | nginx:1.23 | Create a policy from a tar file and compare it to a policy generated from an ARM template
test_arm_template_mixed_mode_tar | python:3.9 & nginx:1.22 | Create a policy with one image from a tar file and one image that must be downloaded or used locally from the daemon
test_arm_template_with_parameter_file_clean_room_tar_invalid | N/A | Fail out if searching for an image in a tar file that does not include it
test_clean_room_fake_tar_invalid | N/A | Fail out if the path to the tar file doesn't exist

## Tar File [test file](test_confcom_kata.py)

This is how to generate security policies for Confidential Containers on AKS

Test Name | Image Used | Purpose
---|---|---
test_invalid_input_path | mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64 | Input a path that does not exist for the pod.yaml file
test_invalid_config_map_path | mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64 | Input a path that does not exist for the config-map.yaml file
test_invalid_settings | mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64 | Input an invalid name for a custom settings file
