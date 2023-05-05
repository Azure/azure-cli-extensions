# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime
import dateutil.parser  # pylint: disable=import-error
from knack.log import get_logger
from msrestazure.tools import is_valid_resource_id, parse_resource_id
from azext_load.vendored_sdks.loadtesting_mgmt import LoadTestMgmtClient
import uuid
from azure.cli.core.azclierror import ValidationError

logger = get_logger(__name__)


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

def get_login_credentials(cli_ctx, subscription_id=None):
    from azure.cli.core._profile import Profile

    credential = Profile(cli_ctx=cli_ctx).get_login_credentials(
        subscription_id=subscription_id
    )
    logger.debug("Fetched login credentials for subscription %s", subscription_id)
    return credential

def generate_test_id(test_name=None):
    return str(uuid.uuid4())

def parse_env(env):
    if env is None:
        return None
    env_dict = {}
    for item in env:
        current = item.split("=",1)
        if len(current) < 2:
            raise ValidationError("Environment variables must be in the format \"<key>=<value> <key>=<value> ...\".")
        env_dict[current[0]] = current[1]
    return env_dict

def parse_secrets(secrets):
    logger.warning("secrets: %s", secrets)
    if secrets is None:
        return None
    secrets_dict = {}
    for secret in secrets:
        current = secret.split("=", 1)
        if len(current) < 2:
            raise ValueError("Secrets must be in the format \"<key>=<value> <key>=<value> ...\".")
        secrets_dict[current[0]] = {}
        secrets_dict[current[0]]["type"] = "AKV_SECRET_URI"
        logger.warning("secrets: %s", current[1])
        if current[1] == "":
            secrets_dict[current[0]] = None
        else:
            secrets_dict[current[0]]["value"] = current[1]
    return secrets_dict

def parse_certificate(certificate):
    if certificate is None:
        return None
    certificate_dict = {}
    current = certificate.split("=", 1)
    if len(current) < 2:
        raise ValueError("Certificate must be in the format \"<key>=<value>;<key>=<value>...\".")
    certificate_dict["name"] = current[0]
    certificate_dict["type"] = "AKV_CERT_URI"
    certificate_dict["value"] = current[1]
    return certificate_dict


def create_or_update_body(body, load_test_config_file=None, display_name=None,
    test_description=None,
    config_file=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    key_vault_reference_identity=None,
    subnet_id=None,):
    IdentityType = {"SystemAssigned": "SystemAssigned", "UserAssigned": "UserAssigned"}
    new_body = {}
    if load_test_config_file is not None:
        if (
            test_description
            or config_file
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
                if body.get("loadTestConfiguration") is None:
                    new_body["loadTestConfiguration"] = {}
                if "engineInstances" in data:
                    new_body["loadTestConfiguration"]["engineInstances"] = data[
                        "engineInstances"
                    ]
                else:
                    new_body["loadTestConfiguration"]["engineInstances"] = "1"
                if "keyvaultReferenceIdentityId" in data:
                    new_body["keyvaultReferenceIdentityId"] = data[
                        "keyvaultReferenceIdentityId"
                    ]
                    new_body["keyvaultReferenceIdentityType"] = IdentityType["UserAssigned"]
                else:
                    new_body["keyvaultReferenceIdentityType"] = IdentityType[
                        "SystemAssigned"
                    ]
                if "subnetId" in data:
                    new_body["subnetId"] = data["subnetId"]
                # quick test and split csv not supported currently in CLI
                if "quickStartTest" in data and data["quickStartTest"] == True:
                    logger.warning(
                        "Quick start test is not supported currently in CLI. Please use portal to run quick start test"
                    )
                if "splitAllCSVs" in data and data["splitAllCSVs"] == True:
                    logger.warning(
                        "CSV splitting is not supported currently in CLI. Please use portal to split CSVs"
                    )
                new_body["loadTestConfiguration"]["quickStartTest"] = False
                new_body["loadTestConfiguration"]["splitAllCSVs"] = False
                # implementation of failure criteria is pending
        except (IOError, OSError) as ex:
            if getattr(ex, "errno", 0) == errno.ENOENT:
                raise ValidationError(
                    "{} does not exist".format(load_test_config_file)
                ) from ex
            raise
        except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
            raise ValidationError(
                "Error parsing {} ({})".format(load_test_config_file, str(ex))
            ) from ex

    else:
        if display_name is not None:
            new_body["displayName"] = display_name
        elif body.get("displayName") is None:
            new_body["displayName"] = generate_test_id("TestName")
        else:
            new_body["displayName"] = body.get("displayName")
        if test_description is not None:
            new_body["description"] = test_description
        else:
            new_body["description"] = body.get("description")
        if body.get("loadTestConfiguration") is None:
            new_body["loadTestConfiguration"] = {}
        else:
            new_body["loadTestConfiguration"] = body.get("loadTestConfiguration")
        if engine_instances:
            new_body["loadTestConfiguration"]["engineInstances"] = engine_instances
        elif not body.get("loadTestConfiguration").get("engineInstances"):
            new_body["loadTestConfiguration"]["engineInstances"] = body.get("loadTestConfiguration").get("engineInstances")
        else:
            new_body["loadTestConfiguration"]["engineInstances"] = "1"
        if key_vault_reference_identity is not None:
            new_body["keyvaultReferenceIdentityId"] = key_vault_reference_identity
            new_body["keyvaultReferenceIdentityType"] = IdentityType["UserAssigned"]
        elif body.get("keyvaultReferenceIdentityId") is None:
            new_body["keyvaultReferenceIdentityType"] = IdentityType["SystemAssigned"]
        else:
            new_body["keyvaultReferenceIdentityId"] = body.get("keyvaultReferenceIdentityId")
            new_body["keyvaultReferenceIdentityType"] = body.get("keyvaultReferenceIdentityId")
        if subnet_id is not None:
            new_body["subnetId"] = subnet_id
        elif body.get("subnetId"):
            new_body["subnetId"] = body.get("subnetId")
        if env is not None:
            if body.get("environmentVariables") is None:
                new_body["environmentVariables"] = {}
            else:
                new_body["environmentVariables"] = body.get("environmentVariables")
            new_body["environmentVariables"].update(parse_env(env))
        if secrets is not None:
            if body.get("secrets") is None:
                new_body["secrets"] = {}
            else:
                new_body["secrets"] = body.get("secrets")
            new_body["secrets"].update(parse_secrets(secrets))
        if certificate is not None:
            new_body["certificate"] = parse_certificate(certificate)
        elif body.get("certificate"):
            new_body["certificate"] = body.get("certificate")
        # quick test and split csv not supported currently
        new_body["loadTestConfiguration"]["quickStartTest"] = False
        new_body["loadTestConfiguration"]["splitAllCSVs"] = False
    return new_body