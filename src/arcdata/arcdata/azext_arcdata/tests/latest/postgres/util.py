# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os


def normalize_path(path, *paths):
    """
    Windows needs this sometimes when running the e2e tests from the
    `build unit-tests` task-runner. This can be slightly different than running
    from PyCharm/editor.
    """
    path = os.path.join(path, *paths)
    return path.replace("\\", "/")
