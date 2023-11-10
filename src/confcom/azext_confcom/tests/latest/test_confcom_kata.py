# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import pytest
from azext_confcom.custom import katapolicygen_confcom

import pytest

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


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
        with open(filename, "w") as f:
            f.write(KataPolicyGen.pod_string)
        with self.assertRaises(SystemExit) as wrapped_exit:
            katapolicygen_confcom(
                filename, "fakepath/configmap.yaml",
            )
        os.remove(filename)
        self.assertNotEqual(wrapped_exit.exception.code, 0)

    def test_invalid_settings(self):
        filename = "pod2.yaml"
        with open(filename, "w") as f:
            f.write(KataPolicyGen.pod_string)
        with self.assertRaises(SystemExit) as wrapped_exit:
            katapolicygen_confcom(
                filename, None, settings_file_name="genpolicy-settings.json"
            )
        os.remove(filename)
        self.assertEqual(wrapped_exit.exception.code, 1)
