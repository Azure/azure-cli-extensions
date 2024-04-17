# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-locals, missing-timeout, too-many-statements, consider-using-with, too-many-branches

from threading import Thread
import os
import re
import tempfile
import time
import requests

from azure.cli.core.azclierror import (
    ValidationError
)

from ._archive_utils import archive_source_code

from ._clients import BuilderClient, BuildClient

from ._utils import (
    log_in_file,
    remove_ansi_characters,
    parse_build_env_vars
)


class CloudBuildError(Exception):
    pass


def run_cloud_build(cmd, source, build_env_vars, location, resource_group_name, environment_name, run_full_id, logs_file, logs_file_path):
    generated_build_name = f"build{run_full_id}"[:12]
    log_in_file(f"Starting the Cloud Build for build of id '{generated_build_name}'\n", logs_file, no_print=True)

    try:
        done_spinner = False
        fail_spinner = False
        cancel_spinner = False
        font_bold_green = "\033[32;1m"
        font_bold_red = "\033[31;1m"
        font_bold_yellow = "\033[33;1m"
        font_default = "\033[0m"
        font_bold = "\033[0;1m"
        hide_cursor = "\033[?25l"
        display_cursor = "\033[?25h"
        substatus_indentation = "              "

        def display_spinner(task_title):
            # Hide the cursor
            print(hide_cursor, end="")

            def spin():
                loop_counter = 0
                start_time = time.time()
                time_elapsed = 0
                while done_spinner is False and fail_spinner is False and cancel_spinner is False:
                    loop_counter = (loop_counter + 1) % 17
                    loading_bar_left_spaces_count = loop_counter - 9 if loop_counter > 9 else 0
                    loading_bar_right_spaces_count = 6 - loop_counter if loop_counter < 7 else 0
                    spinner = f"|{' ' * loading_bar_left_spaces_count}{'=' * (7 - loading_bar_left_spaces_count - loading_bar_right_spaces_count)}{' ' * loading_bar_right_spaces_count}|"
                    time_elapsed = time.time() - start_time
                    print(f"\r    {spinner} {task_title} ({time_elapsed:.1f}s)", end="", flush=True)
                    time.sleep(0.15)
                if cancel_spinner:
                    print(f"\r    {font_bold_yellow}Canceled:{font_default} {task_title} ({time_elapsed:.1f}s)")
                    log_in_file(f"Canceled: {task_title} ({time_elapsed:.1f}s)", logs_file, no_print=True)
                elif fail_spinner:
                    print(f"\r    {font_bold_red}(X) Fail:{font_default} {task_title} ({time_elapsed:.1f}s)")
                    log_in_file(f"Fail: {task_title} ({time_elapsed:.1f}s)", logs_file, no_print=True)
                else:
                    print(f"\r    {font_bold_green}(✓) Done:{font_default} {task_title} ({time_elapsed:.1f}s)")
                    log_in_file(f"Done: {task_title} ({time_elapsed:.1f}s)", logs_file, no_print=True)
                # Display the cursor
                print(display_cursor, end="")
            thread = Thread(target=spin)
            thread.start()
            return thread

        log_in_file(f"\n  {font_bold}Preparing the Container Apps Cloud Build environment{font_default}\n", logs_file)

        # List the builders in the resource group
        thread = display_spinner("Listing the builders available in the Container Apps environment")
        builders_list_json_content = BuilderClient.list(cmd, resource_group_name)
        filtered_builders_list = [builder for builder in builders_list_json_content["value"] if builder["properties"]["environmentId"].endswith(f"/{environment_name}")]
        builder_available = len(filtered_builders_list) > 0
        if builder_available and filtered_builders_list[0]["properties"]["provisioningState"] != "Succeeded":
            non_ready_builder_name = filtered_builders_list[0]["name"]
            non_ready_provisioning_state = filtered_builders_list[0]["properties"]["provisioningState"]
            raise ValidationError(f"The builder selected, {non_ready_builder_name}, isn't ready to build (current state: {non_ready_provisioning_state})")
        done_spinner = True
        thread.join()

        if builder_available:
            builder_name = filtered_builders_list[0]["name"]
            log_in_file(f"{substatus_indentation}Builder selected: {builder_name}", logs_file)
        else:
            log_in_file(f"{substatus_indentation}No builder available in environment {font_bold}{environment_name}{font_default}", logs_file)
            # Builder creation
            done_spinner = False
            thread = display_spinner("Creating the builder in the Container Apps environment")
            builder_name = f"builder{run_full_id}"[:12]
            BuilderClient.create(cmd, builder_name, resource_group_name, environment_name, location)
            done_spinner = True
            thread.join()
            log_in_file(f"{substatus_indentation}Builder created: {builder_name}", logs_file)

        log_in_file(f"\n  {font_bold}Building the application{font_default}\n", logs_file)

        # Build creation
        done_spinner = False
        thread = display_spinner("Starting the Container Apps Cloud Build agent")
        build_env_vars = parse_build_env_vars(build_env_vars)
        build_create_json_content = BuildClient.create(cmd, builder_name, generated_build_name, resource_group_name, location, build_env_vars, True)
        build_name = build_create_json_content["name"]
        upload_endpoint = build_create_json_content["properties"]["uploadEndpoint"]
        log_streaming_endpoint = build_create_json_content["properties"]["logStreamEndpoint"]
        done_spinner = True
        thread.join()
        log_in_file(f"{substatus_indentation}Cloud Build agent started: {build_name}", logs_file)

        # Token retrieval
        done_spinner = False
        thread = display_spinner("Retrieving the authentication token")
        token_retrieval_json_content = BuildClient.list_auth_token(cmd, builder_name, build_name, resource_group_name, location)
        token = token_retrieval_json_content["token"]
        done_spinner = True
        thread.join()

        # Source code compression
        data_file_path = source
        source_is_folder = os.path.isdir(source)
        if source_is_folder:
            done_spinner = False
            thread = display_spinner(f"Compressing data: {font_bold}{source}{font_default}")
            data_file_path = os.path.join(tempfile.gettempdir(), f"{build_name}.tar.gz")
            archive_source_code(data_file_path, source)
            done_spinner = True
            thread.join()

        # File upload
        done_spinner = False
        thread = display_spinner("Uploading data")
        headers = {'Authorization': 'Bearer ' + token}
        try:
            data_file = open(data_file_path, "rb")
            file_name = os.path.basename(data_file_path)
            files = [("file", (file_name, data_file))]
            response_file_upload = requests.post(
                upload_endpoint,
                files=files,
                headers=headers)
        finally:
            # Close the file now that it was uploaded.
            data_file.close()
            # if customer uploaded source file is a folder, delete the temp compressed file
            if source_is_folder:
                os.unlink(data_file_path)
        if not response_file_upload.ok:
            raise ValidationError(f"Error when uploading the file, request exited with {response_file_upload.status_code}")
        done_spinner = True
        thread.join()

        # Wait for provisioning state to succeed and the build status to be InProgress
        done_spinner = False
        thread = display_spinner("Waiting for the Cloud Build agent to report status")
        build_provisioning = True
        while build_provisioning:
            build_json_content = BuildClient.get(cmd, builder_name, build_name, resource_group_name)
            if build_json_content["properties"]["provisioningState"] == "Succeeded":
                build_status = build_json_content["properties"]["buildStatus"]
                if build_status == "InProgress":
                    build_provisioning = False
                elif build_status in ("Failed", "Canceled"):
                    raise ValidationError(f"The build {build_name} was provisioned properly but its build status is {build_status}")
            time.sleep(1)
        done_spinner = True
        thread.join()

        # Initializing logs stream
        done_spinner = False
        thread = display_spinner("Streaming Cloud Build logs")
        headers = {'Authorization': 'Bearer ' + token}
        logs_stream_retries = 0
        maximum_logs_stream_retries = 8
        while logs_stream_retries < maximum_logs_stream_retries:
            logs_stream_retries += 1
            response_log_streaming = requests.get(
                log_streaming_endpoint,
                headers=headers,
                stream=True)
            if not response_log_streaming.ok:
                raise ValidationError(f"Error when streaming the logs, request exited with {response_log_streaming.status_code}")
            # Actually validate that we logs streams successfully
            response_log_streaming_lines = response_log_streaming.iter_lines()
            count_lines_check = 4
            for line in response_log_streaming_lines:
                log_line = remove_ansi_characters(line.decode("utf-8"))
                log_in_file(log_line, logs_file, no_print=True)
                if "Kubernetes error happened" in log_line:
                    if logs_stream_retries >= maximum_logs_stream_retries:
                        # We're getting an error when streaming logs and no retries remaining.
                        raise CloudBuildError(log_line)
                    # Wait for a bit, and then break to try again. Using "logs_stream_retries" as the number of seconds to wait is a primitive exponential retry.
                    time.sleep(logs_stream_retries)
                    break
                count_lines_check -= 1
                if count_lines_check <= 0:
                    break
            if count_lines_check <= 0:
                # We checked the set number of lines and logs stream without error. Let's continue.
                break
            # Wait for a bit, and then break to try again. Using "logs_stream_retries" as the number of seconds to wait is a primitive exponential retry.
            log_in_file(f"{substatus_indentation}Wait logstream for build container...\n", logs_file)
            time.sleep(logs_stream_retries)
        done_spinner = True
        thread.join()

        # Initializing Buildpack and Stream the logs
        done_spinner = False
        thread = display_spinner("Buildpack: Initializing")
        log_execution_phase_pattern = r"===== (.*) =====$"
        current_phase_logs = ""
        for line in response_log_streaming_lines:
            log_line = remove_ansi_characters(line.decode("utf-8"))
            current_phase_logs += f"{log_line}\n{substatus_indentation}"
            if "----- Cloud Build failed with exit code" in log_line or "Exiting with failure status due to previous errors" in log_line:
                raise CloudBuildError(current_phase_logs)

            log_execution_phase_match = re.search(log_execution_phase_pattern, log_line)
            if log_execution_phase_match:
                log_execution_phase = log_execution_phase_match.group(1)
                # Stop the previous execution phase
                done_spinner = True
                thread.join()

                # Start the current one
                current_phase_logs = ""
                done_spinner = False
                thread = display_spinner(f"Buildpack: {log_execution_phase}")
            log_in_file(log_line, logs_file, no_print=True)
        done_spinner = True
        thread.join()

        final_image = build_json_content["properties"]["destinationContainerRegistry"]["image"]
        log_in_file(f"{substatus_indentation}{font_bold}Successfully built and containerized image: {final_image}{font_default}", logs_file)
        log_in_file(f"{substatus_indentation}Full logs: {logs_file_path}\n", logs_file)
        logs_file.close()
        return final_image
    except KeyboardInterrupt as keyboard_interrupt:
        cancel_spinner = True
        thread.join()
        log_in_file(f"{substatus_indentation}Full logs: {logs_file_path}\n", logs_file)
        raise keyboard_interrupt
    except CloudBuildError as cloud_build_error:
        fail_spinner = True
        thread.join()
        log_in_file(f"{substatus_indentation}{font_bold_red}{str(cloud_build_error)}{font_default}", logs_file)
        log_in_file(f"{substatus_indentation}Full logs: {logs_file_path}\n", logs_file)
        raise ValidationError("The Cloud Build failed because of an error during the build process.") from cloud_build_error
    except (ValidationError, Exception) as error:
        fail_spinner = True
        thread.join()
        log_in_file(f"{substatus_indentation}{font_bold_red}{str(error)}{font_default}", logs_file)
        log_in_file(f"{substatus_indentation}Full logs: {logs_file_path}\n", logs_file)
        raise error
