# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from threading import Thread
import os
import re
import requests
import tempfile
import time

from ._archive_utils import archive_source_code

from azure.cli.core.azclierror import (
    ValidationError
)

from ._clients import BuilderClient, BuildClient

from ._utils import (
    log_in_file,
    remove_ansi_characters
)

class CloudBuildError(Exception):
    pass

def run_cloud_build(cmd, image_name, source, location, subscription_id, resource_group_name, environment_name, run_full_id, logs_file, logs_file_path):
    generated_build_name = 'build{}'.format(run_full_id)[:12]
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
        font_blue = "\033[94m"
        substatus_indentation = "              "
        def display_spinner(task_title):
            # Hide the cursor
            print('\033[?25l', end="")
            def spin():
                loop_counter = 0
                start_time = time.time()
                while (done_spinner == False and fail_spinner == False and cancel_spinner == False):
                    loop_counter = (loop_counter + 1) % 17
                    loading_bar_left_spaces_count =  loop_counter - 9 if loop_counter > 9 else 0
                    loading_bar_right_spaces_count =  6 - loop_counter if loop_counter < 7 else 0
                    spinner = f"[{' ' * loading_bar_left_spaces_count}{'=' * (7 - loading_bar_left_spaces_count - loading_bar_right_spaces_count)}{' ' * loading_bar_right_spaces_count}]"
                    time_elapsed = time.time() - start_time
                    print(f"\r    {spinner} {task_title} ({time_elapsed:.1f}s)", end="", flush=True)
                    time.sleep(0.15)
                if (cancel_spinner):
                    print(f"\r    {font_bold_yellow}Canceled:{font_default} {task_title} ({time_elapsed:.1f}s)")
                    log_in_file(f"Canceled: {task_title} ({time_elapsed:.1f}s)", logs_file, no_print=True)
                elif (fail_spinner):
                    print(f"\r    {font_bold_red}(X) Fail:{font_default} {task_title} ({time_elapsed:.1f}s)")
                    log_in_file(f"Fail: {task_title} ({time_elapsed:.1f}s)", logs_file, no_print=True)
                else:
                    print(f"\r    {font_bold_green}(✓) Done:{font_default} {task_title} ({time_elapsed:.1f}s)")
                    log_in_file(f"Done: {task_title} ({time_elapsed:.1f}s)", logs_file, no_print=True)
                # Display the cursor
                print('\033[?25h', end="")
            thread = Thread(target=spin)
            thread.start()
            return thread

        log_in_file(f"\n  {font_bold}Preparing the Container Apps Cloud Build environment{font_default}\n", logs_file)

        # List the builders in the resource group
        thread = display_spinner("Listing the builders available in the Container Apps environment")
        builders_list_json_content = BuilderClient.list(cmd, resource_group_name)
        done_spinner = True
        thread.join()

        if len(builders_list_json_content["value"]) > 0:
            builder_name = builders_list_json_content["value"][0]["name"]
            log_in_file(f"{substatus_indentation}Builder selected: {builder_name}", logs_file)
        else:
            log_in_file(f"{substatus_indentation}No builder available in environment {font_bold}{environment_name}{font_default}", logs_file)
            # Builder creation
            done_spinner = False
            thread = display_spinner("Creating the builder in the Container Apps environment")
            builder_name = 'builder{}'.format(run_full_id)[:12]
            BuilderClient.create(cmd, builder_name, resource_group_name, environment_name, location)
            done_spinner = True
            thread.join()
            log_in_file(f"{substatus_indentation}Builder created: {builder_name}", logs_file)

        log_in_file(f"\n  {font_bold}Building the application{font_default}\n", logs_file)

        # Build creation
        done_spinner = False
        thread = display_spinner("Starting the Container Apps Cloud Build agent")
        build_create_json_content = BuildClient.create(cmd, builder_name, generated_build_name, resource_group_name, location)
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
        done_spinner = False
        thread = display_spinner(f"Compressing data: {font_bold}{source}{font_default}")
        tar_file_path = os.path.join(tempfile.gettempdir(), f"{build_name}.tar.gz")
        archive_source_code(tar_file_path, source)
        done_spinner = True
        thread.join()

        # File upload
        done_spinner = False
        thread = display_spinner(f"Uploading compressed data")
        headers = {'Authorization': 'Bearer ' + token}
        files = [("file", ("build_data.tar.gz", open(tar_file_path, "rb"), "application/x-tar"))]
        response_file_upload = requests.post(
            upload_endpoint,
            files=files,
            headers=headers)
        if not (response_file_upload.ok):
            raise ValidationError(f"Error when uploading the file, request exited with {response_file_upload.status_code}")
        done_spinner = True
        thread.join()

        # Wait for provisioning state to succeed
        done_spinner = False
        thread = display_spinner(f"Waiting for the Cloud Build agent to report status")
        build_provisioning = True
        while (build_provisioning):
            build_json_content = BuildClient.get(cmd, builder_name, build_name, resource_group_name)
            if build_json_content["properties"]["provisioningState"] == "Succeeded":
                build_provisioning = False
            time.sleep(2)
        done_spinner = True
        thread.join()

        # Initializing logs stream
        done_spinner = False
        thread = display_spinner(f"Streaming Cloud Build logs")
        headers = {'Authorization': 'Bearer ' + token}
        response_log_streaming = requests.get(
            log_streaming_endpoint,
            headers=headers,
            stream=True)
        if not (response_log_streaming.ok):
            raise ValidationError(f"Error when streaming the logs, request exited with {response_log_streaming.status_code}")
        done_spinner = True
        thread.join()

        # Initializing Buildpack and Stream the logs
        done_spinner = False
        thread = display_spinner(f"Buildpack: Initializing")
        log_execution_phase_pattern = r"===== (.*) =====$"
        current_phase_logs = ""
        for line in response_log_streaming.iter_lines():
            log_line = remove_ansi_characters(line.decode("utf-8"))
            current_phase_logs += f"{log_line}\n{substatus_indentation}"
            if ("ERROR:" in log_line or "Kubernetes error happened" in log_line):
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

        # TODO: Delete local tar.gz file
        #os.unlink(tar_file_path)

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
        raise ValidationError("The Cloud Build failed because of an error during the build process.")
    except (ValidationError, Exception) as error:
        fail_spinner = True
        thread.join()
        log_in_file(f"{substatus_indentation}{font_bold_red}{str(error)}{font_default}", logs_file)
        log_in_file(f"{substatus_indentation}Full logs: {logs_file_path}\n", logs_file)
        raise error