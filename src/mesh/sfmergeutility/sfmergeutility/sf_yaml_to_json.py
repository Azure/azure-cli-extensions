# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import re
from collections import OrderedDict
import yaml  # pylint: disable=import-error


class YamlToJson(object):

    @staticmethod
    def to_ordered_dict(yaml_node, output_property_filter, primitive_properties):
        ordered_dict = YamlToJson.serialize(yaml_node)

        if primitive_properties:
            YamlToJson.fix_properties(ordered_dict, primitive_properties)

        if output_property_filter:
            desc_node = ordered_dict['description']
            for node in desc_node:
                if node == output_property_filter:
                    ordered_dict['description'] = desc_node[node]
                    break

        return ordered_dict

    @staticmethod
    def to_json(yaml_node, output_property_filter, primitive_properties):
        ordered_dict = YamlToJson.to_ordered_dict(yaml_node, output_property_filter, primitive_properties)

        return json.dumps(ordered_dict, indent=4)

    @staticmethod
    def serialize(yaml_node):

        if isinstance(yaml_node, yaml.MappingNode):
            writer_dict = OrderedDict()
            writer_dict = YamlToJson.serialize_mapping_node(yaml_node)
            return writer_dict
        elif isinstance(yaml_node, yaml.SequenceNode):
            writer_dict = OrderedDict()
            writer_dict = YamlToJson.serialize_sequence_node(yaml_node)
            return writer_dict
        elif isinstance(yaml_node, yaml.ScalarNode):
            return YamlToJson.serialize_scalar_node(yaml_node)
        return None

    @staticmethod
    def serialize_mapping_node(yaml_node):
        writer_dict = OrderedDict()

        for yaml_node_val in yaml_node.value:
            writer_dict[yaml_node_val[0].value] = YamlToJson.serialize(yaml_node_val[1])

        return writer_dict

    @staticmethod
    def serialize_sequence_node(yaml_node):
        writer_dict = []

        for yaml_node_val in yaml_node.value:
            writer_dict.append(YamlToJson.serialize(yaml_node_val))

        return writer_dict

    @staticmethod
    def serialize_scalar_node(yaml_node):
        return yaml_node.value

    @staticmethod
    def fix_properties(json_dict, primitive_properties):
        for primitive_property in primitive_properties:
            path_components = list(filter(None, re.split("[\\/]+", primitive_property['path'])))
            if path_components:
                YamlToJson.find_root_and_fix_property(json_dict, path_components, primitive_property['type'], 0)

    @staticmethod
    def find_root_and_fix_property(json_dict, path_components, primitive_type, level):
        path_head = path_components[0]
        if isinstance(json_dict, list):
            for k in json_dict:
                YamlToJson.find_root_and_fix_property(k, path_components, primitive_type, level)
        elif isinstance(json_dict, OrderedDict):
            for k in json_dict:
                if k == path_head:
                    # root path_head
                    YamlToJson.fix_property(json_dict, path_components, primitive_type, level)
                else:
                    YamlToJson.find_root_and_fix_property(json_dict[k], path_components, primitive_type, level)

    @staticmethod
    def fix_property(json_dict, path_components, primitive_type, level):
        remaining = len(path_components) - level
        if remaining == 0:
            return
        elif remaining == 1:
            YamlToJson.fix_property_at_leaf(json_dict, path_components[level], primitive_type)
        else:
            if isinstance(json_dict, list):
                for k in json_dict:
                    YamlToJson.fix_property(k, path_components, primitive_type, level)
            elif isinstance(json_dict, OrderedDict):
                for k in json_dict:
                    path_component = path_components[level]
                    if k == path_component:
                        YamlToJson.fix_property(json_dict[k], path_components, primitive_type, level + 1)

    @staticmethod
    def fix_property_at_leaf(json_dict, property_name, primitive_type):
        if isinstance(json_dict, list):
            for n in json_dict:
                YamlToJson.fix_property_at_leaf(n, property_name, primitive_type)
        for k in json_dict:
            if k == property_name:
                if primitive_type == 'Integer':
                    json_dict[k] = int(json_dict[k])
                elif primitive_type == 'Boolean':
                    json_dict[k] = (json_dict[k] == 'true' or json_dict[k] == 'True')
                elif primitive_type == 'Double':
                    json_dict[k] = float(json_dict[k])
                break