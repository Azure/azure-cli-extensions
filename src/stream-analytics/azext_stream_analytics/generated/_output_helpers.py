# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Translate legacy output REST payloads into flattened AAZ command args."""

from ._input_helpers import _normalize_key, _snake_keys


_NESTED_DATASOURCES = {
    "microsoft_event_hub_event_hub",
    "microsoft_service_bus_event_hub",
}


def output_data_to_args(datasource=None, serialization=None):
    args = {}
    if datasource:
        datasource_key = _normalize_key(datasource.get('type', ''))
        datasource_properties = _snake_keys(datasource.get('properties', {}) or {})
        if datasource_key in _NESTED_DATASOURCES:
            datasource_properties = {'properties': datasource_properties}
        args['datasource'] = {datasource_key: datasource_properties}
    if serialization:
        serialization_key = _normalize_key(serialization.get('type', ''))
        args['serialization'] = {
            serialization_key: _snake_keys(serialization.get('properties', {}) or {})
        }
    return args
