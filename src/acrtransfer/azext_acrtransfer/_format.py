# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from collections import OrderedDict
from knack.log import get_logger

logger = get_logger(__name__)


def import_pipeline_output_format(result):
    return _output_format(result, _import_pipeline_format_group)


def export_pipeline_output_format(result):
    return _output_format(result, _export_pipeline_format_group)


def pipeline_run_output_format(result):

    return _output_format(result, _pipeline_run_format_group)


def _import_pipeline_format_group(item):
    return OrderedDict([
        ('NAME', _get_value(item, 'name')),
        ('PROVISIONING_STATE', _get_value(item, 'provisioningState')),
        ('STORAGE_ACCOUNT', _get_value(item, 'source', 'uri')),
        ('SOURCE_TRIGGER', _get_value(item, 'trigger', 'sourceTrigger', 'status'))
    ])


def _export_pipeline_format_group(item):
    return OrderedDict([
        ('NAME', _get_value(item, 'name')),
        ('PROVISIONING_STATE', _get_value(item, 'provisioningState')),
        ('STORAGE_ACCOUNT', _get_value(item, 'target', 'uri'))
    ])


def _pipeline_run_format_group(item):
    if "importPipelines" in _get_value(item, 'request', 'pipelineResourceId'):
        d = OrderedDict([
            ('NAME', _get_value(item, 'name')),
            ('PIPELINE', _get_value(item, 'request', 'pipelineResourceId').split('/', maxsplit=-1)[-1]),
            ('START_TIME', _get_value(item, 'response', 'startTime').split('.', maxsplit=1)[0]),
            ('DURATION', _get_duration(_get_value(item, 'response', 'startTime'), _get_value(item, 'response', 'finishTime'))),
            ('SOURCE_TRIGGER', str('_' in _get_value(item, 'name'))),
            ('STATUS', _get_value(item, 'response', 'status')),
            ('ERROR_MESSAGE', _get_value(item, 'response', 'pipelineRunErrorMessage'))
        ])

    else:
        d = OrderedDict([
            ('NAME', _get_value(item, 'name')),
            ('PIPELINE', _get_value(item, 'request', 'pipelineResourceId').split('/', maxsplit=-1)[-1]),
            ('START_TIME', _get_value(item, 'response', 'startTime').split('.', maxsplit=1)[0]),
            ('DURATION', _get_duration(_get_value(item, 'response', 'startTime'), _get_value(item, 'response', 'finishTime'))),
            ('STATUS', _get_value(item, 'response', 'status')),
            ('ERROR_MESSAGE', _get_value(item, 'response', 'pipelineRunErrorMessage'))
        ])
    return d


def _output_format(result, format_group):
    if 'value' in result and isinstance(result['value'], list):
        result = result['value']
    obj_list = result if isinstance(result, list) else [result]
    return [format_group(item) for item in obj_list]


def _get_value(item, *args):
    '''Get a nested value from a dict.
    :param dict item: The dict object
    '''
    try:
        for arg in args:
            item = item[arg]
        return str(item) if item or item == 0 else ' '
    except (KeyError, TypeError, IndexError):
        return ' '


def _get_duration(start_time, finish_time):
    '''Takes datetime strings and returns duration'''

    from dateutil.parser import parse
    try:
        duration = parse(finish_time) - parse(start_time)
        hours = f'{((24 * duration.days) + (duration.seconds // 3600)):02d}'
        minutes = f'{((duration.seconds % 3600) // 60):02d}'
        seconds = f'{(duration.seconds % 60):02d}'
        return f'{hours}:{minutes}:{seconds}'
    except (ValueError, TypeError):
        logger.debug('Unable to get duration with start_time %s and finish_time %s', start_time, finish_time)
        return ' '
