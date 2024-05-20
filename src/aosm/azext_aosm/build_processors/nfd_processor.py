# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from knack.log import get_logger
from azure.cli.core.azclierror import ResourceNotFoundError
from azext_aosm.build_processors.base_processor import BaseInputProcessor
from azext_aosm.common.artifact import BaseArtifact, LocalFileACRArtifact
from azext_aosm.common.constants import CGS_NAME
from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
from azext_aosm.inputs.nfd_input import NFDInput
from azext_aosm.vendored_sdks.models import (
    ArmResourceDefinitionResourceElementTemplate,
    ArtifactType,
    DependsOnProfile,
    ManifestArtifactFormat,
    NetworkFunctionApplication,
    NetworkFunctionDefinitionResourceElementTemplateDetails as NFDResourceElementTemplate,
    NSDArtifactProfile,
    ReferencedResource,
    TemplateType,
    ContainerizedNetworkFunctionDefinitionVersion,
    VirtualNetworkFunctionDefinitionVersion,
)
from azext_aosm.common.constants import (
    NSD_OUTPUT_FOLDER_FILENAME,
    NSD_NF_TEMPLATE_FILENAME,
    NSD_TEMPLATE_FOLDER_NAME,
    VNF_TYPE, CNF_TYPE
)
from azext_aosm.common.utils import render_bicep_contents_from_j2, get_template_path

logger = get_logger(__name__)


