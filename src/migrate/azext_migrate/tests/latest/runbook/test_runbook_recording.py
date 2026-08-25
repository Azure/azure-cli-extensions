# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Recorded ScenarioTests for the ``az migrate runbook`` commands.

Runbooks require a pre-existing migrate project + wave (a
``ResourceGroupPreparer`` cannot provision those), so these scenarios target
fixed, pre-provisioned resources. Override the defaults at RECORD time with
env vars (see below); the subscription id and SAS/cert secrets are scrubbed,
so PLAYBACK needs no live resources or credentials.

    AZURE_MIGRATE_TEST_RG        resource group of the migrate project
    AZURE_MIGRATE_TEST_PROJECT   migrate project name
    AZURE_MIGRATE_TEST_WAVE      wave to generate runbooks from
    AZURE_MIGRATE_TEST_RUNBOOK   an existing runbook (read-only scenarios)
    AZURE_MIGRATE_TEST_EXECUTION an existing execution id (read scenarios)

Recording model:
* Pure-ARM commands (generate/show/list/update/delete/regenerate,
  execution list) record to a cassette and replay offline in CI.
* Commands that fetch/put a SAS blob (definition show/download, parameter
  and execution-parameter download/upload, execution show/visualize) do
  their blob I/O via ``urllib`` -- which the CLI test recorder does NOT
  intercept -- so they are marked ``@live_only`` and are never replayed.
