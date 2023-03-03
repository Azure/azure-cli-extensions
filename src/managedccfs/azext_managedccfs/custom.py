from .aaz.latest.confidentialledger.managedccfs._create import Create as _ManagedCCFCreate

class MemberIdentityCertificate(_ManagedCCFCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg, AAZObjectArg, AAZFileArg, AAZStrArg, AAZFileArgTextFormat

        args_schema = super()._build_arguments_schema(*args, **kwargs)   
        args_schema.certs = AAZListArg(
                options=['--certs'],
                help="Details of the member identity certificate.",
                required=True,
        )
        
        args_schema.certs.Element = AAZObjectArg()

        _Element = args_schema.certs.Element
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

        _Element.tags = AAZStrArg(
            options=["identifier"],
            help="A string value that is used to uniquely identify a member.",
            required=True,
        )
        
        args_schema.member_identity_certificates._registered = False
        return args_schema    

    def pre_operations(self):
        from azure.cli.core.aaz.utils import assign_aaz_list_arg
        from azure.cli.core.aaz import has_value
        args = self.ctx.args

        def item_transform(_, item):
            member_cert = dict()
            member_cert['certificate'] = item.certificate
            member_cert['encryptionkey'] = item.encryption_key if (has_value(item.encryption_key) and item.encryption_key != None and item.encryption_key != "") else None

            tags = dict()
            tags['identifier'] = item.identifier
            member_cert['tags'] = tags

            return member_cert

        args.member_identity_certificates = assign_aaz_list_arg(
            args.member_identity_certificates,
            args.certs,
            element_transformer=item_transform
        )

        print(args.member_identity_certificates.to_serialized_data())

