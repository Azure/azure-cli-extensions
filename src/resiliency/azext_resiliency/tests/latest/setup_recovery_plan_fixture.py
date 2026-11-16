# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Explicit, serial native-CLI setup. Keep manifests and command receipts private."""

import argparse
import json
import subprocess
import uuid
from pathlib import Path


JOB_OPERATOR = '4fe576fe-1146-4730-92eb-48519fa6bf9f'
READER = 'acdd72a7-3385-48ef-bd42-f606fba81ae7'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--az', required=True)
    parser.add_argument('--success-fixture', required=True)
    parser.add_argument('--failure-fixture', help='Optional existing failure-runbook fixture for Retry coverage.')
    parser.add_argument('--identity-name', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError('Refusing to overwrite an existing setup journal; use its exact IDs for readback.')
    success = json.loads(Path(args.success_fixture).read_text(encoding='utf-8-sig'))
    failure = (json.loads(Path(args.failure_fixture).read_text(encoding='utf-8-sig'))
               if args.failure_fixture else None)
    fixtures = [fixture for fixture in (success, failure) if fixture]
    journal = {'status': 'started', 'commands': [], 'grants': [], 'success': success, 'failure': failure}
    output.parent.mkdir(parents=True, exist_ok=True)

    def save():
        output.write_text(json.dumps(journal, indent=2), encoding='utf-8')

    def az(*command):
        journal['currentOperation'] = list(command)
        save()
        result = subprocess.run([args.az, *command, '--only-show-errors', '-o', 'json'],
                                capture_output=True, text=True, timeout=300, check=False)
        journal['commands'].append({'command': command, 'exitCode': result.returncode,
                                    'stdout': result.stdout, 'stderr': result.stderr})
        save()
        result.check_returncode()
        return json.loads(result.stdout) if result.stdout.strip() else None

    save()
    account = az('account', 'show')
    for fixture in fixtures:
        context = az('account', 'show', '--subscription', fixture['subscriptionId'])
        if context['tenantId'].lower() != account['tenantId'].lower():
            raise ValueError('Fixtures and caller must be in one tenant.')
        if fixture['tenantId'].lower() != context['tenantId'].lower():
            raise ValueError('Fixture tenant disagrees with native subscription metadata.')
        az('resource', 'show', '--ids', fixture['automationAccountId'], '--subscription', fixture['subscriptionId'])
        az('resource', 'show', '--ids', fixture['storageAccountId'], '--subscription', fixture['subscriptionId'])
        for key in ('noOpRunbookId', 'intentionalFailureRunbookId'):
            if fixture.get(key):
                prefix = fixture['automationAccountId'] + '/runbooks/'
                if not fixture[key].lower().startswith(prefix.lower()):
                    raise ValueError('Runbook must be a child of the supplied existing account.')
                az('resource', 'show', '--ids', fixture[key], '--api-version', '2023-11-01',
                   '--subscription', fixture['subscriptionId'])
    rg = az('group', 'show', '-n', success['resourceGroup'], '--subscription', success['subscriptionId'])
    # Carry existing policy-required fixture tags; this creates no resource group.
    tags = ['{}={}'.format(key, value) for key, value in (rg.get('tags') or {}).items()]
    command = ['identity', 'create', '-g', success['resourceGroup'], '-n', args.identity_name,
               '-l', success['region'], '--subscription', success['subscriptionId']]
    if tags:
        command += ['--tags', *tags]
    # One create only. A partial setup must be inspected, not rerun with another identity.
    identity = az(*command)
    journal['identity'] = identity
    save()
    grant_specs = set()
    for fixture in fixtures:
        grant_specs.update(((fixture['automationAccountId'], JOB_OPERATOR),
                            (fixture['automationAccountId'], READER),
                            (fixture['storageAccountId'], READER)))
    for scope, role in sorted(grant_specs):
        subscription = scope.split('/')[2]
        name = str(uuid.uuid4())
        grant_id = scope + '/providers/Microsoft.Authorization/roleAssignments/' + name
        journal['grants'].append({'id': grant_id, 'scope': scope, 'role': role, 'status': 'creating'})
        save()
        assignment = az('role', 'assignment', 'create', '--name', name, '--scope', scope, '--role', role,
                        '--assignee-object-id', identity['principalId'],
                        '--assignee-principal-type', 'ServicePrincipal', '--subscription', subscription)
        if assignment['id'].lower() != grant_id.lower():
            raise ValueError('Role assignment did not return the exact requested ID.')
        readback = az('resource', 'show', '--ids', grant_id, '--api-version', '2022-04-01',
                      '--subscription', subscription)
        properties = readback['properties']
        if (properties['principalId'].lower() != identity['principalId'].lower()
                or properties['scope'].lower() != scope.lower()
                or not properties['roleDefinitionId'].lower().endswith('/' + role)):
            raise ValueError('Exact grant readback did not match principal/scope/role.')
        journal['grants'][-1]['status'] = 'verified'
        save()
    journal.update(status='configured_unproven', currentOperation=None,
                   subscriptionId=success['subscriptionId'], tenantId=account['tenantId'])
    save()
    print('Shared identity and exact narrow grants configured; execution/cleanup proof still required.')


if __name__ == '__main__':
    main()