"""

import os
import re
import unittest

from azure.cli.testsdk import ScenarioTest, live_only
from azure.cli.testsdk.scenario_tests import RecordingProcessor

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

RUNBOOK_TYPE = 'Microsoft.Migrate/MigrateProjects/Runbooks'


def _cfg(name, default):
    return os.environ.get(name, default)


PROJECT_RG = _cfg('AZURE_MIGRATE_TEST_RG', 'wave-runbooks-rg')
PROJECT_NAME = _cfg('AZURE_MIGRATE_TEST_PROJECT', 'wave-runbooks-project')
WAVE_NAME = _cfg('AZURE_MIGRATE_TEST_WAVE', 'wave-runbook-01')
RUNBOOK_NAME = _cfg('AZURE_MIGRATE_TEST_RUNBOOK', 'runbook-01')
EXECUTION_ID = _cfg('AZURE_MIGRATE_TEST_EXECUTION', 'exec-01')


class _SasScrubber(RecordingProcessor):
    """Redact SAS signatures, async-op signing blobs and storage hosts.

    The runbook LRO poll URLs (Location/Azure-AsyncOperation) carry large
    ``c=``/``s=``/``h=`` signing blobs, and download responses carry a
    ``sasUrl`` with a live ``sig=`` token; none of these must land in a
    committed cassette.
    """

    _BLOB_HOST = re.compile(
        r'https://[a-z0-9]+\.blob\.core\.windows\.net')

    def _scrub(self, text):
        if not text:
            return text
        text = re.sub(r'(sig=)[^&"\s\\]+', r'\1REDACTED', text)
        text = re.sub(r'([?&](?:c|s|h)=)[^&"\s\\]+', r'\1REDACTED', text)
        text = self._BLOB_HOST.sub(
            'https://mockstorage.blob.core.windows.net', text)
        return text

    def process_request(self, request):
        request.uri = self._scrub(request.uri)
        if isinstance(request.body, bytes):
            try:
                request.body = self._scrub(
                    request.body.decode('utf-8')).encode('utf-8')
            except UnicodeDecodeError:
                pass
        elif isinstance(request.body, str):
            request.body = self._scrub(request.body)
        return request

    def process_response(self, response):
        body = (response.get('body') or {}).get('string')
        if body:
            response['body']['string'] = self._scrub(body)
        return response


class _RunbookScenario(ScenarioTest):
    """Base ScenarioTest that installs the SAS/cert scrubber."""

    def __init__(self, method_name):
        super().__init__(
            method_name, recording_processors=[_SasScrubber()])


# TODO(runbook): record cassettes against a live migrate project + wave,
# then drop @live_only so these replay offline in CI. Until a cassette
# exists the framework would run them live and fail on CI's empty sub.
@live_only()
class RunbookReadScenario(_RunbookScenario):

    def test_runbook_show_and_list(self):
        self.kwargs.update({
            'rg': PROJECT_RG,
            'project': PROJECT_NAME,
            'name': RUNBOOK_NAME,
        })
        self.cmd(
            'migrate runbook show -g {rg} --project-name {project} '
            '-n {name}',
            checks=[
                self.check('name', '{name}'),
                self.check('type', RUNBOOK_TYPE),
            ])
        self.cmd(
            'migrate runbook list -g {rg} --project-name {project}',
            checks=[self.check("length([?name=='{name}'])", 1)])


@live_only()
class RunbookCrudScenario(_RunbookScenario):

    def test_runbook_generate_update_delete(self):
        self.kwargs.update({
            'rg': PROJECT_RG,
            'project': PROJECT_NAME,
            'wave': WAVE_NAME,
            'name': self.create_random_name('cli-rb-', 20),
        })
        self.cmd(
            'migrate runbook generate -g {rg} --project-name {project} '
            '-n {name} --wave-name {wave}',
            checks=[
                self.check('name', '{name}'),
                self.check('type', RUNBOOK_TYPE),
            ])
        self.cmd(
            'migrate runbook show -g {rg} --project-name {project} '
            '-n {name}',
            checks=[self.check('name', '{name}')])
        self.cmd(
            'migrate runbook list -g {rg} --project-name {project}',
            checks=[self.check("length([?name=='{name}'])", 1)])
        self.cmd(
            'migrate runbook update -g {rg} --project-name {project} '
            '-n {name} --description "recorded by scenario test"',
            checks=[self.check(
                'properties.description', 'recorded by scenario test')])
        self.cmd(
            'migrate runbook delete -g {rg} --project-name {project} '
            '-n {name} --yes')
        self.cmd(
            'migrate runbook list -g {rg} --project-name {project}',
            checks=[self.check("length([?name=='{name}'])", 0)])


@live_only()
class RunbookExecutionReadScenario(_RunbookScenario):

    def test_execution_list(self):
        self.kwargs.update({
            'rg': PROJECT_RG,
            'project': PROJECT_NAME,
            'runbook': RUNBOOK_NAME,
        })
        self.cmd(
            'migrate runbook execution list -g {rg} '
            '--project-name {project} --runbook-name {runbook}')


# ---------------------------------------------------------------------------
# Live-only scenarios: these fetch/put a SAS blob (or run a real migration),
# which the CLI test recorder does not intercept, so they cannot be replayed
# from a cassette. Run them with --live against a prepared subscription.
# ---------------------------------------------------------------------------

@live_only()
class RunbookArtifactLiveScenario(ScenarioTest):
    """definition show/download + parameter download go through a SAS blob."""

    def test_definition_show_and_download(self):
        import tempfile
        self.kwargs.update({
            'rg': PROJECT_RG,
            'project': PROJECT_NAME,
            'name': RUNBOOK_NAME,
            'dest': tempfile.mkdtemp(),
        })
        self.cmd(
            'migrate runbook definition show -g {rg} '
            '--project-name {project} -n {name}')
        self.cmd(
            'migrate runbook definition download -g {rg} '
            '--project-name {project} -n {name} --destination {dest}')

    def test_parameter_download(self):
        import tempfile
        self.kwargs.update({
            'rg': PROJECT_RG,
            'project': PROJECT_NAME,
            'runbook': RUNBOOK_NAME,
            'dest': tempfile.mkdtemp(),
        })
        self.cmd(
            'migrate runbook parameter download -g {rg} '
            '--project-name {project} --runbook-name {runbook} '
            '--file {dest}')


@live_only()
class RunbookExecutionLiveScenario(ScenarioTest):
    """Execution status needs live, running state and a SAS status blob."""

    def test_execution_show(self):
        self.kwargs.update({
            'rg': PROJECT_RG,
            'project': PROJECT_NAME,
            'runbook': RUNBOOK_NAME,
            'execution': EXECUTION_ID,
        })
        self.cmd(
            'migrate runbook execution show -g {rg} '
            '--project-name {project} --runbook-name {runbook} '
            '--execution-id {execution}')


if __name__ == '__main__':
    unittest.main()
