# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import re
import yaml
import json
import requests
from functools import wraps
from knack.log import get_logger
from .raise_error import log_and_raise_error
from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
from .utils import get_self_serve_base_url, get_location_from_base_url, get_registry_info, load_inline_md_files, parse_azureml_model_uri, run_registry_mgmt_cmd

from azure.cli.core.azclierror import BadRequestError, ForbiddenError, InvalidArgumentValueError, AzureInternalError


# Command handlers receive the framework 'cmd' (and some CLI params like 'location')
# that the MPSS endpoints do not need; suppress unused-argument for this module.
# pylint: disable=unused-argument

module_logger = get_logger(__name__)

LOCATION = "location"

# Network timeout (seconds) for MPSS HTTP calls; generous enough for uploads/
# downloads but bounded so a hung connection can't block the CLI indefinitely.
REQUEST_TIMEOUT = 300


def validate_config_file(config) -> None:
    if not isinstance(config, dict):
        raise BadRequestError(
            "The YAML file is empty or not a valid mapping of fields. "
            "Please provide a YAML file with the required configuration fields.")

    required_fields = [LOCATION]
    # Sanity check to ensure all required fields are present
    missing_fields = [
        field for field in required_fields if field not in config or config[field] in [None, ""]]

    if missing_fields:
        raise BadRequestError(
            f"Missing or empty required fields: {', '.join(missing_fields)}")


def generate_token() -> AccessToken:
    credential = DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True,
        exclude_interactive_browser_credential=False)
    token = credential.get_token("https://management.azure.com/.default")
    return token


def handle_request_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.ConnectionError:
            endpoint_target = get_location_from_base_url(args[0])
            log_and_raise_error(BadRequestError(
                f"The MPSS endpoint target '{endpoint_target}' is not valid or the service is currently unavailable."))
        except (InvalidArgumentValueError, ForbiddenError, ResourceNotFoundError, AzureInternalError, BadRequestError) as err:
            log_and_raise_error(err)
        except Exception as err:
            log_and_raise_error(err)
    return wrapper


def append_correlation_id_message(user_message, correlation_id, message_type="default"):
    if message_type == "assistance":
        if correlation_id:
            return f"{user_message}\nIf you need assistance, reference this ID: {correlation_id}"
        return f"{user_message}\nIf you need assistance, please contact Microsoft support."

    if message_type == "reference":
        if correlation_id:
            return f"{user_message}\nReference ID: {correlation_id}"
        return user_message

    if message_type == "persist":
        if correlation_id:
            return f"{user_message}\nIf the problem persists, contact Microsoft support with this ID: {correlation_id}"
        return f"{user_message}\nIf the problem persists, contact Microsoft support."

    if correlation_id:
        return f"{user_message}\nPlease contact Microsoft support with this correlation ID: {correlation_id}"
    return f"{user_message}\nPlease contact Microsoft support. If possible, include the timestamp and command used."


@handle_request_errors
def make_request(url, headers, method="GET", data=None, params=None, stream=False):
    if params:
        # Drop unset query params so requests doesn't serialize e.g. currentPage=None
        params = {k: v for k, v in params.items() if v is not None}
    if method == "GET":
        response = requests.get(url, headers=headers,
                                params=params, stream=stream, timeout=REQUEST_TIMEOUT)
    elif method == "PUT":
        response = requests.put(url, headers=headers, data=data, timeout=REQUEST_TIMEOUT)
    elif method == "PATCH":
        response = requests.patch(url, headers=headers, data=data, timeout=REQUEST_TIMEOUT)
    elif method == "POST":
        response = requests.post(url, headers=headers, data=data, timeout=REQUEST_TIMEOUT)
    else:
        raise InvalidArgumentValueError(f"Unsupported HTTP method: {method}")

    module_logger.debug(response.status_code)
    module_logger.debug(response.text if not stream else "Stream response")

    correlation_id = response.headers.get("x-mpss-correlation-id")

    if 200 <= response.status_code < 300:
        if stream:
            return response
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            module_logger.debug(
                f"Invalid JSON in successful response: {response.text[:200]}...")
            user_message = "Received an invalid response format from the service."
            user_message = append_correlation_id_message(
                user_message, correlation_id)
            raise AzureInternalError(user_message)

    if response.status_code == 400:
        try:
            error_data = response.json()
            error_message = error_data.get('title', 'Invalid request')
            error_details = error_data.get('errors', '')
        except ValueError:
            module_logger.debug(
                f"Invalid JSON in 400 response: {response.text[:200]}...")
            error_message = "Bad request"
            error_details = "The request was invalid, but error details are not available."

        user_message = f"{error_message}"
        if error_details:
            user_message += f"\nDetails: {error_details}"
        user_message += "\nPlease check your input and try again."
        user_message = append_correlation_id_message(
            user_message, correlation_id, "assistance")
        module_logger.warning(user_message)
        raise BadRequestError(user_message)

    if response.status_code == 403:
        user_message = ("Access denied. You don't have permission to perform this action.\n"
                        "Please contact your administrator or Microsoft support for access.")
        user_message = append_correlation_id_message(
            user_message, correlation_id, "reference")
        module_logger.warning(user_message)
        raise ForbiddenError(user_message)

    if response.status_code == 404:
        user_message = response.text.strip() or "The requested resource was not found."
        user_message = append_correlation_id_message(
            user_message, correlation_id, "reference")
        module_logger.warning(user_message)
        raise ResourceNotFoundError(user_message)

    if 400 <= response.status_code < 500:
        user_message = f"Client error occurred (Status: {response.status_code})."
        user_message = append_correlation_id_message(
            user_message, correlation_id, "assistance")
        module_logger.warning(user_message)
        raise BadRequestError(user_message)

    if 500 <= response.status_code < 600:
        user_message = f"Server error occurred (Status: {response.status_code})."
        user_message = append_correlation_id_message(
            user_message, correlation_id, "persist")
        module_logger.error(user_message)
        raise AzureInternalError(user_message)

    user_message = f"An unexpected error occurred (Status: {response.status_code})."
    user_message = append_correlation_id_message(
        user_message, correlation_id)
    module_logger.error(user_message)
    module_logger.debug(
        f"Unexpected error - Status: {response.status_code}, Response: {response.text}, Correlation ID: {correlation_id}")
    raise AzureInternalError(user_message)


