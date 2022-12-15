# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,redefined-builtin,bare-except,inconsistent-return-statements

import gzip
import io
import json
import logging
import os
import uuid
import knack.log

from azure.cli.command_modules.storage.operations.account import show_storage_account_connection_string
from azure.cli.core.azclierror import (FileOperationError, AzureInternalError,
                                       InvalidArgumentValueError, AzureResponseError,
                                       RequiredArgumentMissingError)

# from azure.quantum.optimization.problem import Problem
from azure.quantum.storage import create_container, upload_blob
from azure.quantum.target import Quantinuum, IonQ
from azure.quantum.target.rigetti.target import Rigetti

from .._client_factory import cf_jobs, _get_data_credentials
from .workspace import WorkspaceInfo
from .target import TargetInfo


MINIMUM_MAX_POLL_WAIT_SECS = 1
DEFAULT_SHOTS = 500
QIO_DEFAULT_TIMEOUT = 100

ERROR_MSG_MISSING_INPUT_FILE = "The following argument is required: --job-input-file"  # NOTE: The Azure CLI core generates a similar error message, but "the" is lowercase and "arguments" is always plural.
ERROR_MSG_MISSING_OUTPUT_FORMAT = "The following argument is required: --job-output-format"
JOB_SUBMIT_DOC_LINK_MSG = "See https://learn.microsoft.com/cli/azure/quantum/job?view=azure-cli-latest#az-quantum-job-submit"
JOB_TYPE_NOT_VALID_MSG = "Job type not recognized. This is a bug!"

# Job types
QIO_JOB = 1
QIR_JOB = 2
PASS_THROUGH_JOB = 3

logger = logging.getLogger(__name__)
knack_logger = knack.log.get_logger(__name__)


def list(cmd, resource_group_name, workspace_name, location):
    """
    Get the list of jobs in a Quantum Workspace.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    return client.list()


def get(cmd, job_id, resource_group_name=None, workspace_name=None, location=None):
    """
    Get the job's status and details.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    return client.get(job_id)


def _check_dotnet_available():
    """
    Will fail if dotnet cannot be executed on the system.
    """
    args = ["dotnet", "--version"]

    try:
        import subprocess
        result = subprocess.run(args, stdout=subprocess.PIPE, check=False)
    except FileNotFoundError as e:
        raise FileOperationError("Could not find 'dotnet' on the system.") from e

    if result.returncode != 0:
        raise FileOperationError(f"Failed to run 'dotnet'. (Error {result.returncode})")


def build(cmd, target_id=None, project=None, target_capability=None):
    """
    Compile a Q# program to run on Azure Quantum.
    """
    target = TargetInfo(cmd, target_id)

    # Validate that dotnet is available
    _check_dotnet_available()

    args = ["dotnet", "build"]

    if project:
        args.append(project)

    args.append(f"-property:ExecutionTarget={target.target_id}")

    if target_capability:
        args.append(f"-property:TargetCapability={target_capability}")

    logger.debug("Building project with arguments:")
    logger.debug(args)

    knack_logger.warning('Building project...')

    import subprocess
    result = subprocess.run(args, stdout=subprocess.PIPE, check=False)

    if result.returncode == 0:
        return {'result': 'ok'}

    # If we got here, we might have encountered an error during compilation, so propagate standard output to the user.
    logger.error("Compilation stage failed with error code %s", result.returncode)
    print(result.stdout.decode('ascii'))
    raise AzureInternalError("Failed to compile program.")


def _generate_submit_args(program_args, ws, target, token, project, job_name, shots, storage, job_params):
    """ Generates the list of arguments for calling submit on a Q# project """

    args = ["dotnet", "run", "--no-build"]

    if project:
        args.append("--project")
        args.append(project)

    args.append("--")
    args.append("submit")

    args.append("--subscription")
    args.append(ws.subscription)

    args.append("--resource-group")
    args.append(ws.resource_group)

    args.append("--workspace")
    args.append(ws.name)

    args.append("--target")
    args.append(target.target_id)

    args.append("--output")
    args.append("Id")

    if job_name:
        args.append("--job-name")
        args.append(job_name)

    if shots:
        args.append("--shots")
        args.append(shots)

    if storage:
        args.append("--storage")
        args.append(storage)

    args.append("--aad-token")
    args.append(token)

    args.append("--location")
    args.append(ws.location)

    args.append("--user-agent")
    args.append("CLI")

    if job_params:
        args.append("--job-params")
        for k, v in job_params.items():
            if isinstance(v, str):
                # If value is string type already, do not use json.dumps(), since it will add extra escapes to the string
                args.append(f"{k}={v}")
            else:
                args.append(f"{k}={json.dumps(v)}")

    args.extend(program_args)

    logger.debug("Running project with arguments:")
    logger.debug(args)

    return args


