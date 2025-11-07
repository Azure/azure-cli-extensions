# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import tempfile
from typing import BinaryIO
from azext_confcom.lib.serialization import policy_deserialize, policy_serialize
from azext_confcom.lib.policy import Policy, Container
import re
import base64


def radius_policy_insert(
    policy_file: BinaryIO,
    template_path: str,
    container_index: int,
) -> str:

    policy = None
    if policy_file.name == "<stdin>":
        with tempfile.NamedTemporaryFile(delete=True) as temp_policy_file:
            temp_policy_file.write(policy_file.read())
            temp_policy_file.flush()
            policy = policy_deserialize(temp_policy_file.name)
    else:
        policy = policy_deserialize(policy_file.name)

    serialized_policy = policy_serialize(policy)

    # Read the template file
    with open(template_path, 'r') as template_file:
        template_content = template_file.read()

    # Base64 encode the serialized policy
    encoded_policy = base64.b64encode(serialized_policy.encode()).decode()

    # Replace the nth ccePolicy value with the encoded policy, preserving original quote types
    def replace_cce_policy(match):
        full_match = match.group(0)
        # Extract the key part (before the colon)
        key_part = re.match(r'(["\']?)ccePolicy\1\s*:', full_match).group(0)
        # Extract the quote type used for the value
        value_quote_match = re.search(r':\s*(["\'])', full_match)
        value_quote = value_quote_match.group(1) if value_quote_match else '"'
        return f'{key_part} {value_quote}{encoded_policy}{value_quote}'

    # Find all matches and replace only the nth instance
    pattern = r'(["\']?)ccePolicy\1\s*:\s*["\'][^"\']*["\']'
    matches = list(re.finditer(pattern, template_content))

    if len(matches) >= container_index:
        # Replace only the nth match (convert to 0-based index)
        target_match = matches[container_index]
        start, end = target_match.span()
        replacement = replace_cce_policy(target_match)
        updated_content = template_content[:start] + replacement + template_content[end:]
    else:
        updated_content = template_content


    # Write the updated content back to the template file
    with open(template_path, 'w') as template_file:
        template_file.write(updated_content)
