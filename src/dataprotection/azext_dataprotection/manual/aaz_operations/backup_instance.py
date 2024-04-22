# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=line-too-long

from azure.cli.core.aaz import (
    AAZFreeFormDictArg, AAZStrArg, AAZResourceGroupNameArg, AAZResourceLocationArg,
    AAZResourceLocationArgFormat, AAZUndefined, has_value
)
from azure.cli.core.aaz.utils import assign_aaz_list_arg
from azext_dataprotection.aaz.latest.dataprotection.backup_instance import (
    Create as _Create,
    ValidateForBackup as _ValidateForBackup,
    ValidateForRestore as _ValidateForRestore,
    Update as _Update,
    StopProtection as _StopProtection,
    SuspendBackup as _SuspendBackup,
)
from azext_dataprotection.aaz.latest.dataprotection.cross_region_restore import (
    Validate as _ValidateForCRR,
    Trigger as _TriggerCRR
)

from azext_dataprotection.aaz.latest.dataprotection.backup_instance.restore import Trigger as _RestoreTrigger
from ..helpers import (
    convert_dict_keys_snake_to_camel, critical_operation_map,
    transform_resource_guard_operation_request
)


class UpdateWithBI(_Update):
    # For some reason, the auto-generated Backup Instance Update does not contain some fields. Prominently
    # in this situation, it is missing the properties.policyInfo.policyParameters section entirely, even though
    # Backup Instance Create contains it. To get around this, we have a modified Update function that basically
    # does a Create with an entire backup instance input.

    # To achieve that, we have to fetch the currently present backup instance, make any necessary changes
    # to that, and then remove any extranous fields that might be present.

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(cls, *args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.backup_instance = AAZFreeFormDictArg(
            options=["--backup-instance"],
            help="Request backup instance object for operation.",
            required=True,
        )
        _args_schema.backup_instance_name._registered = False
        _args_schema.backup_instance_name._required = False
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        yield self.BackupInstancesCreateOrUpdate(ctx=self.ctx)()
        self.post_operations()

    def pre_operations(self):
        self.ctx.args.backup_instance_name = self.ctx.args.backup_instance['backup_instance_name']
        self.ctx.set_var(
            "instance",
            self.ctx.args.backup_instance.to_serialized_data(),
            schema_builder=self.BackupInstancesCreateOrUpdate._build_schema_on_200_201
        )


class ValidateAndCreate(_Create):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(cls, *args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.backup_instance = AAZFreeFormDictArg(
            options=["--backup-instance"],
            help="Request backup instance object for operation.",
            required=True,
        )
        _args_schema.backup_instance_name._registered = False
        _args_schema.backup_instance_name._required = False
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        yield self.BackupInstancesValidateForBackup(ctx=self.ctx)()
        yield self.BackupInstancesCreateOrUpdate(ctx=self.ctx)()
        self.post_operations()

    def pre_operations(self):
        self.ctx.args.backup_instance_name = self.ctx.args.backup_instance['backup_instance_name']
        self.ctx.set_var(
            "instance",
            self.ctx.args.backup_instance.to_serialized_data(),
            schema_builder=self.BackupInstancesCreateOrUpdate._build_schema_on_200_201
        )

    class BackupInstancesValidateForBackup(_ValidateForBackup.BackupInstancesValidateForBackup):

        @property
        def content(self):
            _content_value, _builder = self.new_content_builder(
                self.ctx.args,
                typ=AAZFreeFormDictArg,
                value=self.ctx.vars.instance.properties,
                typ_kwargs={"flags": {"required": True, "client_flatten": True}}
            )
            return {
                "backupInstance": self.serialize_content(_content_value)
            }

    class BackupInstancesCreateOrUpdate(_Create.BackupInstancesCreateOrUpdate):

        @property
        def content(self):
            _content_value, _builder = self.new_content_builder(
                self.ctx.args,
                value=self.ctx.vars.instance,
            )
            return self.serialize_content(_content_value)


class ValidateForRestore(_ValidateForRestore):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super(_ValidateForRestore, cls)._build_arguments_schema(cls, *args, **kwargs)     # pylint: disable=bad-super-call

        _args_schema = cls._args_schema
        _args_schema.backup_instance_name = AAZStrArg(
            options=["-n", "--name", "--backup-instance-name"],
            help="The name of the backup instance.",
            required=True,
            id_part="child_name_1",
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            help="Name of resource group. You can configure the default group using `az configure --defaults group=<name>`.",
            required=True,
        )
        _args_schema.vault_name = AAZStrArg(
            options=["--vault-name"],
            help="The name of the backup vault.",
            required=True,
            id_part="name",
        )
        _args_schema.restore_request_object = AAZFreeFormDictArg(
            options=["--restore-request-object"],
            help="Gets or sets the restore request object.",
            required=True,
        )
        return cls._args_schema

    class BackupInstancesValidateForRestore(_ValidateForRestore.BackupInstancesValidateForRestore):

        @property
        def content(self):
            return {
                "restoreRequestObject": convert_dict_keys_snake_to_camel(self.ctx.args.restore_request_object.to_serialized_data())
            }


class RestoreTrigger(_RestoreTrigger):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.restore_target_info._required = False
        args_schema.restore_target_info._registered = False
        args_schema.source_data_store_type._required = False
        args_schema.source_data_store_type._registered = False

        args_schema.restore_request_object = AAZFreeFormDictArg(
            options=["--restore-request-object"],
            help="Gets or sets the restore request object. Expected value: json-string/@json-file.",
            required=True,
        )
        args_schema.tenant_id = AAZStrArg(
            options=["--tenant-id"],
            help="Tenant ID for cross-tenant calls"
        )

        return args_schema

    def pre_operations(self):
        # Allow users to enter predefined shorthand instead of the full path, if necessary
        if has_value(self.ctx.args.resource_guard_operation_requests):
            self.ctx.args.resource_guard_operation_requests = assign_aaz_list_arg(
                self.ctx.args.resource_guard_operation_requests,
                self.ctx.args.resource_guard_operation_requests,
                element_transformer=lambda _, operation:
                    transform_resource_guard_operation_request(self, _, operation)
            )
        if has_value(self.ctx.args.tenant_id):
            # ValueError is raised when providing an incorrect tenant ID. Capturing it in a try block does not work.
            self.ctx.update_aux_tenants(str(self.ctx.args.tenant_id))

    class BackupInstancesTriggerRestore(_RestoreTrigger.BackupInstancesTriggerRestore):

        @property
        def content(self):
            request_body = self.ctx.args.restore_request_object.to_serialized_data()
            resource_guard_operation_requests_deserialized = self.ctx.args.resource_guard_operation_requests.to_serialized_data()
            if resource_guard_operation_requests_deserialized != AAZUndefined:
                request_body['resourceGuardOperationRequests'] = resource_guard_operation_requests_deserialized
            request_body = convert_dict_keys_snake_to_camel(request_body)
            return request_body


class ValidateForCRR(_ValidateForCRR):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super(_ValidateForCRR, cls)._build_arguments_schema(cls, *args, **kwargs)     # pylint: disable=bad-super-call

        _args_schema = cls._args_schema
        _args_schema.location = AAZResourceLocationArg(
            required=True,
            id_part="name",
            fmt=AAZResourceLocationArgFormat(
                resource_group_arg="resource_group",
            ),
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )

        # define Arg Group "CrossRegionRestoreDetails"

        _args_schema = cls._args_schema
        _args_schema.source_backup_instance_id = AAZStrArg(
            options=["--source-backup-instance-id"],
            arg_group="CrossRegionRestoreDetails",
            help="The full ARM ID of the source backup instance",
            required=True,
        )
        _args_schema.source_region = AAZStrArg(
            options=["--source-region"],
            arg_group="CrossRegionRestoreDetails",
            help="The region that the source backup instance is present in",
            required=True,
        )

        _args_schema.restore_request_object = AAZFreeFormDictArg(
            options=["--restore-request-object"],
            help="Gets or sets the restore request object. Expected value: json-string/@json-file.",
            required=True,
        )

        return cls._args_schema

    class BackupInstancesValidateCrossRegionRestore(_ValidateForCRR.BackupInstancesValidateCrossRegionRestore):

        @property
        def content(self):
            crr_details = {}
            crr_details["sourceBackupInstanceId"] = self.ctx.args.source_backup_instance_id.to_serialized_data()
            crr_details["sourceRegion"] = self.ctx.args.source_region.to_serialized_data()
            return self.serialize_content({
                'objectType': 'ValidateRestoreRequestObject',
                'restoreRequestObject': convert_dict_keys_snake_to_camel(self.ctx.args.restore_request_object.to_serialized_data()),
                'crossRegionRestoreDetails': crr_details
            })


class TriggerCRR(_TriggerCRR):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super(_TriggerCRR, cls)._build_arguments_schema(cls, *args, **kwargs)     # pylint: disable=bad-super-call

        _args_schema = cls._args_schema
        _args_schema.location = AAZResourceLocationArg(
            required=True,
            id_part="name",
            fmt=AAZResourceLocationArgFormat(
                resource_group_arg="resource_group",
            ),
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )

        # define Arg Group "CrossRegionRestoreDetails"

        _args_schema = cls._args_schema
        _args_schema.source_backup_instance_id = AAZStrArg(
            options=["--source-backup-instance-id"],
            arg_group="CrossRegionRestoreDetails",
            help="The full ARM ID of the source backup instance",
            required=True,
        )
        _args_schema.source_region = AAZStrArg(
            options=["--source-region"],
            arg_group="CrossRegionRestoreDetails",
            help="The region that the source backup instance is present in",
            required=True,
        )

        _args_schema.restore_request_object = AAZFreeFormDictArg(
            options=["--restore-request-object"],
            help="Gets or sets the restore request object. Expected value: json-string/@json-file.",
            required=True,
        )

        return cls._args_schema

    class BackupInstancesTriggerCrossRegionRestore(_TriggerCRR.BackupInstancesTriggerCrossRegionRestore):

        @property
        def content(self):
            crr_details = {}
            restore_request_object = convert_dict_keys_snake_to_camel(self.ctx.args.restore_request_object.to_serialized_data())
            crr_details["sourceBackupInstanceId"] = self.ctx.args.source_backup_instance_id.to_serialized_data()
            crr_details["sourceRegion"] = self.ctx.args.source_region.to_serialized_data()

            return self.serialize_content({
                'objectType': restore_request_object["objectType"],
                'restoreRequestObject': restore_request_object,
                'crossRegionRestoreDetails': crr_details
            })


class SuspendBackup(_SuspendBackup):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.tenant_id = AAZStrArg(
            options=["--tenant-id"],
            help="Tenant ID for cross-tenant calls"
        )
        return cls._args_schema

    def pre_operations(self):
        # Allow users to enter predefined shorthand instead of the full path, if necessary
        if has_value(self.ctx.args.resource_guard_operation_requests):
            self.ctx.args.resource_guard_operation_requests = assign_aaz_list_arg(
                self.ctx.args.resource_guard_operation_requests,
                self.ctx.args.resource_guard_operation_requests,
                element_transformer=lambda _, operation:
                    transform_resource_guard_operation_request(self, _, operation)
            )
        if has_value(self.ctx.args.tenant_id):
            # ValueError is raised when providing an incorrect tenant ID. Capturing it in a try block does not work.
            self.ctx.update_aux_tenants(str(self.ctx.args.tenant_id))


class StopProtection(_StopProtection):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.tenant_id = AAZStrArg(
            options=["--tenant-id"],
            help="Tenant ID for cross-tenant calls"
        )
        return cls._args_schema

    def pre_operations(self):
        # Allow users to enter predefined shorthand instead of the full path, if necessary
        if has_value(self.ctx.args.resource_guard_operation_requests):
            self.ctx.args.resource_guard_operation_requests = assign_aaz_list_arg(
                self.ctx.args.resource_guard_operation_requests,
                self.ctx.args.resource_guard_operation_requests,
                element_transformer=lambda _, operation:
                    transform_resource_guard_operation_request(self, _, operation)
            )
        if has_value(self.ctx.args.tenant_id):
            # ValueError is raised when providing an incorrect tenant ID. Capturing it in a try block does not work.
            self.ctx.update_aux_tenants(str(self.ctx.args.tenant_id))