def _set_cli_version():
    # This is a temporary approach for runtime compatibility between a runtime version
    # before support for the --user-agent parameter is added. We'll rely on the environment
    # variable before the stand alone executable submits to the service.
    try:
        from .._client_factory import get_appid
        os.environ["USER_AGENT"] = get_appid()
    except:
        logger.warning("User Agent environment variable could not be set.")


def _has_completed(job):
    return job.status in ("Succeeded", "Failed", "Cancelled")


def submit(cmd, program_args, resource_group_name, workspace_name, location, target_id,
           project=None, job_name=None, shots=None, storage=None, no_build=False, job_params=None, target_capability=None,
           job_input_file=None, job_input_format=None, job_output_format=None, entry_point=None):
    """
    Submit a quantum program to run on Azure Quantum.
    """
    # # Identify the type of job being submitted
    # if job_input_format is None:
    #     job_type = QSHARP_JOB
    # elif job_input_format.lower() == "microsoft.qio.v2":
    #     job_type = QIO_JOB
    #     if job_input_file is not None and job_input_file.split(".")[-1].lower() == "pb":
    #         job_type = QIO_PB_JOB
    # elif job_input_format.lower() == "qir.v1":
    #     job_type = QIR_JOB
    # else:
    #     raise InvalidArgumentValueError(f"Job input format {job_input_format} is not supported.", JOB_SUBMIT_DOC_LINK_MSG)
    #
    # if job_type == QIO_JOB:
    #     return _submit_directly_to_service(cmd, job_type, program_args, resource_group_name, workspace_name, location, target_id,
    #                                        job_name, shots, storage, job_params, target_capability,
    #                                        job_input_file, job_input_format, job_output_format, entry_point)
    # if job_type == QIO_PB_JOB:
    #     return _submit_directly_to_service(cmd, job_type, program_args, resource_group_name, workspace_name, location, target_id,
    #                                        job_name, shots, storage, job_params, target_capability,
    #                                        job_input_file, job_input_format, job_output_format, entry_point)
    # if job_type == QIR_JOB:
    #     return _submit_directly_to_service(cmd, job_type, program_args, resource_group_name, workspace_name, location, target_id,
    #                                        job_name, shots, storage, job_params, target_capability,
    #                                        job_input_file, job_input_format, job_output_format, entry_point)
    # if job_type == QSHARP_JOB:
    #     return _submit_qsharp(cmd, program_args, resource_group_name, workspace_name, location, target_id,
    #                           project, job_name, shots, storage, no_build, job_params, target_capability)

    if job_input_format is None:
        return _submit_qsharp(cmd, program_args, resource_group_name, workspace_name, location, target_id,
                              project, job_name, shots, storage, no_build, job_params, target_capability)
    # else:
    #     return _submit_directly_to_service(cmd, program_args, resource_group_name, workspace_name, location, target_id,
    #                                        job_name, shots, storage, job_params, target_capability,
    #                                        job_input_file, job_input_format, job_output_format, entry_point)
    return _submit_directly_to_service(cmd, resource_group_name, workspace_name, location, target_id,
                                       job_name, shots, storage, job_params, target_capability,
                                       job_input_file, job_input_format, job_output_format, entry_point)


# def _get_default_job_parameters(provider, workspace):
#     if provider == "quantinuum":
#         target_parameters = Quantinuum(workspace)
#     elif provider == "ionq":
#         target_parameters = IonQ(workspace)
#     elif provider == "rigetti":
#         target_parameters = Rigetti(workspace)
#     else:
#         print("Provider not recognized")
#         return
#
#     if target_parameters is not None:
#         default_input_format = target_parameters.input_data_format
#         default_output_format = target_parameters.output_data_format
#         default_content_type = target_parameters.content_type
#         default_encoding = target_parameters.encoding

