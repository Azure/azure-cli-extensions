import mock

from azure_devtools.scenario_tests import mock_in_unit_test
from azure.cli.testsdk import ScenarioTest

from azext_ai_did_you_mean_this._cmd_table import CommandTable
from azext_ai_did_you_mean_this.tests.latest._mock import MOCK_UUID, MOCK_VERSION
from azext_ai_did_you_mean_this.custom import recommend_recovery_options

TELEMETRY_MODULE = 'azure.cli.core.telemetry'
TELEMETRY_SESSION_OBJECT = f'{TELEMETRY_MODULE}._session'


def patch_ids(unit_test):
    def _mock_uuid(*args, **kwargs):  # pylint: disable=unused-argument
        return MOCK_UUID

    mock_in_unit_test(unit_test,
                      f'{TELEMETRY_SESSION_OBJECT}.correlation_id',
                      _mock_uuid())
    mock_in_unit_test(unit_test,
                      f'{TELEMETRY_MODULE}._get_azure_subscription_id',
                      _mock_uuid)


def patch_version(unit_test):
    mock_in_unit_test(unit_test,
                      'azure.cli.core.__version__',
                      MOCK_VERSION)


class AladdinScenarioTest(ScenarioTest):
    def __init__(self, method_name, **kwargs):
        super().__init__(method_name, **kwargs)

        default_telemetry_patches = {
            patch_ids,
            patch_version
        }

        self._exception = None
        self._exit_code = None

        self.telemetry_patches = kwargs.pop('telemetry_patches', default_telemetry_patches)
        self.recommendations = []

    def setUp(self):
        super().setUp()

        for patch in self.telemetry_patches:
            patch(self)

    def cmd(self, command, checks=None, expect_failure=False, expect_user_fault_failure=False):
        func = recommend_recovery_options

        def _hook(*args, **kwargs):
            result = func(*args, **kwargs)
            self.recommendations.extend(result)
            return result

        with mock.patch('azext_ai_did_you_mean_this.custom.recommend_recovery_options', wraps=_hook):
            try:
                super().cmd(command, checks=checks, expect_failure=expect_failure)
            except SystemExit as ex:
                self._exception = ex
                self._exit_code = ex.code

                if expect_user_fault_failure:
                    self.assert_cmd_was_user_fault_failure()
                else:
                    raise

        if expect_user_fault_failure:
            self.assert_cmd_table_not_empty()

    def assert_cmd_was_user_fault_failure(self):
        is_user_fault_failure = (isinstance(self._exception, SystemExit) and
                                 self._exit_code == 2)

        self.assertTrue(is_user_fault_failure)

    def assert_cmd_table_not_empty(self):
        self.assertIsNotNone(CommandTable.CMD_TBL)

    @property
    def cli_version(self):
        from azure.cli.core import __version__ as core_version
        return core_version