class NFDProcessor(BaseInputProcessor):
    """
    A class for processing NFD inputs.

    :param name: The name of the artifact.
    :param input_artifact: The input artifact.
    """

    input_artifact: NFDInput

    def __init__(self, name: str, input_artifact: NFDInput):
        super().__init__(name, input_artifact, expose_all_params=False)

    def get_artifact_manifest_list(self) -> List[ManifestArtifactFormat]:
        """
        Get the list of artifacts for the artifact manifest.

        :return: A list of artifacts for the artifact manifest.
        :rtype: List[ManifestArtifactFormat]
        """
        logger.debug("Getting artifact manifest list for NFD input %s.", self.name)
        return [
            ManifestArtifactFormat(
                artifact_name=self.input_artifact.artifact_name,
                artifact_type=ArtifactType.OCI_ARTIFACT.value,
                artifact_version=self.input_artifact.artifact_version,
            )
        ]

    def get_artifact_details(
        self,
    ) -> Tuple[List[BaseArtifact], List[LocalFileBuilder]]:
        """
        Get the artifact details for publishing.

        :return: A tuple containing the list of artifacts and the list of local file builders.
        :rtype: Tuple[List[BaseArtifact], List[LocalFileBuilder]]
        """
        logger.info("Getting artifact details for NFD input.")
        # The ARM template is written to a local file to be used as the artifact
        # Path is relative to NSD_OUTPUT_FOLDER_FILENAME as this artifact is stored in the NSD output folder
        artifact_details = LocalFileACRArtifact(
            artifact_name=self.input_artifact.artifact_name,
            artifact_type=ArtifactType.ARM_TEMPLATE.value,
            artifact_version=self.input_artifact.artifact_version,
            file_path=self.input_artifact.arm_template_output_path.relative_to(
                Path(NSD_OUTPUT_FOLDER_FILENAME)
            ),
        )

        template_path = get_template_path(
            NSD_TEMPLATE_FOLDER_NAME, NSD_NF_TEMPLATE_FILENAME
        )

        # This horrendous if statement is required because:
        # - the 'properties' and 'network_function_template' attributes are optional
        # - the isinstance check is because the base
        #   NetworkFunctionDefinitionVersionPropertiesFormat class
        #   doesn't define the network_function_template attribute, even though both subclasses do.
        # Not switching to EAFP style because mypy doesn't
        # account for `except AttributeError` (for good reason).
        # Similar test required in the NFD input, but we can't deduplicate the code because mypy
        # doesn't propagate type narrowing from isinstance().
        if (
            self.input_artifact.network_function_definition.properties
            and isinstance(
                self.input_artifact.network_function_definition.properties,
                (
                    ContainerizedNetworkFunctionDefinitionVersion,
                    VirtualNetworkFunctionDefinitionVersion,
                ),
            )
            and self.input_artifact.network_function_definition.properties.network_function_template
        ):
            # Split for line-too-long linting errors
            nf_type = self.input_artifact.network_function_definition.properties.network_function_type
            nf_templates = self.input_artifact.network_function_definition.properties.network_function_template

            if nf_type == CNF_TYPE:
                nf_application_names = [nf_app.name for nf_app in nf_templates.network_function_applications]
                params = {
                    "nfvi_type":
                    nf_templates.nfvi_type,
                    "is_cnf": True,
                    "nf_application_names": nf_application_names
                }
            elif nf_type == VNF_TYPE:
                params = {
                    "nfvi_type":
                    nf_templates.nfvi_type,
                    "is_cnf": False
                }
            else:
                raise ResourceNotFoundError(f"The NFDV provided has invalid network function type: {nf_type}")
        else:
            raise ResourceNotFoundError("The NFDV provided has no nfvi type.")
        bicep_contents = render_bicep_contents_from_j2(template_path, params)
        # Create a local file builder for the ARM template
        file_builder = LocalFileBuilder(
            self.input_artifact.arm_template_output_path,
            bicep_contents,
        )

        return [artifact_details], [file_builder]

    def generate_nf_application(self) -> NetworkFunctionApplication:
        """
        Generate the network function application from the input.

        :raises NotImplementedError: NFDs cannot be used to generate new NF application templates.
        """
        raise NotImplementedError(
            "NFDs cannot be used to generate new NF application templates."
        )

    def generate_resource_element_template(self) -> NFDResourceElementTemplate:
        """
        Generate the resource element template from the input.

        :return: The resource element template.
        :rtype: NFDResourceElementTemplate
        """
        logger.info("Generating resource element template for NFD input.")
        parameter_values_dict = self.generate_values_mappings(
            self.input_artifact.get_schema(), self.input_artifact.get_defaults(), True
        )

        artifact_profile = NSDArtifactProfile(
            artifact_store_reference=ReferencedResource(id=""),
            artifact_name=self.input_artifact.artifact_name,
            artifact_version=self.input_artifact.artifact_version,
        )

        configuration = ArmResourceDefinitionResourceElementTemplate(
            template_type=TemplateType.ARM_TEMPLATE.value,
            artifact_profile=artifact_profile,
            parameter_values=json.dumps(parameter_values_dict),
        )

        return NFDResourceElementTemplate(
            name=self.name,
            configuration=configuration,
            depends_on_profile=DependsOnProfile(
                install_depends_on=[], uninstall_depends_on=[], update_depends_on=[]
            ),
        )

    def _generate_schema(
        self,
        cg_schema: Dict[str, Any],
        source_schema: Dict[str, Any],
        default_values: Dict[str, Any],
        param_prefix: Optional[str] = None,
    ) -> None:
        """
        Generate the config group schema.

        This method recursively generates the config group schema for the input artifact by updating
        the cg_schema parameter.

        Parameters:
            cg_schema:
                The schema to be modified.
                On first call of this method, it should contain any base nodes for the schema.
                This schema is passed by reference and modified in place.
                This property is defined by the CLI in the base processor.
            source_schema:
                The source schema from which the config group schema is generated.
                E.g., for an NFD this will be the deployParameters schema
                and is created by the NFDInput class using a previously deployed NFDV properties.
                For an ARM template this will be the schema generated from the templates parameters
            default_values:
                The default values used to determine whether a parameter
                should be hardcoded or provided by the user.
                These are generated by the CLI based on the NDFV properties.
            param_prefix:
                The prefix to be added to the parameter name.
                This is used for namespacing nested properties in the schema.
                On first call to this method this should be None.
        """
        if "properties" not in source_schema.keys():
            return

        # configObject is the root object and not needed for namespacing. It just adds confusion, so remove it.
        # There's an edge case where it's not the root object (by coincidence someone else is also using
        # "configObject"). This could be solved by removing the root configObject before starting this recursive
        # algorithm. For now, not handling this edge case is acceptable.
        if param_prefix == "configObject":
            param_prefix = None

        # Abbreviated 'prop' so as not to override built in 'property'.
        for prop, details in source_schema["properties"].items():
            if prop == "deployParameters":
                # These arise due to pulling deployParameters from the NFD schema, but we don't want them in the
                # middle of the config group schema.
                del details["items"]["$schema"]
                del details["items"]["title"]

            param_name = prop if not param_prefix else f"{param_prefix}_{prop}"

            # Note: We don't recurse into deployParams because it's an array. For arrays we just dump all the `details`
            # as is (in this case the NFDV deployParams).
            # This means if NFDV is expose all, NSDV is expose all. That's the
            # behaviour we want for now, but this will need to be changed if we want anything more sophisticated.

            # We have three types of parameter to handle in the following if statements:
            # 1. Parameters that are always hardcoded
            if prop in [
                "location",
                "publisherName",
                "nfdgName",
                "publisherResourceGroup",
            ]:
                continue
            # 2. Required parameters (in 'required' array and no default given).
            if (
                "required" in source_schema
                and prop in source_schema["required"]
                and prop not in default_values
            ):
                if "properties" in details:
                    self._generate_schema(cg_schema, details, {}, param_name)
                else:
                    cg_schema["required"].append(param_name)
                    cg_schema["properties"][param_name] = details
            # 3. Optional parameters that have child properties. These aren't added to the CG schema here, but
            # we check their children
            # Note, given we only have a single depth of params for CGS, this is probably unnecessary, but leaving
            # in case we want to add more nesting in the future (e.g. more sophisticated array handling).
            elif prop in default_values and "properties" in details:
                self._generate_schema(
                    cg_schema, details, default_values[prop], param_name
                )

    def generate_values_mappings(
        self,
        schema: Dict[str, Any],
        mapping: Dict[str, Any],
        is_ret: bool = False,
        param_prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Override the BaseInputProcessor's method, see there for full docstring.

            - Some parameters are always hardcoded, and therefore always in the initial mapping, so we skip these.
            - There's no expose_all_params functionality as for NSD's we simply map `deployParameters` on to the CGV
              `deployParameters`.
        """

        # configObject is the root object and not needed for namespacing. It just adds confusion, so remove it.
        if param_prefix == "configObject":
            param_prefix = None

        for prop, prop_schema in schema["properties"].items():

            param_name = prop if param_prefix is None else f"{param_prefix}_{prop}"

            # We have three types of parameter to handle in the following if statements (analagous to
            # generate_schema()):
            # 1. Parameters that are always hardcoded
            if prop in [
                "location",
                "publisherName",
                "nfdgName",
                "publisherResourceGroup",
            ]:
                continue
            # 2. Required parameters (in 'required' array and no default given).
            if (
                "required" in schema
                and prop in schema["required"]
                and prop not in mapping
            ):
                if "properties" in prop_schema:
                    mapping[prop] = self.generate_values_mappings(
                        prop_schema, {}, is_ret, param_name
                    )
                else:
                    mapping[prop] = (
                        f"{{configurationparameters('{CGS_NAME}').{self.name}.{param_name}}}"
                        if is_ret
                        else f"{{deployParameters.{self.name}.{param_name}}}"
                    )
            # 3. Optional parameters (i.e. they have a default in the mapping dict) that have child properties.
            # These aren't added to the mapping here, but we check their children.
            # Note, given we only have a single depth of params for CGS, this is probably unnecessary, but leaving
            # in case we want to add more nesting in the future (e.g. more sophisticated array handling).
            elif prop in mapping and "properties" in prop_schema:
                # Python evaluates {} as False, so we need to explicitly set to {}
                default_subschema_mapping = mapping[prop] or {}
                mapping[prop] = self.generate_values_mappings(
                    prop_schema, default_subschema_mapping, is_ret, param_name
                )

        logger.debug(
            "Output of generate_values_mappings for %s:\n%s",
            self.name,
            json.dumps(mapping, indent=4),
        )

        return mapping
