# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.core.constants import STRICT_POS_NUMBER

from kubernetes.utils import parse_quantity
from typing import Union


class KubeQuantity(object):
    """
    An abstract kubernetes resource such as Memory/Cores/Pages. Includes parsing/validation/conversion to standard units.
    Also overrides comparison methods to work with standard python binary operators.
    """

    _ALL_QUANTITY_REGEX = r"^\+?((([0-9]+)|([0-9]*\.[0-9]+))([MGTPE]i?|Ki|[numk]|e[1-9]+))|({})$".format(
        STRICT_POS_NUMBER
    )
    VALID_QUANTITY_MSG = (
        "Valid kubernetes resource quantities match {}."
        " See kubernetes documentation for more details".format(
            _ALL_QUANTITY_REGEX
        )
    )

    def __init__(self, quantity: Union[str, "KubeQuantity"]):
        if type(quantity) is str:
            self.quantity = quantity
        elif type(quantity) is KubeQuantity:
            self.quantity = quantity.quantity
        else:
            raise TypeError(
                "Invalid value for quantity, must be str or KubeQuantity"
            )
        self._size = parse_quantity(quantity)

    @property
    def type(self):
        return self._resource_type

    @property
    def quantity(self):
        """
        The quantity of this resource in string format e.g. 10Gi, .6Mi, 10k, 1m
        """
        return self._quantity

    @quantity.setter
    def quantity(self, q):
        if hasattr(self, "_quantity"):
            raise AttributeError("Resource quantities are immutable")

        self._quantity = q

    @staticmethod
    def regex():
        """
        The regex that matches any quantity in this class of resource
        :return: regex that matches all kubernetes quantities
        """
        return KubeQuantity._ALL_QUANTITY_REGEX

    @property
    def size(self):
        """
        Gives a decimal size of this resource
        :return: numeric size of this resource in some standard unit
        """
        return self._size

    def __str__(self):
        """
        @override
        """
        return self.quantity

    def __repr__(self):
        """
        @override
        """
        return "{}".format(self.quantity)

    def __eq__(self, other):
        """
        @override
        """
        if type(self) is not type(other):
            raise NotImplementedError("Cannot compare different resource types")
        return self.size == other.size

    def __ne__(self, other):
        """
        @override
        """
        if type(self) is not type(other):
            raise NotImplementedError("Cannot compare different resource types")
        return not (self == other)

    def __lt__(self, other):
        """
        @override
        """
        if type(self) is not type(other):
            raise NotImplementedError("Cannot compare different resource types")
        return self.size < other.size

    def __gt__(self, other):
        """
        @override
        """
        if type(self) is not type(other):
            raise NotImplementedError("Cannot compare different resource types")
        return self.size > other.size

    def __le__(self, other):
        """
        @override
        """
        if type(self) is not type(other):
            raise NotImplementedError("Cannot compare different resource types")
        return self.size <= other.size

    def __ge__(self, other):
        """
        @override
        """
        if type(self) is not type(other):
            raise NotImplementedError("Cannot compare different resource types")
        return self.size >= other.size
