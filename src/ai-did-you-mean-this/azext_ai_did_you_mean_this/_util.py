# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pprint
from typing import Any, Dict, Union


def safe_repr(obj: Union[type, object], attrs: Dict[str, Any]):
    classname = type(obj).__name__
    buffer = []

    if hasattr(obj, '__name__'):
        classname = obj.__name__

    for name, value in attrs.items():
        buffer.append(f'{name}={pprint.pformat(value)}')

    return '{classname}({args})'.format(
        classname=classname,
        args=', '.join(buffer)
    )
