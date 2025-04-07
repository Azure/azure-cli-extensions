# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
# pylint: disable=protected-access, consider-using-f-string

from azure.cli.core.aaz import has_value, register_command
from azext_notification_hub.aaz.latest.notification_hub import Create as _CreateNotificationHub
from azext_notification_hub.aaz.latest.notification_hub import Update as _UpdateNotificationHub
from azext_notification_hub.aaz.latest.notification_hub.credential.apns import Create as _ApnsUpdate
from azext_notification_hub.aaz.latest.notification_hub.credential.mpns import Create as _MpnsUpdate
from azext_notification_hub.aaz.latest.notification_hub.credential.baidu import Create as _BaiduUpdate
from azext_notification_hub.aaz.latest.notification_hub.credential.adm import Create as _AdmUpdate
from azext_notification_hub.aaz.latest.notification_hub.credential.wns import Create as _WnsUpdate
from azext_notification_hub.aaz.latest.notification_hub.credential.gcm import Create as _GcmUpdate
from azext_notification_hub.aaz.latest.notification_hub.authorization_rule import RegenerateKeys as _RegenerateKeys
from azext_notification_hub.aaz.latest.notification_hub.namespace import Create as _NamespaceCreate
from azext_notification_hub.aaz.latest.notification_hub.namespace.authorization_rule import Create as _NamespaceRuleCreate
from azext_notification_hub.aaz.latest.notification_hub.namespace.authorization_rule import RegenerateKeys as _NamespaceRuleRegenerateKeys


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


@register_command(
    "notification-hub credential apns update",
    is_experimental=True,
)
class ApnsUpdate(_ApnsUpdate):
    """Update credential for Apple(APNS).

    :example: Update APNS certificate
        az notification-hub credential apns update --namespace-name my-namespace --notification-hub-name my-hub --apns-certificate "/path/to/certificate" --certificate-key "xxxxxx" --resource-group MyResourceGroup
    """
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZFileArg, AAZFileArgBase64EncodeFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.apns_certificate = AAZFileArg(
            options=['--apns-certificate'],
            help='The APNS certificate.',
            fmt=AAZFileArgBase64EncodeFormat()
        )
        args_schema.apns_certificate_org._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.apns_certificate):
            args.apns_certificate_org = args.apns_certificate


@register_command(
    "notification-hub credential adm update",
    is_experimental=True,
)
class AdmUpdate(_AdmUpdate):
    """Update credential for Amazon(ADM).
    """
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.client_id._required = True
        args_schema.client_secret._required = True
        return args_schema


@register_command(
    "notification-hub credential wns update",
    is_experimental=True,
)
class WnsUpdate(_WnsUpdate):
    """Update credential for Windows(WNS).
    """
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.package_sid._required = True
        args_schema.secret_key._required = True
        return args_schema


@register_command(
    "notification-hub credential gcm update",
    is_experimental=True,
)
class GcmUpdate(_GcmUpdate):
    """Update the Google GCM/FCM API key.

        :example: Update Android push API key
            az notification-hub credential gcm update --resource-group groupName --namespace-name spaceName --notification-hub-name hubName --google-api-key keyValue
        """
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.google_api_key._required = True
        return args_schema


@register_command(
    "notification-hub credential mpns update",
    is_experimental=True,
)
class MpnsUpdate(_MpnsUpdate):
    """Update credential for Windows Phone(MPNS).
    """
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZFileArg, AAZFileArgBase64EncodeFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.mpns_certificate = AAZFileArg(
            options=['--mpns-certificate'],
            help='The MPNS certificate.',
            fmt=AAZFileArgBase64EncodeFormat(),
            required=True
        )
        args_schema.certificate_key._required = True
        args_schema.mpns_certificate_org._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.mpns_certificate_org = args.mpns_certificate


@register_command(
    "notification-hub credential baidu update",
    is_experimental=True,
)
class BaiduUpdate(_BaiduUpdate):
    """Update credential for Baidu(Andrioid China).
    """
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
        args_schema.policy_key.enum = AAZArgEnum({'Primary Key': 'Primary Key', 'Secondary Key': 'Secondary Key'})
        return args_schema


class NamespaceCreate(_NamespaceCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.sku._required = True
        return args_schema


class NamespaceRuleCreate(_NamespaceRuleCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.rights._required = True
        return args_schema


class NamespaceRuleRegenerateKeys(_NamespaceRuleRegenerateKeys):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZArgEnum
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.policy_key._required = True
        args_schema.policy_key.enum = AAZArgEnum({'Primary Key': 'Primary Key', 'Secondary Key': 'Secondary Key'})
        return args_schema


def debug_send_notificationhubs_hub(cmd, client,
                                    resource_group_name,
                                    namespace_name,
                                    notification_hub_name,
                                    notification_format,
                                    message=None,
                                    title='',
                                    payload=None,
                                    tag=None):
    # Refer to tutorials in https://docs.microsoft.com/azure/notification-hubs/ for more details
    if message is not None:
        if notification_format == 'gcm':
            parameters = {"data": {"message": message}}
        elif notification_format == 'baidu':
            parameters = {"title": title, "description": message}
        elif notification_format == 'apple':
            parameters = {"aps": {"alert": message}}
        elif notification_format == 'template':
            parameters = {"message": message}
        elif notification_format == 'windows':
            parameters = message
        elif notification_format == 'windowsphone':
            parameters = '''<?xml version= "1.0" encoding= "utf-8" ?>
<root>
<Value1>{}</Value1>
<Value2>{}</Value2>
</root>
'''.format(title, message)
    else:
        if notification_format not in ['windows', 'windowsphone']:
            import json
            parameters = json.loads(payload)
        else:
            parameters = payload
    custom_headers = {"servicebusnotification-format": notification_format}
    if tag is not None:
        custom_headers['servicebusnotification-tags'] = tag

    return client.debug_send(resource_group_name=resource_group_name, namespace_name=namespace_name, notification_hub_name=notification_hub_name, parameters=parameters, custom_headers=custom_headers)
