# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import hashlib
import json
import os
import sys
import tempfile

from util import get_ext_metadata, get_index_json_from_repo

EXTENSION_NAME = "arcdata"
DOWNLOAD_URL = (
    "https://azurearcdatacli.z13.web.core.windows.net/{filename}"
)


def get_sha256sum(a_file):
    sha256 = hashlib.sha256()
    with open(a_file, "rb") as f:
        sha256.update(f.read())
    return sha256.hexdigest()


def main():
    try:
        ext_file = sys.argv[1]
        dist_dir = sys.argv[2]

        if not ext_file or not ext_file.endswith(".whl") or not dist_dir:
            raise ValueError(
                "incorrect usage: <PATH TO WHL FILE> <OUTPUT LOCATION>"
            )

        index_json = os.path.join(dist_dir, "index.json")
        filename = os.path.basename(ext_file)
        extensions_dir = tempfile.mkdtemp()
        ext_dir = tempfile.mkdtemp(dir=extensions_dir)

        # -- update index and write back to file --
        curr_index = get_index_json_from_repo(index_json)
        entry = curr_index["extensions"][EXTENSION_NAME]
        entry[0]["downloadUrl"] = DOWNLOAD_URL.format(filename=filename)
        entry[0]["sha256Digest"] = get_sha256sum(ext_file)
        entry[0]["filename"] = filename
        entry[0]["metadata"] = get_ext_metadata(
            ext_dir, ext_file, EXTENSION_NAME
        )

        curr_index["extensions"][EXTENSION_NAME] = entry
        with open(index_json, "w") as outfile:
            outfile.write(json.dumps(curr_index, indent=4, sort_keys=True))
    except IndexError:
        raise ValueError("{} not found in index.json".format(EXTENSION_NAME))


if __name__ == "__main__":
    main()
