# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access

import argparse

from azure.cli.core.aaz import AAZStrArg, AAZBoolArg, AAZListArg
from azure.cli.core.aaz._base import has_value
from knack.util import CLIError

from azext_cdn.vendored_sdks.models import ResourceType
from azext_cdn.aaz.latest.afd.profile import Show as _AFDProfileShow, \
    Create as _AFDProfileCreate, Update as _AFDProfileUpdate, Delete as _AFDProfileDelete, \
    List as _AFDProfileList
from azext_cdn.aaz.latest.cdn._name_exists import NameExists
from azext_cdn.aaz.latest.cdn.origin import Create as _CDNOriginCreate, Update as _CDNOriginUpdate
from azext_cdn.aaz.latest.cdn.endpoint import Create as _CDNEndpointCreate, \
    Update as _CDNEndpointUpdate, Show as _CDNEndpointShow


def default_content_types():
    return ["text/plain",
            "text/html",
            "text/css",
            "text/javascript",
            "application/x-javascript",
            "application/javascript",
            "application/json",
            "application/xml"]


class NameExistsWithType(NameExists):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema

    def pre_operations(self):
        self.ctx.args.type = ResourceType.MICROSOFT_CDN_PROFILES_ENDPOINTS.value


class CDNProfileList(_AFDProfileList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema


class CDNProfileShow(_AFDProfileShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema


class CDNProfileCreate(_AFDProfileCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.location._registered = False
        return args_schema

    def pre_operations(self):
        self.ctx.args.location = 'global'


class CDNProfileUpdate(_AFDProfileUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.sku._registered = False
        return args_schema


class CDNProfileDelete(_AFDProfileDelete):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return args_schema


class CDNOriginCreate(_CDNOriginCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.disabled = AAZBoolArg(
            options=['--disabled'],
            help='Don\'t use the origin for load balancing.',
            blank=True
        )
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.disabled):
            args.disabled = False
        args.enabled = not args.disabled
        if not has_value(args.http_port):
            args.http_port = 80
        if not has_value(args.https_port):
            args.https_port = 443
        if not has_value(args.priority):
            args.priority = 1
        elif int(args.priority.to_serialized_data()) < 1 or int(args.priority.to_serialized_data()) > 1000:
            raise CLIError('Priority must be between 1 and 1000')
        if not has_value(args.weight):
            args.weight = 1000


class CDNOriginUpdate(_CDNOriginUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.disabled = AAZBoolArg(
            options=['--disabled'],
            help='Don\'t use the origin for load balancing.',
            blank=True
        )
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.disabled):
            args.disabled = False
        args.enabled = not args.disabled


class CDNEndpointCreate(_CDNEndpointCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.origin = AAZListArg(
            options=['--origin'],
            help='Endpoint origin specified by the following space-delimited 7 tuple: '
            'www.example.com http_port https_port private_link_resource_id '
            'private_link_location private_link_approval_message origin_name. '
            'The HTTP and HTTPS ports and the private link resource ID and location are optional. '
            'The HTTP and HTTPS ports default to 80 and 443, respectively. '
            'Private link fields are only valid for the sku Standard_Microsoft, '
            'and private_link_location is required if private_link_resource_id is set. '
            'the origin name is optional and defaults to origin.',
            required=True,
        )
        args_schema.origin.Element = AAZStrArg()
        args_schema.no_http = AAZBoolArg(
            options=['--no-http'],
            help='Disable HTTP traffic.Indicates whether HTTP traffic is not allowed on the endpoint. '
            'Default is to allow HTTP traffic.',
            blank=True
        )
        args_schema.no_https = AAZBoolArg(
            options=['--no-https'],
            help='Indicates whether HTTPS traffic is not allowed on the endpoint. '
            'Default is to allow HTTPS traffic.',
            blank=True
        )
        args_schema.enable_compression = AAZBoolArg(
            options=['--enable-compression'],
            help='If compression is enabled, content will be served as compressed '
            'if user requests for a compressed version. '
            'Content won\'t be compressed on CDN when requested content is smaller than 1 byte or larger than 1 MB.',
            blank=True
        )
        args_schema.origins._registered = False
        args_schema.is_http_allowed._registered = False
        args_schema.is_https_allowed._registered = False
        args_schema.is_compression_enabled._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args

        if not 1 <= len(args.origin) <= 3 and not 5 <= len(args.origin) <= 6:
            msg = '%s takes 1, 2, 3, 5, or 6 values, %d given'
            raise argparse.ArgumentError(self, msg % (len(args.origin)))

        host_name = args.origin[0]
        http_port = 80
        https_port = 443
        private_link_resource_id = None
        private_link_location = None
        private_link_approval_message = None
        origin_name = host_name.to_serialized_data().replace('.', '-')

        if len(args.origin) > 1:
            http_port = int(args.origin[1].to_serialized_data())
        if len(args.origin) > 2:
            https_port = int(args.origin[2].to_serialized_data())
        if len(args.origin) > 4:
            private_link_resource_id = args.origin[3]
            private_link_location = args.origin[4]
        if len(args.origin) > 5:
            private_link_approval_message = args.origin[5]
        if len(args.origin) > 6:
            origin_name = args.origin[6]

        if http_port < 1 or http_port > 65535 or https_port < 1 or https_port > 65535:
            raise CLIError('Port number must be between 1 and 65535')

        args.origins = [{
            'name': origin_name,
            'host_name': host_name,
            'http_port': http_port,
            'https_port': https_port,
            'private_link_resource_id': private_link_resource_id,
            'private_link_location': private_link_location,
            'private_link_approval_message': private_link_approval_message
        }]

        if has_value(args.enable_compression):
            args.is_compression_enabled = args.enable_compression
        if has_value(args.no_http):
            args.is_http_allowed = not args.no_http
        if has_value(args.no_https):
            args.is_https_allowed = not args.no_https
        if args.enable_compression.to_serialized_data() and not has_value(args.content_types_to_compress):
            args.content_types_to_compress = default_content_types()


class CDNEndpointUpdate(_CDNEndpointUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.no_http = AAZBoolArg(
            options=['--no-http'],
            help='Disable HTTP traffic.Indicates whether HTTP traffic is not allowed on the endpoint. '
            'Default is to allow HTTP traffic.',
            blank=True
        )
        args_schema.no_https = AAZBoolArg(
            options=['--no-https'],
            help='Indicates whether HTTPS traffic is not allowed on the endpoint. '
            'Default is to allow HTTPS traffic.',
            blank=True
        )
        args_schema.enable_compression = AAZBoolArg(
            options=['--enable-compression'],
            help='If compression is enabled, content will be served as compressed '
            'if user requests for a compressed version. '
            'Content won\'t be compressed on CDN when requested content is smaller than 1 byte or larger than 1 MB.',
            blank=True
        )
        args_schema.is_http_allowed._registered = False
        args_schema.is_https_allowed._registered = False
        args_schema.is_compression_enabled._registered = False
        args_schema.query_string_caching_behavior._default = None
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        existing = _CDNEndpointShow(cli_ctx=self.cli_ctx)(command_args={
            'resource_group': args.resource_group,
            'profile_name': args.profile_name,
            'endpoint_name': args.endpoint_name
        })
        if has_value(args.default_origin_group):
            if '/' not in args.default_origin_group.to_serialized_data():
                args.default_origin_group = f'/subscriptions/{self.ctx.subscription_id}' \
                                            f'/resourceGroups/{args.resource_group}' \
                                            f'/providers/Microsoft.Cdn/profiles/{args.profile_name}' \
                                            f'/endpoints/{args.endpoint_name}' \
                                            f'/originGroups/{args.default_origin_group}'
        if has_value(args.enable_compression):
            args.is_compression_enabled = args.enable_compression
        if not has_value(args.enable_compression):
            args.is_compression_enabled = existing['isCompressionEnabled']
        if args.is_compression_enabled.to_serialized_data() and not has_value(args.content_types_to_compress):
            args.content_types_to_compress = existing['contentTypesToCompress']
            if not has_value(args.content_types_to_compress) is None:
                args.content_types_to_compress = default_content_types()
        if has_value(args.no_http):
            args.is_http_allowed = not args.no_http
        if has_value(args.no_https):
            args.is_https_allowed = not args.no_https
