import pytest

pytest.importorskip("azure.cli.core")

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_alrs.server import iter_results, list_all


class FakeResp:
    def __init__(self, json_data):
        self._json = json_data

    def json(self):
        return self._json


class PagingFake:
    """Serves pre-programmed pages in order, recording each call's params."""

    def __init__(self, pages):
        self._pages = pages
        self.calls = []

    def get(self, path, **kwargs):
        params = kwargs.get("params")
        self.calls.append(params)
        return FakeResp(self._pages[len(self.calls) - 1])


def test_walks_pages_until_count_is_reached():
    # The ALRS server strips `next`; the pager must walk by offset off `count`.
    fake = PagingFake(
        [
            {"count": 105, "results": list(range(100))},
            {"count": 105, "results": list(range(100, 105))},
        ]
    )
    result = list_all(fake, "/repositories/")
    assert result == list(range(105))
    # second page must advance the offset to where the first page left off
    assert fake.calls == [
        {"limit": 100, "offset": 0},
        {"limit": 100, "offset": 100},
    ]


def test_iter_results_fetches_lazily_and_can_stop_after_one_page():
    fake = PagingFake(
        [
            {"count": 200, "results": list(range(100))},
            {"count": 200, "results": list(range(100, 200))},
        ]
    )
    results = iter_results(fake, "/repositories/")
    assert fake.calls == []

    assert next(results) == 0
    assert fake.calls == [{"limit": 100, "offset": 0}]


def test_single_page_stops_without_a_next_link():
    # A full result set on one page (count == len(results)) must not fetch again,
    # even though there's no `next` link to signal the end.
    fake = PagingFake([{"count": 42, "results": list(range(42))}])
    result = list_all(fake, "/repositories/")
    assert result == list(range(42))
    assert fake.calls == [{"limit": 100, "offset": 0}]


def test_empty_page_guards_against_infinite_loop():
    # If the server reports more than it returns (stale count), the empty-page
    # guard stops us instead of looping forever.
    fake = PagingFake(
        [
            {"count": 500, "results": list(range(100))},
            {"count": 500, "results": []},
        ]
    )
    result = list_all(fake, "/repositories/")
    assert result == list(range(100))
    assert fake.calls == [
        {"limit": 100, "offset": 0},
        {"limit": 100, "offset": 100},
    ]


def test_max_items_spanning_pages_caps_and_stops():
    fake = PagingFake(
        [
            {"count": 500, "results": list(range(100))},
            {"count": 500, "results": list(range(100, 150))},
        ]
    )
    result = list_all(fake, "/repositories/", max_items=150)
    assert result == list(range(150))
    # second page requests only the remaining 50 and we stop at the cap
    assert fake.calls == [
        {"limit": 100, "offset": 0},
        {"limit": 50, "offset": 100},
    ]


def test_returns_bare_body_when_not_a_page():
    # A non-paginated endpoint may answer with a plain body instead of the
    # {count, results} envelope; hand it back untouched rather than choke.
    fake = PagingFake([[{"name": "a"}]])
    assert list_all(fake, "/repositories/") == [{"name": "a"}]
    assert fake.calls == [{"limit": 100, "offset": 0}]


@pytest.mark.parametrize("limit", [0, -1])
def test_rejects_a_limit_below_one(limit):
    fake = PagingFake([])
    with pytest.raises(InvalidArgumentValueError, match="--limit must be 1 or greater"):
        list_all(fake, "/tasks/", max_items=limit)
    assert fake.calls == []
