# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access

import unittest

from azure.cli.core.azclierror import InvalidArgumentValueError
from azext_k8s_extension.partner_extensions.OpenServiceMesh import _get_tested_distros


class TestOpenServiceMesh(unittest.TestCase):
    def test_bad_osm_arc_version(self):
        version = "0.7.1"
        err = "Invalid version \'" + str(version) + "\' for microsoft.openservicemesh"
        with self.assertRaises(InvalidArgumentValueError) as argError:
            _get_tested_distros(version)
        self.assertEqual(str(argError.exception), err)
