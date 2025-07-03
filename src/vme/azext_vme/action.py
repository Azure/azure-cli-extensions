# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import argparse
from typing import Any


# pylint: disable=protected-access
class AddIncludedExtensionTypes(argparse._AppendAction):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        include_types = getattr(namespace, self.dest, None)
        if include_types is None:
            include_types = []
        include_types.extend(values)
        setattr(namespace, self.dest, include_types)
