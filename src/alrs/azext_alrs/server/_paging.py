"""Walk Pulp's offset-paginated list endpoints.

The server caps a single page, so ``--limit`` can exceed one page and we can't
just forward it as the page size. ALRS strips Pulp's ``next``/``previous`` links
(they leak the internal Pulp host), so we can't page off ``next`` - we walk by
offset until we've collected ``max_items`` (if given) or all ``count`` items the
server reports.
"""

from collections.abc import Iterator
from typing import Any

from azure.cli.core.azclierror import InvalidArgumentValueError

PAGE_SIZE = 100


def _iter_pages(
    client: Any,
    path: str,
    max_items: int | None = None,
    params: dict[str, Any] | None = None,
) -> Iterator[Any]:
    if max_items is not None and max_items < 1:
        raise InvalidArgumentValueError("--limit must be 1 or greater.")
    base_params = dict(params or {})
    item_count = 0
    offset = 0
    while True:
        page_params = {**base_params, "limit": PAGE_SIZE, "offset": offset}
        if max_items is not None:
            remaining = max_items - item_count
            if remaining <= 0:
                return
            page_params["limit"] = min(PAGE_SIZE, remaining)

        body = client.get(path, params=page_params).json()
        yield body
        if not isinstance(body, dict) or "results" not in body:
            return
        item_count += len(body["results"])
        if max_items is not None and item_count >= max_items:
            return
        # The server reports the total in `count` and strips `next`, so stop once
        # we've collected everything. The empty-page guard prevents an infinite
        # loop if `count` is missing or stale.
        count = body.get("count")
        if not body["results"] or count is None or item_count >= count:
            return
        offset = item_count


def iter_results(
    client: Any,
    path: str,
    max_items: int | None = None,
    params: dict[str, Any] | None = None,
) -> Iterator[Any]:
    """Yield items from a paginated list endpoint as each page is fetched."""
    yielded = 0
    for body in _iter_pages(client, path, max_items=max_items, params=params):
        if not isinstance(body, dict) or "results" not in body:
            return
        results = body["results"]
        if max_items is not None:
            results = results[: max_items - yielded]
        yield from results
        yielded += len(results)


def list_all(
    client: Any,
    path: str,
    max_items: int | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    """Collect results from a paginated list endpoint.

    ``params`` are extra query filters (e.g. ``{"repository": <id>}``) merged
    into every page request. Returns the raw body unchanged if it isn't a
    standard ``{"results": [...]}`` page (so non-paginated endpoints still work).
    """
    items: list[Any] = []
    for body in _iter_pages(client, path, max_items=max_items, params=params):
        if not isinstance(body, dict) or "results" not in body:
            return body
        items.extend(body["results"])
        if max_items is not None and len(items) >= max_items:
            return items[:max_items]
    return items
