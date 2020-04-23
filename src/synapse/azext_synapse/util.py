# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def categorized_files(reference_files):
    files = []
    jars = []
    for file in reference_files:
        file = file.strip()
        if file.endswith(".jar"):
            jars.append(file)
        else:
            files.append(file)
    return files, jars
