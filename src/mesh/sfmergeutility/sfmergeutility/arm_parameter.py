# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class ArmParameter(object):  # pylint: disable=too-few-public-methods
    default_value = None
    type_param = None
    meta_data = None

    def __init__(self, default_value, type_param, description):
        self.default_value = default_value
        self.type_param = type_param
        self.meta_data = MetaData(description)

    def to_dict(self):
        return {"defaultValue": self.default_value, "type": self.type_param, "metadata": self.meta_data.to_dict()}


class MetaData(object):  # pylint: disable=too-few-public-methods
    description = None

    def __init__(self, description):
        self.description = description

    def to_dict(self):
        return {"description": self.description}
