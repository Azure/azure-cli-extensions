# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.util import open_page_in_browser, can_launch_browser, in_cloud_console


def datadog_link_create():

    url = 'https://us3.datadoghq.com/api/v1/liftr/oauth/start'
    if can_launch_browser() and not in_cloud_console():
        open_page_in_browser(url)
    else:
        print("There isn't an available browser to create an issue draft. You can copy and paste the url"
              " below in a browser to submit.\n\n{}\n\n".format(url))

    print("After login and authorize the linking, copy the code and client_id from the broswer address bar.\n"
          "Use code as linking-auth-code and client_id as linking-client-id in monitor create command.\n"
          "example:\n"
          "    az datadog monitor create --name \"myMonitor\" --location \"West US 2\" --identity-type"
          " \"SystemAssigned\" --sku-name \"Linked\" --datadog-organization-properties"
          " linking-auth-code=\"copyFromCode\" linking-client-id=\"00000000-0000-0000-0000-000000000000\""
          " --user-info name=\"Alice\" email-address=\"alice@microsoft.com\" phone-number=\"123-456-789\"")
