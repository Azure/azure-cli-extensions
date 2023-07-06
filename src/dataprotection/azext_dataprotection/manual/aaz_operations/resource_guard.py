# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=line-too-long
from azure.cli.core.aaz import (
    AAZStrArg,
    AAZStrType, AAZObjectType, AAZDictType,
    AAZArgEnum,
    AAZUndefined
)
from azext_dataprotection.aaz.latest.dataprotection.resource_guard import Create as _Create, Update as _Update
from azext_dataprotection.manual.enums import get_resource_type_values, get_critical_operation_values
from knack.log import get_logger
from ..helpers import critical_operation_map

logger = get_logger(__name__)


class Create(_Create):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)
        # define Arg Group "Identity"
        _args_schema = cls._args_schema
        _args_schema.type = AAZStrArg(
            options=["--type"],
            arg_group="Identity",
            help="The identityType which can be either SystemAssigned or None",
        )
        return cls._args_schema

    class ResourceGuardsPut(_Create.ResourceGuardsPut):

        @property
        def content(self):
            _content_value, _builder = self.new_content_builder(
                self.ctx.args,
                typ=AAZObjectType,
                typ_kwargs={"flags": {"required": True, "client_flatten": True}}
            )
            _builder.set_prop("eTag", AAZStrType, ".e_tag")
            _builder.set_prop("location", AAZStrType, ".location")
            _builder.set_prop("properties", AAZObjectType)
            _builder.set_prop("tags", AAZDictType, ".tags")

            _builder.set_prop("identity", AAZObjectType)
            identity = _builder.get(".identity")
            if identity is not None:
                identity.set_prop("type", AAZStrType, ".type")

            tags = _builder.get(".tags")
            if tags is not None:
                tags.set_elements(AAZStrType, ".")

            return self.serialize_content(_content_value)


class Update(_Update):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.resource_type = AAZStrArg(
            options=["--resource-type"],
            help="Type of the resource associated with the protected operations.",
            enum=get_resource_type_values()
        )
        # define Arg Group "Identity"
        _args_schema.type = AAZStrArg(
            options=["--type"],
            arg_group="Identity",
            help="The identityType which can be either SystemAssigned or None",
        )
        enum = get_critical_operation_values()
        _args_schema.critical_operation_exclusion_list.Element.enum = AAZArgEnum(enum, case_sensitive=False)
        return cls._args_schema

    def pre_operations(self):
        critical_operation_exclusion_list = self.ctx.args.critical_operation_exclusion_list
        resource_type = self.ctx.args.resource_type
        if resource_type and critical_operation_exclusion_list.to_serialized_data() != AAZUndefined:
            for idx, critical_operation in enumerate(critical_operation_exclusion_list):
                critical_operation_id = critical_operation_map.get(str(critical_operation), str(critical_operation))
                critical_operation_exclusion_list[idx] = str(resource_type) + critical_operation_id
        else:
            if critical_operation_exclusion_list.to_serialized_data() != AAZUndefined:
                logger.warning("WARNING: --resource-type argument is required to update --critical-operation-exclusion-list.")
                self.ctx.args.critical_operation_exclusion_list = AAZUndefined

    class InstanceUpdateByJson(_Update.InstanceUpdateByJson):   # pylint: disable=too-few-public-methods

        def _update_instance(self, instance):
            _instance = super()._update_instance(instance)
            _instance_value, _builder = self.new_content_builder(
                self.ctx.args,
                value=_instance,
                typ=AAZObjectType
            )
            _builder.set_prop("identity", AAZObjectType)
            identity = _builder.get(".identity")
            if identity is not None:
                identity.set_prop("type", AAZStrType, ".type")
            return _instance_value
