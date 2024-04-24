# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# --------------------------------------------------------------------------

from azure.cli.core.azclierror import ArgumentUsageError
from .aaz.latest.confidentialledger.managedccfs._create import Create as _ManagedCCFCreate


class MemberIdentityCertificate(_ManagedCCFCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg, AAZObjectArg, AAZFileArg, AAZStrArg, AAZFileArgTextFormat

        # Member details.
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.members = AAZListArg(
            options=['--members'],
            help="Member details.",
            required=True,
        )

        args_schema.members.Element = AAZObjectArg()
        _Element = args_schema.members.Element
        _Element.certificate = AAZFileArg(
            options=["certificate"],
            help="Path to the PEM certificate file.",
            required=True,
            fmt=AAZFileArgTextFormat(),
        )

        _Element.encryptionkey = AAZFileArg(
            options=["encryption-key"],
            help="Path to the PEM certificate file containing the encryption key.",
            required=False,
            fmt=AAZFileArgTextFormat(),
        )

        _Element.identifier = AAZStrArg(
            options=["identifier"],
            help="A unique identifier for the member.",
            required=True,
        )

        _Element.group = AAZStrArg(
            options=["group"],
            help="A group name for the member.",
            required=False,
        )

        # pylint: disable=protected-access
        args_schema.member_certificates._registered = False

        # Deployment type properties.
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.app_type = AAZStrArg(
            options=['--app-type'],
            help="Set it to 'sample' to deploy the sample JS application.",
            required=False,
            default="customImage",
        )

        # Deployment type properties.
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.language_runtime = AAZStrArg(
            options=['--language-runtime'],
            help="The application language.",
            required=False,
            default="JS",
        )

        # pylint: disable=protected-access
        args_schema.deployment_type._registered = False
        return args_schema

    def pre_operations(self):
        from azure.cli.core.aaz.utils import assign_aaz_list_arg
        from azure.cli.core.aaz import has_value
        args = self.ctx.args

        if args.node_count < 3 or args.node_count > 9 or (args.node_count.to_serialized_data() % 2 == 0):
            raise ArgumentUsageError("Node consensus requires odd number of nodes. Select a number between 3 and 9.")

        def members_transform(_, item):
            member_cert = {}
            member_cert['certificate'] = item.certificate

            member_cert['encryptionkey'] = None
            if (has_value(item.encryptionkey) and item.encryptionkey is not None and item.encryptionkey != ""):
                member_cert['encryptionkey'] = item.encryptionkey

            tags = {}
            tags['identifier'] = item.identifier
            tags['group'] = item.group if has_value(item.group) else None
            member_cert['tags'] = tags
            return member_cert

        args.member_certificates = assign_aaz_list_arg(
            args.member_certificates,
            args.members,
            element_transformer=members_transform
        )

        args.deployment_type.app_source_uri = args.app_type
        args.deployment_type.language_runtime = "JS" if not has_value(args.language_runtime) else args.language_runtime
