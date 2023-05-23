# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import errno
import uuid

import requests
import yaml
from azext_load.data_plane.utils import validators
from azext_load.vendored_sdks.loadtesting_mgmt import LoadTestMgmtClient
from azure.cli.core.azclierror import ValidationError
from knack.log import get_logger
from msrestazure.tools import is_valid_resource_id, parse_resource_id

logger = get_logger(__name__)


def upload_test_plan(client, test_id, test_plan, wait):
    logger.info("Uploading test plan for the test")
    with open(test_plan, "r") as file:
        upload_poller = client.begin_upload_test_file(
            test_id,
            file_name=file.name.split("\\")[-1],
            body=file,
        )
        if wait:
            response = upload_poller.result()
            if response.get("validationStatus") == "VALIDATION_SUCCESS":
                logger.info("Uploaded test plan for the test")
            elif response.get("validationStatus") == "VALIDATION_FAILED":
                logger.warning("Test plan validation failed for the test")
            else:
                logger.warning("Invalid status for Test plan validation")
            logger.debug("Upload result for test plan: %s", response)


def upload_configuration_files(client, test_id, configuration_files):
    logger.info("Uploading configuration files for the test")
    for configuration_file in configuration_files:
        with open(configuration_file, "r") as file:
            upload_poller = client.begin_upload_test_file(
                test_id,
                file_name=file.name.split("\\")[-1],
                body=file,
            )
            response = upload_poller.result()
            if response.get("validationStatus") == "VALIDATION_NOT_REQUIRED":
                logger.info("Uploaded configuration file %s", file.name)
            else:
                logger.warning("Invalid status for configuration file %s", file.name)
            logger.debug(
                "Upload result for configuration file %s is: %s", file.name, response
            )


def get_load_test_resource_endpoint(
    cred, load_test_resource, resource_group=None, subscription_id=None
):
    if subscription_id is None:
        return None
    if is_valid_resource_id(load_test_resource):
        # load_test_resource is a resource id
        logger.debug(
            "load-test-resource '%s' is an Azure Resource Id", load_test_resource
        )
        parsed = parse_resource_id(load_test_resource)
        resource_group, name = parsed["resource_group"], parsed["name"]
        if subscription_id != parsed["subscription"]:
            logger.info(
                "Subscription ID in load-test-resource parameter and CLI context do not match - %s and %s",
                subscription_id,
                parsed["subscription"],
            )
            return None
    else:
        # load_test_resource is a name
        logger.debug(
            "load-test-resource '%s' is an Azure Load Testing resource name. Using resource group name %s",
            load_test_resource,
            resource_group,
        )
        if resource_group is None:
            return None
        name = load_test_resource

    mgmt_client = LoadTestMgmtClient(credential=cred, subscription_id=subscription_id)
    data_plane_uri = mgmt_client.load_tests.get(resource_group, name).data_plane_uri
    logger.info("Azure Load Testing data plane URI: %s", data_plane_uri)
    return data_plane_uri


def get_login_credentials(cli_ctx, subscription_id=None):
    from azure.cli.core._profile import Profile

    credential = Profile(cli_ctx=cli_ctx).get_login_credentials(
        subscription_id=subscription_id
    )
    logger.debug("Fetched login credentials for subscription %s", subscription_id)
    return credential


def get_admin_data_plane_client(cmd, load_test_resource, resource_group_name=None):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    return admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )


def get_testrun_data_plane_client(cmd, load_test_resource, resource_group_name=None):
    from azext_load.data_plane.client_factory import testrun_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    return testrun_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )


def download_file(url, file_path):
    response = None
    retries = 3
    ex = None
    while retries > 0:
        try:
            response = requests.get(url, stream=True, allow_redirects=True)
            break
        except Exception as e:
            ex = e
            retries -= 1
            logger.debug(
                "Exception occurred while downloading file: %s. Retrying the request. Retries remaining: %d",
                str(ex),
                retries,
            )
    if retries == 0:
        msg = "Request for {} failed after all retries: {}".format(url, str(ex))
        logger.debug(msg)
        raise Exception(msg)

    if response:
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # ignore keep-alive new chunks
                    f.write(chunk)


