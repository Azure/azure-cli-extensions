# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast


def repack_response_json(response):
    # Iterate through the response and build a JSON array
    list_string = "["
    for details in response:
        details_string = str(details)
        list_string += details_string + ", "

    if len(list_string) == 1:
        return []   # Got an empty response page, return an empty array

    list_string = list_string[:-2]
    list_string += "]"

    # Convert the JSON into an array of job_details objects. The Azure CLI core will convert it back to JSON.
    # json.loads doesn't like the all the single quotes in the response, but ast.literal_eval handles them OK.
    return ast.literal_eval(list_string)
