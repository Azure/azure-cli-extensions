from knack.log import get_logger
import yaml, json
from yaml.loader import SafeLoader

from azext_load.data_plane.util import (
    get_load_test_resource_endpoint,
    get_login_credentials,
)

from azure.cli.core.azclierror import ValidationError
from azext_load.data_plane.util import parse_env, parse_secrets, parse_certificate

log = get_logger(__name__)


def create_test(
    cmd,
    load_test_resource,
    display_name =None,
    resource_group_name=None,
    load_test_config_file=None,
    test_description=None,
    test_plan=None,
    config_file=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    kevault_id=None,
    subnet_id=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client
    from azext_load.data_plane.util import generate_test_id
    import errno

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )
    body = {}
    IdentityType = {
        "SystemAssigned": "SystemAssigned",
        "UserAssigned": "UserAssigned"}
    body["loadTestConfiguration"] = {}
    if load_test_config_file is not None:
        if (
            test_description
            or config_file
            or env
            or secrets
            or certificate
            or kevault_id
            or subnet_id
            or engine_instances
        ):
            log.warning(
                "Additional flags were passed along with --load-test-config-file. These flags will be ignored, and the configuration defined in the yaml will be used instead"
            )
        # exception handling for incorrect filepath or name
        try:
            with open(load_test_config_file) as file:
                data = yaml.safe_load(file)
                if "displayName" in data.keys():
                    body["displayName"] = data["displayName"]
                if "description" in data.keys():
                    body["description"] = data["description"]
                if "engineInstances" in data.keys():
                    body["loadTestConfiguration"]["engineInstances"] = data["engineInstances"]
                else:
                    body["loadTestConfiguration"]["engineInstances"] = "1"
                if "keyvaultReferenceIdentityId" in data.keys():
                    body["keyvaultReferenceIdentityId"] = data["keyvaultReferenceIdentityId"]
                    body["keyvaultReferenceIdentityId"] = IdentityType["UserAssigned"]
                else:
                    body["keyvaultReferenceIdentityId"] = IdentityType["SystemAssigned"]
                if "subnetId" in data.keys():
                    body["subnetId"] = data["subnetId"]
                # quick test and split csv not supported currently in CLI
                body["loadTestConfiguration"]["quickStartTest"] = False
                body["loadTestConfiguration"]["splitAllCSVs"] = False
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
            body["displayName"] = display_name
        else:
            body["displayName"] = generate_test_id("TestName")
        if test_description is not None:
            body["description"] = test_description
        if engine_instances is not None:
            body["loadTestConfiguration"]["engineInstances"] = engine_instances
        else:
            body["loadTestConfiguration"]["engineInstances"] = "1"
        if kevault_id is not None:
            body["keyvaultReferenceIdentityId"] = kevault_id
            body["keyvaultReferenceIdentityType"] = IdentityType["UserAssigned"]
        else:
            body["keyvaultReferenceIdentityType"] = IdentityType["SystemAssigned"]
        if subnet_id is not None:
            body["subnetId"] = subnet_id
        if env is not None:
            body["environmentVariables"] = parse_env(env)
        if secrets is not None:
            body["secrets"] = parse_secrets(secrets)
        if certificate is not None:
            body["certificate"] = parse_certificate(certificate)
        # quick test and split csv not supported currently
        body["loadTestConfiguration"]["quickStartTest"] = False
        body["loadTestConfiguration"]["splitAllCSVs"] = False
    test_id=generate_test_id(body["displayName"])
    response_obj = client.create_or_update_test(
        test_id=test_id, body=body
    )
    if test_plan is not None:
        client.begin_upload_test_file(
            test_id,
            file_name= test_id + "TestPlan.jmx",
            body=open(test_plan, "r"),
        )
    return response_obj


