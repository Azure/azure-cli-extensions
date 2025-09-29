# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest import TestCase
from unittest.mock import patch, MagicMock
from pathlib import Path
from typing import List
from azext_aosm.cli_handlers.onboarding_nexus_vnf_handler import (
    OnboardingNexusVNFCLIHandler,
)
from azext_aosm.definition_folder.builder.artifact_builder import (
    ArtifactDefinitionElementBuilder,
)
from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder
from azext_aosm.common.constants import (
    VNF_OUTPUT_FOLDER_FILENAME,
    ARTIFACT_LIST_FILENAME,
)


class VNFNexusBuildTest(TestCase):

    def setUp(self):
        self.nexus_handler = OnboardingNexusVNFCLIHandler()

    def test_build_artifact_list_type(self):
        """Testing build artifact list for Nexus VNFs

        Test if path is as expected, and if list returned is correct type
        """
        self.nexus_handler.processors = MagicMock()
        artifact_list = self.nexus_handler.build_artifact_list()
        self.assertEqual(
            artifact_list.path, Path(VNF_OUTPUT_FOLDER_FILENAME, ARTIFACT_LIST_FILENAME)
        )
        self.assertIsInstance(artifact_list, ArtifactDefinitionElementBuilder)