def _download_file_from_response(response, file_name=None, result_path=None, file_type_description="file"):
    """Helper function to download and save a file from an HTTP response.
    Args:
        response: HTTP response object with file content (with stream=True)
        file_name: Optional filename to use for the downloaded file
        result_path: Optional path where the file should be saved
        file_type_description: Description of the file type for logging
    Returns:
        dict: Dictionary containing the saved file path
    """
    if not 200 <= response.status_code < 300:
        return None

    output_filename = file_name
    if not output_filename and 'content-disposition' in response.headers:
        content_disp = response.headers['content-disposition']
        filename_match = re.search(r'filename=([^;]+)', content_disp)
        if filename_match:
            output_filename = filename_match.group(1).strip('"\'')

    if not output_filename:
        raise BadRequestError(
            "Could not determine the output file name from the server response. "
            "Please provide one explicitly with --file-name.")

    # Sanitize to a bare file name so a server-supplied content-disposition value
    # (e.g. "../../etc/passwd") cannot write outside the target directory.
    output_filename = os.path.basename(output_filename)
    if not output_filename:
        raise BadRequestError("The resolved output file name is not valid.")

    output_dir = result_path if result_path else os.getcwd()
    file_path = os.path.join(output_dir, output_filename)

    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    module_logger.info(
        f"Downloaded {file_type_description} ({os.path.getsize(file_path)/1024:.1f} KB) saved to: {file_path}")

    return {"file_path": file_path}


def ml_model_hosting_create_config(cmd, publisher=None, model=None, file=None):
    token = generate_token()
    try:
        with open(file, "r") as f:
            gpu_config = yaml.safe_load(f)
    except Exception as e:
        raise BadRequestError(
            f"Failed to read or parse the YAML file: {str(e)}")

    module_logger.debug(f"Gpu config: {gpu_config}")
    validate_config_file(gpu_config)

    api_version = '2024-10-31'
    base_url = get_self_serve_base_url(location=gpu_config.get('location'))
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/gpu-config?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}
    payload = json.dumps(gpu_config)

    return make_request(url, headers, method="PUT", data=payload)


def ml_model_hosting_show_config(cmd, publisher=None, location=None, model=None, transaction_id=None):
    token = generate_token()
    api_version = '2024-10-31'
    base_url = get_self_serve_base_url(location=location)
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/gpu-config/{transaction_id}?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers)


def ml_model_hosting_list_config(cmd, publisher=None, location=None, model=None, size=None, page=None):
    token = generate_token()
    api_version = '2024-10-31'
    base_url = get_self_serve_base_url(location=location)
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/gpu-config"
    params = {"api-version": api_version,
              "currentPage": page, "pageSize": size}
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers, params=params)


def ml_model_hosting_publisher_show(cmd, publisher=None):
    token = generate_token()
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers)


