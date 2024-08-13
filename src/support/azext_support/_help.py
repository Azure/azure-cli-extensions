# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['support in-subscription file upload'] = """
type: command
short-summary: Uploads a file to a workspace for the specified subscription.
parameters:
  - name: --file-workspace-name
    short-summary: File Workspace Name

  - name: --file-path
    short-summary: File Path
examples:
  - name: Upload a file to a file workspace (different from the account subscription).
    text: |
          az support in-subscription file upload \\
            --file-workspace-name "TestFileWorkspaceName" \\
            --file-path "C:/Users/TestUsers/TestFolder/ExampleFile.txt" \\
            --subscription "TestSubscription"

  - name: Upload a file to a to an Azure support ticket (different from the account subscription).
    text: |
          az support in-subscription file upload \\
            --file-workspace-name "2300000000000358" \\
            --file-path "C:/Users/TestUsers/TestFolder/ExampleFile.txt" \\
            --subscription "TestSubscription"

  - name: Upload a file to a file workspace (same as the account subscription).
    text: |
          az support in-subscription file upload \\
            --file-workspace-name "TestFileWorkspaceName" \\
            --file-path "C:/Users/TestUsers/TestFolder/ExampleFile.txt"

  - name: Upload a file to an Azure support ticket (same as the account subscription).
    text: |
          az support in-subscription file upload \\
            --file-workspace-name "2300000000000358" \\
            --file-path "C:/Users/TestUsers/TestFolder/ExampleFile.txt"
"""

helps['support no-subscription file upload'] = """
type: command
short-summary: Uploads a file to a workspace.
parameters:
  - name: --file-workspace-name
    short-summary: File Workspace Name

  - name: --file-path
    short-summary: File Path
examples:
  - name: Upload a file to a file workspace.
    text: |
          az support no-subscription file upload \\
            --file-workspace-name "TestFileWorkspaceName" \\
            --file-path "C:/Users/TestUsers/TestFolder/ExampleFile.txt"

  - name: Upload a file to an Azure support ticket..
    text: |
          az support no-subscription file upload \\
            --file-workspace-name "2300000000000358" \\
            --file-path "C:/Users/TestUsers/TestFolder/ExampleFile.txt"
"""