def parse_cert(certificate):
    comps = {}
    if len(certificate) != 1:
        raise ValueError("Only one certificate is supported")
    certificate = certificate[0]
    comps = [certificate.get("name"), certificate.get("value")]
    if not validators._validate_akv_url(comps[1], "certificates"):
        raise ValueError(f"Invalid AKV Certificate URL: {comps[1]}")
    certificate = {
        "name": comps[0],
        "type": "AKV_CERT_URI",
        "value": comps[1],
    }
    return certificate


def parse_secrets(secrets):
    secrets_list = {}
    for secret in secrets:
        if not validators._validate_akv_url(secret.get("value"), "secrets"):
            url = secret.get("value")
            raise ValueError(f"Invalid AKV Certificate URL: {url}")
        secrets_list.update(
            {
                secret.get("name"): {
                    "type": "AKV_SECRET_URI",
                    "value": secret.get("value"),
                }
            }
        )
    return secrets_list


def parse_env(env):
    env_list = {}
    for item in env:
        env_list.update({item.get("name"): item.get("value")})
    return env_list


def create_or_update_body(
    test_id,
    body,
    load_test_config_file=None,
    display_name=None,
    test_description=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    key_vault_reference_identity=None,
    subnet_id=None,
):
    IdentityType = {"SystemAssigned": "SystemAssigned", "UserAssigned": "UserAssigned"}
    new_body = {}
    if load_test_config_file is not None:
        if (
            test_description
            or env
            or secrets
            or certificate
            or key_vault_reference_identity
            or subnet_id
            or engine_instances
        ):
            logger.warning(
                "Additional flags were passed along with --load-test-config-file. These flags will be ignored, and the configuration defined in the yaml will be used instead"
            )
        # exception handling for incorrect filepath or name
        try:
            with open(load_test_config_file) as file:
                data = yaml.safe_load(file)
                if "displayName" in data:
                    new_body["displayName"] = data["displayName"]
                if "description" in data:
                    new_body["description"] = data["description"]

                new_body["keyvaultReferenceIdentityType"] = IdentityType[
                    "SystemAssigned"
                ]
                if "keyvaultReferenceIdentityId" in data:
                    new_body["keyvaultReferenceIdentityId"] = data[
                        "keyvaultReferenceIdentityId"
                    ]
                    new_body["keyvaultReferenceIdentityType"] = IdentityType[
                        "UserAssigned"
                    ]

                if "subnetId" in data:
                    new_body["subnetId"] = data["subnetId"]

                new_body["loadTestConfiguration"] = body.get(
                    "loadTestConfiguration", {}
                )
                new_body["loadTestConfiguration"]["engineInstances"] = data.get(
                    "engineInstances", 1
                )
                if data.get("certificate"):
                    new_body["certificate"] = parse_cert(data.get("certificate"))
                if data.get("secrets"):
                    new_body["secrets"] = parse_secrets(data.get("secrets"))
                if data.get("env"):
                    new_body["environmentVariables"] = parse_env(data.get("env"))
                # quick test and split csv not supported currently in CLI
                new_body["loadTestConfiguration"]["quickStartTest"] = False
                if data.get("quickStartTest"):
                    logger.warning(
                        "Quick start test is not supported currently in CLI. Please use portal to run quick start test"
                    )
                new_body["loadTestConfiguration"]["splitAllCSVs"] = False
                if data.get("splitAllCSVs"):
                    logger.warning(
                        "CSV splitting is not supported currently in CLI. Please use portal to split CSVs"
                    )
                # implementation of failure criteria is pending

                if data.get("failureCriteria"):
                    new_body["passFailCriteria"] = {}
                    new_body["passFailCriteria"]["passFailMetrics"] = {}
                    for index, items in enumerate(data["failureCriteria"]):
                        id = get_random_uuid()
                        name = list(items.keys())[0]
                        components = list(items.values())[0]
                        new_body["passFailCriteria"]["passFailMetrics"][id] = {}
                        new_body["passFailCriteria"]["passFailMetrics"][id][
                            "aggregate"
                        ] = components.split("(")[0].strip()
                        new_body["passFailCriteria"]["passFailMetrics"][id][
                            "clientMetric"
                        ] = (components.split("(")[1].split(")")[0].strip())
                        new_body["passFailCriteria"]["passFailMetrics"][id][
                            "condition"
                        ] = components.split(")")[1].strip()[0]
                        new_body["passFailCriteria"]["passFailMetrics"][id][
                            "value"
                        ] = components.split(
                            new_body["passFailCriteria"]["passFailMetrics"][id][
                                "condition"
                            ]
                        )[
                            1
                        ].strip()
                        new_body["passFailCriteria"]["passFailMetrics"][id][
                            "requestName"
                        ] = name
        except (IOError, OSError) as ex:
            if getattr(ex, "errno", 0) == errno.ENOENT:
                raise ValidationError(f"{load_test_config_file} does not exist") from ex
            raise
        except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
            raise ValidationError(
                f"Error parsing {load_test_config_file} ({str(ex)})"
            ) from ex

    else:
        if display_name is not None:
            new_body["displayName"] = display_name
        else:
            new_body["displayName"] = body.get("displayName", test_id)

        if test_description is not None:
            new_body["description"] = test_description
        else:
            new_body["description"] = body.get("description")

        new_body["keyvaultReferenceIdentityType"] = IdentityType["SystemAssigned"]
        if key_vault_reference_identity is not None:
            new_body["keyvaultReferenceIdentityId"] = key_vault_reference_identity
            new_body["keyvaultReferenceIdentityType"] = IdentityType["UserAssigned"]
        elif body.get("keyvaultReferenceIdentityId") is not None:
            new_body["keyvaultReferenceIdentityId"] = body.get(
                "keyvaultReferenceIdentityId"
            )
            new_body["keyvaultReferenceIdentityType"] = body.get(
                "keyvaultReferenceIdentityType", IdentityType["UserAssigned"]
            )

        if subnet_id is not None:
            new_body["subnetId"] = subnet_id
        elif body.get("subnetId"):
            new_body["subnetId"] = body.get("subnetId")

        if env is not None:
            new_body["environmentVariables"] = body.get("environmentVariables", {})
            new_body["environmentVariables"].update(env)

        if secrets is not None:
            new_body["secrets"] = body.get("secrets", {})
            new_body["secrets"].update(secrets)

        if certificate is not None:
            new_body["certificate"] = certificate
        elif body.get("certificate"):
            new_body["certificate"] = body.get("certificate")

        new_body["loadTestConfiguration"] = body.get("loadTestConfiguration", {})
        if engine_instances:
            new_body["loadTestConfiguration"]["engineInstances"] = engine_instances
        else:
            new_body["loadTestConfiguration"]["engineInstances"] = body.get(
                "loadTestConfiguration", {}
            ).get("engineInstances", 1)
        # quick test and split csv not supported currently
        new_body["loadTestConfiguration"]["quickStartTest"] = False
        new_body["loadTestConfiguration"]["splitAllCSVs"] = False

    return new_body


def create_or_update_test_run_body(
    test_id,
    display_name=None,
    description=None,
    env=None,
    secrets=None,
    certificate=None,
):
    new_body = {"testId": test_id}
    if display_name is not None:
        new_body["displayName"] = display_name
    if description is not None:
        new_body["description"] = description
    if env is not None:
        new_body["environmentVariables"] = env
    if secrets is not None:
        new_body["secrets"] = secrets
    if certificate is not None:
        new_body["certificate"] = certificate

    return new_body


def get_random_uuid():
    return str(uuid.uuid4())


# def get_timespan(_, start_time=None, end_time=None, offset=None):
#     if not start_time and not end_time:
#         # if neither value provided, end_time is now
#         end_time = datetime.utcnow().isoformat()
#     if not start_time:
#         # if no start_time, apply offset backwards from end_time
#         start_time = (dateutil.parser.parse(end_time) - offset).isoformat()
#     elif not end_time:
#         # if no end_time, apply offset fowards from start_time
#         end_time = (dateutil.parser.parse(start_time) + offset).isoformat()
#     timespan = f"{start_time}/{end_time}"
#     return timespan
