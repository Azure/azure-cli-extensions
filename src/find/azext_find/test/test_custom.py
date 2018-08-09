# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azext_find.custom import (
    call_aladdin_service,
)


class FindCustomCommandTest(unittest.TestCase):

    def test_call_aladdin_service(self):
        response = call_aladdin_service("what is azure cli?")
        self.assertEqual(200, response.status_code)


if __name__ == '__main__':
    unittest.main()