#     # >>>>>>>>>>
#         print(f"provider = {provider}")
#         print(f"input_format = {default_input_format}")
#         print(f"output_format = {default_output_format}")
#         print(f"content_type = {default_content_type}")
#         print(f"encoding = {default_encoding}")
#     else:
#         print("Provider not recognized")
#
#     return
#     # <<<<<<<<<<


# def _submit_directly_to_service(cmd, job_type, program_args, resource_group_name, workspace_name, location, target_id,
#                                 job_name, shots, storage, job_params, target_capability,
#                                 job_input_file, job_input_format, job_output_format, entry_point):
def _submit_directly_to_service(cmd, resource_group_name, workspace_name, location, target_id,
                                job_name, shots, storage, job_params, target_capability,
                                job_input_file, job_input_format, job_output_format, entry_point):
    """
    Submit QIR bitcode, QIO problem JSON, or a pass-through job to run on Azure Quantum.
    """
    # Get workspace and target information
    ws_info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    if ws_info is None:
        raise AzureInternalError("Failed to get workspace information.")
    target_info = TargetInfo(cmd, target_id)
    if target_info is None:
        raise AzureInternalError("Failed to get target information.")
    provider_id = target_info.target_id.split('.')[0]                   # <<<<< Is provider_id case sensitive? <<<<<

    # Microsoft provider_id values don't follow the same pattern as all the other companies' provider_id
    if provider_id.lower() == "microsoft":
        after_the_dot = target_info.target_id.split('.')[1]
        if after_the_dot.lower() == "simulator" or after_the_dot.lower() == "fleetmanagement":  # <<<<< Are there more like these?
            provider_id = f"{provider_id}.{after_the_dot}"

    # >>>>>>>>>>
    # print(f"provider_id = {provider_id}")
    # return
    # <<<<<<<<<<

    # >>>>>>>>>> Is this useful??? >>>>>>>>>>
    # Get default job parameters for this provider
    if provider_id == "quantinuum":
        target_parameters = Quantinuum(workspace_name)
    elif provider_id == "ionq":
        target_parameters = IonQ(workspace_name)
    elif provider_id == "rigetti":
        target_parameters = Rigetti(workspace_name)
    else:
        target_parameters = None
        # print("Provider defaults not defined in qdk-python")
        # return

    if target_parameters is None:
        # default_input_format = None
        default_output_format = None
        default_content_type = None
        default_encoding = None
    else:
        # default_input_format = target_parameters.input_data_format
        default_output_format = target_parameters.output_data_format
        default_content_type = target_parameters.content_type
        default_encoding = target_parameters.encoding

    if job_output_format is None and default_output_format is not None:
        job_output_format = default_output_format
    # <<<<<<<<<<

    # >>>>>>>>>>
        # print(f"provider_id = {provider_id}")
        # print(f"input_format = {default_input_format}")
        # print(f"output_format = {default_output_format}")
        # print(f"content_type = {default_content_type}")
        # print(f"encoding = {default_encoding}")
    # else:
    #     print("Provider not recognized")
    # return
    # <<<<<<<<<<

    # Identify the type of job being submitted
    lc_job_input_format = job_input_format.lower()
    if lc_job_input_format == "qir.v1":                 # <<<<< <<<<<< What about Rigetti and Quantimuum QIR?
        job_type = QIR_JOB
    elif lc_job_input_format == "microsoft.qio.v2":
        job_type = QIO_JOB
    else:
        # raise InvalidArgumentValueError(f"Job input format {job_input_format} is not supported.", JOB_SUBMIT_DOC_LINK_MSG)
        job_type = PASS_THROUGH_JOB

    if job_output_format is None:
        if job_type == QIR_JOB:
            job_output_format = "microsoft.quantum-results.v1"
        elif job_type == QIO_JOB:
            job_output_format = "microsoft.qio-results.v2"
        else:
            # raise InvalidArgumentValueError(JOB_TYPE_NOT_VALID_MSG)
            raise RequiredArgumentMissingError(ERROR_MSG_MISSING_OUTPUT_FORMAT, JOB_SUBMIT_DOC_LINK_MSG)

    # Look for an input file based on job_input_format
    if job_input_file is None:
        if job_type == QIR_JOB:
            input_file_extension = ".bc"
        elif job_type == QIO_JOB:
            input_file_extension = ".json"
        else:
            raise RequiredArgumentMissingError(ERROR_MSG_MISSING_INPUT_FILE, JOB_SUBMIT_DOC_LINK_MSG)

        path = os.path.abspath(os.curdir)
        for file_name in os.listdir(path):
            if file_name.endswith(input_file_extension):
                job_input_file = os.path.join(path, file_name)
                break

    if job_input_file is None:
        raise RequiredArgumentMissingError(ERROR_MSG_MISSING_INPUT_FILE, JOB_SUBMIT_DOC_LINK_MSG)

    # Prepare for input file upload according to job type
    if job_type == QIO_JOB:
        container_name_prefix = "cli-qio-job-"
        content_type = "application/json"
        content_encoding = "gzip"
        return_sas_token = True
        with open(job_input_file, encoding="utf-8") as qio_file:
            uncompressed_blob_data = qio_file.read()

        if "content_type" in uncompressed_blob_data and "application/x-protobuf" in uncompressed_blob_data:
            raise InvalidArgumentValueError('Content type "application/x-protobuf" is not supported.')

        # Compress the input data (This code is based on to_blob in qdk-python\azure-quantum\azure\quantum\optimization\problem.py)
        data = io.BytesIO()
        with gzip.GzipFile(fileobj=data, mode="w") as fo:
            fo.write(uncompressed_blob_data.encode())
        blob_data = data.getvalue()

    elif job_type == QIR_JOB:
        container_name_prefix = "cli-qir-job-"
        content_type = "application/x-qir.v1"
        content_encoding = None
        return_sas_token = False
        with open(job_input_file, "rb") as qir_file:
            blob_data = qir_file.read()

    else:
        container_name_prefix = "cli-pass-through-job-"
        # content_type = None         # <<<<< Should we get this from job_params? <<<<<
        # content_encoding = None
        content_type = default_content_type
        content_encoding = default_encoding
        return_sas_token = False
        with open(job_input_file, "rb") as qir_file:
            blob_data = qir_file.read()

    # Upload the input file to the workspace's storage account
    if storage is None:
        from .workspace import get as ws_get
        ws = ws_get(cmd)
        storage = ws.storage_account.split('/')[-1]

    job_id = str(uuid.uuid4())
    container_name = container_name_prefix + job_id
    connection_string_dict = show_storage_account_connection_string(cmd, resource_group_name, storage)
    connection_string = connection_string_dict["connectionString"]
    container_client = create_container(connection_string, container_name)
    blob_name = "inputData"
    blob_uri = upload_blob(container_client, blob_name, content_type, content_encoding, blob_data, return_sas_token)

    # Set the job parameters
    start_of_blob_name = blob_uri.find(blob_name)
    if job_type == QIO_JOB:
        end_of_blob_name = blob_uri.find("?")
        container_uri = blob_uri[0:start_of_blob_name - 1] + blob_uri[end_of_blob_name:]

        # input_params = dict()
        input_params = {}
        if job_params is None:
            input_params = {"params": {"timeout": QIO_DEFAULT_TIMEOUT}}
        else:
            if "timeout" not in job_params:
                job_params["timeout"] = QIO_DEFAULT_TIMEOUT
            input_params["params"] = job_params

    elif job_type == QIR_JOB:
        container_uri = blob_uri[0:start_of_blob_name - 1]
        if shots is None:
            shots = DEFAULT_SHOTS
        else:
            error_msg = "--shots value is not valid."
            recommendation = "Enter a positive integer."
            try:
                shots = int(shots)
                if shots < 1:
                    raise InvalidArgumentValueError(error_msg, recommendation)
            except:
                raise InvalidArgumentValueError(error_msg, recommendation)

        if target_capability is None:
            target_capability = "AdaptiveExecution"     # <<<<< Cesar said to use this for QCI. Does it apply to other providers?

        # >>>>> TODO: Get additional parameters from the command line <<<<<
        input_params = {'arguments': [], 'name': job_name, 'targetCapability': target_capability, 'shots': shots, 'entryPoint': entry_point}
        # if job_params is not None:
        #     input_params.extend(job_params)
    else:
        # input_params = job_params
        # >>>>>>>>>>
        container_uri = blob_uri[0:start_of_blob_name - 1]
        input_params = {"count": 2}                         # <<<<< Is there a default for "count", like for "shots"?
        # <<<<<<<<<<
        # >>>>> TODO: Get additional parameters from the command line <<<<<

    client = cf_jobs(cmd.cli_ctx, ws_info.subscription, ws_info.resource_group, ws_info.name, ws_info.location)
    job_details = {'name': job_name,                # job_details is defined in vendored_sdks\azure_quantum\models\_models_py3.py, starting at line 132
                   'container_uri': container_uri,
                   'input_data_format': job_input_format,
                   'output_data_format': job_output_format,
                   'inputParams': input_params,
                   'provider_id': provider_id,
                   'target': target_info.target_id}

    # Submit the job
    return client.create(job_id, job_details)


