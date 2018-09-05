# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import subprocess


public_index = json.loads(subprocess.check_output('az extension list-available -d', shell=True))

with open('./src/index.json', 'r') as myfile:
    curr_index = json.loads(myfile.read()).get("extensions")

for extension in curr_index:
    if curr_index[extension] != public_index.get(extension):
        print(extension)
