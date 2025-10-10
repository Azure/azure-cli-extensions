from typing import MutableMapping
from typing import Any, MutableMapping


def case_insensitive_dict(*args: Any, **kwargs: Any) -> MutableMapping:
    """Return a case-insensitive mutable mapping from an inputted mapping structure.

    :return: A case-insensitive mutable mapping object.
    :rtype: ~collections.abc.MutableMapping
    """

    # Rational is I don't want to re-implement this, but I don't want
    # to assume "requests" or "aiohttp" are installed either.
    # So I use the one from "requests" or the one from "aiohttp" ("multidict")
    # If one day this library is used in an HTTP context without "requests" nor "aiohttp" installed,
    # we can add "multidict" as a dependency or re-implement our own.
    try:
        from requests.structures import CaseInsensitiveDict

        return CaseInsensitiveDict(*args, **kwargs)
    except ImportError:
        pass
    try:
        # multidict is installed by aiohttp
        from multidict import CIMultiDict

        if len(kwargs) == 0 and len(args) == 1 and (not args[0]):
            return (
                CIMultiDict()
            )  # in case of case_insensitive_dict(None), we don't want to raise exception
        return CIMultiDict(*args, **kwargs)
    except ImportError:
        raise ValueError(
            "Neither 'requests' or 'multidict' are installed and no case-insensitive dict impl have been found"
        )