def _submit_qsharp(cmd, program_args, resource_group_name, workspace_name, location, target_id,
                   project, job_name, shots, storage, no_build, job_params, target_capability):
    """
    Submit a Q# project to run on Azure Quantum.
    """

    # We first build and then call run.
    # Can't call run directly because it fails to understand the
    # `ExecutionTarget` property when passed in the command line
    if not no_build:
        build(cmd, target_id=target_id, project=project, target_capability=target_capability)
        logger.info("Project built successfully.")
    else:
        _check_dotnet_available()

    ws = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    target = TargetInfo(cmd, target_id)
    token = _get_data_credentials(cmd.cli_ctx, ws.subscription).get_token().token

    args = _generate_submit_args(program_args, ws, target, token, project, job_name, shots, storage, job_params)
    _set_cli_version()

    knack_logger.warning('Submitting job...')

    import subprocess
    result = subprocess.run(args, stdout=subprocess.PIPE, check=False)

    if result.returncode == 0:
        std_output = result.stdout.decode('ascii').strip()
        # Retrieve the job-id as the last line from standard output.
        job_id = std_output.split()[-1]
        # Query for the job and return status to caller.
        return get(cmd, job_id, resource_group_name, workspace_name, location)

    # The program compiled successfully, but executing the stand-alone .exe failed to run.
    logger.error("Submission of job failed with error code %s", result.returncode)
    print(result.stdout.decode('ascii'))
    raise AzureInternalError("Failed to submit job.")


