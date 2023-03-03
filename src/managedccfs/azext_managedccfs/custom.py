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
            fmt = AAZFileArgTextFormat(),
        )
        
        _Element.encryptionkey = AAZFileArg(
            options=["encryption-key"],
            help="Path to the PEM certificate file containing the encryption key.",
            required=False,
            fmt = AAZFileArgTextFormat(),
        )

        _Element.identifier = AAZStrArg(
            options=["identifier"],
            help="A string value that is used to uniquely identify a member.",
            required=True,
        )
        
        args_schema.member_identity_certificates._registered = False

        # Deployment type properties.
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.app_type = AAZStrArg(
            options=['--app-type'],
            help="The type of the JS application. Set it to 'sample' to deploy the sample JS application.",
            required=False,
            default="customImage",
        )

        args_schema.deployment_type._registered = False

        return args_schema    

    def pre_operations(self):
        from azure.cli.core.aaz.utils import assign_aaz_list_arg
        from azure.cli.core.aaz import has_value
        args = self.ctx.args

        def members_transform(_, item):
            member_cert = dict()
            member_cert['certificate'] = item.certificate
            member_cert['encryptionkey'] = item.encryptionkey if (has_value(item.encryptionkey) and item.encryptionkey != None and item.encryptionkey != "") else None

            tags = dict()
            tags['identifier'] = item.identifier
            member_cert['tags'] = tags

            return member_cert
    
        args.member_identity_certificates = assign_aaz_list_arg(
            args.member_identity_certificates,
            args.members,
            element_transformer=members_transform
        )

        args.deployment_type.app_source_uri = args.app_type
        args.deployment_type.language_runtime = "JS"
