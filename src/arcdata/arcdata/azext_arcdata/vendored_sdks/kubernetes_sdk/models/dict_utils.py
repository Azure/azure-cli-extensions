# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from abc import ABC, abstractmethod


class SerializationUtils(ABC):
    @abstractmethod
    def _to_dict(self) -> dict:
        """
        Provides a dictionary representation of this object that can be serialized
        :returns: A dictionary representation of this object
        """
        pass

    @abstractmethod
    def _hydrate(self, d: dict):
        """
        Hydrates an instance of this class using the data contained in d
        :param d: The dict used to hydrate this object
        :returns: An instance of this class hydrated by d
        """
        pass
