# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=line-too-long

from azure.cli.core.aaz import (
    AAZStrArg, AAZResourceGroupNameArg, AAZFreeFormDictArg,
    AAZObjectType, AAZFreeFormDictType
)
from azext_dataprotection.aaz.latest.dataprotection.backup_policy import Create as _Create


class Create(_Create):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super(_Create, cls)._build_arguments_schema(cls, *args, **kwargs)    # pylint: disable=bad-super-call

        _args_schema = cls._args_schema
        _args_schema.backup_policy_name = AAZStrArg(
            options=["-n", "--name", "--backup-policy-name"],
            help="Name of the policy",
            required=True,
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            help="Name of resource group. You can configure the default group using `az configure --defaults group=<name>`.",
            required=True,
        )
        _args_schema.vault_name = AAZStrArg(
            options=["--vault-name"],
            help="The name of the backup vault.",
            required=True,
        )
        # Replacing AAZObjectArg with AAZFreeFormDictArg (schemaless)
        _args_schema.policy = AAZFreeFormDictArg(
            options=["--policy"],
            help="Request body for operation Expected value: json-string/@json-file.",
            required=True,
        )

        return cls._args_schema

    class BackupPoliciesCreateOrUpdate(_Create.BackupPoliciesCreateOrUpdate):

        @property
        def content(self):
            _content_value, _builder = self.new_content_builder(
                self.ctx.args,
                typ=AAZObjectType,
                typ_kwargs={"flags": {"required": True, "client_flatten": True}}
            )
            _builder.set_prop("properties", AAZFreeFormDictType, '.policy')
            properties = _builder.get('.properties')
            properties.set_anytype_elements('.')

            return self.serialize_content(_content_value)
