# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import unittest

import azext_confcom.config as config
from azext_confcom.security_policy import (OutputType, UserContainerImage,
                                           load_policy_from_json)
from azext_confcom.template_util import DockerClient, case_insensitive_dict_get

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


class MountEnforcement(unittest.TestCase):
    custom_json = """
    {
        "version": "1.0",
        "containers": [
            {
                "name": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                "containerImage": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
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
                "name": "mcr.microsoft.com/azurelinux/base/python:3.12",
                "containerImage": "mcr.microsoft.com/azurelinux/base/python:3.12",
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
        with load_policy_from_json(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

    def test_user_container_customized_mounts(self):
        image = next(
            (
                img
                for img in self.aci_policy.get_images()
                if isinstance(img, UserContainerImage) and img.base == "mcr.microsoft.com/azurelinux/distroless/base"
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
                if isinstance(img, UserContainerImage) and img.base == "mcr.microsoft.com/azurelinux/base/python"
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
                "name": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201203.1",
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
        with load_policy_from_json(cls.custom_json) as aci_policy:
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
                "name": "mcr.microsoft.com/azurelinux/base/python:3.12",
                "containerImage": "mcr.microsoft.com/azurelinux/base/python:3.12",
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
        with load_policy_from_json(cls.custom_json, debug_mode=True) as aci_policy:
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
            "name": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1",
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
            "name": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1",
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
        with load_policy_from_json(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy
        with load_policy_from_json(cls.custom_json2) as aci_policy2:
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
                    "name": "mcr.microsoft.com/azurelinux/base/python:3.12",
                    "containerImage": "mcr.microsoft.com/azurelinux/base/python:3.12",
                    "environmentVariables": [],
                    "command": ["echo", "hello"],
                    "workingDir": "/customized/absolute/path"
                }
            ]
        }
        """
        with load_policy_from_json(custom_json) as aci_policy:
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
                    "name": "mcr.microsoft.com/azurelinux/base/python:3.12",
                    "containerImage": "mcr.microsoft.com/azurelinux/base/python:3.12",
                    "environmentVariables": [],
                    "command": ["echo", "hello"],
                    "workingDir": "/customized/absolute/path",
                    "allow_elevated": true
                }
            ]
        }
        """
        with load_policy_from_json(custom_json) as aci_policy:
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
                    "name": "mcr.microsoft.com/azurelinux/base/python:3.12",
                    "containerImage": "mcr.microsoft.com/azurelinux/base/python@sha256:ec2e8a66b7a5ad1da168bf13463e03ea79c3a18d7142818d52fbcc8772bbba8d",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_json(custom_json) as aci_policy:
            # pull actual image to local for next step
            with DockerClient() as client:
                image_ref = aci_policy.get_images()[0]
                image = client.images.pull(image_ref.containerImage)
            aci_policy.populate_policy_content_for_all_images()
            layers = aci_policy.get_images()[0]._layers
            expected_layers = [
                "679545575069dd4dc31f4d991094d669ca346950c3bc3aa465a9343a7369a8c9",
                "ff808293653ce6dc4aa63381a8ceaec73c15618bbc6ccb30a44441d638c07af7",
                "1dd5fd89c3a5a58b669d14d9a693aff3f16d3a8ec643c9d7f2d24f25297cfbc7"
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
                    "name": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "containerImage": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_json(custom_json) as aci_policy:
            with DockerClient() as client:
                image_ref = aci_policy.get_images()[0]
                image = client.images.pull(image_ref.base, tag=image_ref.tag)
            self.assertIsNotNone(image.id)

            self.assertEqual(
                image.tags[0],
                "mcr.microsoft.com/azurelinux/distroless/base:3.0",
            )

    def test_infrastructure_svn(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "name": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "containerImage": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_json(custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            output = aci_policy.get_serialized_output(OutputType.PRETTY_PRINT)

            self.assertTrue('"0.2.3"' in output)

    def test_environment_variables_parsing(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "name": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "containerImage": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
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
        containers = load_policy_from_json(custom_json).get_images()
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
                    "name": "mcr.microsoft.com/azurelinux/base/python:3.12",
                    "containerImage": "mcr.microsoft.com/azurelinux/base/python:3.12",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_json(custom_json) as aci_policy:
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
                    "name": "mcr.microsoft.com/azurelinux/base/python:3.12",
                    "containerImage": "mcr.microsoft.com/azurelinux/base/python:3.12",
                    "environmentVariables": [],
                    "command": ["echo", "hello"],
                    "allowStdioAccess": false
                }
            ]
        }
        """
        with load_policy_from_json(custom_json, disable_stdio=True) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()

            self.assertFalse(
                json.loads(
                    aci_policy.get_serialized_output(
                        output_type=OutputType.RAW, rego_boilerplate=False
                    )
                )[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_STDIO_ACCESS]
            )

    def test_omit_id(self):
        image_name = "mcr.microsoft.com/azurelinux/base/python:3.12"
        custom_json = f"""
        {{
            "version": "1.0",
            "containers": [
                {{
                    "name": "{image_name}",
                    "containerImage": "{image_name}",
                    "environmentVariables": [],
                    "command": ["echo", "hello"],
                    "allowStdioAccess": false
                }}
            ]
        }}
        """
        with load_policy_from_json(custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()

            self.assertIsNone(
                json.loads(
                    aci_policy.get_serialized_output(
                        output_type=OutputType.RAW, rego_boilerplate=False, omit_id=True
                    )
                )[0].get(config.POLICY_FIELD_CONTAINERS_ID)
            )

            self.assertEqual(
                json.loads(
                    aci_policy.get_serialized_output(
                        output_type=OutputType.RAW, rego_boilerplate=False, omit_id=False
                    )
                )[0].get(config.POLICY_FIELD_CONTAINERS_ID), image_name
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
                    "name": "fake-name",
                    "containerImage": "notexists:1.0.0",
                    "environmentVariables": [],
                    "command": ["echo", "hello"]
                }
            ]
        }
        """
        with load_policy_from_json(custom_json) as aci_policy:
            with self.assertRaises(SystemExit) as exc_info:
                aci_policy.populate_policy_content_for_all_images()
            self.assertEqual(exc_info.exception.code, 1)

    def test_incorrect_allow_elevated_data_type(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "name": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "containerImage": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
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
            load_policy_from_json(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_incorrect_workingdir_path(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "name": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "containerImage": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "environmentVariables": [],
                    "command": "echo hello",
                    "workingDir": "relative/string/path"
                }
            ]
        }
        """
        # workingDir can only be absolute path string
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_json(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_incorrect_workingdir_data_type(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "name": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "containerImage": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "environmentVariables": [],
                    "command": "echo hello",
                    "workingDir": ["hello"]
                }
            ]
        }
        """
        # workingDir can only be single string
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_json(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_incorrect_command_data_type(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "name": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "containerImage": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "environmentVariables": [],
                    "command": "echo hello"
                }
            ]
        }
        """
        # command can only be list of strings
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_json(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_json_missing_containers(self):
        custom_json = """
        {
            "version": "1.0"
        }
        """
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_json(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_json_missing_containerImage(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "name": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
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
            load_policy_from_json(custom_json)
        self.assertEqual(exc_info.exception.code, 1)

    def test_json_missing_environmentVariables(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "name": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "containerImage": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "command": ["python", "app.py"]
                }
            ]
        }
        """
        with load_policy_from_json(custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()

            self.assertIsNotNone(
                json.loads(
                    aci_policy.get_serialized_output(
                        output_type=OutputType.RAW, rego_boilerplate=False, omit_id=True
                    )
                )[0].get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS)
            )


    def test_json_missing_command(self):
        custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "name": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1",
                    "containerImage": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1",
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
        with load_policy_from_json(custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()

            self.assertIsNotNone(
                json.loads(
                    aci_policy.get_serialized_output(
                        output_type=OutputType.RAW, rego_boilerplate=False, omit_id=True
                    )
                )[0].get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_COMMANDS)
            )


