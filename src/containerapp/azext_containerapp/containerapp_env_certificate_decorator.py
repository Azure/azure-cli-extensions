# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, Dict
from knack.log import get_logger

from azure.cli.command_modules.containerapp._utils import certificate_matches, certificate_location_matches, \
    load_cert_file, generate_randomized_cert_name
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.core.azclierror import MutuallyExclusiveArgumentError, ValidationError
from azure.cli.core.commands import AzCliCommand
from knack.prompting import prompt_y_n
from knack.util import CLIError
from msrestazure.tools import is_valid_resource_id, parse_resource_id

from ._constants import PRIVATE_CERTIFICATE_RT, MANAGED_CERTIFICATE_RT, CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE, \
    NAME_ALREADY_EXISTS, NAME_INVALID
from ._client_factory import handle_non_404_exception, handle_raw_exception
from ._models import ContainerAppCertificateEnvelope as ContainerAppCertificateEnvelopeModel

logger = get_logger(__name__)


class ContainerappEnvCertificateDecorator(BaseResource):
    def get_argument_location(self):
        return self.get_param("location")

    def get_argument_thumbprint(self):
        return self.get_param("thumbprint")

    def get_argument_certificate(self):
        return self.get_param("certificate")

    def get_argument_managed_certificates_only(self):
        return self.get_param("managed_certificates_only")

    def get_argument_private_key_certificates_only(self):
        return self.get_param("private_key_certificates_only")

    def check_cert_name_availability(self, resource_group_name, name, cert_name):
        name_availability_request = {"name": cert_name, "type": CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE}
        try:
            return self.client.check_name_availability(self.cmd, resource_group_name, name, name_availability_request)
        except CLIError as e:
            handle_raw_exception(e)

    def get_private_certificates(self, certificate_name=None):
        if certificate_name:
            try:
                r = self.client.show_certificate(self.cmd, self.get_argument_resource_group_name(), self.get_argument_name(), certificate_name)
                return [r] if certificate_matches(r, self.get_argument_location(), self.get_argument_thumbprint()) else []
            except Exception as e:
                handle_non_404_exception(e)
                return []
        else:
            try:
                r = self.client.list_certificates(self.cmd, self.get_argument_resource_group_name(), self.get_argument_name())
                return list(filter(lambda c: certificate_matches(c, self.get_argument_location(), self.get_argument_thumbprint()), r))
            except Exception as e:
                handle_raw_exception(e)

    def get_managed_certificates(self, certificate_name=None):
        if certificate_name:
            try:
                r = self.client.show_managed_certificate(self.cmd, self.get_argument_resource_group_name(), self.get_argument_name(), certificate_name)
                return [r] if certificate_location_matches(r, self.get_argument_location()) else []
            except Exception as e:
                handle_non_404_exception(e)
                return []
        else:
            try:
                r = self.client.list_managed_certificates(self.cmd, self.get_argument_resource_group_name(), self.get_argument_name())
                return list(filter(lambda c: certificate_location_matches(c, self.get_argument_location()), r))
            except Exception as e:
                handle_raw_exception(e)


class ContainerappEnvCertificateListDecorator(ContainerappEnvCertificateDecorator):
    def validate_arguments(self):
        if self.get_argument_managed_certificates_only() and self.get_argument_private_key_certificates_only():
            raise MutuallyExclusiveArgumentError(
                "Use either '--managed-certificates-only' or '--private-key-certificates-only'.")
        if self.get_argument_managed_certificates_only() and self.get_argument_thumbprint():
            raise MutuallyExclusiveArgumentError("'--thumbprint' not supported for managed certificates.")

    def list(self):
        if self.get_argument_certificate() and is_valid_resource_id(self.get_argument_certificate()):
            certificate_name = parse_resource_id(self.get_argument_certificate())["resource_name"]
            certificate_type = parse_resource_id(self.get_argument_certificate())["resource_type"]
        else:
            certificate_name = self.get_argument_certificate()
            certificate_type = PRIVATE_CERTIFICATE_RT if self.get_argument_private_key_certificates_only() or self.get_argument_thumbprint() else (MANAGED_CERTIFICATE_RT if self.get_argument_managed_certificates_only() else None)

        if certificate_type == MANAGED_CERTIFICATE_RT:
            return self.get_managed_certificates(certificate_name)
        if certificate_type == PRIVATE_CERTIFICATE_RT:
            return self.get_private_certificates(certificate_name)
        managed_certs = self.get_managed_certificates(certificate_name)
        private_certs = self.get_private_certificates(certificate_name)
        return managed_certs + private_certs


class ContainerappEnvCertificateUploadDecorator(ContainerappEnvCertificateDecorator):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.certificate = ContainerAppCertificateEnvelopeModel
        self.cert_name = None

    def get_argument_certificate_name(self):
        return self.get_param("certificate_name")

    def get_argument_certificate_file(self):
        return self.get_param("certificate_file")

    def get_argument_certificate_password(self):
        return self.get_param("certificate_password")

    def get_argument_prompt(self):
        return self.get_param("prompt")

    def construct_payload(self):
        blob, thumbprint = load_cert_file(self.get_argument_certificate_file(), self.get_argument_certificate_password())

        if self.get_argument_certificate_name():
            name_availability = self.check_cert_name_availability(self.get_argument_resource_group_name(), self.get_argument_name(), self.get_argument_certificate_name())
            if not name_availability["nameAvailable"]:
                if name_availability["reason"] == NAME_ALREADY_EXISTS:
                    msg = '{}. If continue with this name, it will be overwritten by the new certificate file.\nOverwrite?'
                    overwrite = True
                    if self.get_argument_prompt():
                        overwrite = prompt_y_n(msg.format(name_availability["message"]))
                    else:
                        logger.warning('{}. It will be overwritten by the new certificate file.'.format(
                            name_availability["message"]))
                    if overwrite:
                        self.cert_name = self.get_argument_certificate_name()
                else:
                    raise ValidationError(name_availability["message"])
            else:
                self.cert_name = self.get_argument_certificate_name()

        while not self.cert_name:
            random_name = generate_randomized_cert_name(thumbprint, self.get_argument_name(), self.get_argument_resource_group_name())
            check_result = self.check_cert_name_availability(self.get_argument_resource_group_name(), self.get_argument_name(), random_name)
            if check_result["nameAvailable"]:
                self.cert_name = random_name
            elif not check_result["nameAvailable"] and (check_result["reason"] == NAME_INVALID):
                raise ValidationError(check_result["message"])

        self.certificate["properties"]["password"] = self.get_argument_certificate_password()
        self.certificate["properties"]["value"] = blob
        self.certificate["location"] = self.get_argument_location()
        if not self.certificate["location"]:
            try:
                managed_env = self.client.show(self.cmd, self.get_argument_resource_group_name(), self.get_argument_name())
                self.certificate["location"] = managed_env["location"]
            except Exception as e:
                handle_raw_exception(e)

    def create_or_update(self):
        try:
            r = self.client.create_or_update_certificate(self.cmd, self.get_argument_resource_group_name(), self.get_argument_name(), self.cert_name, self.certificate)
            return r
        except Exception as e:
            handle_raw_exception(e)