def ml_model_hosting_update_publisher_details(cmd, publisher=None, description=None, name=None, website=None):
    token = generate_token()
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/updatePublisherDetails?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}
    parameters = {"description": description,
                  "displayName": name, "website": website}
    payload = json.dumps(parameters)

    return make_request(url, headers, method="PUT", data=payload)


def ml_model_hosting_set_registry(cmd, publisher=None, file=None):
    token = generate_token()
    try:
        with open(file, "r") as f:
            registry_config = yaml.safe_load(f)
    except Exception as e:
        raise BadRequestError(
            f"Failed to read or parse the YAML file: {str(e)}")

    module_logger.debug(f"Registry details config: {registry_config}")

    api_version = '2024-12-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/updateSourceRegistry?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}
    payload = json.dumps(registry_config)

    return make_request(url, headers, method="PUT", data=payload)


def ml_model_hosting_create_plan(cmd, publisher=None, model=None, file=None):
    token = generate_token()
    try:
        with open(file, "r") as f:
            plan_config = yaml.safe_load(f)
    except Exception as e:
        raise BadRequestError(
            f"Failed to read or parse the YAML file: {str(e)}")

    module_logger.debug(f"Plan details config: {plan_config}")
    validate_config_file(plan_config)

    api_version = '2024-12-31'
    base_url = get_self_serve_base_url(location=plan_config['location'])
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/plan-details?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}
    payload = json.dumps(plan_config)

    return make_request(url, headers, method="PUT", data=payload)


def ml_model_hosting_plan_details_list(cmd, publisher=None, location=None, model=None):
    token = generate_token()
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url(location=location)
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/plan-details?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers)


def ml_model_hosting_plan_config_show(cmd, publisher=None, location=None, model=None, plan_id=None, offer_id=None):
    token = generate_token()
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url(location=location)
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/plan-details"
    params = {"api-version": api_version, "offerId": offer_id, "planId": plan_id}
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers, params=params)


def ml_model_hosting_plan_details_update_status(cmd, publisher=None, location=None, model=None, plan_id=None, status=None):
    token = generate_token()
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url(location=location)
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/plan-details/requestStatus?api-version={api_version}&planId={plan_id}"
    parameters = {"requestedStatus": status}
    payload = json.dumps(parameters)
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers, method="PUT", data=payload)


def ml_model_hosting_create_model(cmd, publisher=None, model=None, file=None):
    token = generate_token()
    if (file is not None):
        raise BadRequestError(
            "File param is deprecated, please rerun command without file parameter")

    api_version = '2025-01-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}
    return make_request(url, headers, method="PUT")


def ml_model_hosting_approve_model(cmd, publisher=None, model=None, version=None, status=None):
    token = generate_token()
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/approval?api-version={api_version}"
    params = {"releaseCandidateVersion": version,
              "status": status}
    payload = json.dumps(params)
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers, method="PUT", data=payload)


def ml_model_hosting_list_model(cmd, publisher=None, size=None, page=None):
    token = generate_token()
    api_version = '2025-01-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models"
    params = {"api-version": api_version,
              "currentPage": page, "pageSize": size}
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers, params=params)


def ml_model_hosting_show_model(cmd, publisher=None, model=None):
    token = generate_token()
    api_version = '2025-01-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers)


def ml_model_hosting_create_release_candidate(cmd, publisher=None, model=None, file=None):
    token = generate_token()
    try:
        with open(file, "r") as f:
            model_config = yaml.safe_load(f)
    except Exception as e:
        raise BadRequestError(
            f"Failed to read or parse the YAML file: {str(e)}")

    module_logger.debug(f"Model version details config: {model_config}")

    api_version = '2024-12-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/release-candidate?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}
    payload = json.dumps(model_config)

    return make_request(url, headers, method="PUT", data=payload)


def ml_model_hosting_list_release_candidate(cmd, publisher=None, model=None, size=None, page=None):
    token = generate_token()
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/release-candidate"
    params = {"api-version": api_version,
              "currentPage": page, "pageSize": size}
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers, params=params)


def ml_model_hosting_show_release_candidate(cmd, publisher=None, model=None, version=None):
    token = generate_token()
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/release-candidate/{version}?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers)


def ml_model_hosting_download_validation_result_release_candidate(cmd, publisher=None, model=None, version=None, validation_id=None, file_name=None, result_path=None):
    token = generate_token()
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/versions/{version}/validations/{validation_id}/download?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}"}

    response = make_request(url, headers, stream=True)
    return _download_file_from_response(response, file_name, result_path, "validation result")


