# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import pytest
import json

from azext_confcom.security_policy import (
    UserContainerImage,
    OutputType,
    load_policy_from_str,
)

import azext_confcom.config as config
from azext_confcom.template_util import case_insensitive_dict_get

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


# @unittest.skip("not in use")
@pytest.mark.run(order=1)
class MountEnforcement(unittest.TestCase):
    custom_json = """
    {
        "version": "1.0",
        "containers": [
            {
                "containerImage": "rust:1.52.1",
                "environmentVariables": [
                    {
                        "name": "PATH",
                        "value": "/customized/path/value",
                        "strategy": "string"
                    },
                    {
                        "name": "TEST_REGEXP_ENV",
                        "value": "test_regexp_env_[[:alpha:]]*",
                        "strategy": "re2"
                    }
                ],
                "command": ["rustc", "--help"],
                "mounts": [
                    {
                        "mountType": "azureFile",
                        "mountPath": "/custom/azurefile/mount",
                        "readonly": true
                    }
                ]
            },
            {
                "containerImage": "python:3.6.14-slim-buster",
                "environmentVariables": [],
                "command": ["echo", "hello"],
                "workingDir": "/customized/absolute/path",
                "wait_mount_points": [
                    "/path/to/container/mount-1",
                    "/path/to/container/mount-2"
                ]
            }
        ]
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_str(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

    def test_user_container_customized_mounts(self):
        image = next(
            (
                img
                for img in self.aci_policy.get_images()
                if isinstance(img, UserContainerImage) and img.base == "rust"
            ),
            None,
        )

        self.assertIsNotNone(image)
        data = image.get_policy_json()

        self.assertEqual(
            len(
                case_insensitive_dict_get(
                    data, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS
                )
            ),
            2,
        )
        mount = case_insensitive_dict_get(
            data, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS
        )[0]
        self.assertIsNotNone(mount)
        self.assertEqual(
            case_insensitive_dict_get(mount, "source"),
            "sandbox:///tmp/atlas/azureFileVolume/.+",
        )
        self.assertEqual(
            case_insensitive_dict_get(
                mount, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION
            ),
            "/custom/azurefile/mount",
        )
        self.assertEqual(
            mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS][2], "ro"
        )

    def test_user_container_mount_injected_dns(self):
        image = next(
            (
                img
                for img in self.aci_policy.get_images()
                if isinstance(img, UserContainerImage) and img.base == "python"
            ),
            None,
        )

        self.assertIsNotNone(image)
        data = image.get_policy_json()
        self.assertEqual(
            len(
                case_insensitive_dict_get(
                    data, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS
                )
            ),
            1,
        )
        mount = case_insensitive_dict_get(
            data, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS
        )[0]
        self.assertIsNotNone(mount)
        self.assertEqual(
            case_insensitive_dict_get(
                mount, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_SOURCE
            ),
            "sandbox:///tmp/atlas/resolvconf/.+",
        )
        self.assertEqual(
            case_insensitive_dict_get(
                mount, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION
            ),
            "/etc/resolv.conf",
        )
        self.assertEqual(
            mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS][2], "rw"
        )


# @unittest.skip("not in use")
@pytest.mark.run(order=2)
class PolicyGenerating2(unittest.TestCase):
    custom_json = """
      {
        "version": "1.0",
        "containers": [
            {
                "containerImage": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201203.1",
                "environmentVariables": [
                {
                    "name": "IDENTITY_API_VERSION",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "IDENTITY_HEADER",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "IDENTITY_SERVER_THUMBPRINT",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "ACI_MI_CLIENT_ID_.+",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "ACI_MI_RES_ID_.+",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "HOSTNAME",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "TERM",
                    "value": "xterm",
                    "strategy": "string"
                },
                {
                    "name": "PATH",
                    "value": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                    "strategy": "string"
                },
                {
                    "name": "((?i)FABRIC)_.+",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "Fabric_Id+",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "Fabric_ServiceName",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "Fabric_ApplicationName",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "Fabric_CodePackageName",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "Fabric_ServiceDnsName",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "ACI_MI_DEFAULT",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "TokenProxyIpAddressEnvKeyName",
                    "value": "[ContainerToHostAddress|Fabric_NodelPOrFQDN]",
                    "strategy": "re2"
                },
                {
                    "name": "ContainerToHostAddress",
                    "value": "",
                    "strategy": "string"
                },
                {
                    "name": "Fabric_NetworkingMode",
                    "value": ".+",
                    "strategy": "re2"
                },
                {
                    "name": "azurecontainerinstance_restarted_by",
                    "value": ".+",
                    "strategy": "re2"
                }
            ],
            "command": ["/bin/sh","-c","until ./msiAtlasAdapter; do echo $? restarting; done"],
            "mounts": null
            }
        ]
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_str(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

    def test_injected_sidecar_container_msi(self):
        expected_sidecar_container_ser = "eyJjb250YWluZXJzIjp7ImVsZW1lbnRzIjp7IjAiOnsiYWxsb3dfZWxldmF0ZWQiOnRydWUsImFsbG93X3N0ZGlvX2FjY2VzcyI6dHJ1ZSwiY29tbWFuZCI6eyJlbGVtZW50cyI6eyIwIjoiL2Jpbi9zaCIsIjEiOiItYyIsIjIiOiJ1bnRpbCAuL21zaUF0bGFzQWRhcHRlcjsgZG8gZWNobyAkPyByZXN0YXJ0aW5nOyBkb25lIn0sImxlbmd0aCI6M30sImVudl9ydWxlcyI6eyJlbGVtZW50cyI6eyIwIjp7InBhdHRlcm4iOiJJREVOVElUWV9BUElfVkVSU0lPTj0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSwiMSI6eyJwYXR0ZXJuIjoiSURFTlRJVFlfSEVBREVSPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LCIxMCI6eyJwYXR0ZXJuIjoiRmFicmljX1NlcnZpY2VOYW1lPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LCIxMSI6eyJwYXR0ZXJuIjoiRmFicmljX0FwcGxpY2F0aW9uTmFtZT0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSwiMTIiOnsicGF0dGVybiI6IkZhYnJpY19Db2RlUGFja2FnZU5hbWU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0sIjEzIjp7InBhdHRlcm4iOiJGYWJyaWNfU2VydmljZURuc05hbWU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0sIjE0Ijp7InBhdHRlcm4iOiJBQ0lfTUlfREVGQVVMVD0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSwiMTUiOnsicGF0dGVybiI6IlRva2VuUHJveHlJcEFkZHJlc3NFbnZLZXlOYW1lPVtDb250YWluZXJUb0hvc3RBZGRyZXNzfEZhYnJpY19Ob2RlbFBPckZRRE5dIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LCIxNiI6eyJwYXR0ZXJuIjoiQ29udGFpbmVyVG9Ib3N0QWRkcmVzcz0iLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0sIjE3Ijp7InBhdHRlcm4iOiJGYWJyaWNfTmV0d29ya2luZ01vZGU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0sIjE4Ijp7InBhdHRlcm4iOiJhenVyZWNvbnRhaW5lcmluc3RhbmNlX3Jlc3RhcnRlZF9ieT0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSwiMiI6eyJwYXR0ZXJuIjoiSURFTlRJVFlfU0VSVkVSX1RIVU1CUFJJTlQ9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0sIjMiOnsicGF0dGVybiI6IkFDSV9NSV9DTElFTlRfSURfLis9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0sIjQiOnsicGF0dGVybiI6IkFDSV9NSV9SRVNfSURfLis9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0sIjUiOnsicGF0dGVybiI6IkhPU1ROQU1FPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LCI2Ijp7InBhdHRlcm4iOiJURVJNPXh0ZXJtIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LCI3Ijp7InBhdHRlcm4iOiJQQVRIPS91c3IvbG9jYWwvc2JpbjovdXNyL2xvY2FsL2JpbjovdXNyL3NiaW46L3Vzci9iaW46L3NiaW46L2JpbiIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSwiOCI6eyJwYXR0ZXJuIjoiKCg/aSlGQUJSSUMpXy4rPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LCI5Ijp7InBhdHRlcm4iOiJGYWJyaWNfSWQrPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9fSwibGVuZ3RoIjoxOX0sImV4ZWNfcHJvY2Vzc2VzIjp7ImVsZW1lbnRzIjp7fSwibGVuZ3RoIjowfSwiaWQiOiJtY3IubWljcm9zb2Z0LmNvbS9hY2kvbXNpLWF0bGFzLWFkYXB0ZXI6bWFzdGVyXzIwMjAxMjAzLjEiLCJsYXllcnMiOnsiZWxlbWVudHMiOnsiMCI6IjYwNmZkNmJhZjVlYjFhNzFmZDI4NmFlYTI5NjcyYTA2YmZlNTVmMDAwN2RlZDkyZWU3MzE0MmEzNzU5MGVkMTkiLCIxIjoiOTBhZDJmNWIyYzQyNWE3YzQ1OGY5ZjVkMjFjZjA2NGMyMTVmMTRlNDA2ODAwOTY4ZjY0NGQyYWIwYjRkMDRkZiIsIjIiOiIxYzRiNjM2NWE3YjkzODM4N2RmZDgyMjg2MmNhNDFhZTU0OTBiNTQ5MGU0YzI2ZWI0YjVkYTk2YzY0MDk2MGNmIn0sImxlbmd0aCI6M30sIm1vdW50cyI6eyJlbGVtZW50cyI6e30sImxlbmd0aCI6MH0sInNpZ25hbHMiOnsiZWxlbWVudHMiOnt9LCJsZW5ndGgiOjB9LCJ3b3JraW5nX2RpciI6Ii9yb290LyJ9fSwibGVuZ3RoIjoxfX0="
        image = self.aci_policy.get_images()[0]
        self.assertEqual(image.base, "mcr.microsoft.com/aci/msi-atlas-adapter")
        self.assertIsNotNone(image)
        
        self.maxDiff = None
        expected_workingdir = "/root/"
        self.assertEqual(image._workingDir, expected_workingdir)
        self.assertEqual(
            self.aci_policy.get_serialized_output(use_json=True),
            expected_sidecar_container_ser,
        )


# @unittest.skip("not in use")
@pytest.mark.run(order=12)
class PolicyGeneratingDebugMode(unittest.TestCase):
    custom_json = """
      {
        "version": "1.0",
        "containers": [
            {
                "containerImage": "python:3.6.14-slim-buster",
            "environmentVariables": [

            ],
            "command": ["python3"],
            "mounts": null
            }
        ]
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_str(cls.custom_json, debug_mode=True) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

    def test_logging_enabled(self):

        policy = self.aci_policy.get_serialized_output(
            output_type=OutputType.RAW, rego_boilerplate=True
        )
        self.assertIsNotNone(policy)

        expected_logging_string = "allow_runtime_logging := true"
        expected_properties_access = "allow_properties_access := true"
        expected_dump_stacks = "allow_dump_stacks := true"

        # make sure all these are included in the policy
        self.assertTrue(expected_logging_string in policy)
        self.assertTrue(expected_properties_access in policy)
        self.assertTrue(expected_dump_stacks in policy)


# @unittest.skip("not in use")
@pytest.mark.run(order=11)
class SidecarValidation(unittest.TestCase):
    custom_json = """
      {
    "version": "1.0",
    "containers": [
        {
            "containerImage": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1",
            "environmentVariables": [
                {
                    "name": "PATH",
                    "value": ".+",
                    "strategy": "re2"
                }
            ],
            "command": [
                "/bin/sh",
                "-c",
                "until ./msiAtlasAdapter; do echo $? restarting; done"
            ],
            "workingDir": "/root/",
            "mounts": null
        }
    ]
}
    """
    custom_json2 = """
      {
    "version": "1.0",
    "containers": [
        {
            "containerImage": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1",
            "environmentVariables": [
               {"name": "PATH",
               "value":"/",
               "strategy":"string"}
            ],
            "command": [
                "/bin/sh",
                "-c",
                "until ./msiAtlasAdapter; do echo $? restarting; done"
            ],
            "workingDir": "/root/",
            "mounts": null
        }
    ]
}
    """

    aci_policy = None
    existing_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_str(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy
        with load_policy_from_str(cls.custom_json2) as aci_policy2:
            aci_policy2.populate_policy_content_for_all_images()
            cls.aci_policy2 = aci_policy2

    def test_sidecar(self):
        is_valid, diff = self.aci_policy.validate_sidecars()
        self.assertTrue(is_valid)
        self.assertTrue(not diff)

    def test_sidecar_stdio_access_default(self):
        self.assertTrue(
            json.loads(
                self.aci_policy.get_serialized_output(
                    use_json=True, output_type=OutputType.RAW
                )
            )[config.POLICY_FIELD_CONTAINERS][config.POLICY_FIELD_CONTAINERS_ELEMENTS][
                "0"
            ][
                config.POLICY_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS
            ]
        )

    def test_incorrect_sidecar(self):

        is_valid, diff = self.aci_policy2.validate_sidecars()

        self.assertFalse(is_valid)
        expected_diff = {
            "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1": {
                "env_rules": [
                    "environment variable with rule "
                    + "'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'"
                    + " does not match strings or regex in policy rules"
                ]
            }
        }

        self.assertEqual(diff, expected_diff)


# @unittest.skip("not in use")
@pytest.mark.run(order=4)
class CustomJsonParsing(unittest.TestCase):
    def test_customized_workingdir(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "python:3.6.14-slim-buster",
                    "environmentVariables": [],
                    "command": ["echo", "hello"],
                    "workingDir": "/customized/absolute/path"
                }
            ]
        }
        """
        with load_policy_from_str(custom_json) as aci_policy:
            # pull actual image to local for next step
            image = next(
                (
                    img
                    for img in aci_policy.get_images()
                    if isinstance(img, UserContainerImage)
                ),
                None,
            )

            expected_working_dir = "/customized/absolute/path"
            self.assertEqual(image._workingDir, expected_working_dir)

    def test_allow_elevated(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "python:3.6.14-slim-buster",
                    "environmentVariables": [],
                    "command": ["echo", "hello"],
                    "workingDir": "/customized/absolute/path",
                    "allow_elevated": true
                }
            ]
        }
        """
        with load_policy_from_str(custom_json) as aci_policy:
            # pull actual image to local for next step
            image = next(
                (
                    img
                    for img in aci_policy.get_images()
                    if isinstance(img, UserContainerImage)
                ),
                None,
            )

            expected_allow_elevated = True
            self.assertEqual(image._allow_elevated, expected_allow_elevated)

    def test_image_layers_python(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "python:3.6.14-slim-buster",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_str(custom_json) as aci_policy:
            # pull actual image to local for next step
            aci_policy.pull_image(aci_policy.get_images()[0])
            aci_policy.populate_policy_content_for_all_images()
            layers = aci_policy.get_images()[0]._layers
            expected_layers = [
                "254cc853da6081905c9109c8b9d99c9fb0987ba1d88f729088903cffb80f55f1",
                "a568f1900bed60a0641b76b991ad431446d9c3a344d7b261f10de8d8e73763ac",
                "c70c530e842f66215b0bd955877157ba24c3799303567c3f5673c45663ea4d15",
                "3e86c3ccf1642bf584de33b49c7248f87eecd0f6d8c08353daa36cc7ad0a7b6a",
                "1e4684d8c7caa74c6524172b4d5a159a10887613ed70f18d0a55d05b2af61acd",
            ]
            self.assertEqual(len(layers), len(expected_layers))
            for i in range(len(expected_layers)):
                self.assertEqual(layers[i], expected_layers[i])

    def test_image_layers_rust(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "rust:1.52.1",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_str(custom_json) as aci_policy:
            # pull actual image to local for next step
            aci_policy.pull_image(aci_policy.get_images()[0])
            aci_policy.populate_policy_content_for_all_images()
            layers = aci_policy.get_images()[0]._layers

            expected_layers = [
                "fe84c9d5bfddd07a2624d00333cf13c1a9c941f3a261f13ead44fc6a93bc0e7a",
                "4dedae42847c704da891a28c25d32201a1ae440bce2aecccfa8e6f03b97a6a6c",
                "41d64cdeb347bf236b4c13b7403b633ff11f1cf94dbc7cf881a44d6da88c5156",
                "eb36921e1f82af46dfe248ef8f1b3afb6a5230a64181d960d10237a08cd73c79",
                "e769d7487cc314d3ee748a4440805317c19262c7acd2fdbdb0d47d2e4613a15c",
                "1b80f120dbd88e4355d6241b519c3e25290215c469516b49dece9cf07175a766",
            ]
            self.assertEqual(len(layers), len(expected_layers))
            for i in range(len(expected_layers)):
                self.assertEqual(layers[i], expected_layers[i])

    def test_docker_pull(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "rust:1.52.1",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_str(custom_json) as aci_policy:
            image = aci_policy.pull_image(aci_policy.get_images()[0])
            self.assertIsNotNone(image)
            self.assertEqual(
                image.id,
                "sha256:83ac22b6cf50c51a1d11b3220316be73271e59d30a65f33f4391dc4cfabdc856",
            )

    def test_environment_variables_parsing(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "mcr.microsoft.com/azuredocs/aci-dataprocessing-cc:v1",
                    "environmentVariables": [
                        {
                            "name": "env-name1",
                            "value": "env-val1",
                            "strategy": "string"
                        },
                        {
                            "name": "env-name2",
                            "value": "env-val2",
                            "strategy": "string"
                        }
                    ],
                    "command": ["python", "app.py"]
                }
            ]
        }
        """
        containers = load_policy_from_str(custom_json).get_images()
        self.assertEqual(len(containers), 1)
        envs = containers[0]._environmentRules
        self.assertIsNotNone(envs)

        self.assertEqual(
            len(
                [
                    x
                    for x in envs
                    if case_insensitive_dict_get(
                        x, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE
                    )
                    == "env-name1=env-val1"
                ]
            ),
            1,
        )

        self.assertEqual(
            len(
                [
                    x
                    for x in envs
                    if case_insensitive_dict_get(
                        x, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE
                    )
                    == "env-name2=env-val2"
                ]
            ),
            1,
        )

    def test_stdio_access_default(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "python:3.6.14-slim-buster",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_str(custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            self.assertTrue(
                json.loads(
                    aci_policy.get_serialized_output(use_json=True, output_type=OutputType.RAW)
                )[config.POLICY_FIELD_CONTAINERS][
                    config.POLICY_FIELD_CONTAINERS_ELEMENTS
                ][
                    "0"
                ][
                    config.POLICY_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS
                ]
            )

    def test_stdio_access_updated(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "python:3.6.14-slim-buster",
                    "environmentVariables": [],
                    "command": ["echo", "hello"],
                    "allowStdioAccess": false
                }
            ]
        }
        """
        with load_policy_from_str(custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()

            self.assertFalse(
                json.loads(
                    aci_policy.get_serialized_output(use_json=True, output_type=OutputType.RAW)
                )[config.POLICY_FIELD_CONTAINERS][
                    config.POLICY_FIELD_CONTAINERS_ELEMENTS
                ][
                    "0"
                ][
                    config.POLICY_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS
                ]
            )


# @unittest.skip("not in use")
@pytest.mark.run(order=5)
class CustomJsonParsingIncorrect(unittest.TestCase):
    def test_get_layers_from_not_exists_image(self):
        # if an image does not exists in local container repo/daemon, an
        # Exception will be raised
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "notexists:1.0.0",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_str(custom_json) as aci_policy:
            with self.assertRaises(SystemExit) as exc_info:
                aci_policy.populate_policy_content_for_all_images()
            self.assertEqual(exc_info.exception.code, 1)

    def test_incorrect_allow_elevated_data_type(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "rust:1.52.1",
                    "environmentVariables": [],
                    "command": "echo hello",
                    "workingDir": "relative/string/path",
                    "allow_elevated": "true"
                }
            ]
        }
        """
        # allow_elevated can only be a boolean
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_str(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_incorrect_workingdir_path(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "rust:1.52.1",
                    "environmentVariables": [],
                    "command": "echo hello",
                    "workingDir": "relative/string/path"
                }
            ]
        }
        """
        # workingDir can only be absolute path string
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_str(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_incorrect_workingdir_data_type(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "rust:1.52.1",
                    "environmentVariables": [],
                    "command": "echo hello",
                    "workingDir": ["hello"]
                }
            ]
        }
        """
        # workingDir can only be single string
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_str(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_incorrect_command_data_type(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "rust:1.52.1",
                    "environmentVariables": [],
                    "command": "echo hello"
                }
            ]
        }
        """
        # command can only be list of strings
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_str(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_json_missing_containers(self):
        custom_json = """
        {
            "version": "1.0"
        }
        """
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_str(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_json_missing_version(self):
        custom_json = """
        {
            "containers": [
                {
                    "containerImage": "mcr.microsoft.com/azuredocs/aci-dataprocessing-cc:v1",
                    "environmentVariables": [
                        {
                            "name": "port",
                            "value": "80",
                            "strategy": "string"
                        }
                    ],
                    "command": ["python", "app.py"]
                }
            ]
        }
        """
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_str(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_json_missing_containerImage(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "environmentVariables": [
                        {
                            "name": "port",
                            "value": "80",
                            "strategy": "string"
                        }
                    ],
                    "command": ["python", "app.py"]
                }
            ]
        }
        """
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_str(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_json_missing_environmentVariables(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "mcr.microsoft.com/azuredocs/aci-dataprocessing-cc:v1",
                    "command": ["python", "app.py"]
                }
            ]
        }
        """
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_str(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_json_missing_command(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "mcr.microsoft.com/azuredocs/aci-dataprocessing-cc:v1",
                    "environmentVariables": [
                        {
                            "name": "port",
                            "value": "80",
                            "strategy": "string"
                        }
                    ]
                }
            ]
        }
        """
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_str(custom_json)
        self.assertEqual(exc_info.exception.code, 1)