def update_test(
    cmd,
    test_id,
    load_test_resource,
    display_name=None,
    resource_group_name=None,
    load_test_config_file=None,
    test_description=None,
    test_plan=None,
    config_file=None,
    engine_instances=None,
    env=None,
    secrets=None,
    certificate=None,
    kevault_id=None,
    subnet_id=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client
    from azext_load.data_plane.util import generate_test_id

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )
    log.warning("ENV : %s", env)
    body = client.get_test(test_id)
    IdentityType = {
        "SystemAssigned": "SystemAssigned",
        "UserAssigned": "UserAssigned"}
    if load_test_config_file is not None:
        if (
            test_description
            or config_file
            or env
            or secrets
            or certificate
            or kevault_id
            or subnet_id
            or engine_instances
        ):
            log.warning(
                "Additional flags were passed along with --load-test-config-file. These flags will be ignored, and the configuration defined in the yaml file will be used instead"
            )
        # exception handling for incorrect filepath or name
        try:
            with open(load_test_config_file, 'r') as file:
                data = yaml.safe_load(file)
                if 'displayName' in data:
                    body['displayName'] = data['displayName']
                if 'description' in data:
                    body['description'] = data['description']
                if 'engineInstances' in data:
                    body['loadTestConfiguration']['engineInstances'] = data['engineInstances']
                else:
                    body['loadTestConfiguration']['engineInstances'] = '1'
                if 'keyvaultReferenceIdentityId' in data:
                    body['keyvaultReferenceIdentityId'] = data['keyvaultReferenceIdentityId']
                    body['keyvaultReferenceIdentityType'] = IdentityType['UserAssigned']
                else:
                    body['keyvaultReferenceIdentityType'] = IdentityType['SystemAssigned']
                if 'subnetId' in data:
                    body['subnetId'] = data['subnetId']
                # quick test and split csv not supported currently in CLI
                body['loadTestConfiguration']['quickStartTest'] = False
                body['loadTestConfiguration']['splitAllCSVs'] = False
                # implementation of failure criteria is pending
        except (IOError, OSError) as ex:
            if getattr(ex, 'errno', 0) == errno.ENOENT:
                raise ValidationError(
                    '{} does not exist'.format(load_test_config_file)
                ) from ex
            raise
        except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
            raise ValidationError(
                'Error parsing {} ({})'.format(load_test_config_file, str(ex))
            ) from ex

    else:
        if display_name is not None:
            body['displayName'] = display_name
        if test_description is not None:
            body['description'] = test_description
        if engine_instances is not None:
            body['loadTestConfiguration']['engineInstances'] = engine_instances
        elif not body.get('loadTestConfiguration') or not body['loadTestConfiguration'].get('engineInstances'):
            body['loadTestConfiguration']['engineInstances'] = '1'
        if kevault_id is not None:
            body['keyvaultReferenceIdentityId'] = kevault_id
            body['keyvaultReferenceIdentityType'] = IdentityType['UserAssigned']
        elif not body.get('keyvaultReferenceIdentityType'):
            body['keyvaultReferenceIdentityType'] = IdentityType['SystemAssigned']
        if subnet_id is not None:
            body['subnetId'] = subnet_id
    body['displayName'] = body.get('displayName') if not body.get('displayName') else generate_test_id('TestName')
    response_obj = client.create_or_update_test(
        test_id=generate_test_id(body['displayName']), body=body
    )
    if test_plan is not None:
        client.begin_upload_test_file(
            response_obj['testId'],
            file_name=response_obj['displayName'] + 'TestPlan.jmx',
            body=open(test_plan, 'r'),
        )
    return response_obj

def list_tests(
    cmd,
    load_test_resource,
    resource_group_name=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )

    return client.list_tests()


def get_test(
    cmd,
    load_test_resource,
    test_id,
    resource_group_name=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )
    return client.get_test(test_id)


def download_test_files(
    cmd,
    load_test_resource,
    test_id,
    path,
    resource_group_name=None,
):
    from azext_load.data_plane.client_factory import admin_data_plane_client
    import requests
    import os

    credential, subscription_id, _ = get_login_credentials(cmd.cli_ctx)
    endpoint = get_load_test_resource_endpoint(
        credential,
        load_test_resource,
        resource_group=resource_group_name,
        subscription_id=subscription_id,
    )
    client = admin_data_plane_client(
        cmd.cli_ctx,
        subscription=subscription_id,
        endpoint=endpoint,
        credential=credential,
    )
    list_of_file_details = client.list_test_files(test_id)
    if list_of_file_details:
        if not os.path.exists(path):
            os.mkdir(path)
        for file_detail in list_of_file_details:
            with requests.get(file_detail["url"]) as current_file:
                with open(path + "\\" + file_detail["fileName"], "w+") as f:
                    f.write(current_file.text)
    return (
        "Files belonging to test "
        + test_id
        + " are downloaded in "
        + path
        + " location."
    )
