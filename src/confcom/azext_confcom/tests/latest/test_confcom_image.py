# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import pytest
import json
import deepdiff
import docker

from azext_confcom.security_policy import (
    OutputType,
    load_policy_from_image_name,
)
import azext_confcom.config as config

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


# @unittest.skip("not in use")
@pytest.mark.run(order=1)
class PolicyGeneratingImage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with load_policy_from_image_name("python:3.6.14-slim-buster") as aci_policy:
            aci_policy.populate_policy_content_for_all_images(individual_image=True)
            cls.aci_policy = aci_policy

    def test_image_policy(self):
        expected_policy = "cGFja2FnZSBwb2xpY3kKCmltcG9ydCBmdXR1cmUua2V5d29yZHMuZXZlcnkKaW1wb3J0IGZ1dHVyZS5rZXl3b3Jkcy5pbgoKYXBpX3ZlcnNpb24gOj0gIjAuMTAuMCIKZnJhbWV3b3JrX3ZlcnNpb24gOj0gIjAuMi4zIgoKZnJhZ21lbnRzIDo9IFsKICB7CiAgICAiZmVlZCI6ICJtY3IubWljcm9zb2Z0LmNvbS9hY2kvYWNpLWNjLWluZnJhLWZyYWdtZW50IiwKICAgICJpbmNsdWRlcyI6IFsKICAgICAgImNvbnRhaW5lcnMiCiAgICBdLAogICAgImlzc3VlciI6ICJkaWQ6eDUwOTowOnNoYTI1NjpJX19pdUwyNW9YRVZGZFRQX2FCTHhfZVQxUlBIYkNRX0VDQlFmWVpwdDlzOjpla3U6MS4zLjYuMS40LjEuMzExLjc2LjU5LjEuMyIsCiAgICAibWluaW11bV9zdm4iOiAiMSIKICB9Cl0KCmNvbnRhaW5lcnMgOj0gW3siYWxsb3dfZWxldmF0ZWQiOnRydWUsImFsbG93X3N0ZGlvX2FjY2VzcyI6dHJ1ZSwiY29tbWFuZCI6WyJweXRob24zIl0sImVudl9ydWxlcyI6W3sicGF0dGVybiI6IlBBVEg9L3Vzci9sb2NhbC9iaW46L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi91c3Ivc2JpbjovdXNyL2Jpbjovc2JpbjovYmluIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IkxBTkc9Qy5VVEYtOCIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJHUEdfS0VZPTBEOTZERjRENDExMEU1QzQzRkJGQjE3RjJEMzQ3RUE2QUE2NTQyMUQiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiUFlUSE9OX1ZFUlNJT049My42LjE0IiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlBZVEhPTl9QSVBfVkVSU0lPTj0yMS4yLjQiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiUFlUSE9OX0dFVF9QSVBfVVJMPWh0dHBzOi8vZ2l0aHViLmNvbS9weXBhL2dldC1waXAvcmF3L2MyMGIwY2ZkNjQzY2Q0YTE5MjQ2Y2NmMjA0ZTI5OTdhZjcwZjZiMjEvcHVibGljL2dldC1waXAucHkiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiUFlUSE9OX0dFVF9QSVBfU0hBMjU2PWZhNmYzZmI5M2NjZTIzNGNkNGU4ZGQyYmViNTRhNTFhYjljMjQ3NjUzYjUyODU1YTQ4ZGQ0NGU2YjIxZmYyOGIiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiVEVSTT14dGVybSIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiIoKD9pKUZBQlJJQylfLis9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSE9TVE5BTUU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiVChFKT9NUD0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJGYWJyaWNQYWNrYWdlRmlsZU5hbWU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSG9zdGVkU2VydmljZU5hbWU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSURFTlRJVFlfQVBJX1ZFUlNJT049LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSURFTlRJVFlfSEVBREVSPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IklERU5USVRZX1NFUlZFUl9USFVNQlBSSU5UPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6ImF6dXJlY29udGFpbmVyaW5zdGFuY2VfcmVzdGFydGVkX2J5PS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9XSwiZXhlY19wcm9jZXNzZXMiOltdLCJpZCI6InB5dGhvbjozLjYuMTQtc2xpbS1idXN0ZXIiLCJsYXllcnMiOlsiMjU0Y2M4NTNkYTYwODE5MDVjOTEwOWM4YjlkOTljOWZiMDk4N2JhMWQ4OGY3MjkwODg5MDNjZmZiODBmNTVmMSIsImE1NjhmMTkwMGJlZDYwYTA2NDFiNzZiOTkxYWQ0MzE0NDZkOWMzYTM0NGQ3YjI2MWYxMGRlOGQ4ZTczNzYzYWMiLCJjNzBjNTMwZTg0MmY2NjIxNWIwYmQ5NTU4NzcxNTdiYTI0YzM3OTkzMDM1NjdjM2Y1NjczYzQ1NjYzZWE0ZDE1IiwiM2U4NmMzY2NmMTY0MmJmNTg0ZGUzM2I0OWM3MjQ4Zjg3ZWVjZDBmNmQ4YzA4MzUzZGFhMzZjYzdhZDBhN2I2YSIsIjFlNDY4NGQ4YzdjYWE3NGM2NTI0MTcyYjRkNWExNTlhMTA4ODc2MTNlZDcwZjE4ZDBhNTVkMDViMmFmNjFhY2QiXSwibW91bnRzIjpbeyJkZXN0aW5hdGlvbiI6Ii9ldGMvcmVzb2x2LmNvbmYiLCJvcHRpb25zIjpbInJiaW5kIiwicnNoYXJlZCIsInJ3Il0sInNvdXJjZSI6InNhbmRib3g6Ly8vdG1wL2F0bGFzL3Jlc29sdmNvbmYvLisiLCJ0eXBlIjoiYmluZCJ9XSwic2lnbmFscyI6W10sIndvcmtpbmdfZGlyIjoiLyJ9LHsiYWxsb3dfZWxldmF0ZWQiOmZhbHNlLCJhbGxvd19zdGRpb19hY2Nlc3MiOnRydWUsImNvbW1hbmQiOlsiL3BhdXNlIl0sImVudl9ydWxlcyI6W3sicGF0dGVybiI6IlBBVEg9L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi91c3Ivc2JpbjovdXNyL2Jpbjovc2JpbjovYmluIiwicmVxdWlyZWQiOnRydWUsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiVEVSTT14dGVybSIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifV0sImV4ZWNfcHJvY2Vzc2VzIjpbXSwibGF5ZXJzIjpbIjE2YjUxNDA1N2EwNmFkNjY1ZjkyYzAyODYzYWNhMDc0ZmQ1OTc2Yzc1NWQyNmJmZjE2MzY1Mjk5MTY5ZTg0MTUiXSwibW91bnRzIjpbXSwic2lnbmFscyI6W10sIndvcmtpbmdfZGlyIjoiLyJ9XQoKYWxsb3dfcHJvcGVydGllc19hY2Nlc3MgOj0gZmFsc2UKYWxsb3dfZHVtcF9zdGFja3MgOj0gZmFsc2UKYWxsb3dfcnVudGltZV9sb2dnaW5nIDo9IGZhbHNlCmFsbG93X2Vudmlyb25tZW50X3ZhcmlhYmxlX2Ryb3BwaW5nIDo9IHRydWUKYWxsb3dfdW5lbmNyeXB0ZWRfc2NyYXRjaCA6PSBmYWxzZQoKCgptb3VudF9kZXZpY2UgOj0gZGF0YS5mcmFtZXdvcmsubW91bnRfZGV2aWNlCnVubW91bnRfZGV2aWNlIDo9IGRhdGEuZnJhbWV3b3JrLnVubW91bnRfZGV2aWNlCm1vdW50X292ZXJsYXkgOj0gZGF0YS5mcmFtZXdvcmsubW91bnRfb3ZlcmxheQp1bm1vdW50X292ZXJsYXkgOj0gZGF0YS5mcmFtZXdvcmsudW5tb3VudF9vdmVybGF5CmNyZWF0ZV9jb250YWluZXIgOj0gZGF0YS5mcmFtZXdvcmsuY3JlYXRlX2NvbnRhaW5lcgpleGVjX2luX2NvbnRhaW5lciA6PSBkYXRhLmZyYW1ld29yay5leGVjX2luX2NvbnRhaW5lcgpleGVjX2V4dGVybmFsIDo9IGRhdGEuZnJhbWV3b3JrLmV4ZWNfZXh0ZXJuYWwKc2h1dGRvd25fY29udGFpbmVyIDo9IGRhdGEuZnJhbWV3b3JrLnNodXRkb3duX2NvbnRhaW5lcgpzaWduYWxfY29udGFpbmVyX3Byb2Nlc3MgOj0gZGF0YS5mcmFtZXdvcmsuc2lnbmFsX2NvbnRhaW5lcl9wcm9jZXNzCnBsYW45X21vdW50IDo9IGRhdGEuZnJhbWV3b3JrLnBsYW45X21vdW50CnBsYW45X3VubW91bnQgOj0gZGF0YS5mcmFtZXdvcmsucGxhbjlfdW5tb3VudApnZXRfcHJvcGVydGllcyA6PSBkYXRhLmZyYW1ld29yay5nZXRfcHJvcGVydGllcwpkdW1wX3N0YWNrcyA6PSBkYXRhLmZyYW1ld29yay5kdW1wX3N0YWNrcwpydW50aW1lX2xvZ2dpbmcgOj0gZGF0YS5mcmFtZXdvcmsucnVudGltZV9sb2dnaW5nCmxvYWRfZnJhZ21lbnQgOj0gZGF0YS5mcmFtZXdvcmsubG9hZF9mcmFnbWVudApzY3JhdGNoX21vdW50IDo9IGRhdGEuZnJhbWV3b3JrLnNjcmF0Y2hfbW91bnQKc2NyYXRjaF91bm1vdW50IDo9IGRhdGEuZnJhbWV3b3JrLnNjcmF0Y2hfdW5tb3VudAoKcmVhc29uIDo9IHsiZXJyb3JzIjogZGF0YS5mcmFtZXdvcmsuZXJyb3JzfQ=="

        # deep diff the output policies from the regular policy.json and the ARM template
        aci_policy_str = self.aci_policy.get_serialized_output()

        self.assertEqual(aci_policy_str, expected_policy)


