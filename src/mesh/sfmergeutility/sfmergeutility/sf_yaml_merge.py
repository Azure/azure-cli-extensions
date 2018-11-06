# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import yaml  # pylint: disable=import-error


class ArgumentException(Exception):
    def __init__(self, expression, message):
        super(ArgumentException, self).__init__(message)
        self.expression = expression
        self.message = message


class PartialDocument(object):  # pylint: disable=too-few-public-methods
    def __init__(self, document, name):
        self.document = document
        self.name = name


class PartialYamlObject(object):  # pylint: disable=too-few-public-methods
    def __init__(self, name, node):
        self.name = name
        self.node = node


class YamlMerge(object):
    TAG_MAP = 'tag:yaml.org,2002:map'
    TAG_STR = 'tag:yaml.org,2002:str'
    TAG_SEQ = 'tag:yaml.org,2002:seq'
    YAML_ERR_DOCUMENT_NO_OBJECT = 'Document does not contain object'
    YAML_ERR_OBJECT_PRIMARY_KEY_NOT_SCALAR = 'Object primary key passed is not a scalar node'
    YAML_ERR_OBJECT_DOES_NOT_HAVE_PRIMARY_KEY = 'Object does not have primary key associated'
    YAML_ERR_OBJECT_PRIMARY_KEY_DIFFERENT = 'Object primary keys are different'
    YAML_ERR_SRC_AND_DEST_NODE_DIFFERENT = 'Source and destination nodes are of different types'
    YAML_ERR_UNSUPPORTED_NODE_TYPE = 'Node type is not supported'

    @staticmethod
    def Merge(partial_documents, object_identifier, object_primary_key):
        """Merge partial_documents into a final merged root yaml node"""
        # Nothing to merge
        if not partial_documents:
            return None

        partial_nodes = []

        for doc in partial_documents:
            if isinstance(doc.document, yaml.MappingNode):
                if len(doc.document.value) != 1:
                    raise ArgumentException(YamlMerge.YAML_ERR_DOCUMENT_NO_OBJECT, doc.name)

                child_key_node, child_val_node = doc.document.value[0]

                if child_key_node.value != object_identifier and not isinstance(child_val_node, yaml.MappingNode):
                    raise ArgumentException(YamlMerge.YAML_ERR_DOCUMENT_NO_OBJECT, doc.name)

                partial_node = PartialYamlObject(doc.name, child_val_node)
                partial_nodes.append(partial_node)
            else:
                raise ArgumentException(YamlMerge.YAML_ERR_DOCUMENT_NO_OBJECT, doc.name)

        merged_node = YamlMerge.merge_partial_nodes(partial_nodes, object_primary_key)
        merged_root_node = yaml.MappingNode(YamlMerge.TAG_MAP,
                                            [(yaml.ScalarNode(YamlMerge.TAG_STR, object_identifier), merged_node)])

        return merged_root_node

    @staticmethod
    def ensure_same_object_primary_key(partial_nodes, object_primary_key):
        """Ensure that object primary key exists and is scalar and correct"""
        primary_key_value = None
        for partial_node in partial_nodes:
            key_found_flag = False
            for node_child_key, node_child_val in partial_node.node.value:
                if node_child_key.value == object_primary_key:
                    key_found_flag = True

                    if not isinstance(node_child_key, yaml.ScalarNode):
                        raise ArgumentException(YamlMerge.YAML_ERR_OBJECT_PRIMARY_KEY_NOT_SCALAR,
                                                partial_node.name)

                    if not primary_key_value:
                        primary_key_value = node_child_val.value
                    else:
                        if primary_key_value != node_child_val.value:
                            raise ArgumentException(YamlMerge.YAML_ERR_OBJECT_PRIMARY_KEY_DIFFERENT,
                                                    partial_node.name)

            if not key_found_flag:
                raise ArgumentException(YamlMerge.YAML_ERR_OBJECT_DOES_NOT_HAVE_PRIMARY_KEY,
                                        partial_node.name)

    @staticmethod
    def merge_partial_nodes(partial_nodes, object_primary_key):
        """Merge partial nodes into a final destination node"""
        if object_primary_key:
            YamlMerge.ensure_same_object_primary_key(partial_nodes, object_primary_key)
        dest_node = YamlMerge.create_dest_node(yaml.MappingNode('', None), "")
        for node in partial_nodes:
            YamlMerge.merge_mapping_nodes(dest_node, node.node, node.name, object_primary_key)
        return dest_node

    @staticmethod
    def get_child_node(parent, key):
        """Get the child node from a parent as addressed by the key"""
        for k, v in parent.value:
            if k.value == key:
                return v
        return None

    @staticmethod
    def get_child_from_seq_node(node, key):
        """Get the child node from a parent sequence node as addressed by the key"""
        for child_node in node.value:
            # if mapping node's scalar node's value is key
            if child_node.value[0].value == key:
                return child_node
        return None

    @staticmethod
    def merge_mapping_nodes(dest_node, src_node, src_identifier, object_primary_key):
        """"Merge destination and source mapping nodes"""
        dest_key_set = set(map(lambda x: x[0].value, dest_node.value))
        for key_node, val_node in src_node.value:
            if key_node.value not in dest_key_set:
                dest_child_node = YamlMerge.create_dest_node(val_node, src_identifier)
                dest_node.value.append((yaml.ScalarNode(YamlMerge.TAG_STR, key_node.value), dest_child_node))
            else:
                dest_child_node = YamlMerge.get_child_node(dest_node, key_node.value)
            YamlMerge.merge_nodes(dest_child_node, val_node, src_identifier, object_primary_key)

    @staticmethod
    def merge_nodes(dest, src, src_identifier, object_primary_key):
        """Merge nodes by first identifying the type and merging individual pairs"""
        dest_type = type(dest)
        src_type = type(src)
        if dest_type != src_type:
            raise ArgumentException(YamlMerge.YAML_ERR_SRC_AND_DEST_NODE_DIFFERENT,
                                    src_identifier)

        if isinstance(src, yaml.ScalarNode):
            YamlMerge.merge_scalar_nodes(dest, src)
        elif isinstance(src, yaml.SequenceNode):
            YamlMerge.merge_sequence_nodes(dest, src, src_identifier, object_primary_key)
        elif isinstance(src, yaml.MappingNode):
            YamlMerge.merge_mapping_nodes(dest, src, src_identifier, object_primary_key)
        else:
            raise ArgumentException(YamlMerge.YAML_ERR_UNSUPPORTED_NODE_TYPE,
                                    src_identifier)

    @staticmethod
    def merge_scalar_nodes(dest, src):
        """Merge scalar nodes"""
        dest.value = src.value

    @staticmethod
    def seq_node_contains(node, key):
        """Check if sequence node contains a certain key"""
        keys = set(map(lambda x: x.value[0].value, node.value))
        return key in keys

    @staticmethod
    def merge_sequence_nodes(dest, src, src_identifier, object_primary_key):
        """Merge destination and source sequence nodes"""
        if isinstance(src.value[0], yaml.MappingNode) and not object_primary_key:
            # add it to the list of mapping nodes
            for src_child_node in src.value:
                src_child_key = src_child_node.value
                if YamlMerge.seq_node_contains(dest, src_child_key):
                    dest_child_node = YamlMerge.create_dest_node(src_child_node, src_identifier)
                    dest.value.append(dest_child_node)
                else:
                    dest_child_node = YamlMerge.get_child_from_seq_node(dest, src_child_key)
                YamlMerge.merge_nodes(dest_child_node, src_child_node, src_identifier, object_primary_key)
        else:
            # just combine the sequence
            for src_child_node in src.value:
                dest_child_node = YamlMerge.create_dest_node(src_child_node, src_identifier)
                dest.value.append(dest_child_node)
                YamlMerge.merge_nodes(dest_child_node, src_child_node, src_identifier, object_primary_key)

    @staticmethod
    def create_dest_node(src_node, src_identifier):
        """Create a destination yaml node to merge source node in"""
        if isinstance(src_node, yaml.ScalarNode):
            return yaml.ScalarNode(YamlMerge.TAG_STR, '')
        elif isinstance(src_node, yaml.MappingNode):
            return yaml.MappingNode(YamlMerge.TAG_MAP, [])
        elif isinstance(src_node, yaml.SequenceNode):
            return yaml.SequenceNode(YamlMerge.TAG_SEQ, [])
        else:
            raise ArgumentException(YamlMerge.YAML_ERR_UNSUPPORTED_NODE_TYPE,
                                    src_identifier)
