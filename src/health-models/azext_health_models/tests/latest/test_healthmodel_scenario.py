# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Smoke tests for the AAZ-generated healthmodel command tree.

These tests exercise the CLI command surface via ``--help`` to confirm
the AAZ-generated commands load correctly without contacting Azure.
``--help`` always exits via ``SystemExit(0)`` — that is the success signal.

``HealthModelListRecordedTest`` exercises the AAZ HTTP path against a live
subscription and is recorded into a VCR cassette under ``recordings/``. The
``_HealthModelRedactProcessor`` strips tenant IDs, principal/client GUIDs,
resource-group names, health-model names, and managed-identity names from
recorded responses so the cassette is safe to commit.
"""

import re
import unittest

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import RecordingProcessor


class _HealthModelHelpBase(ScenarioTest):
    """Shared helper: ``--help`` succeeds iff the parser exits with status 0."""

    def _help(self, command):
        with self.assertRaises(SystemExit) as ctx:
            self.cmd(command)
        self.assertEqual(ctx.exception.code, 0)


class HealthModelHelpSmokeTest(_HealthModelHelpBase):

    def test_healthmodel_group_help(self):
        self._help('monitor health-models --help')

    def test_healthmodel_create_help(self):
        self._help('monitor health-models create --help')

    def test_healthmodel_entity_help(self):
        self._help('monitor health-models entity --help')

    def test_healthmodel_entity_create_help(self):
        self._help('monitor health-models entity create --help')

    def test_healthmodel_entity_ingest_health_report_help(self):
        self._help('monitor health-models entity ingest-health-report --help')

    def test_healthmodel_signaldefinition_create_help(self):
        # Discriminator polymorphism — verifies AAZ emitted the polymorphic args.
        self._help('monitor health-models signal-definition create --help')

    def test_healthmodel_discoveryrule_create_help(self):
        self._help('monitor health-models discovery-rule create --help')

    def test_healthmodel_authentication_setting_create_help(self):
        self._help('monitor health-models authentication-setting create --help')

    def test_healthmodel_relationship_create_help(self):
        self._help('monitor health-models relationship create --help')

    def test_healthmodel_identity_assign_help(self):
        self._help('monitor health-models identity assign --help')


class HealthModelArgValidationTest(ScenarioTest):
    """Missing required arguments must trigger a non-zero parser exit."""

    def _expect_arg_error(self, command):
        with self.assertRaises(SystemExit) as ctx:
            self.cmd(command)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_healthmodel_create_missing_args(self):
        self._expect_arg_error('monitor health-models create')

    def test_healthmodel_entity_create_missing_args(self):
        self._expect_arg_error('monitor health-models entity create')


class HealthModelDualRegistrationTest(_HealthModelHelpBase):
    """Verify only the discoverable ``az monitor health-models ...`` namespace
    is registered.

    Boundary: ``--help`` exits via ``SystemExit(0)`` for registered paths and
    non-zero for the retired standalone path. Loader-table assertions catch
    hidden duplicate registration that help smoke could miss.
    """

    def _unknown(self, command):
        with self.assertRaises(SystemExit) as ctx:
            self.cmd(command)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_monitor_root_help_and_direct_root_absent(self):
        self._help('monitor health-models --help')
        self._unknown('healthmodel --help')

    def test_monitor_subgroup_create_help(self):
        for group in (
            'entity',
            'signal-definition',
            'discovery-rule',
            'authentication-setting',
            'relationship',
        ):
            with self.subTest(group=group):
                self._help(f'monitor health-models {group} create --help')

    def test_monitor_identity_help(self):
        self._help('monitor health-models identity --help')

    def test_loader_command_table_is_monitor_only(self):
        from azext_health_models import HealthModelsCommandsLoader

        loader = HealthModelsCommandsLoader(cli_ctx=self.cli_ctx)
        loader.load_command_table(None)

        command_names = set(loader.command_table)
        group_names = set(loader.command_group_table)
        all_names = command_names | group_names

        self.assertIn('monitor health-models create', command_names)
        self.assertIn('monitor health-models entity create', command_names)
        self.assertIn('monitor health-models signal-definition create', command_names)
        self.assertIn('monitor health-models', group_names)
        self.assertEqual(
            [],
            sorted(
                name for name in all_names
                if name == 'healthmodel' or name.startswith('healthmodel ')
            ),
        )


class HealthModelListRecordedTest(ScenarioTest):
    """Recorded scenario test: ``az monitor health-models list`` against a live
    subscription, replayed from a VCR cassette on subsequent runs.

    Exercises the AAZ-generated ``HealthModelsListBySubscription`` HTTP path
    (URL build, response parse, pagination). Run once with
    ``AZURE_TEST_RUN_LIVE=true`` to (re-)record the cassette; subsequent runs
    replay offline.
    """

    def __init__(self, method_name):
        super().__init__(
            method_name,
            recording_processors=[_HealthModelRedactProcessor()],
            replay_processors=[_HealthModelRedactProcessor()],
        )

    def test_healthmodel_list_recorded(self):
        result = self.cmd(
            'monitor health-models list',
            checks=[self.check('type(@)', 'array')],
        ).get_output_in_json()
        self.assertIsInstance(result, list)


class HealthModelFullCrudRecordedTest(ScenarioTest):
    """Recorded scenario test: full create / update / show / delete cycle on a
    health model and its entity, replayed from a VCR cassette on subsequent
    runs.

    Exercises the AAZ-generated HTTP path end-to-end (URL build, polymorphic
    body serialization, response parse, LRO polling) for the most-used CRUD
    commands. Run once with ``AZURE_TEST_RUN_LIVE=true`` to (re-)record the
    cassette; subsequent runs replay offline.
    """

    def __init__(self, method_name):
        super().__init__(
            method_name,
            recording_processors=[_HealthModelRedactProcessor()],
            replay_processors=[_HealthModelRedactProcessor()],
        )

    @ResourceGroupPreparer(name_prefix='cli_test_healthmodel_crud', location='centralus')
    def test_healthmodel_crud_cycle(self, resource_group):
        self.kwargs.update({
            'model': self.create_random_name('clihm', 24),
            'entity': self.create_random_name('client', 24),
        })

        # ── Health model: create → show → update tags → list
        self.cmd(
            'monitor health-models create -g {rg} -n {model} --location centralus',
            checks=[
                self.check('name', '{model}'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('location', 'centralus'),
            ],
        )
        self.cmd(
            'monitor health-models show -g {rg} -n {model}',
            checks=[self.check('name', '{model}')],
        )
        self.cmd(
            'monitor health-models update -g {rg} -n {model} --tags env=test owner=cli',
            checks=[
                self.check('tags.env', 'test'),
                self.check('tags.owner', 'cli'),
            ],
        )
        self.cmd(
            'monitor health-models list -g {rg}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{model}'),
            ],
        )

        # ── Entity: create → show → list → delete
        self.cmd(
            'monitor health-models entity create -g {rg} --health-model-name {model} -n {entity} '
            '--display-name "CLI Test Entity" --impact Standard',
            checks=[
                self.check('name', '{entity}'),
                self.check('properties.displayName', 'CLI Test Entity'),
                self.check('properties.impact', 'Standard'),
            ],
        )
        self.cmd(
            'monitor health-models entity show -g {rg} --health-model-name {model} -n {entity}',
            checks=[self.check('name', '{entity}')],
        )
        self.cmd(
            'monitor health-models entity list -g {rg} --health-model-name {model}',
            checks=[self.greater_than('length(@)', 0)],
        )
        self.cmd(
            'monitor health-models entity delete -g {rg} --health-model-name {model} -n {entity} --yes'
        )

        # ── Health model: delete
        self.cmd('monitor health-models delete -g {rg} -n {model} --yes')


class _HealthModelRedactProcessor(RecordingProcessor):
    """Scrub tenant, principal/client GUIDs, RG names, model names, and
    managed-identity names from recorded responses.

    Default ``azure.cli.testsdk`` processors handle the subscription ID, AAD
    bearer tokens, and email addresses; they do NOT touch the tenant ID in
    the body, managed-identity GUIDs, or human-recognizable resource names.
    This processor closes that gap so the on-disk cassette only contains
    opaque placeholders.

    Applied at both record and replay time (idempotent — safe-GUID set is
    fixed and reapplying the substitutions on an already-clean cassette is a
    no-op).
    """

    # GUIDs already public-safe in the cassette and must be preserved.
    _SAFE_GUIDS = frozenset({
        '00000000-0000-0000-0000-000000000000',  # mocked subscription
    })
    _OPAQUE_GUID = '00000000-0000-0000-0000-000000000001'

    # Recognisable customer-facing names → opaque placeholders. Substring
    # replacements are applied longest-first so contained names (e.g.
    # ``hm-ai-gateway`` inside ``hm-ai-gateway-identity``) don't clobber the
    # outer name.
    _NAME_MAP = {
        # tenant
        '5380364e-35d4-4293-8bfe-fa76e835384e': _OPAQUE_GUID,
        # managed identities (longer than the model/RG names below)
        'id-healthmodel-ai-translator': 'cli-test-mi-001',
        'hm-ai-gateway-identity': 'cli-test-mi-002',
        'id-healthmodel-aon2': 'cli-test-mi-003',
        'mi-u7cggpq7qizqs': 'cli-test-mi-004',
        'id-hm-aidemo': 'cli-test-mi-005',
        # resource groups
        'lab-token-metrics-emitting': 'cli-test-rg-001',
        'lab-private-connectivity': 'cli-test-rg-002',
        'lab-message-storing-2': 'cli-test-rg-003',
        'lab-zero-to-production': 'cli-test-rg-004',
        'lab-finops-framework': 'cli-test-rg-005',
        'lab-built-in-logging': 'cli-test-rg-006',
        'ahm-kpi-reporting-rg': 'cli-test-rg-007',
        'rg-aon2-global': 'cli-test-rg-008',
        'rg-anbodemo2': 'cli-test-rg-009',
        'rg-anborobit': 'cli-test-rg-010',
        # health-model resource names
        'hm-canihazhouze': 'cli-test-hm-001',
        'hm-ai-translator': 'cli-test-hm-002',
        'hm-helloagents': 'cli-test-hm-003',
        'hm-helloorleons': 'cli-test-hm-004',
        'hm-graphorleons': 'cli-test-hm-005',
        'hm-ai-gateway': 'cli-test-hm-006',
        'hm-aidemo': 'cli-test-hm-007',
        'hm-darkux': 'cli-test-hm-008',
        'sd-test': 'cli-test-hm-009',
    }

    _GUID_RE = re.compile(
        r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
        r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
    )

    # Azure-internal request/correlation tracking IDs that leak via headers.
    _STRIP_HEADERS = (
        'x-ms-original-request-ids',
        'x-msedge-ref',
        'x-ms-correlation-request-id',
        'x-ms-request-id',
        'x-ms-routing-request-id',
        'x-ms-operation-identifier',          # leaks tenantId / objectId / region
        'x-ms-providerhub-traffic',           # internal RPaaS routing flag
        'x-ms-resource-provider-hint',        # internal RPaaS routing hint
        'x-ms-async-operation-timeout',       # LRO timing hint, not strictly leaky but noisy
    )

    def _scrub(self, text):
        # Longest-first ensures e.g. 'hm-ai-gateway-identity' is replaced
        # before its substring 'hm-ai-gateway'.
        for old, new in sorted(self._NAME_MAP.items(), key=lambda kv: -len(kv[0])):
            text = text.replace(old, new)
        text = self._GUID_RE.sub(
            lambda m: m.group()
            if m.group().lower() in self._SAFE_GUIDS or m.group() == self._OPAQUE_GUID
            else self._OPAQUE_GUID,
            text,
        )
        return text

    def process_response(self, response):
        body = response.get('body', {}).get('string', b'')
        if isinstance(body, bytes):
            response['body']['string'] = self._scrub(
                body.decode('utf-8', errors='replace')
            ).encode('utf-8')
        elif isinstance(body, str):
            response['body']['string'] = self._scrub(body)
        headers = response.get('headers', {})
        for header in self._STRIP_HEADERS:
            for key in list(headers.keys()):
                if key.lower() == header:
                    headers[key] = ['REDACTED']
        return response

    def process_request(self, request):
        # URLs are already sanitized by SubscriptionRecordingProcessor.
        return request


if __name__ == '__main__':
    unittest.main()
