# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def password_handler(ex):
    from msrestazure.azure_exceptions import CloudError
    if isinstance(ex, CloudError) and ex.error.error == "PasswordNotComplex":
        raise CloudError(ex.response,
                         "{} Minimum 8 characters and maximum 128 characters. Password must contain characters from "
                         "three of the following categories: English uppercase letters, English lowercase letters, "
                         "numbers, and non-alphanumeric characters.".format(ex.message))
    raise ex
