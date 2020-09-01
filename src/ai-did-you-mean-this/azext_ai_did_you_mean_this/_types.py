# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Dict, List, Union, Iterable, Any

from knack.arguments import CLICommandArgument
from knack.deprecation import Deprecated

ParameterTableType = Dict[str, CLICommandArgument]
OptionListType = List[Union[str, Deprecated]]

ArgumentsType = Union[Iterable[Any], str]
