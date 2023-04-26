# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a class for generating VNF NFDs and associated resources."""
from typing import Dict, Any
from .nfd_generator_base import NFDGenerator

class CnfNfdGenerator(NFDGenerator):
    """_summary_

    :param NFDGenerator: _description_
    :type NFDGenerator: _type_
    """
    def __init__(
        self,
        config: Dict[Any, Any]
    ):
        super(NFDGenerator, self).__init__(
            config=config,
        )
