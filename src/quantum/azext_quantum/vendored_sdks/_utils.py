# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# This def was not built into Azure CLI 2.36.0, but since it was already in the Azure SDK for Python,
# AutoRest included it in the new control-plane client files (azext_quantum\vendored_sdks\azure_mgmt_quantum)
# generated to access the Quantum API version 2022-01-10-preview for PR #4784

def case_insensitive_dict(*args, **kwargs):
    """Return a case-insensitive dict from a structure that a dict would have accepted.

    Rational is I don't want to re-implement this, but I don't want
    to assume "requests" or "aiohttp" are installed either.
    So I use the one from "requests" or the one from "aiohttp" ("multidict")
    If one day this library is used in an HTTP context without "requests" nor "aiohttp" installed,
    we can add "multidict" as a dependency or re-implement our own.
    """
    try:
        from requests.structures import CaseInsensitiveDict

        return CaseInsensitiveDict(*args, **kwargs)
    except ImportError:
        pass
    try:
        # multidict is installed by aiohttp
        from multidict import CIMultiDict

        if len(kwargs) == 0 and len(args) == 1 and (not args[0]):
            return CIMultiDict()    # in case of case_insensitive_dict(None), we don't want to raise exception
        return CIMultiDict(*args, **kwargs)
    except ImportError:
        raise ValueError(
            "Neither 'requests' or 'multidict' are installed and no case-insensitive dict impl have been found"
        )
