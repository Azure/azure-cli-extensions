# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Patch vcrpy to skip aiohttp stubs — avoids AttributeError on aiohttp 3.10+
# where 'AsyncStreamReaderMixin' was removed from aiohttp.streams.
try:
    from aiohttp import streams as _aiohttp_streams
    if not hasattr(_aiohttp_streams, 'AsyncStreamReaderMixin'):
        import vcr.patch as _vcr_patch

        def _noop_aiohttp(self):
            """Skip aiohttp patching — incompatible aiohttp version."""
            return iter(())

        _vcr_patch.CassettePatcherBuilder._aiohttp = _noop_aiohttp
except ImportError:
    pass


# Custom VCR host matcher — normalizes regional ARM endpoints so cassettes
# recorded against management.azure.com also match requests to
# eastus2euap.management.azure.com (and vice versa).
import re

_REGIONAL_ARM_RE = re.compile(r'^[a-z0-9]+\.management\.azure\.com$')


def _normalize_host(host):
    """Strip regional prefix from ARM hostname."""
    if _REGIONAL_ARM_RE.match(host):
        return 'management.azure.com'
    return host


try:
    import vcr.matchers as _vcr_matchers

    _original_host = _vcr_matchers.host

    def _patched_host(r1, r2):
        """Treat regional and global ARM endpoints as equal."""
        r1_host = _normalize_host(r1.host)
        r2_host = _normalize_host(r2.host)
        assert r1_host == r2_host, f"{r1.host} != {r2.host}"

    _vcr_matchers.host = _patched_host
except (ImportError, AttributeError):
    pass
