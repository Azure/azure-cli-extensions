# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import unittest
from typing import Any, Dict

from azext_confcom.template_util import (
    convert_config_v0_to_v1,
    detect_old_format,
)
import azext_confcom.config as cfg

class ConvertConfigTests(unittest.TestCase):
    """Tests for the conversion of old-format ACI configs to v1 format.

    This includes:
    • Old-format detection
    • Default propagation of top-level fields (`version`, `fragments`)
    • Environment-variable strategy → `regex` flag mapping
    • `command` + liveness / readiness probes → `execProcesses` aggregation
    • Volume-mount translation and naming rules
    • Migration of `workingDir` and `allow_elevated` into security context
    • Idempotence when input is already v1
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls._old_json = """
        {
            "version": "1.0",
            "containers": [{
                "name": "demo",
                "containerImage": "demo:latest",
                "environmentVariables": [
                    {"name": "FOO", "value": "bar", "strategy": "string"},
                    {"name": "REGEXP_VAR", "value": "v.*", "strategy": "re2"}
                ],
                "command": ["python", "app.py"],
                "livenessProbe": {"exec": {"command": ["echo", "alive"]}},
                "readinessProbe": {"exec": {"command": ["echo", "ready"]}},
                "workingDir": "/work",
                "allow_elevated": true,
                "mounts": [{
                    "mountType": "azureFile",
                    "mountPath": "/mnt/af",
                    "readonly": true
                },
                {
                    "mountType": "emptyDir",
                    "mountPath": "/mnt/empty",
                    "readOnly": false
                }]
            }]
        }
        """
        cls._old_cfg: Dict[str, Any] = json.loads(cls._old_json)
        cls._new_cfg: Dict[str, Any] = convert_config_v0_to_v1(copy.deepcopy(cls._old_cfg))

    def test_detect_old_format(self) -> None:
        self.assertTrue(detect_old_format(self._old_cfg))
        self.assertFalse(detect_old_format(self._new_cfg))

    def test_top_level_fields_propagated(self) -> None:
        self.assertEqual(self._new_cfg[cfg.ACI_FIELD_VERSION], "1.0")
        self.assertEqual(self._new_cfg[cfg.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS], [])

    def test_container_count_preserved(self) -> None:
        self.assertEqual(
            len(self._new_cfg[cfg.ACI_FIELD_CONTAINERS]),
            len(self._old_cfg[cfg.ACI_FIELD_CONTAINERS]),
        )

    def test_env_strategy_to_regex_flag(self) -> None:
        new_container = self._new_cfg[cfg.ACI_FIELD_CONTAINERS][0]
        envs = new_container[cfg.ACI_FIELD_TEMPLATE_PROPERTIES][
            cfg.ACI_FIELD_CONTAINERS_ENVS
        ]

        string_env = next(e for e in envs if e["name"] == "FOO")
        self.assertNotIn("regex", string_env)

        regex_env = next(e for e in envs if e["name"] == "REGEXP_VAR")
        self.assertTrue(regex_env.get("regex", False))

    def test_exec_processes_built_correctly(self) -> None:
        props = self._new_cfg[cfg.ACI_FIELD_CONTAINERS][0][cfg.ACI_FIELD_TEMPLATE_PROPERTIES]

        # Primary entrypoint stays in `command`
        self.assertEqual(props[cfg.ACI_FIELD_CONTAINERS_COMMAND], ["python", "app.py"])

        # Only probe commands land in execProcesses
        proc_cmds = [
            p[cfg.ACI_FIELD_CONTAINERS_COMMAND]
            for p in props[cfg.ACI_FIELD_CONTAINERS_EXEC_PROCESSES]
        ]
        self.assertCountEqual(proc_cmds, [["echo", "alive"], ["echo", "ready"]])
        self.assertEqual(len(proc_cmds), 2)

    def test_volume_mount_basic_fields(self) -> None:
        props = self._new_cfg[cfg.ACI_FIELD_CONTAINERS][0][
            cfg.ACI_FIELD_TEMPLATE_PROPERTIES
        ]
        vm = props[cfg.ACI_FIELD_TEMPLATE_VOLUME_MOUNTS][0]

        self.assertEqual(vm[cfg.ACI_FIELD_CONTAINERS_ENVS_NAME], "azurefile")
        self.assertEqual(vm[cfg.ACI_FIELD_TEMPLATE_MOUNTS_PATH], "/mnt/af")
        self.assertEqual(vm[cfg.ACI_FIELD_TEMPLATE_MOUNTS_TYPE], "azureFile")
        self.assertTrue(vm[cfg.ACI_FIELD_TEMPLATE_MOUNTS_READONLY])

        vm = props[cfg.ACI_FIELD_TEMPLATE_VOLUME_MOUNTS][1]

        self.assertEqual(vm[cfg.ACI_FIELD_CONTAINERS_ENVS_NAME], "emptydir")
        self.assertEqual(vm[cfg.ACI_FIELD_TEMPLATE_MOUNTS_PATH], "/mnt/empty")
        self.assertEqual(vm[cfg.ACI_FIELD_TEMPLATE_MOUNTS_TYPE], "emptyDir")
        self.assertFalse(vm[cfg.ACI_FIELD_TEMPLATE_MOUNTS_READONLY])

    def test_workingdir_and_allow_elevated_migrated(self) -> None:
        props = self._new_cfg[cfg.ACI_FIELD_CONTAINERS][0][
            cfg.ACI_FIELD_TEMPLATE_PROPERTIES
        ]
        self.assertEqual(props[cfg.ACI_FIELD_CONTAINERS_WORKINGDIR], "/work")
        self.assertTrue(
            props[cfg.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT][
                cfg.ACI_FIELD_CONTAINERS_PRIVILEGED
            ]
        )

    def test_already_v1_returns_same_object(self) -> None:
        v1_in = {"version": "1.0", "fragments": [], "containers": []}
        v1_out = convert_config_v0_to_v1(copy.deepcopy(v1_in))
        self.assertEqual(v1_out, v1_in)
