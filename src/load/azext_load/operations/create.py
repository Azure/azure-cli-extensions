from ..aaz.latest.load._create import *
from azure.cli.core.aaz import *

class LoadTestCreate(Create):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        
        args_schema.user_assigned_identities = AAZListArg(
            options=['--user-assigned-identities'],
            arg_group="Optional Parameters", 
            help="The list of user assigned identities associated with the resource. The list elements will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}."
        )
        args_schema.user_assigned_identities.Element = AAZStrArg()

        return args_schema

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        args = [(name, arg) for (name, arg) in args if name not in ("user_assigned")]
        return args

    def pre_operations(self):

        args = self.ctx.args
        identity_type_str = str(args.identity_type)
        if "userassigned" in identity_type_str.lower():
            self.ctx.args.user_assigned = {}
            for user_assigned_identity in args.user_assigned_identities:
                identity_id = str(user_assigned_identity)
                self.ctx.args.user_assigned[identity_id] = {}