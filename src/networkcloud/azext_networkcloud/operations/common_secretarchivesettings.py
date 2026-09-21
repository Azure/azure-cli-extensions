# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access, too-few-public-methods
# pylint: disable=duplicate-code,no-member

"""
This is custom code for secret archive settings
"""

from azure.cli.core.aaz import AAZObjectType, AAZStrArg, AAZStrType
from azure.cli.core.aaz._base import has_value
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)
from knack.log import get_logger

logger = get_logger(__name__)


class SecretArchiveSettings:
    @staticmethod
    def build_arguments_schema(args_schema):
        settings = args_schema.secret_archive_settings
        settings.provider_configuration._registered = False
        settings.provider = AAZStrArg(
            options=["provider"],
            help="The self-supplied secret archive provider.",
            enum={
                "CyberArk": "CyberArk",
                "HashiCorpVault": "HashiCorpVault",
                "OpenBao": "OpenBao",
            },
        )
        settings.application_id = AAZStrArg(
            options=["application-id"],
            help="The CyberArk application ID.",
        )
        settings.safe_name = AAZStrArg(
            options=["safe-name"],
            help="The CyberArk safe name for credential storage.",
        )
        settings.folder_name = AAZStrArg(
            options=["folder-name"],
            help="The CyberArk folder name within the safe.",
        )
        settings.object_name_template = AAZStrArg(
            options=["object-name-template"],
            help="The CyberArk object naming pattern within the safe.",
        )
        settings.authentication_method = AAZStrArg(
            options=["authentication-method"],
            help="The HashiCorp Vault or OpenBao authentication method.",
            enum={"AppRole": "AppRole", "ClientCertificate": "ClientCertificate"},
        )
        settings.application_role_id = AAZStrArg(
            options=["application-role-id"],
            help="The application role ID used with AppRole authentication.",
        )
        settings.authentication_mount_path = AAZStrArg(
            options=["authentication-mount-path"],
            help="The authentication method mount path in the archive.",
        )
        settings.key_value_version = AAZStrArg(
            options=["key-value-version"],
            help="The key value engine version.",
            enum={"V1": "V1", "V2": "V2"},
        )
        settings.mount_path = AAZStrArg(
            options=["mount-path"],
            help="The key value secrets engine mount path.",
        )
        settings.namespace = AAZStrArg(
            options=["namespace"],
            help="The vault namespace.",
        )
        settings.path_template = AAZStrArg(
            options=["path-template"],
            help="The secret path pattern.",
        )
        return args_schema

    @classmethod
    def pre_operations_create(cls, args):
        cls.pre_operations_update(args)

    @classmethod
    def pre_operations_update(cls, args):
        if has_value(args.secret_archive_settings):
            # skip validation when the value is explicitly set to null
            if args.secret_archive_settings._data is None:
                return
            if not has_value(args.secret_archive_settings.vault_uri):
                raise RequiredArgumentMissingError(
                    "Key Vault URI is missing for secret archive settings."
                )
            # if system assigned is provided, user assigned should not also be provided
            if args.secret_archive_settings.identity_type == "SystemAssignedIdentity":
                if has_value(args.secret_archive_settings.identity_resource_id):
                    logger.warning(
                        "For --secret-archive-settings, SystemAssignedIdentity type is "
                        "mutually exclusive with UserAssignedIdentity "
                        "type. Ignoring provided user-assigned identity %s",
                        args.secret_archive_settings.identity_resource_id,
                    )
                    args.secret_archive_settings.identity_resource_id = None
            elif args.secret_archive_settings.identity_type == "UserAssignedIdentity":
                if not has_value(args.secret_archive_settings.identity_resource_id):
                    raise InvalidArgumentValueError(
                        "User-assigned identity resource ID is missing for secret archive settings."
                    )

            provider = args.secret_archive_settings.provider
            if provider == "CyberArk":
                if not has_value(args.secret_archive_settings.application_id):
                    raise RequiredArgumentMissingError(
                        "CyberArk application ID is missing for secret archive settings."
                    )
                if not has_value(args.secret_archive_settings.safe_name):
                    raise RequiredArgumentMissingError(
                        "CyberArk safe name is missing for secret archive settings."
                    )
            elif provider in ("HashiCorpVault", "OpenBao") and not has_value(
                args.secret_archive_settings.authentication_method
            ):
                raise RequiredArgumentMissingError(
                    f"Authentication method is missing for {provider} secret archive settings."
                )


class SecretArchiveSettingsContent:
    """Serialize flat secret archive provider arguments into providerConfiguration."""

    @property
    def content(self):
        content = super().content
        settings = self.ctx.args.secret_archive_settings
        if (
            not has_value(settings)
            or settings._data is None
            or not has_value(settings.provider)
        ):
            return content

        config_value, builder = self.new_content_builder(settings, typ=AAZObjectType)
        builder.set_prop(
            "provider",
            AAZStrType,
            ".provider",
            typ_kwargs={"flags": {"required": True}},
        )

        if settings.provider == "CyberArk":
            builder.set_prop("applicationId", AAZStrType, ".application_id")
            builder.set_prop("folderName", AAZStrType, ".folder_name")
            builder.set_prop("objectNameTemplate", AAZStrType, ".object_name_template")
            builder.set_prop("safeName", AAZStrType, ".safe_name")
        else:
            builder.set_prop("applicationRoleId", AAZStrType, ".application_role_id")
            builder.set_prop(
                "authenticationMethod", AAZStrType, ".authentication_method"
            )
            builder.set_prop(
                "authenticationMountPath",
                AAZStrType,
                ".authentication_mount_path",
            )
            builder.set_prop("keyValueVersion", AAZStrType, ".key_value_version")
            builder.set_prop("mountPath", AAZStrType, ".mount_path")
            builder.set_prop("namespace", AAZStrType, ".namespace")
            builder.set_prop("pathTemplate", AAZStrType, ".path_template")

        provider_configuration = self.serialize_content(config_value)
        content["properties"]["secretArchiveSettings"][
            "providerConfiguration"
        ] = provider_configuration
        return content
