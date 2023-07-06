# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=line-too-long
from azure.cli.core.aaz import (
    AAZFreeFormDictArg, AAZStrArg, AAZResourceGroupNameArg,
)
from azext_dataprotection.aaz.latest.dataprotection.backup_instance import (
    AdhocBackup as _AdhocBackup,
    Create as _Create,
    ValidateForBackup as _ValidateForBackup,
    ValidateForRestore as _ValidateForRestore,
)
from azext_dataprotection.aaz.latest.dataprotection.backup_instance.restore import Trigger as _RestoreTrigger
from ..helpers import convert_dict_keys_snake_to_camel


class AdhocBackup(_AdhocBackup):

    class BackupInstancesAdhocBackup(_AdhocBackup.BackupInstancesAdhocBackup):

        def on_200(self, session):
            data = self.deserialize_http_content(session)
            data = data.get('properties')
            self.ctx.set_var(
                "instance",
                data,
                schema_builder=self._build_schema_on_200
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

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [202]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200,
                    self.on_error,
                    lro_options={"final-state-via": "location"},
                    path_format_arguments=self.url_parameters,
                )
            if session.http_response.status_code in [200]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200,
                    self.on_error,
                    lro_options={"final-state-via": "location"},
                    path_format_arguments=self.url_parameters,
                )
            return self.on_error(session.http_response)

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

        return args_schema

    class BackupInstancesTriggerRestore(_RestoreTrigger.BackupInstancesTriggerRestore):

        @property
        def content(self):
            return convert_dict_keys_snake_to_camel(self.ctx.args.restore_request_object.to_serialized_data())

        def on_200(self, session):
            data = self.deserialize_http_content(session)
            data = data.get('properties')
            self.ctx.set_var(
                "instance",
                data,
                schema_builder=self._build_schema_on_200
            )


class ValidateForBackup(_ValidateForBackup):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super(_ValidateForBackup, cls)._build_arguments_schema(*args, **kwargs)  # pylint: disable=bad-super-call

        _args_schema = cls._args_schema
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )
        _args_schema.vault_name = AAZStrArg(
            options=["--vault-name"],
            help="The name of the backup vault.",
            required=True,
            id_part="name",
        )
        _args_schema.backup_instance = AAZFreeFormDictArg(
            options=["--backup-instance"],
            help="Backup Instance",
            required=True,
        )
        return cls._args_schema

    class BackupInstancesValidateForBackup(_ValidateForBackup.BackupInstancesValidateForBackup):

        # TODO: Reach out to swagger team about potentially fixing this in the swagger-side.
        #       We have to replace "final-state-via" to "location" instead of "azure-async-operation"
        # In case of debug issues, compare against the equivalent call in
        #  src\dataprotection\azext_dataprotection\aaz\latest\dataprotection\backup_instance\_validate_for_backup.py
        #  to see if there are any new divergences.
        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [202]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200,
                    self.on_error,
                    lro_options={"final-state-via": "location"},
                    path_format_arguments=self.url_parameters,
                )
            if session.http_response.status_code in [200]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200,
                    self.on_error,
                    lro_options={"final-state-via": "location"},
                    path_format_arguments=self.url_parameters,
                )
            return self.on_error(session.http_response)

        @property
        def content(self):
            body = convert_dict_keys_snake_to_camel(self.ctx.args.backup_instance['properties'])
            return {
                "backupInstance": convert_dict_keys_snake_to_camel(body)
            }
