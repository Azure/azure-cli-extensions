from unittest import TestCase
from unittest.mock import patch, MagicMock
from pathlib import Path
from typing import List
from azext_aosm.build_processors.arm_processor import NexusArmBuildProcessor
from azext_aosm.inputs.arm_template_input import ArmTemplateInput

from azext_aosm.cli_handlers.onboarding_nexus_vnf_handler import OnboardingNexusVNFCLIHandler
from azext_aosm.definition_folder.builder.artifact_builder import ArtifactDefinitionElementBuilder
from azext_aosm.definition_folder.builder.bicep_builder import BicepDefinitionElementBuilder
from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
from azext_aosm.common.constants import VNF_OUTPUT_FOLDER_FILENAME, ARTIFACT_LIST_FILENAME


class NexusArmProcessorTest(TestCase):

    def setUp(self):
        nexus_arm_input = ArmTemplateInput(
            artifact_name="test-artifact-name",
            artifact_version="1.1.1",
            template_path="",
            default_config=None
        )
        self.processor = NexusArmBuildProcessor()
