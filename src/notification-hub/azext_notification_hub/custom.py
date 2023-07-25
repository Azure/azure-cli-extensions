# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
# pylint: disable=protected-access

from azure.cli.core.aaz import has_value
from azext_notification_hub.aaz.latest.notification_hub import Create as _CreateNotificationHub
from azext_notification_hub.aaz.latest.notification_hub import Update as _UpdateNotificationHub
from azext_notification_hub.aaz.latest.notification_hub.credential.apns import Create as _ApnsUpdate
from azext_notification_hub.aaz.latest.notification_hub.credential.mpns import Create as _MpnsUpdate
from azext_notification_hub.aaz.latest.notification_hub.credential.baidu import Create as _BaiduUpdate
from azext_notification_hub.aaz.latest.notification_hub.credential.adm import Create as _AdmUpdate
from azext_notification_hub.aaz.latest.notification_hub.authorization_rule import RegenerateKeys as _RegenerateKeys


class NotificationHubCreate(_CreateNotificationHub):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.location._required = True
        return args_schema


class NotificationHubUpdate(_UpdateNotificationHub):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.adm_credential._registered = False
        args_schema.apns_credential._registered = False
        args_schema.baidu_credential._registered = False
        args_schema.gcm_credential._registered = False
        args_schema.mpns_credential._registered = False
        args_schema.wns_credential._registered = False
        return args_schema


class ApnsUpdate(_ApnsUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZFreeFormDictArg, AAZFreeFormDictArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.apns_certificate = AAZFreeFormDictArg(
            options=['--apns-certificate'],
            help='The APNS certificate.',
            fmt=AAZFreeFormDictArgFormat()
        )
        args_schema.apns_certificate_org._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.apns_certificate):
            args.apns_certificate_org = args.apns_certificate


class AdmUpdate(_AdmUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.client_id._required = True
        args_schema.client_secret._required = True
        return args_schema


class MpnsUpdate(_MpnsUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZFreeFormDictArg, AAZFreeFormDictArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.mpns_certificate = AAZFreeFormDictArg(
            options=['--mpns-certificate'],
            help='The MPNS certificate.',
            fmt=AAZFreeFormDictArgFormat(),
            required=True
        )
        args_schema.mpns_certificate_org._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.mpns_certificate_org = args.mpns_certificate


class BaiduUpdate(_BaiduUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.api_key = AAZStrArg(
            options=['--api-key'],
            help='Baidu API key.',
            required=True
        )
        args_schema.secret_key = AAZStrArg(
            options=['--secret-key'],
            help='Baidu secret key.',
            required=True
        )
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.baidu_api_key = args.api_key
        args.baidu_secret_key = args.secret_key


class RuleRegenerateKeys(_RegenerateKeys):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZArgEnum
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.policy_key._required = True
        args_schema.policy_key.enum = AAZArgEnum({'primary key': 'Primary Key', 'secondary key': 'Secondary Key'})
        return args_schema
