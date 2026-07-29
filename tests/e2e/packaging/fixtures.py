# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class PackagingFixture:
    name: str
    path: Path
    kind: str
    requires_build_isolation_off: bool


def load_fixtures(repo_root: Path, manifest_path: Path, include_disabled: bool = False) -> List[PackagingFixture]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    fixtures: List[PackagingFixture] = []
    for raw in data.get("fixtures", []):
        if not include_disabled and not raw.get("enabled", False):
            continue

        fixtures.append(
            PackagingFixture(
                name=raw["name"],
                path=repo_root / raw["path"],
                kind=raw.get("kind", "unspecified"),
                requires_build_isolation_off=raw.get("requires_build_isolation_off", False),
            )
        )

    return fixtures
