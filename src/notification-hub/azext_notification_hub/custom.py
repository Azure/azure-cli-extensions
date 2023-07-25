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
from azext_notification_hub.aaz.latest.notification_hub import Update as _UpdateNotificationHub

DEFAULT_APNS_ENDPOINT = "gateway.push.apple.com"


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


class GcmUpdate(_UpdateNotificationHub):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.google_api_key = AAZStrArg(
            options=['--google-api-key'],
            help='The Google API key.',
            required=True
        )
        args_schema.adm_credential._registered = False
        args_schema.apns_credential._registered = False
        args_schema.baidu_credential._registered = False
        args_schema.gcm_credential._registered = False
        args_schema.mpns_credential._registered = False
        args_schema.wns_credential._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.gcm_credential.google_api_key = args.google_api_key


class ApnsUpdate(_UpdateNotificationHub):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZFreeFormDictArg, AAZFreeFormDictArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.apns_certificate = AAZFreeFormDictArg(
            options=['--apns-certificate'],
            help='The APNS certificate.',
            fmt=AAZFreeFormDictArgFormat()
        )
        args_schema.app_id = AAZStrArg(
            options=['--app-id'],
            help='The issuer (iss) registered claim key, whose value is your 10-character Team ID, obtained from your developer account.'
        )
        args_schema.app_name = AAZStrArg(
            options=['--app-name'],
            help='The name of the application/bundle id.'
        )
        args_schema.certificate_key = AAZStrArg(
            options=['--certificate-key'],
            help='The certificate key.'
        )
        args_schema.endpoint = AAZStrArg(
            options=['--endpoint'],
            help='The endpoint of this credential. Example values:"gateway.sandbox.push.apple.com","gateway.push.apple.com".  Default: gateway.push.apple.com.',
            default=DEFAULT_APNS_ENDPOINT
        )
        args_schema.key_id = AAZStrArg(
            options=['--key-id'],
            help='A 10-character key identifier (kid) key, obtained from your developer account.'
        )
        args_schema.token = AAZStrArg(
            options=['--token'],
            help='Provider Authentication Token, obtained through your developer account.'
        )
        args_schema.adm_credential._registered = False
        args_schema.apns_credential._registered = False
        args_schema.baidu_credential._registered = False
        args_schema.gcm_credential._registered = False
        args_schema.mpns_credential._registered = False
        args_schema.wns_credential._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.apns_certificate):
            args.gcm_credential.google_api_key = args.google_api_key
        if has_value(args.app_id):
            args.apns_credential.app_id = args.app_id
        if has_value(args.app_name):
            args.apns_credential.app_name = args.app_name
        if has_value(args.certificate_key):
            args.apns_credential.certificate_key = args.certificate_key
        if has_value(args.endpoint):
            args.apns_credential.endpoint = args.endpoint
        if has_value(args.key_id):
            args.apns_credential.key_id = args.key_id
        if has_value(args.token):
            args.apns_credential.token = args.token


class WnsUpdate(_UpdateNotificationHub):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.package_sid = AAZStrArg(
            options=['--package-sid'],
            help='The package ID for this credential.',
            required=True
        )
        args_schema.secret_key = AAZStrArg(
            options=['--secret-key'],
            help='The secret key.',
            required=True
        )
        args_schema.adm_credential._registered = False
        args_schema.apns_credential._registered = False
        args_schema.baidu_credential._registered = False
        args_schema.gcm_credential._registered = False
        args_schema.mpns_credential._registered = False
        args_schema.wns_credential._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.wns_credential.package_sid = args.package_sid
        args.wns_credential.secret_key = args.secret_key


class MpnsUpdate(_UpdateNotificationHub):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZFreeFormDictArg, AAZFreeFormDictArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.mpns_certificate = AAZFreeFormDictArg(
            options=['--mpns-certificate'],
            help='The MPNS certificate.',
            fmt=AAZFreeFormDictArgFormat(),
            required=True
        )
        args_schema.certificate_key = AAZStrArg(
            options=['--certificate-key'],
            help='The certificate key for this credential.',
            required=True
        )
        args_schema.adm_credential._registered = False
        args_schema.apns_credential._registered = False
        args_schema.baidu_credential._registered = False
        args_schema.gcm_credential._registered = False
        args_schema.mpns_credential._registered = False
        args_schema.wns_credential._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.mpns_credential.mpns_certificate = args.mpns_certificate
        args.mpns_credential.certificate_key = args.certificate_key


class AdmUpdate(_UpdateNotificationHub):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.client_id = AAZStrArg(
            options=['--client-id'],
            help='The client identifier.',
            required=True
        )
        args_schema.client_secret = AAZStrArg(
            options=['--client-secret'],
            help='The credential secret access key.',
            required=True
        )
        args_schema.adm_credential._registered = False
        args_schema.apns_credential._registered = False
        args_schema.baidu_credential._registered = False
        args_schema.gcm_credential._registered = False
        args_schema.mpns_credential._registered = False
        args_schema.wns_credential._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.adm_credential.client_id = args.client_id
        args.adm_credential.client_secret = args.client_secret


class BaiduUpdate(_UpdateNotificationHub):
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
        args_schema.adm_credential._registered = False
        args_schema.apns_credential._registered = False
        args_schema.baidu_credential._registered = False
        args_schema.gcm_credential._registered = False
        args_schema.mpns_credential._registered = False
        args_schema.wns_credential._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.baidu_credential.api_key = args.api_key
        args.baidu_credential.secret_key = args.secret_key
