# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Helpers to translate the legacy `--properties` REST blob of a Stream Analytics
input into the flattened AAZ command args, preserving the CLI interface."""

import re

# Datasource types whose request args keep a nested "properties" object
# (all other types hoist their inner properties directly onto the datasource).
_NESTED_DATASOURCES = {
    "raw",
    "microsoft_event_hub_event_hub",
    "microsoft_service_bus_event_hub",
}


def _camel_to_snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def _normalize_key(type_name):
    return '_'.join(_camel_to_snake(part) for part in re.split(r'[./]', type_name))


def _snake_keys(obj):
    if isinstance(obj, dict):
        return {_camel_to_snake(k): _snake_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_snake_keys(v) for v in obj]
    return obj


def input_properties_to_args(properties):
    if not properties:
        return {}
    args = {}
    datasource = properties.get('datasource')
    if datasource:
        ds_key = _normalize_key(datasource.get('type', ''))
        ds_props = _snake_keys(datasource.get('properties', {}) or {})
        ds_value = {ds_key: {'properties': ds_props} if ds_key in _NESTED_DATASOURCES else ds_props}
        top = 'reference' if properties.get('type') == 'Reference' else 'stream'
        args[top] = {'datasource': ds_value}
    serialization = properties.get('serialization')
    if serialization:
        ser_key = _normalize_key(serialization.get('type', ''))
        args['serialization'] = {ser_key: _snake_keys(serialization.get('properties', {}) or {})}
    if properties.get('compression'):
        args['compression'] = _snake_keys(properties['compression'])
    if properties.get('partitionKey') is not None:
        args['partition_key'] = properties['partitionKey']
    if properties.get('watermarkSettings'):
        args['watermark_settings'] = _snake_keys(properties['watermarkSettings'])
    return args
