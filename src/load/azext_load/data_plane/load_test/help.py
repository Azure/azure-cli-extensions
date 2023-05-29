# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

helps = {}

helps[
    "load test create"
] = """
type: command
short-summary: Create a new load test.
long-summary: Create a new load test.
"""

helps[
    "load test list"
] = """
type: command
short-summary: List all tests.
long-summary: List all tests in the given load test resource.
"""

helps[
    "load test show"
] = """
type: command
short-summary: Show details of test.
long-summary: Show details of the test identified by given test-id.
"""

helps[
    "load test update"
] = """
type: command
short-summary: Update an existing load test.
long-summary: Update an existing load test.
"""

helps[
    "load test delete"
] = """
type: command
short-summary: Delete an existing load test.
long-summary: Delete an existing load test.
"""

helps[
    "load test download-files"
] = """
type: command
short-summary: Download files of existing load test.
long-summary: Download files of an existing load test.
"""

helps[
    "load test app-component add"
] = """
type: command
short-summary: Add app component to test.
long-summary: Add app component to an existing load test.
"""

helps[
    "load test app-component list"
] = """
type: command
short-summary: List all app component of test.
long-summary: List all app component of a test.
"""

helps[
    "load test app-component remove"
] = """
type: command
short-summary: Remove an app component from test.
long-summary: Remove the given app component from the test.
"""

helps[
    "load test server-metric add"
] = """
type: command
short-summary: Add server-metrics to test.
long-summary: Add server-metrics to an existing load test.
"""

helps[
    "load test server-metric list"
] = """
type: command
short-summary: List all server-metrics of test.
long-summary: List all server-metrics of a test.
"""

helps[
    "load test server-metric remove"
] = """
type: command
short-summary: Remove an server-metrics from test.
long-summary: Remove the given server-metrics from the test.
"""

helps[
    "load test file delete"
] = """
type: command
short-summary: Delete file of test.
long-summary: Delete a file of test by providing the file name and test id.
"""

helps[
    "load test file download"
] = """
type: command
short-summary: Download file of test.
long-summary: Download a file of test by providing the file name, test id and path where to download to path.
"""

helps[
    "load test file list"
] = """
type: command
short-summary: List details of files related to test.
long-summary: List details of all the files related to a test by providing the corresponding test id.
"""

helps[
    "load test file upload"
] = """
type: command
short-summary: Upload file to a test.
long-summary: Upload a file to a test by providing path to file and test id.
"""