def _parse_blob_url(url):
    from urllib.parse import urlparse
    o = urlparse(url)

    try:
        account_name = o.netloc.split('.')[0]
        container = o.path.split('/')[-2]
        blob = o.path.split('/')[-1]
        sas_token = o.query
    except IndexError as e:
        raise InvalidArgumentValueError(f"Failed to parse malformed blob URL: {url}") from e

    return {
        "account_name": account_name,
        "container": container,
        "blob": blob,
        "sas_token": sas_token
    }


def output(cmd, job_id, resource_group_name, workspace_name, location):
    """
    Get the results of running a Q# job.
    """
    import tempfile
    # import json
    # import os
    from azure.cli.command_modules.storage._client_factory import blob_data_service_factory

    path = os.path.join(tempfile.gettempdir(), job_id)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    job = client.get(job_id)

    if os.path.exists(path):
        logger.debug("Using existing blob from %s", path)
    else:
        logger.debug("Downloading job results blob into %s", path)

        if job.status != "Succeeded":
            return job  # If "-o table" is specified, this allows transform_output() in commands.py
            #             to format the output, so the error info is shown. If "-o json" or no "-o"
            #             parameter is specified, then the full JSON job output is displayed, being
            #             consistent with other commands.

        args = _parse_blob_url(job.output_data_uri)
        blob_service = blob_data_service_factory(cmd.cli_ctx, args)
        blob_service.get_blob_to_path(args['container'], args['blob'], path)

    with open(path) as json_file:
        lines = [line.strip() for line in json_file.readlines()]

        # Receiving an empty response is valid.
        if len(lines) == 0:
            return

        if job.target.startswith("microsoft.simulator") and job.target != "microsoft.simulator.resources-estimator":
            result_start_line = len(lines) - 1
            is_result_string = lines[-1].endswith('"')
            if is_result_string:
                while result_start_line >= 0 and not lines[result_start_line].startswith('"'):
                    result_start_line -= 1
            if result_start_line < 0:
                raise AzureResponseError("Job output is malformed, mismatched quote characters.")

            # Print the job output and then the result of the operation as a histogram.
            # If the result is a string, trim the quotation marks.
            print('\n'.join(lines[:result_start_line]))
            raw_result = ' '.join(lines[result_start_line:])
            result = raw_result[1:-1] if is_result_string else raw_result
            print('_' * len(result) + '\n')

            json_string = '{ "histogram" : { "' + result + '" : 1 } }'
            data = json.loads(json_string)
        else:
            json_file.seek(0)  # Reset the file pointer before loading
            data = json.load(json_file)
        return data


