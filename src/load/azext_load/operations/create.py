from ..aaz.latest.load._create import Create
from azure.cli.core.aaz import AAZListArg, AAZStrArg, has_value
from msrestazure.tools import is_valid_resource_id
from azure.core.exceptions import raise_with_traceback, ServiceRequestError


class LoadTestCreate(Create):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.user_assigned = AAZListArg(
            options=['--user-assigned'],
            arg_group="Optional Parameters",
            help="The list of user identities associated with the resource separated by spaces. The user identity will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'"
        )
        args_schema.user_assigned.Element = AAZStrArg()

        return args_schema

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        args = [(name, arg) for (name, arg) in args if name not in ["user_assigned_identities", "encryption_identity_type"]]
        return args

    def pre_operations(self):
        args = self.ctx.args
        identity_type_str = str(args.identity_type)
        if "userassigned" in identity_type_str.lower():
            args.user_assigned_identities = {}
            for user_assigned_identity in args.user_assigned:
                identity_id = str(user_assigned_identity)
                args.user_assigned_identities[identity_id] = {}

        if has_value(args.encryption_identity):
            encryption_identity_id = str(args.encryption_identity)
            if not is_valid_resource_id(encryption_identity_id):
                raise ServiceRequestError("Invalid encryption identity parameter: " + encryption_identity_id + ". Please enter a valid resource id.")
            else:
                args.encryption_identity_type = "UserAssigned"
                if identity_type_str.lower() == "none":
                    args.identity_type = "UserAssigned"
                elif identity_type_str.lower() == "systemassigned":
                    args.identity_type = "SystemAssigned,UserAssigned"
                args.user_assigned_identities = {}
                args.user_assigned_identities[encryption_identity_id] = {}
