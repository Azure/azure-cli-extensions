# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=protected-access, disable=unused-argument, line-too-long

import argparse
from collections import defaultdict
from knack.util import CLIError


class AddPropertiesParameters(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.properties_parameters = action

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise CLIError(f'usage error: {option_string} [KEY=VALUE ...]') from ValueError
        d = {}
        for k in properties:
            v = properties[k]
            d[k] = v[0]
        return d


def validator_duration(cmd, namespace):
    if namespace.duration is not None:
        namespace.duration = period_type(namespace.duration)


def validator_offset(cmd, namespace):
    if namespace.start_time_offset_minutes is not None:
        namespace.start_time_offset_minutes = period_type(namespace.start_time_offset_minutes, as_timedelta=True)


def period_type(value, as_timedelta=False):

    import re

    def _get_substring(indices):
        if indices == tuple([-1, -1]):
            return ''
        return value[indices[0]: indices[1]]

    regex = r'(p)?(\d+y)?(\d+m)?(\d+d)?(t)?(\d+h)?(\d+m)?(\d+s)?'
    # example: P3Y6M4DT12H30M5S represents a duration of "three years, six months, four days, twelve hours, thirty minutes, and five seconds"
    match = re.match(regex, value.lower())
    match_len = match.span(0)
    if match_len != tuple([0, len(value)]):
        raise ValueError('PERIOD should be of the form "##h##m##s" or ISO8601')
    # simply return value if a valid ISO8601 string is supplied
    if match.span(1) != tuple([-1, -1]) and match.span(5) != tuple([-1, -1]):
        return value.upper()

    # if shorthand is used, only support days, minutes, hours, seconds
    # ensure M is interpretted as minutes
    days = _get_substring(match.span(4))
    hours = _get_substring(match.span(6))
    minutes = _get_substring(match.span(7)) or _get_substring(match.span(3))
    seconds = _get_substring(match.span(8))

    if as_timedelta:
        from datetime import timedelta
        return timedelta(
            days=int(days[:-1]) if days else 0,
            hours=int(hours[:-1]) if hours else 0,
            minutes=int(minutes[:-1]) if minutes else 0,
            seconds=int(seconds[:-1]) if seconds else 0
        )
    return f'P{days}T{minutes}{hours}{seconds}'.upper()
