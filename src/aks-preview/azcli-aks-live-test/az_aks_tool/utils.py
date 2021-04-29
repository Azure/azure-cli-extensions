# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os

def get_test_matrix(matrix_file_path):
    json_file = open(matrix_file_path, 'r')
    test_matrix = json.load(json_file)
    json_file.close()
    return test_matrix

def decorate_qualified_prefix(test_cases, prefix):
    decorated_test_cases = ["{}.{}".format(prefix, x) for x in test_cases]
    return decorated_test_cases

def check_file_existence(file_path):
    if file_path is not None and os.path.isfile(file_path):
        return True
    return False
