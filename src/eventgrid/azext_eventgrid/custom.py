# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines

from azure.cli.core.aaz import has_value
from azext_eventgrid.aaz.latest.eventgrid.namespace import ListKey as _NamespaceListKey, RegenerateKey as _NamespaceRegenerateKey
from azext_eventgrid.aaz.latest.eventgrid.namespace.ca_certificate import Create as _CaCertificateCreate, Update as _CaCertificateUpdate


class NamespaceListKey(_NamespaceListKey):
    def _output(self, *args, **kwargs):
        return self.deserialize_output(self.ctx.vars.instance.to_serialized_data(), client_flatten=True)


class NamespaceRegenerateKey(_NamespaceRegenerateKey):
    def _output(self, *args, **kwargs):
        return self.deserialize_output(self.ctx.vars.instance.to_serialized_data(), client_flatten=True)


class CaCertificateCreate(_CaCertificateCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZFileArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.certificate = AAZFileArg(
            options=["--certificate"],
            help="Path to the base64 encoded PEM (Privacy Enhanced Mail) format certificate data file.",
        )
        args_schema.encoded_certificate._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.certificate):
            args.encoded_certificate = args.certificate


class CaCertificateUpdate(_CaCertificateUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZFileArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.certificate = AAZFileArg(
            options=["--certificate"],
            help="Path to the base64 encoded PEM (Privacy Enhanced Mail) format certificate data file.",
        )
        args_schema.encoded_certificate._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.certificate):
            args.encoded_certificate = args.certificate
