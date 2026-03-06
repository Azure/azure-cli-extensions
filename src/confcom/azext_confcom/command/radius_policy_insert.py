# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import tempfile
from typing import BinaryIO
from azext_confcom.lib.serialization import policy_deserialize, policy_serialize
import re
import base64


# ccePolicy pattern: any key containing 'ccepolicy' (case-insensitive) followed by a quoted value
_CCE_POLICY_PATTERN = re.compile(
    r'["\']?[^"\']*[cC][cC][eE][pP][oO][lL][iI][cC][yY][^"\']*["\']?\s*:\s*["\'][^"\']*["\']'
)


def insert_policy_into_template(
    encoded_policy: str,
    template_content: str,
    container_index: int,
) -> str:
    """Replace the nth ccePolicy value in *template_content* with *encoded_policy*.

    Preserves the original quote style (single or double) around the value.
    Returns the modified template string unchanged when *container_index* is
    out of range.
    """

    def replace_cce_policy(match):
        full_match = match.group(0)
        colon_match = re.search(r':\s*', full_match)
        key_part = full_match[:colon_match.end()].rstrip()
        value_quote_match = re.search(r':\s*(["\'])', full_match)
        value_quote = value_quote_match.group(1) if value_quote_match else '"'
        return f'{key_part} {value_quote}{encoded_policy}{value_quote}'

    matches = list(_CCE_POLICY_PATTERN.finditer(template_content))

    if container_index < len(matches):
        target_match = matches[container_index]
        start, end = target_match.span()
        replacement = replace_cce_policy(target_match)
        return template_content[:start] + replacement + template_content[end:]

    return template_content


def radius_policy_insert(
    policy_file: BinaryIO,
    template_path: str,
    container_index: int,
) -> None:

    if policy_file.name == "<stdin>":
        with tempfile.NamedTemporaryFile(delete=True) as temp_policy_file:
            temp_policy_file.write(policy_file.read())
            temp_policy_file.flush()
            policy = policy_deserialize(temp_policy_file.name)
    else:
        policy = policy_deserialize(policy_file.name)

    serialized_policy = policy_serialize(policy)
    encoded_policy = base64.b64encode(serialized_policy.encode()).decode()

    with open(template_path, 'r') as template_file:
        template_content = template_file.read()

    updated_content = insert_policy_into_template(
        encoded_policy, template_content, container_index,
    )

    with open(template_path, 'w') as template_file:
        template_file.write(updated_content)
