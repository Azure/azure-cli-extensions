# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json
import subprocess
from knack.util import CLIError

from azext_confcom.security_policy import (
    UserContainerImage,
    OutputType,
    load_policy_from_config_str
)

import azext_confcom.config as config
from azext_confcom.template_util import (
    case_insensitive_dict_get,
    extract_containers_and_fragments_from_text,
)
from azext_confcom.custom import acifragmentgen_confcom
from azure.cli.testsdk import ScenarioTest

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


class FragmentMountEnforcement(unittest.TestCase):
    custom_json = """
    {
        "version": "1.0",
        "containers": [
            {
                "name": "test-container",
                "properties": {
                    "image": "mcr.microsoft.com/cbl-mariner/distroless/minimal:2.0",
                    "environmentVariables": [
                        {
                            "name": "PATH",
                            "value": "/customized/path/value"
                        },
                        {
                            "name": "TEST_REGEXP_ENV",
                            "value": "test_regexp_env_[[:alpha:]]*",
                            "regex": true
                        }
                    ],
                    "command": ["rustc", "--help"],
                    "volumeMounts": [
                        {
                            "name": "azurefile",
                            "mountPath": "/mount/azurefile",
                            "mountType": "azureFile",
                            "readonly": true
                        }
                    ]
                }
            }
        ]
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_config_str(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

    def test_fragment_user_container_customized_mounts(self):
        image = next(
            (
                img
                for img in self.aci_policy.get_images()
                if isinstance(img, UserContainerImage) and img.base == "mcr.microsoft.com/cbl-mariner/distroless/minimal"
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
        resolv_mount = case_insensitive_dict_get(
            data, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS
        )[1]
        self.assertIsNotNone(resolv_mount)
        self.assertEqual(
            case_insensitive_dict_get(mount, "source"),
            "sandbox:///tmp/atlas/azureFileVolume/.+",
        )
        self.assertEqual(
            case_insensitive_dict_get(
                resolv_mount, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION
            ),
            "/etc/resolv.conf",
        )
        self.assertEqual(
            resolv_mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS][2], "rw"
        )

    def test_fragment_user_container_mount_injected_dns(self):
        image = next(
            (
                img
                for img in self.aci_policy.get_images()
                if isinstance(img, UserContainerImage) and img.base == "mcr.microsoft.com/cbl-mariner/distroless/minimal"
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
        )[1]
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


class FragmentGenerating(unittest.TestCase):
    custom_json = """
      {
        "version": "1.0",
        "containers": [
            {
                "name": "sidecar-container",
                "properties": {
                    "image": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201203.1",
                    "environmentVariables": [
                    {
                        "name": "IDENTITY_API_VERSION",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "IDENTITY_HEADER",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "IDENTITY_SERVER_THUMBPRINT",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "ACI_MI_CLIENT_ID_.+",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "ACI_MI_RES_ID_.+",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "HOSTNAME",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "TERM",
                        "value": "xterm",
                        "regex": false
                    },
                    {
                        "name": "PATH",
                        "value": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                    },
                    {
                        "name": "(?i)(FABRIC)_.+",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "Fabric_Id+",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "Fabric_ServiceName",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "Fabric_ApplicationName",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "Fabric_CodePackageName",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "Fabric_ServiceDnsName",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "ACI_MI_DEFAULT",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "TokenProxyIpAddressEnvKeyName",
                        "value": "[ContainerToHostAddress|Fabric_NodelPOrFQDN]",
                        "regex": true
                    },
                    {
                        "name": "ContainerToHostAddress",
                        "value": "sidecar-container"
                    },
                    {
                        "name": "Fabric_NetworkingMode",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "azurecontainerinstance_restarted_by",
                        "value": ".+",
                        "regex": true
                    }
                ],
                "command": ["/bin/sh","-c","until ./msiAtlasAdapter; do echo $? restarting; done"],
                "mounts": null
                }
            }
        ]
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_config_str(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

    def test_fragment_injected_sidecar_container_msi(self):
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
                "value": "sidecar-container",
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
        env_names = list(map(lambda x: x['pattern'], image._environmentRules + image._extraEnvironmentRules))
        for env_var in env_vars:
            self.assertIn(env_var['name'] + "=" + env_var['value'], env_names)

        expected_workingdir = "/root/"
        self.assertEqual(image._workingDir, expected_workingdir)


class FragmentPolicyGeneratingDebugMode(unittest.TestCase):
    custom_json = """
      {
        "version": "1.0",
        "containers": [
            {
            "name": "test-container",
            "properties": {
                    "image": "mcr.microsoft.com/cbl-mariner/distroless/minimal:2.0",
                "environmentVariables": [

                ],
                "command": ["python3"]
            }
        }
        ]
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_config_str(cls.custom_json, debug_mode=True) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

    def test_debug_processes(self):
        policy = self.aci_policy.get_serialized_output(
            output_type=OutputType.RAW, rego_boilerplate=True
        )
        self.assertIsNotNone(policy)

        # see if debug mode is enabled
        containers, _ = extract_containers_and_fragments_from_text(policy)

        self.assertTrue(containers[0]["allow_stdio_access"])
        self.assertTrue(containers[0]["exec_processes"][0]["command"] == ["/bin/sh"])


class FragmentSidecarValidation(unittest.TestCase):
    custom_json = """
      {
    "version": "1.0",
    "containers": [
        {
            "name": "test-container",
            "properties": {
                "image": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1",
                "environmentVariables": [
                    {
                        "name": "PATH",
                        "value": ".+",
                        "regex": true
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
        }
    ]
}
    """
    custom_json2 = """
      {
    "version": "1.0",
    "containers": [
        {
            "name": "test-container",
            "properties": {
                "image": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1",
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
        }
    ]
}
    """

    aci_policy = None
    existing_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_config_str(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy
        with load_policy_from_config_str(cls.custom_json2) as aci_policy2:
            aci_policy2.populate_policy_content_for_all_images()
            cls.aci_policy2 = aci_policy2

    def test_fragment_sidecar(self):
        is_valid, diff = self.aci_policy.validate_sidecars()
        self.assertTrue(is_valid)
        self.assertTrue(not diff)

    def test_fragment_sidecar_stdio_access_default(self):
        self.assertTrue(
            json.loads(
                self.aci_policy.get_serialized_output(
                    output_type=OutputType.RAW, rego_boilerplate=False
                )
            )[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_STDIO_ACCESS]
        )

    def test_fragment_incorrect_sidecar(self):

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


class InitialFragmentErrors(ScenarioTest):
    def test_invalid_input(self):
        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --image mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 -i fakepath/parameters.json --namespace fake_namespace --svn 1")
        self.assertEqual(wrapped_exit.exception.args[0], "Must provide either an image name or an input file to generate a fragment")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --generate-import --minimum-svn 1")
        self.assertEqual(wrapped_exit.exception.args[0], "Must provide either a fragment path, an input file, or " +
            "an image name to generate an import statement")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --image mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 -k fakepath/key.pem --namespace fake_namespace --svn 1")
        self.assertEqual(wrapped_exit.exception.args[0], "Must provide both --key and --chain to sign a fragment")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --fragment-path ./fragment.json --image mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 --namespace fake_namespace --svn 1 --minimum-svn 1")
        self.assertEqual(wrapped_exit.exception.args[0], "Must provide --generate-import to specify a fragment path")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --input ./input.json --namespace example --svn -1")
        self.assertEqual(wrapped_exit.exception.args[0], "--svn must be an integer")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --input ./input.json --namespace policy --svn 1")
        self.assertEqual(wrapped_exit.exception.args[0], "Namespace 'policy' is reserved")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --algo fake_algo --key ./key.pem --chain ./cert-chain.pem --namespace example --svn 1 -i ./input.json")
        self.assertEqual(wrapped_exit.exception.args[0], f"Algorithm 'fake_algo' is not supported. Supported algorithms are {config.SUPPORTED_ALGOS}")