# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from datetime import datetime

from dateutil import parser, tz


def parse_restore_time(time):
    t = parser.parse(time)
    if t.tzinfo is None:
        t = datetime(
            t.year,
            t.month,
            t.day,
            t.hour,
            t.minute,
            t.second,
            t.microsecond,
            tz.tzlocal(),
        )
    return t.astimezone(tz.tzutc())
