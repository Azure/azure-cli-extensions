# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from collections import OrderedDict
from azure.cli.core.commands import CliCommandType
from ._validators import validate_workspace_info, validate_target_info, validate_workspace_and_target_info


def transform_targets(providers):
    def one(provider, target):
        return OrderedDict([
            ('Provider', provider),
            ('Target-id', target['id']),
            ('Current Availability', target['currentAvailability']),
            ('Average Queue Time', target['averageQueueTime'])
        ])

    return [
        one(provider['id'], target)
        for provider in providers
        for target in provider['targets']
    ]


def transform_job(result):
    result = OrderedDict([
        ('Name', result['name']),
        ('Id', result['id']),
        ('Status', result['status']),
        ('Target', result['target']),
        ('Submission time', result['creationTime']),
        ('Completion time', result['endExecutionTime'])
    ])
    return result


def transform_jobs(results):
    def creation(job):
        return job['creationTime']

    return [transform_job(job) for job in sorted(results, key=creation, reverse=True)]


def transform_output(results):
    def one(key, value):
        repeat = round(20 * value)
        barra = "\u2588" * repeat
        return OrderedDict([
            ('Result', key),
            ('Frequency', f"{value:10.8f}"),
            ('', f"\u2590{barra:<22} |"),
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

    return results


def load_command_table(self, _):

    workspace_ops = CliCommandType(operations_tmpl='azext_quantum.operations.workspace#{}')
    job_ops = CliCommandType(operations_tmpl='azext_quantum.operations.job#{}')
    target_ops = CliCommandType(operations_tmpl='azext_quantum.operations.target#{}')

    with self.command_group('quantum workspace', workspace_ops) as w:
        w.command('list', 'list')
        w.command('show', 'show', validator=validate_workspace_info)
        w.command('set', 'set', validator=validate_workspace_info)
        w.command('clear', 'clear')

    with self.command_group('quantum target', target_ops) as t:
        t.command('list', 'list', validator=validate_workspace_info, table_transformer=transform_targets)
        t.command('show', 'show', validator=validate_target_info)
        t.command('set', 'set', validator=validate_target_info)
        t.command('clear', 'clear')

    with self.command_group('quantum job', job_ops) as j:
        j.command('list', 'list', validator=validate_workspace_info, table_transformer=transform_jobs)
        j.command('show', 'show', validator=validate_workspace_info, table_transformer=transform_job)
        j.command('submit', 'submit', validator=validate_workspace_and_target_info, table_transformer=transform_job)
        j.command('wait', 'wait', validator=validate_workspace_info, table_transformer=transform_job)
        j.command('output', 'output', validator=validate_workspace_info, table_transformer=transform_output)

    with self.command_group('quantum', job_ops, is_preview=True) as q:
        q.command('execute', 'execute', validator=validate_workspace_and_target_info, table_transformer=transform_output)
