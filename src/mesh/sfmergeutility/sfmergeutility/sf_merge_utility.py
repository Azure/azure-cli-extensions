# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import os
import re
import yaml  # pylint: disable=import-error
from sfmergeutility.constants import Constants
from sfmergeutility.schema import Schema
from sfmergeutility.sf_yaml_merge import YamlMerge, PartialDocument
from sfmergeutility.sf_yaml_to_json import YamlToJson
from sfmergeutility.arm_document_generator import ArmDocumentGenerator

# pylint: disable=line-too-long


class SFMergeUtility(object):

    resourceCreationOrder = [
        Constants.Secret,
        Constants.SecretValue,
        Constants.Volume,
        Constants.Network,
        Constants.Gateway,
        Constants.Application
    ]

    @staticmethod
    def sf_merge_utility(input_list, output_format, parameter_file=None, output_dir=None, prefix="merged-", region="westus"):
        """Method which is the main interface to the utility, merges yaml files
           into given output_format
        """

        if(not output_dir or not output_dir.strip()):
            output_dir = os.getcwd()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Read the settings.json file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        settings_file = os.path.join(dir_path, "settings.json")
        primitives_list = {}
        with open(settings_file) as fp_settings:
            settings_data = json.load(fp_settings, encoding='utf-8')
            primitives_list = settings_data.get("primitiveProperties")

        merged_resource_documents = SFMergeUtility.load_and_merge_partial_documents(input_list)
        # read parametes file and replace params
        parameters = SFMergeUtility.get_parameters(parameter_file)
        if parameters and parameters.keys:
            for merged_resource_doc in merged_resource_documents:
                merged_resource_documents[merged_resource_doc] = SFMergeUtility.replace_parameter_values(merged_resource_documents[merged_resource_doc], parameters)

        if output_format.upper() == "SF_SBZ_YAML":
            # for mode generate yaml
            SFMergeUtility.save_all_merged_documents(merged_resource_documents, prefix, output_dir, "yaml", None)
        elif output_format.upper() == "SF_SBZ_JSON":
            # for mode generate JSON
            # call yaml to json
            SFMergeUtility.save_all_merged_documents(merged_resource_documents, prefix, output_dir, "json", primitives_list)
        elif output_format.upper() == "SF_SBZ_RP_JSON":
            # for mode generate ARMDocument
            # call arm document generator
            merged_jsons = {}
            for resource_iter in merged_resource_documents:
                resource_json = YamlToJson.to_ordered_dict(merged_resource_documents[resource_iter], None, primitives_list)
                merged_jsons[resource_iter] = resource_json

            ArmDocumentGenerator.generate(merged_jsons, region, os.path.join(output_dir, prefix + "arm_rp.json"))

    @staticmethod
    def get_parameters(parameter_file):
        """Get Parameters from the parameter_file if passed"""
        params_list = None
        json_object = None
        if parameter_file:
            extension = os.path.splitext(parameter_file)[1]
            if extension.lower() == ".yaml":
                # load yaml
                yaml_file = yaml.compose(open(parameter_file))
                json_object = YamlToJson.to_ordered_dict(yaml_file, None, None)
            elif extension.lower() == ".json":
                # load json
                with open(parameter_file, 'r') as parameter_file_fp:
                    json_object = json.load(parameter_file_fp)

            params_list = {}
            for obj in json_object['parameters']:
                params_list[obj] = json_object['parameters'][obj]['value']

        return params_list

    @staticmethod
    def replace_parameter_values(merged_resource_documents, parameters_to_replace):
        """Replace parameter values with values in parameters_to_replace"""
        yaml_string = yaml.serialize(merged_resource_documents)

        for parameter_iter in parameters_to_replace:
            if yaml_string.find("'[parameters(''{0}'')]'".format(parameter_iter)) >= 0:
                yaml_string = yaml_string.replace("'[parameters(''{0}'')]'".format(parameter_iter), parameters_to_replace[parameter_iter])

        yaml_dict = yaml.compose(yaml_string)
        return yaml_dict

    @staticmethod
    def save_merged_documents_as_yaml(merged_document, output_dir, file_name):
        """Save merged dcouments as yaml into the provided output_dir"""
        final_yaml = yaml.serialize(merged_document)
        output_file_path = os.path.join(output_dir, file_name + ".yaml")
        with open(output_file_path, 'w+') as f:
            f.write(final_yaml)

    @staticmethod
    def save_merged_documents_as_json(merged_document, kind, output_dir, file_name, primitives_list):
        """Save merged documents as json into the provided output_dir"""
        final_json = YamlToJson.to_json(merged_document, kind, primitives_list)
        output_file_path = os.path.join(output_dir, file_name + ".json")
        with open(output_file_path, 'w+') as f:
            f.write(final_json)

    @staticmethod
    def save_all_merged_documents(resource_merged_document_map, file_name_prefix, output_dir, yaml_json_switch, primitives_list):
        """Group all documents into their kinds, and merge into complete yaml/json files"""
        count = 1
        for kind in SFMergeUtility.resourceCreationOrder:
            # Group documents by kind
            docs = [key for key in resource_merged_document_map if key[0] == kind]
            for doc in docs:
                root_mapping_node = resource_merged_document_map[doc]
                # Root node is wrapped in arr, hence extracting along with key and value
                key_node = root_mapping_node.value[0][0]
                value_node = root_mapping_node.value[0][1]
                selected_name_node = YamlMerge.get_child_node(value_node, Constants.PrimaryPropertyName)
                selected_schema_version_node = YamlMerge.get_child_node(value_node, Constants.SchemaVersion)
                resource_kind = key_node.value
                resource_name = selected_name_node.value
                schema_version = selected_schema_version_node.value

                fully_qualified_resource_name = resource_name

                if Constants.FullyQualifiedResourceNameSeparator in resource_name:
                    resource_name = resource_name[(resource_name.index(Constants.FullyQualifiedResourceNameSeparator) + 1):]

                selected_name_node.value = resource_name

                file_name = "%s%s_%s_%s" % (file_name_prefix, str(count).zfill(4), resource_kind, fully_qualified_resource_name)
                file_name = re.sub(r'[^\w\-_\. ]', '_', file_name)
                file_name = re.sub(r'/', '_', file_name)

                root_n = yaml.MappingNode(YamlMerge.TAG_MAP, [])
                root_n.value.append((yaml.ScalarNode(YamlMerge.TAG_STR, 'type'), yaml.ScalarNode(YamlMerge.TAG_STR, resource_kind)))
                root_n.value.append((yaml.ScalarNode(YamlMerge.TAG_STR, 'name'), yaml.ScalarNode(YamlMerge.TAG_STR, resource_name)))
                root_n.value.append((yaml.ScalarNode(YamlMerge.TAG_STR, 'api-version'), yaml.ScalarNode(YamlMerge.TAG_STR, Schema.SchemaVersionFabricApiVersionMap[schema_version])))
                root_n.value.append((yaml.ScalarNode(YamlMerge.TAG_STR, 'fullyQualifiedResourceName'), yaml.ScalarNode(YamlMerge.TAG_STR, fully_qualified_resource_name)))
                root_n.value.append((yaml.ScalarNode(YamlMerge.TAG_STR, 'description'), root_mapping_node))

                if yaml_json_switch == 'yaml':
                    SFMergeUtility.save_merged_documents_as_yaml(root_n, output_dir, file_name)
                elif yaml_json_switch == 'json':
                    SFMergeUtility.save_merged_documents_as_json(root_n, resource_kind, output_dir, file_name, primitives_list)

                count += 1

    @staticmethod
    def load_and_merge_partial_documents(input_list):
        """Classify input yamls into their kinds and package into resource_document_map"""
        # load all yamls inputs
        partial_resource_document_map = {}
        for input_file in input_list:
            with open(input_file) as input_file_handle:
                my_dict = yaml.load(input_file_handle)

            with open(input_file) as input_file_handle:
                mapping_node = yaml.compose(input_file_handle)

            kind = list(my_dict.keys())[0]
            name = my_dict.get(kind).get(Constants.PrimaryPropertyName)
            key = (kind, name)

            yaml_document = PartialDocument(mapping_node, input_file)

            # create a map inputs, group by kind and name
            if key in partial_resource_document_map:
                partial_resource_document_map[key].append(yaml_document)
            else:
                temp_list = []
                temp_list.append(yaml_document)
                partial_resource_document_map[key] = temp_list

        merged_document_map = {}
        for key in partial_resource_document_map:
            merged_document = YamlMerge.Merge(partial_resource_document_map[key], key[0], Constants.PrimaryPropertyName)
            merged_document_map[key] = merged_document

        return merged_document_map
