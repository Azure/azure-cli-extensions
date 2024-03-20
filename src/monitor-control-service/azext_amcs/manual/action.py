# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access, raise-missing-from, consider-using-f-string

import argparse
from collections import defaultdict
from azure.cli.core.azclierror import ValidationError


class AddDataFlows(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super().__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise ValidationError('{} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'streams':
                d['streams'] = v
            elif kl == 'destinations':
                d['destinations'] = v
        return d


class AddDestinationsLogAnalytics(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super().__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise ValidationError('{} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'resource-id':
                d['workspace_resource_id'] = v[0]
            elif kl == 'name':
                d['name'] = v[0]
        return d


class AddDestinationsAzureMonitorMetrics(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.destinations_azure_monitor_metrics = action

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise ValidationError('{} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'name':
                d['name'] = v[0]
        return d


class AddDataSourcesPerformanceCounters(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super().__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise ValidationError('{} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'streams':
                d['streams'] = v
            elif kl == 'sampling-frequency':
                try:
                    d['sampling_frequency_in_seconds'] = int(v[0])
                except ValueError:
                    raise ValidationError('invalid sampling-frequency={}'.format(v[0]))
            elif kl == 'counter-specifiers':
                d['counter_specifiers'] = v
            elif kl == 'name':
                d['name'] = v[0]
        return d


class AddDataSourcesWindowsEventLogs(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super().__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise ValidationError('{} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'streams':
                d['streams'] = v
            elif kl == 'x-path-queries':
                d['x_path_queries'] = v
            elif kl == 'name':
                d['name'] = v[0]
        return d


class AddDataSourcesSyslog(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super().__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise ValidationError('{} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'streams':
                d['streams'] = v
            elif kl == 'facility-names':
                d['facility_names'] = v
            elif kl == 'log-levels':
                d['log_levels'] = v
            elif kl == 'name':
                d['name'] = v[0]
        return d
