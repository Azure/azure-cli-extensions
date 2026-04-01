# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest


class VICameraTests(ScenarioTest):
    def test_add_camera(self):
        name = "test-vi"
        resource_group = f"{name}-rg"
        connected_cluster = f"{name}-connected-aks"
        command = f"az vi camera add -g {resource_group} -c {connected_cluster} --camera-name test --rtsp-url rtsp://test"
        camera = self.cmd(command).get_output_in_json()
        self.assertIsInstance(camera, dict)
        self.assertTrue(camera is not None)
        self.assertTrue(len(camera['id']) > 0)
        self.assertTrue(len(camera['createTime']) > 0)
        self.assertTrue(len(camera['name']) > 0)
        self.assertTrue(len(camera['rtspUrl']) > 0)

    def test_camera_list(self):
        name = "test-vi"
        resource_group = f"{name}-rg"
        connected_cluster = f"{name}-connected-aks"
        command = f'az vi camera list -g "{resource_group}" -c "{connected_cluster}"'
        response = self.cmd(command).get_output_in_json()
        self.assertIsInstance(response, list)
        self.assertTrue(len(response) > 0)
        camera = response[0]
        self.assertTrue(camera is not None)
        self.assertTrue(len(camera['id']) > 0)
        self.assertTrue(len(camera['createTime']) > 0)
        self.assertTrue(len(camera['name']) > 0)
        self.assertTrue(len(camera['rtspUrl']) > 0)
