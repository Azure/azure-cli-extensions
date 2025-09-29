# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from pathlib import Path
from typing import Dict
from knack.log import get_logger
from azext_aosm.vendored_sdks.models import (
    NfviDetails,
)
from azext_aosm.definition_folder.builder.json_builder import (
    JSONDefinitionElementBuilder,
)
from azext_aosm.common.constants import SNS_DEPLOYMENT_INPUT_FILENAME

logger = get_logger(__name__)


class SNSDeploymentInputDefinitionElementBuilder(JSONDefinitionElementBuilder):
    """Deployment input builder"""

    nfvis: Dict[str, NfviDetails]
    schema_to_cgv_map = []

    def __init__(
        self,
        path: Path,
        nfvis: Dict[str, NfviDetails],
        schema_to_cgv_map,
        only_delete_on_clean: bool = False,
    ):
        super().__init__(path, only_delete_on_clean)
        self.nfvis = nfvis
        self.schema_to_cgv_map = schema_to_cgv_map

    def write(self):
        """Write the definition element to disk."""
        self.path.mkdir(exist_ok=True)
        nfvis_list = []
        cgv_list = []
        for nfvi in self.nfvis:
            logger.debug(
                "Writing nfvi %s as: %s", self.nfvis[nfvi].name, self.nfvis[nfvi].type
            )
            nfvi_dict = {
                "name": self.nfvis[nfvi].name,
                "nfviType": self.nfvis[nfvi].type,
                "customLocationReference": {
                    "id": ""
                }
            }
            nfvis_list.append(nfvi_dict)

        for cgv in self.schema_to_cgv_map:
            cgv_dict = {
                "cgv_name": cgv["cgv_name"],
                "cgv_configuration_type": cgv["cgv_configuration_type"],
                "cgv_file_path": cgv["cgv_file_path"]
            }
            cgv_list.append(cgv_dict)

        combined_data = {
            "nfvis_list": nfvis_list,
            "cgv_list": cgv_list
        }
        json_data = json.dumps(combined_data, indent=4)

        # Write the deployment input file
        with open(self.path / SNS_DEPLOYMENT_INPUT_FILENAME, 'w') as file:
            file.write(json_data)
