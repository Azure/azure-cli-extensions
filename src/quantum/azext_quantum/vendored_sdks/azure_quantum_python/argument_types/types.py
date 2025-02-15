##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

class Pauli(Enum):
    """Pauli operators"""

    I = "PauliI"
    X = "PauliX"
    Y = "PauliY"
    Z = "PauliZ"


class Result(Enum):
    """Result value"""

    Zero = False
    One = True


@dataclass
class Range:
    """Range value
    
    :param start: Start
    :type start: int
    :param end: End
    :type end: int
    :param step: Step
    :type step: int
    """

    start: int
    end: int
    step: Optional[int] = None

    @property
    def value(self):
        """Range value"""
        
        if self.step is None:
            return {"start": self.start, "end": self.end}
        else:
            return {"start": self.start, "end": self.end, "step": self.step}

@dataclass
class EmptyArray:
    """Empty array value"""
    
    element_type: Type
    """Element type"""
