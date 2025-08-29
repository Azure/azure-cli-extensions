# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os


def get_test_data_file_path(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, "data", filename)
