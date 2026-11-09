# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Test-only fail-closed ownership ledger and coordinated terminal-job cleanup."""


class OwnedScenarioLedger:
    TERMINAL_JOB_STATES = frozenset(('Completed', 'Failed', 'CompletedWithWarnings', 'Canceled', 'Cancelled'))

    def __init__(self, plan_id, persist=lambda state: None):
        self.persist = persist
        self.state = {
            'planId': plan_id, 'creationConfirmed': False, 'actions': {},
            'assignments': {}, 'events': [], 'cleanup': 'NotStarted',
        }
        self.save()

    def save(self):
        self.persist(self.state)

    def action_started(self, key):
        self.state['actions'][key] = 'Pending'
        self.save()

    def confirm_creation_from_native(self, resource, expected_group):
        identity = resource.get('identity', {})
        group = resource.get('properties', {}).get('recoveryGroupsSetting', {}).get(
            'defaultGroup', {}).get('properties', {}).get('groupUniqueId')
        if (resource.get('id', '').lower() != self.state['planId'].lower()
                or not identity.get('principalId') or identity.get('type') != 'SystemAssigned'
                or not expected_group or group != expected_group):
            return False
        self.state.update(creationConfirmed=True, identityPrincipal=identity['principalId'],
                          groupUniqueId=expected_group)
        self.save()
        return True

    def action_resolved(self, key):
        self.state['actions'][key] = 'Resolved'
        self.save()

    def resolve_nonworkflow_terminal(self, key, monitor, expected_monitor_id):
        """Resolve cleanup uncertainty, NEVER replace failed native command output."""
        if (not key.startswith(('update ', 'identity ', 'finalize ', 'validate-for-', 'update-resource '))
                or monitor.get('status') not in ('Succeeded', 'Failed', 'Canceled', 'Cancelled')
                or monitor.get('resourceId', '').lower() != self.state['planId'].lower()
                or monitor.get('id', '').lower() != expected_monitor_id.lower()):
            return False
        self.state['events'].append({'cleanupOnlyTerminalProof': monitor, 'action': key})
        self.action_resolved(key)
        return True

    def assignment_intent(self, assignment_id, principal, scope, role):
        assert assignment_id not in self.state['assignments']
        self.state['assignments'][assignment_id] = {
            'id': assignment_id, 'principalId': principal, 'scope': scope,
            'roleDefinitionIdSuffix': '/' + role.lower(), 'status': 'Intended',
        }
        # Durable BEFORE the native PUT. Intended/ambiguous grants are never removed
        # automatically, even if the request may have succeeded before interruption.
        self.save()

    def assignment_confirmed(self, assignment_id, response):
        intent = self.state['assignments'][assignment_id]
        if (response.get('id', '').lower() != assignment_id.lower()
                or response.get('principalId', '').lower() != intent['principalId'].lower()
                or response.get('scope', '').lower() != intent['scope'].lower()
                or not response.get('roleDefinitionId', '').lower().endswith(intent['roleDefinitionIdSuffix'])):
            intent['status'] = 'Ambiguous'
            self.save()
            raise AssertionError('Native role response does not prove exact intended ownership.')
        intent['status'] = 'Confirmed'
        self.save()

    def assignment_ambiguous(self, assignment_id):
        self.state['assignments'][assignment_id]['status'] = 'Ambiguous'
        self.save()

    def blockers(self, snapshot):
        reasons = []
        if not self.state['creationConfirmed']:
            reasons.append('Plan creation not confirmed')
        if any(status != 'Resolved' for status in self.state['actions'].values()):
            reasons.append('Unresolved native operation')
        if any(grant['status'] not in ('Confirmed', 'Deleted') for grant in self.state['assignments'].values()):
            reasons.append('Unresolved assignment intent')
        if not isinstance(snapshot, dict) or snapshot.get('provisioningState') not in ('Succeeded', 'Failed'):
            reasons.append('Plan state unknown or nonterminal')
        if isinstance(snapshot, dict):
            for nonce in ('identityPrincipal', 'groupUniqueId'):
                if self.state.get(nonce) and snapshot.get(nonce) != self.state[nonce]:
                    reasons.append('Plan ownership nonce mismatch')
        jobs = snapshot.get('jobs') if isinstance(snapshot, dict) else None
        if not isinstance(jobs, list):
            reasons.append('Authoritative job inventory unavailable')
        else:
            for job in jobs:
                properties = job.get('properties', {})
                if (properties.get('resourceId', '').lower() != self.state['planId'].lower()
                        or not job.get('id', '').lower().startswith(self.state['planId'].lower() + '/recoveryjobs/')):
                    reasons.append('Job ownership mismatch')
                if properties.get('status') not in self.TERMINAL_JOB_STATES:
                    reasons.append('Active or unknown job status')
        return reasons

    def cleanup(self, read_snapshot, remove_assignment, delete_plan):
        """Recheck exact terminal state BEFORE each mutation; stop on any ambiguity."""
        try:
            reasons = self.blockers(read_snapshot())
            if reasons:
                self.state.update(cleanup='Retained', cleanupReasons=reasons)
                self.save()
                return False
            for assignment_id, grant in self.state['assignments'].items():
                if grant['status'] == 'Deleted':
                    continue
                reasons = self.blockers(read_snapshot())
                if reasons:
                    self.state.update(cleanup='Retained', cleanupReasons=reasons)
                    self.save()
                    return False
                grant['deleteStarted'] = True
                self.save()
                remove_assignment(assignment_id)
                grant['status'] = 'Deleted'
                self.save()
            reasons = self.blockers(read_snapshot())
            if reasons:
                self.state.update(cleanup='Retained', cleanupReasons=reasons)
                self.save()
                return False
            self.state['cleanup'] = 'PlanDeleteStarted'
            self.save()
            delete_plan()
            self.state['cleanup'] = 'VerifiedDeleted'
            self.save()
            return True
        except Exception as error:
            self.state.update(cleanup='Retained', cleanupReasons=[str(error)])
            self.save()
            return False
