# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import platform
from azext_confcom.custom import katapolicygen_confcom

import pytest

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
host_os_linux = platform.system() == "Linux"

# @unittest.skip("not in use")
@pytest.mark.run(order=1)
class KataPolicyGen(unittest.TestCase):

    pod_string = """
apiVersion: v1
kind: Pod
metadata:
  name: cm2
spec:
  restartPolicy: Never
  runtimeClassName: kata-cc
  containers:
    - name: busybox
      image: "mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64"
      volumeMounts:
        - mountPath: /cm2
          name: cm2-volume
      command:
        - /bin/sh
      args:
        - "-c"
        - while true; do echo hello; sleep 10; done

"""

    def test_invalid_input_path(self):
        with self.assertRaises(SystemExit) as wrapped_exit:
            katapolicygen_confcom(
                "fakepath/input.json",
                None,
            )
        self.assertNotEqual(wrapped_exit.exception.code, 0)

    def test_invalid_config_map_path(self):
        filename = "pod.yaml"
        try:
            with open(filename, "w") as f:
                f.write(KataPolicyGen.pod_string)
            with self.assertRaises(SystemExit) as wrapped_exit:
                katapolicygen_confcom(
                    filename, "fakepath/configmap.yaml",
                )
        finally:
            if os.path.exists(filename):
                os.remove(filename)
        self.assertNotEqual(wrapped_exit.exception.code, 0)

    # def test_valid_settings(self):
    #     filename = "pod2.yaml"
    #     try:
    #         with open(filename, "w") as f:
    #             f.write(KataPolicyGen.pod_string)
    #         if host_os_linux:
    #             katapolicygen_confcom(
    #                 filename, None
    #             )
    #         else:
    #             with self.assertRaises(SystemExit) as wrapped_exit:
    #                 katapolicygen_confcom(
    #                 filename, None
    #             )
    #             self.assertNotEqual(wrapped_exit.exception.code, 0)
    #             return

    #         with open(filename, "r") as f:
    #             content = f.read()
    #     finally:
    #         if os.path.exists(filename):
    #             os.remove(filename)
    #     if host_os_linux:
    #         self.assertNotEqual(content, KataPolicyGen.pod_string, "Policy content not changed in yaml")

    # def test_print_version(self):
    #     if host_os_linux:
    #         katapolicygen_confcom(
    #             None, None, print_version=True
    #         )
    #     else:
    #         with self.assertRaises(SystemExit) as wrapped_exit:
    #             katapolicygen_confcom(
    #                 None, None, print_version=True
    #             )
    #         self.assertNotEqual(wrapped_exit.exception.code, 0)
