# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import re
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError


logger = get_logger(__name__)


def validate_cpu(cpu):
    '''
    CPU quantity should be either integer, or millis. Currently, 500m (aka 0.5) is the only allowed fractional value.
    Note that 1 can be represented as 1000m.
    '''
    if cpu is None:
        return None

    # some digit(s) followed by an optional m
    if not re.match(r"^\d+m?$", cpu):
        raise InvalidArgumentValueError("CPU quantity should be millis (250m, 500m, 750m, 1250m) or integer (1, 2, ...)")

    return cpu


def validate_memory(memory):
    '''
    Memory quantity should be in gigabytes (Gi) or megabytes (Mi). Currently, the only allowed fractional gigabytes
    quantity is 512Mi. Note that 1Gi can be specified with 1024Mi.

    In the legacy extension, gigabytes is specified with integer. This will generate a warning now.
    '''
    if memory is None:
        return None

    unified = memory
    try:
        # For backward compatibility, convert integer value to value with Gi unit
        int(memory)
        logger.warning("Memory quantity [--memory] should be specified with unit, such as 512Mi, 1Gi. "
                       "Support for integer quantity will be dropped in future release.")
        unified = memory + "Gi"
    except ValueError:
        pass

    # Some digit(s) followed by explicit unit (Mi or Gi)
    if not re.match(r"^\d+[MG]i$", unified):
        raise InvalidArgumentValueError("Memory quantity should be integer followed by unit (Mi/Gi)")

    return unified
