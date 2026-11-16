# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Create one explicitly authorized failure runbook in the existing fixture account."""

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path


CONTENT = 'raise RuntimeError("Intentional CLI Drills validation fixture failure")\n'
DESCRIPTION = 'Owned CLI Drills validation intentional-failure fixture; no workload mutations.'
API_VERSION = '2023-11-01'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--az', required=True)
    parser.add_argument('--manifest', required=True, help='Existing private shared-UAI setup journal.')
    parser.add_argument('--name', required=True, help='One unique validation-owned runbook name.')
    parser.add_argument('--receipts', required=True, help='Private resumable provisioning journal.')
    args = parser.parse_args()
    if not args.name.startswith('ro-cli-drills-failure-') or any(char in args.name for char in '/\\?#%'):
        raise ValueError('Use a unique ro-cli-drills-failure-* name, without URL or path components.')
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    success = manifest['success']
    runbook_id = success['automationAccountId'] + '/runbooks/' + args.name
    endpoint = 'https://management.azure.com'
    url = endpoint + runbook_id + '?api-version=' + API_VERSION
    receipts = Path(args.receipts)
    receipts.parent.mkdir(parents=True, exist_ok=True)
    journal = json.loads(receipts.read_text()) if receipts.exists() else {
        'runbookId': runbook_id, 'ownedCreateRequested': False, 'commands': [], 'status': 'preflight'}
    if journal['runbookId'].lower() != runbook_id.lower():
        raise ValueError('Do not reuse a provisioning journal for another runbook.')

    def save():
        receipts.write_text(json.dumps(journal, indent=2), encoding='utf-8')

    def az(*command, allow_missing=False):
        journal['currentOperation'] = list(command)
        save()
        result = subprocess.run([args.az, *command, '--subscription', success['subscriptionId'],
                                 '--only-show-errors', '-o', 'json'],
                                capture_output=True, text=True, timeout=300)
        journal['commands'].append({'command': command, 'exitCode': result.returncode,
                                    'stdout': result.stdout, 'stderr': result.stderr})
        save()
        if result.returncode:
            if allow_missing and any(code in result.stderr for code in (
                    'ResourceNotFound', 'RunbookNotFound', '"code":"NotFound"')):
                return None
            raise RuntimeError('Native fixture setup failed; inspect private receipt ' + str(receipts))
        try:
            return json.loads(result.stdout) if result.stdout.strip() else None
        except ValueError:
            return result.stdout

    account = az('account', 'show')
    if account['tenantId'].lower() != manifest['tenantId'].lower():
        raise ValueError('The fixture and caller must share a tenant.')
    automation = az('rest', '--method', 'get', '--url',
                    endpoint + success['automationAccountId'] + '?api-version=' + API_VERSION)
    if automation['id'].lower() != success['automationAccountId'].lower():
        raise ValueError('The existing Automation account readback must match the supplied exact ID.')
    existing_success = az('rest', '--method', 'get', '--url',
                          endpoint + success['noOpRunbookId'] + '?api-version=' + API_VERSION)
    if (existing_success['properties']['runbookType'] != 'Python3'
            or existing_success['properties']['state'] != 'Published'):
        raise ValueError('The supplied existing success fixture must demonstrate published Python3 support.')
    if (existing_success['id'].lower() != success['noOpRunbookId'].lower()
            or existing_success['location'].lower() != automation['location'].lower()):
        raise ValueError('The existing success runbook must match its exact ID and parent account region.')
    journal['successRunbookBefore'] = existing_success
    current = az('rest', '--method', 'get', '--url', url, allow_missing=True)
    if current:
        if not journal['ownedCreateRequested'] or current['properties'].get('description') != DESCRIPTION:
            raise ValueError('Refusing to change an existing runbook without this exact owned provisioning journal.')
    else:
        journal['ownedCreateRequested'] = True
        save()
        # The protected storage/plan region may differ from the existing
        # Automation account region; child creation must use the account's location.
        body = {'location': automation['location'], 'properties': {
            'runbookType': 'Python3', 'logProgress': False, 'logVerbose': False,
            'description': DESCRIPTION}}
        try:
            current = az('rest', '--method', 'put', '--url', url, '--body', json.dumps(body))
        except RuntimeError:
            # A failed earlier child PUT can reserve an ARM location without
            # creating a runbook in the account. Repair ONLY this journal's
            # exact reservation, only if no create/content/publish ever succeeded.
            successful_writes = [entry for entry in journal['commands'] if entry['exitCode'] == 0
                                 and tuple(entry['command'][:3]) in (
                                     ('rest', '--method', 'put'), ('rest', '--method', 'post'))
                                 and any(runbook_id in argument for argument in entry['command'])]
            if 'InvalidResourceLocation' not in journal['commands'][-1]['stderr'] or successful_writes:
                raise
            journal['partialReservationRepair'] = 'Exact owned unpublished reservation; zero successful writes.'
            save()
            # A native 404 remains in receipts. It is not a successful create:
            # require both absence readback and a subsequent exact-ID PUT.
            az('rest', '--method', 'delete', '--url', url, allow_missing=True)
            if az('rest', '--method', 'get', '--url', url, allow_missing=True) is not None:
                raise ValueError('The exact failed reservation was not removed; do not create another name.')
            current = az('rest', '--method', 'put', '--url', url, '--body', json.dumps(body))
    if current['id'].lower() != runbook_id.lower() or current['properties']['runbookType'] != 'Python3':
        raise ValueError('Create/readback must identify the exact owned Python3 runbook.')
    # Resumption never creates another resource or republishes a verified fixture.
    if journal['status'] != 'verified':
        az('rest', '--method', 'put', '--url',
           endpoint + runbook_id + '/draft/content?api-version=' + API_VERSION,
           '--headers', 'Content-Type=text/plain', '--body', CONTENT)
        az('rest', '--method', 'post', '--url',
           endpoint + runbook_id + '/publish?api-version=' + API_VERSION)
    for _ in range(61):
        current = az('rest', '--method', 'get', '--url', url)
        if current['properties']['state'] == 'Published':
            break
        time.sleep(5)
    else:
        raise RuntimeError('The exact owned failure runbook did not become Published within the bounded poll.')
    if current['id'].lower() != runbook_id.lower() or current['properties']['runbookType'] != 'Python3':
        raise ValueError('Published readback must still identify the exact owned Python3 runbook.')
    published_content = az('rest', '--method', 'get', '--url',
                           endpoint + runbook_id + '/content?api-version=' + API_VERSION)
    if not isinstance(published_content, str) or published_content.strip() != CONTENT.strip():
        raise ValueError('Published content must be exactly the intentional-failure-only script.')
    after = az('rest', '--method', 'get', '--url',
               endpoint + success['noOpRunbookId'] + '?api-version=' + API_VERSION)
    if after != existing_success:
        raise ValueError('The existing success runbook metadata changed during fixture setup; inspect receipts.')
    failure = dict(success)
    failure['intentionalFailureRunbookId'] = runbook_id
    manifest.update(failure=failure, failureRunbookId=runbook_id,
                    failureRunbookProvisioningReceipt=str(receipts))
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    journal.update(status='verified', currentOperation=None, runbookReadback=current,
                   contentSha256=hashlib.sha256(CONTENT.encode('utf-8')).hexdigest(),
                   contentType='text/plain', runbookType='Python3', successRunbookUnchanged=True)
    save()
    print('One owned Python3 failure runbook published and exact content verified; existing success fixture unchanged.')


if __name__ == '__main__':
    main()
