# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import tempfile

from pathlib import Path
from typing import Optional

from azext_confcom.lib.cose import cose_get_properties
from azext_confcom.lib.fragments import get_fragments_from_image
from azext_confcom.lib.opa import opa_eval


def fragment_references_from_image(image: str, minimum_svn: Optional[str]):

    for signed_fragment in get_fragments_from_image(image):

        package_name = signed_fragment.name.split(".")[0]
        cose_properties = cose_get_properties(signed_fragment)

        with tempfile.NamedTemporaryFile("w+b") as payload:
            payload.write(cose_properties["payload"].encode("utf-8"))
            payload.flush()
            fragment_properties = opa_eval(
                Path(payload.name),
                f"data.{package_name}",
            )["result"][0]["expressions"][0]["value"]

            yield {
                "feed": cose_properties["feed"],
                "includes": sorted(list(set(fragment_properties.keys()).intersection({
                    "containers",
                    "fragmnents",
                    "namespace",
                    "external_processes",
                }))),
                "issuer": cose_properties["iss"],
                "minimum_svn": minimum_svn or fragment_properties["svn"],
            }
