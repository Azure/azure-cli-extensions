# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json
import deepdiff
import docker

from azext_confcom.security_policy import (
    OutputType,
    load_policy_from_image_name,
    load_policy_from_str,
)
import azext_confcom.config as config

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


class PolicyGeneratingImage(unittest.TestCase):
    custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "python:3.6.14-slim-buster",
                    "environmentVariables": [

                    ],
                    "command": [
                        "python3"
                    ],
                    "workingDir": ""
                }
            ]
        }
        """

    @classmethod
    def setUpClass(cls):
        with load_policy_from_image_name("python:3.6.14-slim-buster") as aci_policy:
            aci_policy.populate_policy_content_for_all_images(individual_image=True)
            cls.aci_policy = aci_policy
        with load_policy_from_str(cls.custom_json) as custom_policy:
            custom_policy.populate_policy_content_for_all_images()
            cls.custom_policy = custom_policy

    def test_image_policy(self):
        # deep diff the output policies from the regular policy.json and the single image
        self.assertEqual(self.aci_policy.get_serialized_output(), self.custom_policy.get_serialized_output())


class PolicyGeneratingImageSidecar(unittest.TestCase):
    custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "mcr.microsoft.com/aci/atlas-mount-azure-file-volume:master_20201210.2",
                    "environmentVariables": [

                    ],
                    "command": [
                         "/mount_azure_file.sh"
                    ],
                    "workingDir": ""
                }
            ]
        }
        """

    @classmethod
    def setUpClass(cls):
        with load_policy_from_image_name(
            "mcr.microsoft.com/aci/atlas-mount-azure-file-volume:master_20201210.2"
        ) as aci_policy:
            aci_policy.populate_policy_content_for_all_images(individual_image=True)
            cls.aci_policy = aci_policy
        with load_policy_from_str(cls.custom_json) as custom_policy:
            custom_policy.populate_policy_content_for_all_images(individual_image=True)
            cls.custom_policy = custom_policy

    def test_sidecar_image_policy(self):
        self.assertEqual(self.aci_policy.get_serialized_output(), self.custom_policy.get_serialized_output())


class PolicyGeneratingImageInvalid(unittest.TestCase):
    def test_invalid_image_policy(self):

        policy = load_policy_from_image_name(
            "mcr.microsoft.com/aci/fake-image:master_20201210.2"
        )
        with self.assertRaises(SystemExit) as exc_info:
            policy.populate_policy_content_for_all_images(individual_image=True)
        self.assertEqual(exc_info.exception.code, 1)


class PolicyGeneratingImageCleanRoom(unittest.TestCase):
    def test_clean_room_policy(self):
        client = docker.from_env()
        original_image = (
            "mcr.microsoft.com/aci/atlas-mount-azure-file-volume:master_20201210.2"
        )
        try:
            client.images.remove(original_image)
        except:
            # do nothing
            pass
        regular_image = load_policy_from_image_name(original_image)
        regular_image.populate_policy_content_for_all_images(individual_image=True)
        # create and tag same image to the new name to see if docker will error out that the image is not in a remote repo
        new_repo = "mcr.microsoft.com"
        new_image_name = "aci/atlas-mount-azure-file-volume"
        new_tag = "fake-tag"

        image = client.images.get(original_image)
        try:
            client.images.remove(new_repo + "/" + new_image_name + ":" + new_tag)
        except:
            # do nothing
            pass
        image.tag(new_repo + "/" + new_image_name, tag=new_tag)
        try:
            client.images.remove(original_image)
        except:
            # do nothing
            pass
        client.close()

        policy = load_policy_from_image_name(
            new_repo + "/" + new_image_name + ":" + new_tag
        )
        policy.populate_policy_content_for_all_images(individual_image=True)

        regular_image_json = json.loads(
            regular_image.get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        clean_room_json = json.loads(
            policy.get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        regular_image_json[0].pop(config.POLICY_FIELD_CONTAINERS_ID)
        clean_room_json[0].pop(config.POLICY_FIELD_CONTAINERS_ID)

        # see if the remote image and the local one produce the same output
        self.assertEqual(
            deepdiff.DeepDiff(regular_image_json, clean_room_json, ignore_order=True),
            {},
        )
