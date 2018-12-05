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
        """Convert yaml_node to ordered_dict to easily access data"""
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
        """Convert yaml_node to equivalent json"""
        ordered_dict = YamlToJson.to_ordered_dict(yaml_node, output_property_filter, primitive_properties)

        return json.dumps(ordered_dict, indent=4)

    @staticmethod
    def serialize(yaml_node):
        """Serialize yaml_node by traversal and storing data in ordered_dict"""
        if isinstance(yaml_node, yaml.MappingNode):
            yaml_data_store = OrderedDict()
            yaml_data_store = YamlToJson.serialize_mapping_node(yaml_node)
            return yaml_data_store
        elif isinstance(yaml_node, yaml.SequenceNode):
            yaml_data_store = OrderedDict()
            yaml_data_store = YamlToJson.serialize_sequence_node(yaml_node)
            return yaml_data_store
        elif isinstance(yaml_node, yaml.ScalarNode):
            return YamlToJson.serialize_scalar_node(yaml_node)
        return None

    @staticmethod
    def serialize_mapping_node(yaml_node):
        """Serialize yaml mapping node which contains key node and value node"""
        yaml_data_store = OrderedDict()

        # Serialize recursively the value node and
        # store data with key as value of key node
        for yaml_node_val in yaml_node.value:
            yaml_data_store[yaml_node_val[0].value] = YamlToJson.serialize(yaml_node_val[1])

        return yaml_data_store

    @staticmethod
    def serialize_sequence_node(yaml_node):
        """Serialize yaml sequence node which has many yaml_nodes in a sequence"""
        yaml_data_store = []

        # Serialize recursively all children
        # of sequence node and store in list
        for yaml_node_val in yaml_node.value:
            yaml_data_store.append(YamlToJson.serialize(yaml_node_val))

        return yaml_data_store

    @staticmethod
    def serialize_scalar_node(yaml_node):
        """Serialize yaml scalar node by returning its' value"""
        return yaml_node.value

    @staticmethod
    def fix_properties(nodes_data_store, primitive_properties):
        """Fix properties of yaml contents by their type in json"""
        for primitive_property in primitive_properties:
            path_components = list(filter(None, re.split("[\\/]+", primitive_property['path'])))
            if path_components:
                YamlToJson.find_root_and_fix_property(nodes_data_store, path_components, primitive_property['type'], 0)

    @staticmethod
    def find_root_and_fix_property(nodes_data_store, path_components, primitive_type, level):
        """Find the root of the path in path_components to find property to fix"""
        path_head = path_components[0]
        if isinstance(nodes_data_store, list):
            for node in nodes_data_store:
                YamlToJson.find_root_and_fix_property(node, path_components, primitive_type, level)
        elif isinstance(nodes_data_store, OrderedDict):
            for node in nodes_data_store:
                if node == path_head:
                    # root path_head
                    YamlToJson.fix_property(nodes_data_store, path_components, primitive_type, level)
                else:
                    YamlToJson.find_root_and_fix_property(nodes_data_store[node], path_components,
                                                          primitive_type, level)

    @staticmethod
    def fix_property(nodes_data_store, path_components, primitive_type, level):
        """Fix the property of the node in the path as defined in path_components"""
        remaining = len(path_components) - level
        if remaining == 0:
            return
        elif remaining == 1:
            YamlToJson.fix_property_at_leaf(nodes_data_store, path_components[level], primitive_type)
        else:
            if isinstance(nodes_data_store, list):
                for node in nodes_data_store:
                    YamlToJson.fix_property(node, path_components, primitive_type, level)
            elif isinstance(nodes_data_store, OrderedDict):
                for node in nodes_data_store:
                    path_component = path_components[level]
                    if node == path_component:
                        YamlToJson.fix_property(nodes_data_store[node], path_components, primitive_type, level + 1)

    @staticmethod
    def fix_property_at_leaf(nodes_data_store, property_name, primitive_type):
        """Fix the property as found in traversal at the leaf by casting to specified primitive_type"""
        if isinstance(nodes_data_store, list):
            for node in nodes_data_store:
                YamlToJson.fix_property_at_leaf(node, property_name, primitive_type)
        for node in nodes_data_store:
            if node == property_name:
                if primitive_type == 'Integer':
                    nodes_data_store[node] = int(nodes_data_store[node])
                elif primitive_type == 'Boolean':
                    nodes_data_store[node] = (nodes_data_store[node] == 'true' or nodes_data_store[node] == 'True')
                elif primitive_type == 'Double':
                    nodes_data_store[node] = float(nodes_data_store[node])
                break
