# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access

from azure.cli.core.aaz import AAZObjectArg
from azure.cli.core.aaz._base import has_value
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.core.exceptions import ResourceNotFoundError
from knack.log import get_logger

from azext_cdn.vendored_sdks.models import SkuName
from azext_cdn.aaz.latest.afd.custom_domain import Create as _AFDCustomDomainCreate, \
    Update as _AFDCustomDomainUpdate
from azext_cdn.aaz.latest.afd.endpoint import Create as _AFDEndpointCreate, Update as _AFDEndpointUpdate
from azext_cdn.aaz.latest.afd.profile import Show as _AFDProfileShow, \
    Create as _AFDProfileCreate, Update as _AFDProfileUpdate
from azext_cdn.aaz.latest.afd.profile.log_scrubbing import Show as _AFDProfileLogScrubbingShow
from azext_cdn.aaz.latest.afd.rule import Create as _AFDRuleCreate
from azext_cdn.aaz.latest.afd.rule.action import Add as _AFDRuleActionAdd
from azext_cdn.aaz.latest.afd.rule.condition import Add as _AFDRuleConditionAdd
from azext_cdn.aaz.latest.afd.origin_group import Update as _AFDOriginGroupUpdate
from azext_cdn.aaz.latest.afd.origin import Update as _AFDOriginUpdate
from azext_cdn.aaz.latest.afd.route import Create as _AFDRouteCreate, Update as _AFDRouteUpdate

logger = get_logger(__name__)


def _allow_enum_extensions(arg):
    if hasattr(arg, 'enum') and arg.enum is not None:
        arg.enum.support_extension = True
    if hasattr(arg, 'Element'):
        _allow_enum_extensions(arg.Element)
    for field in getattr(arg, '_fields', {}).values():
        _allow_enum_extensions(field)


def _normalize_origin_group_id(cmd):
    args = cmd.ctx.args
    if has_value(args.origin_group):
        origin_group = args.origin_group.to_serialized_data()
        if origin_group and not origin_group.startswith('/'):
            args.origin_group = f'/subscriptions/{cmd.ctx.subscription_id}/resourceGroups/{args.resource_group}' \
                                f'/providers/Microsoft.Cdn/profiles/{args.profile_name}' \
                                f'/originGroups/{origin_group}'


class AFDCustomDomainCreate(_AFDCustomDomainCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.azure_dns_zone) and "/dnszones/" not in args.azure_dns_zone.to_serialized_data().lower():
            raise InvalidArgumentValueError('azure_dns_zone should be valid Azure dns zone ID.')
        if has_value(args.secret) and "/secrets/" not in args.secret.to_serialized_data().lower():
            args.secret = f'/subscriptions/{self.ctx.subscription_id}/resourceGroups/{args.resource_group}' \
                          f'/providers/Microsoft.Cdn/profiles/{args.profile_name}/secrets/{args.secret}'


class AFDCustomDomainUpdate(_AFDCustomDomainUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.azure_dns_zone) and "/dnszones/" not in args.azure_dns_zone.to_serialized_data().lower():
            raise InvalidArgumentValueError('azure_dns_zone should be valid Azure dns zone ID.')
        if has_value(args.secret) and "/secrets/" not in args.secret.to_serialized_data().lower():
            args.secret = f'/subscriptions/{self.ctx.subscription_id}/resourceGroups/{args.resource_group}' \
                          f'/providers/Microsoft.Cdn/profiles/{args.profile_name}/secrets/{args.secret}'