def ml_model_hosting_download_deployment_logs_release_candidate(cmd, publisher=None, model=None, version=None, validation_id=None, file_name=None, result_path=None):
    token = generate_token()
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/versions/{version}/validations/{validation_id}/downloadDeploymentLogs?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}"}

    response = make_request(url, headers, stream=True)
    return _download_file_from_response(response, file_name, result_path, "deployment logs result")


def ml_model_hosting_promote_to_prod_release_candidate(cmd, publisher=None, model=None, version=None):
    token = generate_token()
    api_version = '2025-03-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/release-candidate/{version}/promoteToProd?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}

    return make_request(url, headers, method="PUT")


def ml_model_hosting_enable_marketplace_integration(cmd, publisher=None, file=None):
    token = generate_token()
    try:
        with open(file, "r") as f:
            marketplace_config = yaml.safe_load(f)
    except Exception as e:
        raise BadRequestError(
            f"Failed to read or parse the YAML file: {str(e)}")

    module_logger.debug(f"Marketplace integration config: {marketplace_config}")
    api_version = '2024-12-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/createMarketplaceIdentity?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}
    payload = json.dumps(marketplace_config)

    return make_request(url, headers, method="PUT", data=payload)


# Update model card system metadata
def ml_model_hosting_update_model_card(cmd, publisher=None, model=None, file=None):
    try:
        model_card = load_inline_md_files(file)
    except Exception as e:
        user_message = "Failed to read or parse the YAML file for model card."
        module_logger.debug(e)
        raise AzureInternalError(user_message) from e

    token = generate_token()
    api_version = '2025-03-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/model-card?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}
    payload = json.dumps(model_card)
    return make_request(url, headers, method="POST", data=payload)


# Get model card system metadata
def ml_model_hosting_get_model_card(cmd, publisher=None, model=None):
    token = generate_token()
    api_version = '2025-03-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/model-card/latest"
    params = {"api-version": api_version}
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}
    return make_request(url, headers, params=params)


# Apply model card system metadata to a specific RC
def ml_model_hosting_attach_model_card(cmd, publisher=None, model=None, version=None):
    token = generate_token()
    api_version = '2025-03-31'
    base_url = get_self_serve_base_url()
    url = f"{base_url}/model-publisher-self-serve/publishers/{publisher}/models/{model}/model-card/applyModelCard?api-version={api_version}&version={version}"
    headers = {"Authorization": f"Bearer {token.token}",
               "Content-Type": "application/json"}
    return make_request(url, headers, method="POST", data=json.dumps({}))


# Generate model card template
def ml_model_hosting_generate_model_card_template(cmd, model_card_dir=None):
    print(f"Creating model card template at {model_card_dir}")
    os.makedirs(model_card_dir, exist_ok=True)

    github_branch = "mpss/model_card"
    github_template_folder_path = "assets/models/template"
    api_url = f"https://api.github.com/repos/Azure/azureml-assets/contents/{github_template_folder_path}?ref={github_branch}"

    try:
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        items = response.json()

        for item in items:
            if item["type"] == "file":
                download_url = item["download_url"]
                file_name = os.path.join(model_card_dir, os.path.basename(item["name"]))
                file_resp = requests.get(download_url, timeout=REQUEST_TIMEOUT)
                file_resp.raise_for_status()
                with open(file_name, "wb") as f:
                    f.write(file_resp.content)
                print(f"Created {item['name']}")
        print("Model card template successfully created!")
    except requests.ConnectionError as err:
        raise BadRequestError(
            "Network connection error while downloading the model card template. Please retry.") from err
    except requests.RequestException as err:
        raise AzureInternalError(
            f"Failed to download the model card template: {err}") from err

# validate model card files


def ml_model_hosting_validate_model_card_template(cmd, model_card_dir=None):
    cmd = [
        "asset", "validate",
        "--asset-path", model_card_dir,
    ]
    run_registry_mgmt_cmd(cmd)


# apply model card tags & properties on given model


def ml_model_hosting_apply_model_card_template(cmd, model_id=None, model_card_dir=None):
    print(f"Applying model card from {model_card_dir} to model {model_id}")

    info = parse_azureml_model_uri(model_id)
    if not info:
        raise InvalidArgumentValueError(
            f"Invalid --model-id '{model_id}'. Expected format: "
            "azureml://registries/<registry>/models/<model>/versions/<version>")

    registry_config = get_registry_info(info["registry_name"])
    if not registry_config:
        raise AzureInternalError(
            f"Failed to resolve registry info for '{info['registry_name']}'.")

    cmd = [
        "asset", "deploy",
        "--asset-path", model_card_dir,
        "--registry-name", info["registry_name"],
        "--subscription", registry_config["subscription_id"],
        "--resource-group", registry_config["resource_group_name"]
    ]
    run_registry_mgmt_cmd(cmd)
