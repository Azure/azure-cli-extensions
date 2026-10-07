import re
import unittest

from azure.cli.core.mock import DummyCli

from azext_redisenterprise import RedisEnterpriseManagementClientCommandsLoader
from azext_redisenterprise.aaz.latest.redisenterprise.database.access_policy_assignment._create import Create
from azext_redisenterprise.aaz.latest.redisenterprise.database.access_policy_assignment._delete import Delete
from azext_redisenterprise.aaz.latest.redisenterprise.database.access_policy_assignment._show import Show
from azext_redisenterprise.aaz.latest.redisenterprise.database.access_policy_assignment._update import Update
from azext_redisenterprise.aaz.latest.redisenterprise.database.access_policy_assignment._wait import Wait


GUID_NAME = "76e670c5-eaf4-4674-8a48-2def9d37929c"


class TestAccessPolicyAssignmentNameFormat(unittest.TestCase):

    def setUp(self):
        self.cli_ctx = DummyCli()
        self.loader = RedisEnterpriseManagementClientCommandsLoader(cli_ctx=self.cli_ctx)

    def test_guid_name_is_allowed_for_all_access_policy_assignment_commands(self):
        for command_cls in [Create, Delete, Show, Update, Wait]:
            with self.subTest(command=command_cls.__name__):
                if command_cls is Wait:
                    cmd = command_cls(loader=self.loader)
                else:
                    cmd = command_cls(loader=self.loader, cli_ctx=self.cli_ctx)
                args_schema = cmd._build_arguments_schema()
                pattern = args_schema.access_policy_assignment_name._fmt._pattern
                self.assertRegex(GUID_NAME, re.compile(pattern))