class AFDProfileShow(_AFDProfileShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema

    def _output(self, *args, **kwargs):
        existing = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        if existing['sku']['name'] not in (SkuName.premium_azure_front_door, SkuName.standard_azure_front_door):
            logger.warning('Unexpected SKU type, only Standard_AzureFrontDoor and Premium_AzureFrontDoor are supported')
            raise ResourceNotFoundError("Operation returned an invalid status code 'Not Found'")
        return existing


class AFDProfileCreate(_AFDProfileCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.location._registered = False
        args_schema.location._required = False
        return args_schema

    def pre_operations(self):
        self.ctx.args.location = 'global'


class AFDProfileUpdate(_AFDProfileUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.sku._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        existing = _AFDProfileShow(cli_ctx=self.cli_ctx)(command_args={
            'resource_group': args.resource_group,
            'profile_name': args.profile_name
        })
        if existing['sku']['name'] not in (SkuName.premium_azure_front_door, SkuName.standard_azure_front_door):
            logger.warning('Unexpected SKU type, only Standard_AzureFrontDoor and Premium_AzureFrontDoor are supported')
            raise ResourceNotFoundError("Operation returned an invalid status code 'Not Found'")


class AFDProfileLogScrubbingShow(_AFDProfileLogScrubbingShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema

    def _output(self, *args, **kwargs):
        existing = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return existing['logScrubbing']


class AFDRuleCreate(_AFDRuleCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        _allow_enum_extensions(args_schema.conditions)
        return args_schema


class AFDRuleActionAdd(_AFDRuleActionAdd):
    class SubresourceSelector(_AFDRuleActionAdd.SubresourceSelector):
        def _get(self):
            result = self.ctx.vars.instance
            result = result.properties.actions
            filters = enumerate(result)
            filters = filter(
                lambda e: e[1].name == self.ctx.args.action_name,
                filters
            )
            idx = list(filters)[-1][0]
            return result[idx]

        def _set(self, value):
            result = self.ctx.vars.instance
            result = result.properties.actions
            result.append(value)
            return


class AFDRuleConditionAdd(_AFDRuleConditionAdd):
    class SubresourceSelector(_AFDRuleConditionAdd.SubresourceSelector):
        def _get(self):
            result = self.ctx.vars.instance
            result = result.properties.conditions
            filters = enumerate(result)
            filters = filter(
                lambda e: e[1].name == self.ctx.args.condition_name,
                filters
            )
            idx = list(filters)[-1][0]
            return result[idx]

        def _set(self, value):
            result = self.ctx.vars.instance
            result = result.properties.conditions
            result.append(value)
            return


class AFDOriginGroupUpdate(_AFDOriginGroupUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.health_probe_settings = AAZObjectArg(
            options=["--health-probe-settings"],
            nullable=True,
            help="Legacy health probe settings. Use flat --probe-* arguments for field updates.",
        )
        return args_schema

    class InstanceUpdateByJson(_AFDOriginGroupUpdate.InstanceUpdateByJson):
        def _update_instance(self, instance):
            _instance_value = super()._update_instance(instance)
            if has_value(self.ctx.args.health_probe_settings) and \
                    self.ctx.args.health_probe_settings.to_serialized_data() is None:
                _instance_value.properties.health_probe_settings = None
            return _instance_value


class AFDOriginUpdate(_AFDOriginUpdate):
    _SHARED_PRIVATE_LINK_RESOURCE_FIELDS = ("private_link", "private_link_location", "request_message", "status")

    def pre_instance_update(self, instance):
        self._existing_shared_private_link_resource = {}
        if has_value(self.ctx.args.shared_private_link_resource) and \
                self.ctx.args.shared_private_link_resource.to_serialized_data() is not None:
            existing = instance.properties.shared_private_link_resource
            if existing is not None:
                self._existing_shared_private_link_resource = {
                    field: getattr(existing, field).to_serialized_data()
                    for field in self._SHARED_PRIVATE_LINK_RESOURCE_FIELDS
                    if has_value(getattr(existing, field))
                }

    def post_instance_update(self, instance):
        if has_value(self.ctx.args.shared_private_link_resource) and \
                self.ctx.args.shared_private_link_resource.to_serialized_data() is not None:
            existing = self._existing_shared_private_link_resource
            updated = instance.properties.shared_private_link_resource
            if existing is not None and updated is not None:
                for field, value in existing.items():
                    if not has_value(getattr(updated, field)):
                        if field == "private_link":
                            updated.private_link.id = value.get("id")
                        else:
                            setattr(updated, field, value)


class AFDRouteCreate(_AFDRouteCreate):
    def pre_operations(self):
        _normalize_origin_group_id(self)


class AFDRouteUpdate(_AFDRouteUpdate):
    def pre_operations(self):
        _normalize_origin_group_id(self)


class AFDEndpointCreate(_AFDEndpointCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.location._registered = False
        return args_schema

    def pre_operations(self):
        self.ctx.args.location = 'global'


class AFDEndpointUpdate(_AFDEndpointUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name_reuse_scope._registered = False
        return args_schema
