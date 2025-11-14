# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any
from pydantic.dataclasses import dataclass as _dataclass, Field
from pydantic import field_serializer


# The policy model is represented as pydantic dataclasses, this makes
# serialisation to/from JSON trivial.

# For some collections in the model, the order has no semantic meaning
# (e.g. environment rules). We mark such fields using a custom OrderlessField
# class which is an extension of the pydantic Field class. This custom class
# just sets a metadata flag we can read later.

# We then also extend the dataclass decorator to sort these fields with this
# flag before serialisation and comparison.


def dataclass(cls=None, **dataclass_kwargs):
    def wrap(inner_cls):

        # This method uses a pydantic field serializer to operate on fields
        # before serialisation. Here we look for "orderless" fields and sort them.
        @field_serializer("*")
        def _sort_orderless(self, value, info):
            field = type(self).__pydantic_fields__[info.field_name]
            if (field.json_schema_extra or {}).get("orderless"):
                return sorted(value, key=repr)
            return value
        setattr(inner_cls, "_sort_orderless", _sort_orderless)

        # This custom equality method sorts "orderless" fields before comparison.
        def __eq__(self, other):
            def compare_field(name, field_info):
                if (field_info.json_schema_extra or {}).get("orderless"):
                    return (
                        sorted(getattr(self, name), key=repr) ==
                        sorted(getattr(other, name), key=repr)
                    )
                return getattr(self, name) == getattr(other, name)

            return (
                type(self) is type(other) and
                all(
                    compare_field(name, field_info)
                    for name, field_info in self.__pydantic_fields__.items()
                )
            )
        setattr(inner_cls, "__eq__", __eq__)

        return _dataclass(inner_cls, eq=False, **dataclass_kwargs)

    # This adds support for using the decorator with or without parentheses.
    if cls is None:
        return wrap
    return wrap(cls)


def OrderlessField(**kwargs: Any):
    return Field(json_schema_extra={"orderless": True}, **kwargs)
