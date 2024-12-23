# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import

import json

from azure.cli.core.aaz import AAZFileArg, AAZObjectArg, AAZStrArg, has_value
from azure.cli.core.util import CLIError
from azure.cli.core.azclierror import ArgumentUsageError

from .aaz.latest.portal.dashboard import Create as _Create
from .aaz.latest.portal.dashboard import Update as _Update


def _parse_properties(self):
    args = self.ctx.args
    property_err = "Usage error: Provide either --input-path, or --lenses with --metadata."
    if not has_value(args.input_path) and not has_value(args.lenses) and not has_value(args.metadata):
        raise ArgumentUsageError(property_err)
    if has_value(args.input_path) and (has_value(args.lenses) or has_value(args.metadata)):
        raise ArgumentUsageError(property_err)

    if has_value(args.input_path):
        try:
            properties = json.loads(args.input_path.to_serialized_data())
        except json.decoder.JSONDecodeError as ex:
            raise CLIError(
                'JSON decode error: {}'.format(str(ex)))
        if 'lenses' not in properties:
            raise CLIError("Failed to parse 'lenses' from property.")
        args.lenses = properties['lenses']
        if 'metadata' not in properties:
            raise CLIError("Failed to parse 'metadata' from property.")
        args.metadata = properties['metadata']

def _parse_dashboard_json(self):
    args = self.ctx.args
    try:
        dashboard = json.loads(args.input_path.to_serialized_data())
    except json.decoder.JSONDecodeError as ex:
        raise CLIError(
            'JSON decode error: {}'.format(str(ex)))
    if 'location' not in dashboard:
        raise CLIError("Input file does not contain the property 'location'")
    if 'properties' not in dashboard:
        raise CLIError("Input file does not contain the property 'properties'")
    if 'lenses' not in dashboard['properties']:
        raise CLIError("Input file does not contain the property 'lenses' in 'properties'")
    if 'metadata' not in dashboard['properties']:
        raise CLIError("Input file does not contain the property 'metadata' in 'properties'")
    args.location = dashboard['location']
    args.lenses = dashboard['properties']['lenses']
    args.metadata = dashboard['properties']['metadata']


class Create(_Create):
    
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.input_path = AAZFileArg(
            options=['--input-path'],
            arg_group="Properties",
            help='The path to the dashboard properties JSON file. If provided, no other Properties arguments should be specified.'
        )
        return args_schema

    def pre_operations(self):
        _parse_properties(self)


class Update(_Update):
    
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.input_path = AAZFileArg(
            options=['--input-path'],
            arg_group="Properties",
            help='The path to the dashboard properties JSON file. If provided, no other Properties arguments should be specified.'
        )

        return args_schema

    def pre_operations(self):
        _parse_properties(self)


class Import(_Create):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.input_path = AAZFileArg(
            options=['--input-path'],
            arg_group="Properties",
            help='The path to the dashboard properties JSON file. If provided, no other Properties arguments should be specified.'
        )
        args_schema.lenses._registered = False
        args_schema.metadata._registered = False
        args_schema.location._registered = False

        return args_schema
    
    def pre_operations(self):
        _parse_dashboard_json(self)