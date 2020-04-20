# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['account subscription'] = """
    type: group
    short-summary: Manage subscriptions
"""

helps['account subscription create'] = """
    type: command
    short-summary: Create a new WebDirect or EA Azure subscription.
    examples:
      - name: Create subscription
        text: |-
               az account subscription create --billing-account-name \\
               "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx_XXXX-XX-XX" \\
               --billing-profile-name "27VR-HDWX-BG7-TGB" --cost-center "135366376" --display-name \\
               "Contoso MCA subscription" --owner xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx \\
               --sku-id "0001" --invoice-section-name "JGF7-NSBG-PJA-TGB"
"""


helps['account subscription create-in-enrollment-account'] = """
    type: command
    short-summary: Create subscription in enrolment account
    examples:
      - name: Create subscription in enrollment account
        text: |-
               az account subscription create-in-enrollment-account --display-name \\
               "Test Ea Azure Sub" --offer-type "MS-AZR-0017P" --owners \\
               xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx \\
               xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx --enrollment-account-name \\
               "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
"""

helps['account subscription create-csp'] = """
    type: command
    short-summary: Create a new CSP subscription.
    examples:
      - name: Create CSP subscription
        text: |-
               az account subscription create-csp --billing-account-name \\
               "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx_XXXX-XX-XX" \\
               --display-name "Contoso MCA subscription" --sku-id "0001" --customer-name \\
               "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
"""

helps['account subscription rename'] = """
    type: command
    short-summary: Rename subscription
    examples:
      - name: Rename subscription
        text: |-
               az account subscription rename --subscription-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
"""

helps['account subscription cancel'] = """
    type: command
    short-summary: Cancel subscription
    examples:
      - name: Cancel subscription
        text: |-
               az account subscription cancel --subscription-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
"""

helps['account subscription enable'] = """
    type: command
    short-summary: Enable subscription
    examples:
      - name: Enable subscription
        text: |-
               az account subscription enable --subscription-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
"""
