# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import json
from collections import OrderedDict
from sfmergeutility.property_names import PropertyNames
from sfmergeutility.constants import Constants
from sfmergeutility.schema import Schema
from sfmergeutility.arm_parameter import ArmParameter

# pylint: disable=line-too-long


class ArmDocumentGenerator(object):

    @staticmethod
    def generate(sf_json_resources, region, output_file_name):
        """ Entry point to this class. This function constructs and writes the ARM template """
        with open(output_file_name, 'w') as fp:
            arm_dict = OrderedDict()
            parameter_info = OrderedDict()
            property_value_map = OrderedDict()
            arm_dict = ArmDocumentGenerator.begin_write_arm_document(arm_dict)
            parameter_info[PropertyNames.Location] = ArmDocumentGenerator.get_location_parameter(region)
            property_value_map[PropertyNames.Location] = "[" + PropertyNames.Parameters + \
                                                         "('" + PropertyNames.Location + "')]"
            arm_dict = ArmDocumentGenerator.write_parameters(arm_dict, parameter_info)
            outputs_list = []
            arm_dict = ArmDocumentGenerator.write_arm_resources(arm_dict, sf_json_resources, property_value_map, outputs_list)
            arm_dict = ArmDocumentGenerator.WriteArmOutputs(arm_dict, outputs_list)
            arm_doc_string = ArmDocumentGenerator.end_write_arm_document(arm_dict)
            fp.write(arm_doc_string)

    @staticmethod
    def begin_write_arm_document(writer):
        """ Adds the ARM schema and content version to the writer """
        writer[PropertyNames.Schema] = Constants.ArmSchemaVersion
        writer[PropertyNames.ContentVersion] = Constants.ContentVersion
        return writer

    @staticmethod
    def end_write_arm_document(writer):
        """ Converts the dictionary to writer"""
        return json.dumps(writer, indent=4)

    @staticmethod
    def write_parameters(writer, parameters_info):
        """ Adds the parameter section of the ARM template to the writer """
        if PropertyNames.Parameters not in writer:
            writer[PropertyNames.Parameters] = OrderedDict()
        for parameter in parameters_info.keys():
            writer[PropertyNames.Parameters][parameter] = parameters_info[parameter].to_dict()
        return writer

    @staticmethod
    def WriteArmOutputs(writer, outputs_list):
        writer[PropertyNames.Outputs] = OrderedDict()
        if len(outputs_list) > 0:
            writer[PropertyNames.Outputs][PropertyNames.PublicIPAddress] = OrderedDict()
            writer[PropertyNames.Outputs][PropertyNames.PublicIPAddress]["value"] = outputs_list.pop()
            writer[PropertyNames.Outputs][PropertyNames.PublicIPAddress]["type"] = "string"

        return writer

    @staticmethod
    def write_arm_resources(writer, sf_json_resources, property_value_map, outputs_list):
        """ Writes all the provided resources one by one in ARM format to the writer """
        dependencies = ArmDocumentGenerator.get_dependencies(sf_json_resources)
        for sf_json_resource_iter in sf_json_resources:
            sf_resource = sf_json_resources[sf_json_resource_iter]
            kind = sf_json_resource_iter[0]
            description = sf_resource.get(kind)
            # Process resources specifically which need a specific handling of properties or resource references, all others use the generic method.
            if kind == Constants.Application:
                writer = ArmDocumentGenerator.process_application(writer, description, dependencies, property_value_map)
            elif kind == Constants.Gateway:
                writer = ArmDocumentGenerator.process_sf_resource(writer, description, kind, dependencies,
                                                                  property_value_map, ArmDocumentGenerator.process_resource_refs_for_gateway, outputs_list)
            else:
                writer = ArmDocumentGenerator.process_sf_resource(writer, description, kind,
                                                                  dependencies, property_value_map, ArmDocumentGenerator.process_resource_refs, outputs_list)
        return writer

    @staticmethod
    def get_location_parameter(region):
        """ Returns a ARM parameter object based on the region provided """
        return ArmParameter(region, "String", "Location of the resources.")

    @staticmethod
    def get_dependencies(sf_json_resources):  # pylint: disable=too-many-branches
        """ Constructs the dependencies section for every resource based on the provided resources """
        dependencies = OrderedDict()
        resource_types = OrderedDict()
        for sf_json_resource in sf_json_resources:
            name = sf_json_resource[1]
            kind = sf_json_resource[0]
            resource = sf_json_resources[sf_json_resource]
            schemaversion = Constants.DefaultSchemaVersion
            for prop, value in resource.items():
                if prop == PropertyNames.SchemaVersion:
                    schemaversion = value
                elif prop == PropertyNames.Name:
                    name = value

            if name == "" or kind == "":
                raise ValueError("Required properties name or kind missing")

            if kind in resource_types:
                resource_types[kind].append(ArmDocumentGenerator.get_sbz_resource_name(ArmDocumentGenerator.get_sbz_resource_type(kind, schemaversion), name))
            else:
                resource_types[kind] = [ArmDocumentGenerator.get_sbz_resource_name(ArmDocumentGenerator.get_sbz_resource_type(kind, schemaversion), name)]

        applications = resource_types.get(Constants.Application, [])
        networks = resource_types.get(Constants.Network, [])
        secrets = resource_types.get(Constants.Secret, [])
        secret_values = resource_types.get(Constants.SecretValue, [])
        volumes = resource_types.get(Constants.Volume, [])
        gateways = resource_types.get(Constants.Gateway, [])

        if not applications == []:
            for application in applications:
                dependencies[application] = []
                if not networks == []:
                    dependencies[application] += networks
                if not secret_values == []:
                    dependencies[application] += secret_values
                if not volumes == []:
                    dependencies[application] += volumes

        if not volumes == []:
            for volume in volumes:
                dependencies[volume] = []
                if not secret_values == []:
                    dependencies[volume] += secret_values

        if not secret_values == []:
            for secret_value in secret_values:
                dependencies[secret_value] = []
                if not secrets == []:
                    dependencies[secret_value] += secrets

        if not gateways == []:
            for gateway in gateways:
                dependencies[gateway] = []
                if not networks == []:
                    dependencies[gateway] += networks
        return dependencies

    @staticmethod
    def process_application(writer, application, dependencies, property_value_map):
        """ Writes Application resource in ARM format to writer"""
        sf_application_writer = OrderedDict()
        if PropertyNames.Name not in application:
            raise ValueError("name is not specified in description")

        name = application.get(PropertyNames.Name)

        # apiVersion
        schema_version = Constants.DefaultSchemaVersion
        if PropertyNames.SchemaVersion in application:
            schema_version = application[PropertyNames.SchemaVersion]
            # schemaVersion is not needed by RP, so remove it.
            del application[PropertyNames.SchemaVersion]

        sf_application_writer[PropertyNames.ApiVersion] = Schema.SchemaVersionRpApiVersionMap[schema_version]

        # name
        sf_application_writer[PropertyNames.Name] = name
        del application[PropertyNames.Name]

        # type: Microsoft.Seabreeze/applications
        sf_application_writer[PropertyNames.Type] = Schema.SchemaVersionSupportedResourcesTypeMap[schema_version][Constants.Applications]

        # location
        sf_application_writer[PropertyNames.Location] = property_value_map[PropertyNames.Location]

        # dependsOn
        sf_application_writer[PropertyNames.DependsOn] = dependencies.get(ArmDocumentGenerator.get_sbz_resource_name(ArmDocumentGenerator.get_sbz_resource_type(Constants.Application, schema_version), name), [])

        if PropertyNames.Kind in application:
            del application[PropertyNames.Kind]

        # Get all JsonProperties for application, handle the "properties" JsonProperty, write others as is.
        for app_property in application.keys():
            if app_property == PropertyNames.Properties:
                sf_application_writer[app_property] = OrderedDict()
                properties = application[app_property]
                for prop in properties.keys():
                    if prop == Constants.Services:
                        sf_services_writer = ArmDocumentGenerator.process_services(properties[prop], schema_version)
                        sf_application_writer[app_property][prop] = sf_services_writer
                    else:
                        sf_application_writer[app_property][prop] = properties[prop]
            else:
                sf_application_writer[app_property] = application[app_property]
        if PropertyNames.Resources in writer:
            writer[PropertyNames.Resources].append(sf_application_writer)
        else:
            writer[PropertyNames.Resources] = [sf_application_writer]
        return writer

    @staticmethod
    def process_services(services, schema_version):
        """ Writes all services of application resource in ARM format to writer """
        sf_services_writer = []
        for service in services:
            sf_services_writer.append(ArmDocumentGenerator.process_service(service, schema_version))
        return sf_services_writer

    @staticmethod
    def process_service(service, schema_version):
        """ Writes service of list of services in ARM format to writer """
        service_writer = OrderedDict()
        if PropertyNames.Name not in service:
            raise ValueError("name is not specified in description")

        name = service.get(PropertyNames.Name)

        # apiVersion
        schema_version = Constants.DefaultSchemaVersion
        if PropertyNames.SchemaVersion in service:
            schema_version = service[PropertyNames.SchemaVersion]
            # schemaVersion is not needed by RP, so remove it.
            del service[PropertyNames.SchemaVersion]

        # name
        service_writer[PropertyNames.Name] = name
        del service[PropertyNames.Name]

        # Get all JsonProperties for service, handle the "properties" JsonProperty, write others as is.
        for service_property in service.keys():
            if service_property == PropertyNames.Properties:
                properties = service[service_property]
                properties = ArmDocumentGenerator.process_resource_refs(properties, schema_version)
                service_writer[service_property] = properties

            else:
                service_writer[service_property] = service[service_property]
        return service_writer

    @staticmethod
    def process_resource_refs(properties, schema_version):
        """ Process resource ref to the correct format """
        # fix refs for ARM
        for resource_kind in Schema.SchemaVersionSupportedResourcesKindMap[schema_version]:
            resource_refs = properties.get(resource_kind + "Refs", [])
            if not resource_refs == []:
                for index, resource_ref in enumerate(resource_refs):
                    ref_value = resource_ref[PropertyNames.Name]
                    properties[resource_kind + "Refs"][index][PropertyNames.Name] = "[resourceId('{0}','{1}')]".format(ArmDocumentGenerator.get_sbz_resource_type(resource_kind, schema_version), ref_value)

        # Recursively calling ref resolve for subnodes, as resource refs can be present in the subnodes as well
        for prop in properties.keys():
            if isinstance(properties[prop], list):
                for index in range(0, len(properties[prop])):
                    properties[prop][index] = ArmDocumentGenerator.process_resource_refs(properties[prop][index], schema_version)
        return properties

    @staticmethod
    def process_resource_refs_for_gateway(properties, schema_version):
        """ Process resource ref for gateway to the correct format """
        #  Process resources which are specified as {resourceKind}Refs
        properties = ArmDocumentGenerator.process_resource_refs(properties, schema_version)
        # networkRefs in Gateways are specified as sourceNetwork & destinationNetwork
        for resource in ["sourceNetwork", "destinationNetwork"]:
            resource_ref = properties.get(resource, "")
            if resource_ref != "":
                ref_value = resource_ref[PropertyNames.Name]
                # Do not resolve reference for Open
                if ref_value.lower() != "open":
                    properties[resource]["name"] = "[resourceId('{0}', '{1}')]".format(ArmDocumentGenerator.get_sbz_resource_type(Constants.Network, schema_version), ref_value)
        return properties

    @staticmethod
    def process_sf_resource(writer, sf_resource, resource_kind, dependencies, property_value_map, function_delegate, outputs_list):
        """ This method processes and writes a resource (excluding application resource)  to writer """
        sf_resource_writer = OrderedDict()
        if PropertyNames.Name not in sf_resource:
            raise ValueError("name is not specified for %s resource" % resource_kind)

        name = sf_resource.get(PropertyNames.Name)
        # apiVersion
        schema_version = Constants.DefaultSchemaVersion
        if PropertyNames.SchemaVersion in sf_resource:
            schema_version = sf_resource[PropertyNames.SchemaVersion]
            # schemaVersion is not needed by RP, so remove it.
            del sf_resource[PropertyNames.SchemaVersion]

        api_version = Schema.SchemaVersionRpApiVersionMap[schema_version]
        sf_resource_writer[PropertyNames.ApiVersion] = api_version

        # name
        sf_resource_writer[PropertyNames.Name] = name

        if api_version == Constants.RpApiVersion_2018_07_01_preview:
            if resource_kind == Constants.Network:
                outputs_list.append("[reference('{}').ingressConfig.publicIpAddress]".format(name))
        elif api_version == Constants.RpApiVersion_2018_09_01_preview:
            if resource_kind == Constants.Gateway:
                outputs_list.append("[reference('{}').ipAddress]".format(name))

        del sf_resource[PropertyNames.Name]

        # "type" : "Microsoft.Seabreeze/<resource name>"
        sf_resource_writer[PropertyNames.Type] = ArmDocumentGenerator.get_sbz_resource_type(resource_kind, schema_version)

        # location
        sf_resource_writer[PropertyNames.Location] = property_value_map[PropertyNames.Location]

        # dependsOn
        sf_resource_writer[PropertyNames.DependsOn] = dependencies.get(ArmDocumentGenerator.get_sbz_resource_name(ArmDocumentGenerator.get_sbz_resource_type(resource_kind, schema_version), name), [])

        # Get all JsonProperties for resource, handle the "properties" JsonProperty, write others as is.
        for prop in sf_resource.keys():
            if prop == PropertyNames.Properties:
                properties = sf_resource.get(prop)
                function_delegate(properties, schema_version)
                sf_resource_writer[prop] = properties
            else:
                sf_resource_writer[prop] = sf_resource.get(prop)
        if PropertyNames.Resources in writer:
            writer[PropertyNames.Resources].append(sf_resource_writer)
        else:
            writer[PropertyNames.Resources] = [sf_resource_writer]
        return writer

    @staticmethod
    def get_sbz_resource_type(resource_type, schema_version):
        """ Returns the resource type for the provided resource type and schema version"""
        if resource_type == Constants.Secret:
            return Schema.SchemaVersionSupportedResourcesTypeMap[schema_version][Constants.Secrets]
        elif resource_type == Constants.SecretValue:
            return Schema.SchemaVersionSupportedResourcesTypeMap[schema_version][Constants.SecretValues]
        elif resource_type == Constants.Network:
            return Schema.SchemaVersionSupportedResourcesTypeMap[schema_version][Constants.Networks]

        elif resource_type == Constants.Volume:
            return Schema.SchemaVersionSupportedResourcesTypeMap[schema_version][Constants.Volumes]
        elif resource_type == Constants.Application:
            return Schema.SchemaVersionSupportedResourcesTypeMap[schema_version][Constants.Applications]
        elif resource_type == Constants.Gateway:
            return Schema.SchemaVersionSupportedResourcesTypeMap[schema_version][Constants.Gateways]
        else:
            raise ValueError("Unknown SF resource %s" % (resource_type))

    @staticmethod
    def get_sbz_resource_name(resource_type, name):
        """ Returns the resource name for the provided resource type and name"""
        if resource_type in Schema.HierarchichalSbzResourceNameBuilderMap:
            resource_format_string = Schema.HierarchichalSbzResourceNameBuilderMap[resource_type]
            name = name.split('/')
            return resource_format_string.format(name[0], name[1])
        return "{0}/{1}".format(resource_type, name)