def _validate_max_poll_wait_secs(max_poll_wait_secs):
    valid_max_poll_wait_secs = 0.0
    error_message = f"--max-poll-wait-secs parameter is not valid: {max_poll_wait_secs}"
    error_recommendation = f"Must be a number greater than or equal to {MINIMUM_MAX_POLL_WAIT_SECS}"

    try:
        valid_max_poll_wait_secs = float(max_poll_wait_secs)
    except ValueError as e:
        raise InvalidArgumentValueError(error_message, error_recommendation) from e

    if valid_max_poll_wait_secs < MINIMUM_MAX_POLL_WAIT_SECS:
        raise InvalidArgumentValueError(error_message, error_recommendation)

    return valid_max_poll_wait_secs


def wait(cmd, job_id, resource_group_name, workspace_name, location, max_poll_wait_secs=5):
    """
    Place the CLI in a waiting state until the job finishes running.
    """
    import time

    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)

    # TODO: LROPoller...
    wait_indicators_used = False
    poll_wait = 0.2
    max_poll_wait_secs = _validate_max_poll_wait_secs(max_poll_wait_secs)
    job = client.get(job_id)

    while not _has_completed(job):
        print('.', end='', flush=True)
        wait_indicators_used = True
        time.sleep(poll_wait)
        job = client.get(job_id)
        poll_wait = max_poll_wait_secs if poll_wait >= max_poll_wait_secs else poll_wait * 1.5

    if wait_indicators_used:
        # Insert a new line if we had to display wait indicators.
        print()

    return job


def job_show(cmd, job_id, resource_group_name, workspace_name, location):
    """
    Get the job's status and details.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    job = client.get(job_id)
    return job


def run(cmd, program_args, resource_group_name, workspace_name, location, target_id,
        project=None, job_name=None, shots=None, storage=None, no_build=False, job_params=None, target_capability=None,
        job_input_file=None, job_input_format=None, job_output_format=None, entry_point=None):
    """
    Submit a job to run on Azure Quantum, and wait for the result.
    """
    job = submit(cmd, program_args, resource_group_name, workspace_name, location, target_id,
                 project, job_name, shots, storage, no_build, job_params, target_capability,
                 job_input_file, job_input_format, job_output_format, entry_point)
    logger.warning("Job id: %s", job.id)
    logger.debug(job)

    job = wait(cmd, job.id, resource_group_name, workspace_name, location)
    logger.debug(job)

    if not job.status == "Succeeded":
        return job

    return output(cmd, job.id, resource_group_name, workspace_name, location)


def cancel(cmd, job_id, resource_group_name, workspace_name, location):
    """
    Request to cancel a job on Azure Quantum if it hasn't completed.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    job = client.get(job_id)

    if _has_completed(job):
        print(f"Job {job_id} has already completed with status: {job.status}.")
        return

    # If the job hasn't succeeded or failed, attempt to cancel.
    client.cancel(job_id)

    # Wait for the job status to complete or be reported as cancelled
    return wait(cmd, job_id, info.resource_group, info.name, info.location)
