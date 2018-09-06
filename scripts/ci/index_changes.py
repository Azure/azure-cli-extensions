# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import subprocess
from pkg_resources import parse_version

public_index = json.loads(subprocess.check_output('az extension list-available -d', shell=True))

with open('./src/index.json', 'r') as myfile:
    curr_index = json.loads(myfile.read()).get("extensions")

for extension in curr_index:
    new_entries = [entry for entry in curr_index[extension] if entry not in public_index.get(extension, [])]
    if not new_entries:
        continue  # no change in index for extension or entries were deleted

    # new_entry = []
    # for entry in curr_index[extension]:
    #     if entry not in public_index.get(extension, []):
    #         new_sources.append(entry['downloadUrl'])
    latest_new_entry = max(new_entries, key=lambda c: parse_version(c['metadata']['version']))
    print('{} {}'.format(extension, latest_new_entry['downloadUrl']))
