# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def password_handler(ex):
    from msrestazure.azure_exceptions import CloudError
    if isinstance(ex, CloudError):
        if ex.error.error == "PasswordNotComplex":
            raise CloudError(
                ex.response,
                "{} Password must contain characters from at least three of the following categories: "
                "English uppercase letters, English lowercase letters, numbers, and non-alphanumeric characters. "
                "Your password cannot contain all or part of login name. Part of a login name is defined as three "
                "or more consecutive alphanumeric characters.".format(ex.message))
        if ex.error.error == "PasswordTooShort":
            raise CloudError(
                ex.response,
                "{} Password must contain minimum 8 characters and maximum 128 characters.".format(ex.message))

    raise ex
