from pathlib import Path
import unittest

from azext_aosm.template_parsers.arm_parser import ArmParser


class ArmParserTest(unittest.TestCase):
    here = Path(__file__).parent
    arm_parser = ArmParser(here / "mock_vnf/ubuntu-template.json")

    assert arm_parser.get_defaults() == None
    assert arm_parser.get_schema() == {'location': {'type': 'string', 'defaultValue': '[resourceGroup().location]'}, 'subnetName': {'type': 'string'}, 'ubuntuVmName': {'type': 'string', 'defaultValue': 'ubuntu-vm'}, 'virtualNetworkId': {'type': 'string'}, 'sshPublicKeyAdmin': {'type': 'string'}, 'imageName': {'type': 'string'}}