# @unittest.skip("not in use")
@pytest.mark.run(order=2)
class PolicyGeneratingImageSidecar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with load_policy_from_image_name(
            "mcr.microsoft.com/aci/atlas-mount-azure-file-volume:master_20201210.2"
        ) as aci_policy:
            aci_policy.populate_policy_content_for_all_images(individual_image=True)
            cls.aci_policy = aci_policy

    def test_sidecar_image_policy(self):
        expected_policy = "cGFja2FnZSBtaWNyb3NvZnRjb250YWluZXJpbnN0YW5jZQoKYXBpX3ZlcnNpb24gOj0gIjAuMTAuMCIKZnJhbWV3b3JrX3ZlcnNpb24gOj0gIjAuMi4zIgoKY29udGFpbmVycyA6PSBbeyJhbGxvd19lbGV2YXRlZCI6dHJ1ZSwiYWxsb3dfc3RkaW9fYWNjZXNzIjp0cnVlLCJjb21tYW5kIjpbIi9tb3VudF9henVyZV9maWxlLnNoIl0sImVudl9ydWxlcyI6W3sicGF0dGVybiI6IlBBVEg9L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi91c3Ivc2JpbjovdXNyL2Jpbjovc2JpbjovYmluIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9XSwiZXhlY19wcm9jZXNzZXMiOltdLCJpZCI6Im1jci5taWNyb3NvZnQuY29tL2FjaS9hdGxhcy1tb3VudC1henVyZS1maWxlLXZvbHVtZTptYXN0ZXJfMjAyMDEyMTAuMiIsImxheWVycyI6WyI2MDZmZDZiYWY1ZWIxYTcxZmQyODZhZWEyOTY3MmEwNmJmZTU1ZjAwMDdkZWQ5MmVlNzMxNDJhMzc1OTBlZDE5IiwiM2FkMWEyZmY0YTQ0YmM4NjBiM2NkMDI3Y2M4NmNlNDVhMzk5YzRjOTk1YzM2ZTk4MDBjNTM2OGNiNzI3YTdlMSIsImIxY2ZjMzBmMzdmMDhlNjA2NjhkYjNmNzE2MDY5N2IxOWQyYWQ0NWIxMmYwNzUxODg1Mjk5MzczNjE2YTZlMGEiLCJlZjM2NDg0NmM4ZjFmNDNkMTRkMmUzZTc5MTlhMDY0YjBjODI1NTNjMDhiMzU0MjJmNWQxZjA3YzM0MzViNDYyIiwiNTgyZmUzOWJkMzU5MDliYWY2YzQwMzY3MzRlMjBmNzY2MzkxYmE4MzcyN2ZiMWQ2ODNiZTA0NWZlNDUzYjVhZiIsImFhYzlmYjQwNDI1OGMwNjlhZTg1MzgyMzY0ZjVkMmJhMWQ0MDUxOGM2YjFmNTZhZGU2YmMyMmYzMDI4ZWFmZjAiXSwibW91bnRzIjpbXSwic2lnbmFscyI6W10sIndvcmtpbmdfZGlyIjoiLyJ9XQ=="
        aci_policy_str = self.aci_policy.get_serialized_output()

        self.assertEqual(aci_policy_str, expected_policy)


# @unittest.skip("not in use")
@pytest.mark.run(order=3)
class PolicyGeneratingImageInvalid(unittest.TestCase):
    def test_invalid_image_policy(self):

        policy = load_policy_from_image_name(
            "mcr.microsoft.com/aci/fake-image:master_20201210.2"
        )
        with self.assertRaises(SystemExit) as exc_info:
            policy.populate_policy_content_for_all_images(individual_image=True)
        self.assertEqual(exc_info.exception.code, 1)


# @unittest.skip("not in use")
@pytest.mark.run(order=4)
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
            regular_image.get_serialized_output(output_type=OutputType.RAW, use_json=True)
        )

        clean_room_json = json.loads(
            policy.get_serialized_output(output_type=OutputType.RAW, use_json=True)
        )

        regular_image_json[config.POLICY_FIELD_CONTAINERS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ]["0"].pop(config.POLICY_FIELD_CONTAINERS_ID)
        clean_room_json[config.POLICY_FIELD_CONTAINERS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ]["0"].pop(config.POLICY_FIELD_CONTAINERS_ID)

        # see if the remote image and the local one produce the same output
        self.assertEqual(
            deepdiff.DeepDiff(regular_image_json, clean_room_json, ignore_order=True),
            {},
        )
