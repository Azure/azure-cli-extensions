import pytest

pytest.importorskip("azure.cli.core")

from azext_alrs.server._resolve import (
    resolve_id_or_name,
    resolve_release,
    resolve_release_name,
)

ID = "repositories-deb-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
RELEASE_ID = "content-deb-releases-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


class FakeResp:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class FakeClient:
    def __init__(self, data):
        self._data = data
        self.calls = []

    def get(self, path, **kwargs):
        self.calls.append((path, kwargs))
        return FakeResp(self._data)


class PagingClient:
    def __init__(self, pages):
        self._pages = pages
        self.calls = []

    def get(self, path, **kwargs):
        self.calls.append((path, kwargs))
        return FakeResp(self._pages[len(self.calls) - 1])


def test_id_is_passed_through_without_hitting_the_server():
    client = FakeClient({})
    assert resolve_id_or_name(client, "repositories", ID) == ID
    assert client.calls == []


def test_empty_value_passes_through():
    client = FakeClient({})
    assert resolve_id_or_name(client, "repositories", "") == ""
    assert client.calls == []


def test_name_is_resolved_via_list_name_filter():
    client = FakeClient({"results": [{"id": ID}]})
    assert resolve_id_or_name(client, "repositories", "myrepo") == ID
    path, kwargs = client.calls[0]
    assert path == "/repositories/"
    assert kwargs["params"] == {"name": "myrepo"}


def test_name_that_embeds_a_uuid_is_still_treated_as_a_name():
    # fullmatch: trailing text after a uuid means it's a name, not an id,
    # so it must go through the name lookup instead of straight to the server.
    client = FakeClient({"results": [{"id": ID}]})
    name = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee-nightly"
    assert resolve_id_or_name(client, "repositories", name) == ID
    assert client.calls[0][0] == "/repositories/"


def test_leading_name_before_a_uuid_is_treated_as_a_name():
    # "my-repo-<uuid>" is a name, not an id: the id prefix is anchored to the
    # resource ("repositories-..."), so a user name that merely ends in a uuid
    # falls through to the name lookup instead of being shoved into a path.
    client = FakeClient({"results": [{"id": ID}]})
    name = "my-repo-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    assert resolve_id_or_name(client, "repositories", name) == ID
    assert client.calls[0][0] == "/repositories/"


def test_bare_uuid_is_treated_as_an_id():
    client = FakeClient({})
    bare = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    assert resolve_id_or_name(client, "repositories", bare) == bare
    assert client.calls == []


def test_id_with_trailing_newline_is_not_treated_as_an_id():
    # fullmatch rejects a trailing newline (which .match()+$ would have allowed),
    # so a dirty value goes to the name lookup instead of into a request path.
    client = FakeClient({"results": [{"id": ID}]})
    assert resolve_id_or_name(client, "repositories", ID + "\n") == ID
    assert client.calls[0][0] == "/repositories/"


def test_unknown_name_raises_not_found():
    from azure.cli.core.azclierror import ResourceNotFoundError

    # name filter matched nothing - empty results list
    client = FakeClient({"results": []})
    with pytest.raises(ResourceNotFoundError):
        resolve_id_or_name(client, "remotes", "ghost")


def test_release_id_passes_through_without_a_repo_or_server_call():
    client = FakeClient({})
    assert resolve_release(client, None, RELEASE_ID) == RELEASE_ID
    assert client.calls == []


def test_release_name_resolves_against_the_nested_repo_endpoint():
    client = FakeClient({"results": [{"id": RELEASE_ID}]})
    assert resolve_release(client, ID, "jammy") == RELEASE_ID
    path, kwargs = client.calls[0]
    assert path == f"/repositories/{ID}/releases/"
    assert kwargs["params"] == {"name": "jammy"}


def test_release_name_without_a_repo_raises():
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    client = FakeClient({})
    with pytest.raises(RequiredArgumentMissingError):
        resolve_release(client, None, "jammy")
    assert client.calls == []


def test_release_unknown_name_raises_not_found():
    from azure.cli.core.azclierror import ResourceNotFoundError

    client = FakeClient({"results": []})
    with pytest.raises(ResourceNotFoundError):
        resolve_release(client, ID, "ghost")


def test_release_name_passes_through_without_a_server_call():
    # The packages endpoint wants a name, so a name needs no lookup at all.
    client = FakeClient({})
    assert resolve_release_name(client, ID, "jammy") == "jammy"
    assert client.calls == []


def test_release_id_resolves_back_to_its_distribution_name():
    client = FakeClient({"results": [{"id": RELEASE_ID, "distribution": "jammy"}]})
    assert resolve_release_name(client, ID, RELEASE_ID) == "jammy"
    path, _ = client.calls[0]
    assert path == f"/repositories/{ID}/releases/"


def test_release_id_matches_the_right_release_among_several():
    other_id = "content-deb-releases-11111111-2222-3333-4444-555555555555"
    client = FakeClient(
        {
            "results": [
                {"id": other_id, "distribution": "focal"},
                {"id": RELEASE_ID, "distribution": "jammy"},
            ]
        }
    )
    assert resolve_release_name(client, ID, RELEASE_ID) == "jammy"


def test_release_id_pages_until_match_and_stops_early():
    client = PagingClient(
        [
            {
                "count": 300,
                "results": [{"id": f"other-{index}"} for index in range(100)],
            },
            {
                "count": 300,
                "results": [{"id": RELEASE_ID, "distribution": "jammy"}],
            },
        ]
    )

    assert resolve_release_name(client, ID, RELEASE_ID) == "jammy"
    assert client.calls == [
        (f"/repositories/{ID}/releases/", {"params": {"limit": 100, "offset": 0}}),
        (f"/repositories/{ID}/releases/", {"params": {"limit": 100, "offset": 100}}),
    ]


def test_release_id_without_a_repo_raises():
    from azure.cli.core.azclierror import RequiredArgumentMissingError

    client = FakeClient({})
    with pytest.raises(RequiredArgumentMissingError):
        resolve_release_name(client, None, RELEASE_ID)
    assert client.calls == []


def test_release_id_from_another_repository_raises_not_found():
    from azure.cli.core.azclierror import ResourceNotFoundError

    # The id is only meaningful inside the repo the caller named.
    client = FakeClient({"results": [{"id": "content-deb-releases-" + "9" * 8, "d": "x"}]})
    with pytest.raises(ResourceNotFoundError):
        resolve_release_name(client, ID, RELEASE_ID)
