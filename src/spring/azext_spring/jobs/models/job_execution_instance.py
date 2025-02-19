# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import List, TYPE_CHECKING

from ...vendored_sdks.appplatform import _serialization

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from .. import model as _model


class JobExecutionInstance(_serialization.Model):
    _attribute_map = {
        "name": {"key": "name", "type": "str"}
    }

    def __init__(self, *, name, **kwargs):
        self.name = name


class JobExecutionInstanceCollection(_serialization.Model):
    _attribute_map = {
        "value": {"key": "value", "type": "[JobExecutionInstance]"}
    }

    def __init__(self, *, value: List["_model.JobExecutionInstance"], **kwargs) -> None:
        self.value = value
