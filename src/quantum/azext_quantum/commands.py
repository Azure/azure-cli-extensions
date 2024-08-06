# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

import logging

from collections import OrderedDict
from azure.cli.core.commands import CliCommandType
from ._validators import validate_workspace_info, validate_target_info, validate_workspace_and_target_info, validate_workspace_info_no_location, validate_provider_and_sku_info

logger = logging.getLogger(__name__)


def transform_targets(providers):
    def one(provider, target):
        return OrderedDict([
            ('Provider', provider),
            ('Target-id', target['id']),
            ('Current Availability', target['currentAvailability']),
            ('Average Queue Time (seconds)', target['averageQueueTime'])
        ])

    return [
        one(provider['id'], target)
        for provider in providers
        for target in provider['targets']
    ]


def transform_job(result):
    transformed_result = OrderedDict([
        ('Name', result['name']),
        ('Id', result['id']),
        ('Status', result['status']),
        ('Target', result['target']),
        ('Submission time', result['creationTime']),
        ('Completion time', result['endExecutionTime'])
    ])

    # For backwards compatibility check if the field is present and only display if present
    cost_estimate = result['costEstimate']
    if cost_estimate is not None:
        amount = cost_estimate['estimatedTotal']
        currency = cost_estimate['currencyCode']
        if (amount is not None) and (currency is not None):
            price = str(amount) + ' ' + currency
            transformed_result['Cost estimate'] = price

    return transformed_result


def transform_jobs(results):
    def creation(job):
        return job['creationTime']

    return [transform_job(job) for job in sorted(results, key=creation, reverse=True)]


def transform_offerings(offerings):
    def one(offering):
        return OrderedDict([
            ('Provider ID', offering['id']),
            ('SKU', ', '.join([s['id'] for s in offering['properties']['skus']])),
            ('Publisher ID', offering['properties']['managedApplication']['publisherId']),
            ('Offer ID', offering['properties']['managedApplication']['offerId'])
        ])

    return [one(offering) for offering in offerings]


def transform_output(results):
    def one(key, value):
        repeat = round(20 * value)
        barra = "\u2588" * repeat
        return OrderedDict([
            ('Result', key),
            ('Frequency', f"{value:10.8f}"),
            ('', f"\u007C{barra:<20}\u007C")
        ])

    if 'Histogram' in results:
        histogram = results['Histogram']
        # The Histogram serialization is odd entries are key and even entries values
        # Make sure we have even entries
        if (len(histogram) % 2) == 0:
            table = []
            items = range(0, len(histogram), 2)
            for i in items:
                key = histogram[i]
                value = histogram[i + 1]
                table.append(one(key, value))
            return table

    elif 'histogram' in results:
        histogram = results['histogram']
        return [one(key, histogram[key]) for key in histogram]

    elif 'reportData' in results:
        table = []
        for group in results['reportData']['groups']:
            table.append(OrderedDict([
                ("Label", (f"---{group['title']}---")),
                ('Value', '---'),
                ('Description', '---')
            ]))
            for entry in group['entries']:
                val = results
                for key in entry['path'].split("/"):
                    val = val[key]
                table.append(OrderedDict([
                    ("Label", entry['label']),
                    ('Value', val),
                    ('Description', entry['description'])
                ]))
        return table

    elif isinstance(results, list) and len(results) > 0 and 'reportData' in results[0]:  # pylint: disable=too-many-nested-blocks
        table = []

        indices = range(len(results))

        for group_index, group in enumerate(results[0]['reportData']['groups']):
            table.append(OrderedDict([
                ("Label", f"---{group['title']}---"),
                *[(f"{i}", '---') for i in indices]
            ]))

            visited_entries = set()

            for entry in [entry for index in indices for entry in results[index]['reportData']['groups'][group_index]['entries']]:
                label = entry['label']
                if label in visited_entries:
                    continue
                visited_entries.add(label)

                row = [("Label", label)]

                for index in indices:
                    val = results[index]
                    for key in entry['path'].split("/"):
                        if key in val:
                            val = val[key]
                        else:
                            val = "N/A"
                            break
                    row.append((f"{index}", val))
                table.append(OrderedDict(row))

        return table

    elif 'errorData' in results:
        notFound = 'Not found'
        errorData = results['errorData']
        status = results.get('status', notFound)
        errorCode = errorData.get('code', notFound)
        errorMessage = errorData.get('message', notFound)
        target = results.get('target', notFound)
        jobId = results.get('id', notFound)
        submissionTime = results.get('creationTime', notFound)

        logger.error("Job was not successful. Job ID: %s, Status: %s, Error Code: %s, Error Message: %s, Target: %s", jobId, status, errorCode, errorMessage, target)
        return {'Status': status, 'Error Code': errorCode, 'Error Message': errorMessage, 'Target': target, 'Job ID': jobId, 'Submission Time': submissionTime}

    return results


def load_command_table(self, _):

    workspace_ops = CliCommandType(operations_tmpl='azext_quantum.operations.workspace#{}')
    job_ops = CliCommandType(operations_tmpl='azext_quantum.operations.job#{}')
    target_ops = CliCommandType(operations_tmpl='azext_quantum.operations.target#{}')
    offerings_ops = CliCommandType(operations_tmpl='azext_quantum.operations.offerings#{}')

    with self.command_group('quantum workspace', workspace_ops) as w:
        w.command('create', 'create')
        w.command('delete', 'delete', validator=validate_workspace_info_no_location)
        w.command('list', 'list')
        w.show_command('show', validator=validate_workspace_info_no_location)
        w.command('set', 'set', validator=validate_workspace_info)
        w.command('clear', 'clear')
        w.command('quotas', 'quotas', validator=validate_workspace_info)
        w.command('keys list', 'list_keys')
        w.command('keys regenerate', 'regenerate_keys')
        w.command('update', 'enable_keys')

    with self.command_group('quantum target', target_ops) as t:
        t.command('list', 'list', validator=validate_workspace_info, table_transformer=transform_targets)
        t.show_command('show', 'target_show', validator=validate_target_info)
        t.command('set', 'set', validator=validate_target_info)
        t.command('clear', 'clear')

    with self.command_group('quantum job', job_ops) as j:
        j.command('list', 'list', validator=validate_workspace_info, table_transformer=transform_jobs)
        j.show_command('show', 'job_show', validator=validate_workspace_info, table_transformer=transform_job)
        j.command('submit', 'submit', validator=validate_workspace_and_target_info, table_transformer=transform_job)
        j.command('wait', 'wait', validator=validate_workspace_info, table_transformer=transform_job)
        j.command('output', 'output', validator=validate_workspace_info, table_transformer=transform_output)
        j.command('cancel', 'cancel', validator=validate_workspace_info, table_transformer=transform_job)

    with self.command_group('quantum', job_ops, is_preview=True) as q:
        q.command('run', 'run', validator=validate_workspace_and_target_info, table_transformer=transform_output)
        q.command('execute', 'run', validator=validate_workspace_and_target_info, table_transformer=transform_output)

    with self.command_group('quantum offerings', offerings_ops) as o:
        o.command('list', 'list_offerings', table_transformer=transform_offerings)
        o.command('accept-terms', 'accept_terms', validator=validate_provider_and_sku_info)
        o.command('show-terms', 'show_terms', validator=validate_provider_and_sku_info)
