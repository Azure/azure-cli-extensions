# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from pathlib import Path


def get_binaries_dir():
    binaries_dir = Path(__file__).parent.parent / "bin"
    binaries_dir.mkdir(parents=True, exist_ok=True)
    return binaries_dir


def get_data_dir():
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
