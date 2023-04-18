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
        expected_policy = "cGFja2FnZSBwb2xpY3kKCmltcG9ydCBmdXR1cmUua2V5d29yZHMuZXZlcnkKaW1wb3J0IGZ1dHVyZS5rZXl3b3Jkcy5pbgoKYXBpX3ZlcnNpb24gOj0gIjAuMTAuMCIKZnJhbWV3b3JrX3ZlcnNpb24gOj0gIjAuMi4zIgoKZnJhZ21lbnRzIDo9IFsKICB7CiAgICAiZmVlZCI6ICJtY3IubWljcm9zb2Z0LmNvbS9hY2kvYWNpLWNjLWluZnJhLWZyYWdtZW50IiwKICAgICJpbmNsdWRlcyI6IFsKICAgICAgImNvbnRhaW5lcnMiLAogICAgICAiZnJhZ21lbnRzIgogICAgXSwKICAgICJpc3N1ZXIiOiAiZGlkOng1MDk6MDpzaGEyNTY6SV9faXVMMjVvWEVWRmRUUF9hQkx4X2VUMVJQSGJDUV9FQ0JRZllacHQ5czo6ZWt1OjEuMy42LjEuNC4xLjMxMS43Ni41OS4xLjMiLAogICAgIm1pbmltdW1fc3ZuIjogIjEiCiAgfQpdCgpjb250YWluZXJzIDo9IFt7ImFsbG93X2VsZXZhdGVkIjp0cnVlLCJhbGxvd19zdGRpb19hY2Nlc3MiOnRydWUsImNvbW1hbmQiOlsicHl0aG9uMyJdLCJlbnZfcnVsZXMiOlt7InBhdHRlcm4iOiJQQVRIPS91c3IvbG9jYWwvYmluOi91c3IvbG9jYWwvc2JpbjovdXNyL2xvY2FsL2JpbjovdXNyL3NiaW46L3Vzci9iaW46L3NiaW46L2JpbiIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJMQU5HPUMuVVRGLTgiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiR1BHX0tFWT0wRDk2REY0RDQxMTBFNUM0M0ZCRkIxN0YyRDM0N0VBNkFBNjU0MjFEIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlBZVEhPTl9WRVJTSU9OPTMuNi4xNCIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJQWVRIT05fUElQX1ZFUlNJT049MjEuMi40IiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlBZVEhPTl9HRVRfUElQX1VSTD1odHRwczovL2dpdGh1Yi5jb20vcHlwYS9nZXQtcGlwL3Jhdy9jMjBiMGNmZDY0M2NkNGExOTI0NmNjZjIwNGUyOTk3YWY3MGY2YjIxL3B1YmxpYy9nZXQtcGlwLnB5IiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlBZVEhPTl9HRVRfUElQX1NIQTI1Nj1mYTZmM2ZiOTNjY2UyMzRjZDRlOGRkMmJlYjU0YTUxYWI5YzI0NzY1M2I1Mjg1NWE0OGRkNDRlNmIyMWZmMjhiIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlRFUk09eHRlcm0iLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiKCg/aSlGQUJSSUMpXy4rPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IkhPU1ROQU1FPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IlQoRSk/TVA9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiRmFicmljUGFja2FnZUZpbGVOYW1lPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6Ikhvc3RlZFNlcnZpY2VOYW1lPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IklERU5USVRZX0FQSV9WRVJTSU9OPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IklERU5USVRZX0hFQURFUj0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJJREVOVElUWV9TRVJWRVJfVEhVTUJQUklOVD0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJhenVyZWNvbnRhaW5lcmluc3RhbmNlX3Jlc3RhcnRlZF9ieT0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifV0sImV4ZWNfcHJvY2Vzc2VzIjpbXSwiaWQiOiJweXRob246My42LjE0LXNsaW0tYnVzdGVyIiwibGF5ZXJzIjpbIjI1NGNjODUzZGE2MDgxOTA1YzkxMDljOGI5ZDk5YzlmYjA5ODdiYTFkODhmNzI5MDg4OTAzY2ZmYjgwZjU1ZjEiLCJhNTY4ZjE5MDBiZWQ2MGEwNjQxYjc2Yjk5MWFkNDMxNDQ2ZDljM2EzNDRkN2IyNjFmMTBkZThkOGU3Mzc2M2FjIiwiYzcwYzUzMGU4NDJmNjYyMTViMGJkOTU1ODc3MTU3YmEyNGMzNzk5MzAzNTY3YzNmNTY3M2M0NTY2M2VhNGQxNSIsIjNlODZjM2NjZjE2NDJiZjU4NGRlMzNiNDljNzI0OGY4N2VlY2QwZjZkOGMwODM1M2RhYTM2Y2M3YWQwYTdiNmEiLCIxZTQ2ODRkOGM3Y2FhNzRjNjUyNDE3MmI0ZDVhMTU5YTEwODg3NjEzZWQ3MGYxOGQwYTU1ZDA1YjJhZjYxYWNkIl0sIm1vdW50cyI6W3siZGVzdGluYXRpb24iOiIvZXRjL3Jlc29sdi5jb25mIiwib3B0aW9ucyI6WyJyYmluZCIsInJzaGFyZWQiLCJydyJdLCJzb3VyY2UiOiJzYW5kYm94Oi8vL3RtcC9hdGxhcy9yZXNvbHZjb25mLy4rIiwidHlwZSI6ImJpbmQifV0sInNpZ25hbHMiOltdLCJ3b3JraW5nX2RpciI6Ii8ifSx7ImFsbG93X2VsZXZhdGVkIjpmYWxzZSwiYWxsb3dfc3RkaW9fYWNjZXNzIjp0cnVlLCJjb21tYW5kIjpbIi9wYXVzZSJdLCJlbnZfcnVsZXMiOlt7InBhdHRlcm4iOiJQQVRIPS91c3IvbG9jYWwvc2JpbjovdXNyL2xvY2FsL2JpbjovdXNyL3NiaW46L3Vzci9iaW46L3NiaW46L2JpbiIsInJlcXVpcmVkIjp0cnVlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlRFUk09eHRlcm0iLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn1dLCJleGVjX3Byb2Nlc3NlcyI6W10sImxheWVycyI6WyIxNmI1MTQwNTdhMDZhZDY2NWY5MmMwMjg2M2FjYTA3NGZkNTk3NmM3NTVkMjZiZmYxNjM2NTI5OTE2OWU4NDE1Il0sIm1vdW50cyI6W10sInNpZ25hbHMiOltdLCJ3b3JraW5nX2RpciI6Ii8ifV0KCmFsbG93X3Byb3BlcnRpZXNfYWNjZXNzIDo9IGZhbHNlCmFsbG93X2R1bXBfc3RhY2tzIDo9IGZhbHNlCmFsbG93X3J1bnRpbWVfbG9nZ2luZyA6PSBmYWxzZQphbGxvd19lbnZpcm9ubWVudF92YXJpYWJsZV9kcm9wcGluZyA6PSB0cnVlCmFsbG93X3VuZW5jcnlwdGVkX3NjcmF0Y2ggOj0gZmFsc2UKCgoKbW91bnRfZGV2aWNlIDo9IGRhdGEuZnJhbWV3b3JrLm1vdW50X2RldmljZQp1bm1vdW50X2RldmljZSA6PSBkYXRhLmZyYW1ld29yay51bm1vdW50X2RldmljZQptb3VudF9vdmVybGF5IDo9IGRhdGEuZnJhbWV3b3JrLm1vdW50X292ZXJsYXkKdW5tb3VudF9vdmVybGF5IDo9IGRhdGEuZnJhbWV3b3JrLnVubW91bnRfb3ZlcmxheQpjcmVhdGVfY29udGFpbmVyIDo9IGRhdGEuZnJhbWV3b3JrLmNyZWF0ZV9jb250YWluZXIKZXhlY19pbl9jb250YWluZXIgOj0gZGF0YS5mcmFtZXdvcmsuZXhlY19pbl9jb250YWluZXIKZXhlY19leHRlcm5hbCA6PSBkYXRhLmZyYW1ld29yay5leGVjX2V4dGVybmFsCnNodXRkb3duX2NvbnRhaW5lciA6PSBkYXRhLmZyYW1ld29yay5zaHV0ZG93bl9jb250YWluZXIKc2lnbmFsX2NvbnRhaW5lcl9wcm9jZXNzIDo9IGRhdGEuZnJhbWV3b3JrLnNpZ25hbF9jb250YWluZXJfcHJvY2VzcwpwbGFuOV9tb3VudCA6PSBkYXRhLmZyYW1ld29yay5wbGFuOV9tb3VudApwbGFuOV91bm1vdW50IDo9IGRhdGEuZnJhbWV3b3JrLnBsYW45X3VubW91bnQKZ2V0X3Byb3BlcnRpZXMgOj0gZGF0YS5mcmFtZXdvcmsuZ2V0X3Byb3BlcnRpZXMKZHVtcF9zdGFja3MgOj0gZGF0YS5mcmFtZXdvcmsuZHVtcF9zdGFja3MKcnVudGltZV9sb2dnaW5nIDo9IGRhdGEuZnJhbWV3b3JrLnJ1bnRpbWVfbG9nZ2luZwpsb2FkX2ZyYWdtZW50IDo9IGRhdGEuZnJhbWV3b3JrLmxvYWRfZnJhZ21lbnQKc2NyYXRjaF9tb3VudCA6PSBkYXRhLmZyYW1ld29yay5zY3JhdGNoX21vdW50CnNjcmF0Y2hfdW5tb3VudCA6PSBkYXRhLmZyYW1ld29yay5zY3JhdGNoX3VubW91bnQKCnJlYXNvbiA6PSB7ImVycm9ycyI6IGRhdGEuZnJhbWV3b3JrLmVycm9yc30="

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
