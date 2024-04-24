# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json

from azext_confcom.security_policy import (
    UserContainerImage,
    OutputType,
    load_policy_from_str,
)

import azext_confcom.config as config
from azext_confcom.template_util import case_insensitive_dict_get

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


class MountEnforcement(unittest.TestCase):
    custom_json = """
    {
        "version": "1.0",
        "containers": [
            {
                "containerImage": "alpine:3.16",
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
                "containerImage": "nginx:1.24",
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
                if isinstance(img, UserContainerImage) and img.base == "alpine"
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
                if isinstance(img, UserContainerImage) and img.base == "nginx"
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


class PolicyGenerating(unittest.TestCase):
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
                    "name": "(?i)(FABRIC)_.+",
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
        image = self.aci_policy.get_images()[0]
        env_vars = [
            {
                "name": "IDENTITY_API_VERSION",
                "value": ".+",
            },
            {
                "name": "IDENTITY_HEADER",
                "value": ".+",
            },
            {
                "name": "IDENTITY_SERVER_THUMBPRINT",
                "value": ".+",
            },
            {
                "name": "ACI_MI_CLIENT_ID_.+",
                "value": ".+",
            },
            {
                "name": "ACI_MI_RES_ID_.+",
                "value": ".+",
            },
            {
                "name": "HOSTNAME",
                "value": ".+",
            },
            {
                "name": "TERM",
                "value": "xterm",
            },
            {
                "name": "PATH",
                "value": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            },
            {
                "name": "(?i)(FABRIC)_.+",
                "value": ".+",
            },
            {
                "name": "Fabric_Id+",
                "value": ".+",
            },
            {
                "name": "Fabric_ServiceName",
                "value": ".+",
            },
            {
                "name": "Fabric_ApplicationName",
                "value": ".+",
            },
            {
                "name": "Fabric_CodePackageName",
                "value": ".+",
            },
            {
                "name": "Fabric_ServiceDnsName",
                "value": ".+",
            },
            {
                "name": "ACI_MI_DEFAULT",
                "value": ".+",
            },
            {
                "name": "TokenProxyIpAddressEnvKeyName",
                "value": "[ContainerToHostAddress|Fabric_NodelPOrFQDN]",
            },
            {
                "name": "ContainerToHostAddress",
                "value": "",
            },
            {
                "name": "Fabric_NetworkingMode",
                "value": ".+",
            },
            {
                "name": "azurecontainerinstance_restarted_by",
                "value": ".+",
            }
        ]
        command = ["/bin/sh", "-c", "until ./msiAtlasAdapter; do echo $? restarting; done"]
        self.assertEqual(image.base, "mcr.microsoft.com/aci/msi-atlas-adapter")
        self.assertIsNotNone(image)

        self.assertEqual(image._command, command)
        for env_var in env_vars:
            env_names = map(lambda x: x['pattern'], image._environmentRules + image._extraEnvironmentRules)
            self.assertIn(env_var['name'] + "=" + env_var['value'], env_names)

        expected_workingdir = "/root/"
        self.assertEqual(image._workingDir, expected_workingdir)


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

    def test_debug_flags(self):

        policy = self.aci_policy.get_serialized_output(
            output_type=OutputType.RAW, rego_boilerplate=True
        )
        self.assertIsNotNone(policy)

        expected_logging_string = "allow_runtime_logging := true"
        expected_properties_access = "allow_properties_access := true"
        expected_dump_stacks = "allow_dump_stacks := true"
        expected_env_var_dropping = "allow_environment_variable_dropping := true"
        expected_capability_dropping = "allow_capability_dropping := true"
        expected_unencrypted_scratch = "allow_unencrypted_scratch := false"

        # make sure all these are included in the policy
        self.assertTrue(expected_logging_string in policy)
        self.assertTrue(expected_properties_access in policy)
        self.assertTrue(expected_dump_stacks in policy)
        self.assertTrue(expected_env_var_dropping in policy)
        self.assertTrue(expected_capability_dropping in policy)
        self.assertTrue(expected_unencrypted_scratch in policy)


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
                    output_type=OutputType.RAW, rego_boilerplate=False
                )
            )[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_STDIO_ACCESS]
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

    def test_image_layers_nginx(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "nginx:1.22",
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
                "5250e7d2517bcae4d264c84d8e7c6da14607ce867e29a81bf4327ee6896218a3",
                "b6d54ad6a7223dd687d308c8562aaa7dfef2f5a88ec701fb3f89e49312832b82",
                "8608c5be3af25ed58b2291999fe76cc021ced0ea70b6387c4373c6551f4d6ddb",
                "1e0878890d701c494c8aeade31d15eaaf9b9c382c27e2519727cb5d1e91df764",
                "233b6e2f8931a4d67930ac602688acc16c930926fcadc9e31195440db0737791",
                "1053a7714644b99537bc0e8058a7e4771d2fe679ef54097e128a813f3c80a9cf",
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
                    "containerImage": "alpine:3.16",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_str(custom_json) as aci_policy:
            image = aci_policy.pull_image(aci_policy.get_images()[0])
            self.assertIsNotNone(image.id)

            self.assertEqual(
                image.id,
                "sha256:d49a5025be10344cce77d178103a225cb5d7316861e5d8f106e7ff278ae51b62",
            )

    def test_infrastructure_svn(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "alpine:3.16",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_str(custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            output = aci_policy.get_serialized_output(OutputType.PRETTY_PRINT)

            self.assertTrue('"0.2.3"' in output)

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
                    aci_policy.get_serialized_output(
                        output_type=OutputType.RAW, rego_boilerplate=False
                    )
                )[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_STDIO_ACCESS]
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
                    aci_policy.get_serialized_output(
                        output_type=OutputType.RAW, rego_boilerplate=False
                    )
                )[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_STDIO_ACCESS]
            )


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
                    "containerImage": "alpine:3.16",
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
                    "containerImage": "alpine:3.16",
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
                    "containerImage": "alpine:3.16",
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
                    "containerImage": "alpine:3.16",
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
