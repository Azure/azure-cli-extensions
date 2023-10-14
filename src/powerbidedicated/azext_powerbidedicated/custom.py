# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .aaz.latest.powerbi.embedded_capacity._create import Create as _EmbeddedCapacityCreate


class EmbeddedCapacityCreate(_EmbeddedCapacityCreate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.administration_members._required = False
        return args_schema
