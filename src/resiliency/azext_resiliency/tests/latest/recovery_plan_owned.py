"""One owned native Failover recording; historical scenarios are not collected."""

import hashlib
import sys
from pathlib import Path


from . import recovery_plan_safe as _safe_module


class ResiliencyFailoverOnly20261108Scenario(_safe_module.ResiliencySafeRecoveryPlanScenario):
    def setUp(self):
        super().setUp()
        modules = {}
        for name in ('azext_resiliency', 'azext_resiliency.custom',
                     'azext_resiliency.aaz.latest.resiliency.recovery_plan._failover',
                     'azext_resiliency.aaz.latest.resiliency.recovery_plan._update_resource'):
            module = __import__(name, fromlist=['__file__'])
            path = Path(module.__file__).resolve()
            modules[name] = {'path': str(path),
                             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        self._evidence('runtime-provenance', {'python': sys.version, 'modules': modules})

    def _storage(self):
        resources, selected = super()._storage()
        expected = self.automation_id.rsplit('/providers/', 1)[0] + (
            '/providers/Microsoft.Storage/storageAccounts/robcdrcustomersa1')
        self.assertEqual(selected['properties']['resourceId'].lower(), expected.lower(),
                         'Only the explicitly approved discovered storage may be selected.')
        return resources, selected

    def _coordinated_cleanup(self):
        result = self.ledger.cleanup(self._cleanup_snapshot, self._delete_role, self._delete)
        self._evidence('coordinated-cleanup', self.ledger.state)
        if self.successful_scenario:
            self.assertTrue(result, 'A passing scenario must verify terminal-gated cleanup.')

    def _delete_role(self, assignment_id):
        super()._delete_role(assignment_id)
        grant = self.ledger.state['assignments'][assignment_id]
        self.kwargs.update(assignment_scope=grant['scope'],
                           assignment_principal=grant['principalId'],
                           assignment_subscription=grant['scope'].split('/')[2])
        self.active_command = 'role assignment absence'
        remaining = self._role_cmd(
            'az role assignment list --scope {assignment_scope} '
            '--assignee-object-id {assignment_principal} --fill-principal-name false '
            '--fill-role-definition-name false --subscription {assignment_subscription}'
        ).get_output_in_json()
        self.assertFalse(any(item['id'].lower() == assignment_id.lower() for item in remaining))
        self._evidence('owned-role-absence', {'assignmentId': assignment_id, 'remaining': remaining})
