# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.aaz import AAZArgEnum, AAZResourceIdArg, has_value
from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_workload_manager.aaz.latest.workload_manager.workload_space.capability import (
    Create as _CapabilityCreate,
)
from azext_workload_manager.aaz.latest.workload_manager.workload_space.runtime_binding import (
    Create as _RuntimeBindingCreate,
)
from azext_workload_manager.aaz.latest.workload_manager.workload_space.runtime_link import (
    Create as _RuntimeLinkCreate,
)


class CapabilityCreate(_CapabilityCreate):

    _args_schema = None
    _arguments_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.kind.enum = AAZArgEnum({
            **args_schema.kind.enum.items,
            "PodSnapshotRestore": "PodSnapshotRestore",
        })
        return args_schema


class RuntimeBindingCreate(_RuntimeBindingCreate):

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.managed) and has_value(args.referenced):
            raise InvalidArgumentValueError(
                "Specify exactly one of --managed or --referenced."
            )

        execution_identity = args.identity_profile.execution_identity
        if has_value(execution_identity.referenced) and has_value(execution_identity.service_managed):
            raise InvalidArgumentValueError(
                "Specify exactly one execution identity variant: referenced or service-managed."
            )


class RuntimeLinkCreate(_RuntimeLinkCreate):

    _args_schema = None
    _arguments_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.subnet_resource_id = AAZResourceIdArg(
            options=["--subnet-resource-id"],
            arg_group="Properties",
            help="Resource ID of the subnet used by the runtime link.",
        )
        return args_schema

    class RuntimeLinksCreateOrUpdate(_RuntimeLinkCreate.RuntimeLinksCreateOrUpdate):

        @property
        def content(self):
            content = super().content
            subnet = self.ctx.args.subnet_resource_id
            if has_value(subnet):
                content["properties"]["subnetResourceId"] = subnet.to_serialized_data()
            return content
