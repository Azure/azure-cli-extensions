"""Turn a repository/remote reference into an id.

Users can pass either an ALRS resource id or a plain name. If it's a name, we
look it up by filtering the list endpoint on an exact name
(/<resource>/?name=<value>), which returns 0 or 1 matches.

Note: these ids are the ALRS data-plane's own single-segment ids (they slot
into paths like /repositories/<id>/), not Pulp hrefs. Pulp's native ids are
hrefs such as /pulp/api/v3/repositories/rpm/rpm/<uuid>/ and are never surfaced
to the CLI - the data-plane abstracts Pulp away.
"""

import re
from typing import Any

from azure.cli.core.azclierror import RequiredArgumentMissingError, ResourceNotFoundError

from azext_alrs.server._paging import iter_results

_UUID = r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"

# Apt releases (deb + debsrc share them) translate from Pulp's
# /content/deb/releases/<uuid>/ href, so their ALRS id is content-deb-releases-<uuid>.
# This is server-defined and may shift as the data plane matures.
_RELEASE_ID_PREFIX = "content-deb-releases"

# Release components translate from /content/deb/release_components/<uuid>/, so
# their ALRS id is content-deb-release_components-<uuid>.
_RELEASE_COMPONENT_ID_PREFIX = "content-deb-release_components"


def _looks_like_id(resource: str, value: str) -> bool:
    # an ALRS resource id is a single path segment ending in a uuid, optionally
    # with a leading resource/type token (e.g. "<resource>-deb-<uuid>"). we key
    # off the uuid and anchor any prefix to the known resource (not an open-ended
    # [a-z-]*) so a plain name that happens to end in a uuid (e.g. "my-repo-<uuid>")
    # isn't misread as an id and shoved straight into a request path. fullmatch so
    # trailing junk or newlines fall through to the name lookup too.
    return re.fullmatch(rf"(?:{re.escape(resource)}-[a-z-]*)?{_UUID}", value) is not None


def resolve_id_or_name(client: Any, resource: str, value: str) -> str:
    """Return value as-is if it already looks like an id, else look it up by name.

    resource is the collection path segment, e.g. "repositories" or "remotes".
    Raises ResourceNotFoundError if nothing by that name exists.
    """
    if not value or _looks_like_id(resource, value):
        return value

    body = client.get(f"/{resource}/", params={"name": value}).json()
    results = body.get("results") if isinstance(body, dict) else body
    if not results:
        raise ResourceNotFoundError(f"Could not find {resource} with id or name '{value}'.")
    return str(results[0]["id"])


def resolve_release(client: Any, repository_id: str | None, value: str) -> str:
    """Resolve an apt release name-or-id to an id.

    Releases are nested under a repository, so a name lookup needs the repo in
    the path: GET /repositories/<repo>/releases/?name=<value>. A value that is
    already an id needs no repo context and is returned as-is.
    """
    if not value or _looks_like_id(_RELEASE_ID_PREFIX, value):
        return value
    if not repository_id:
        raise RequiredArgumentMissingError("Resolving a release by name requires --repository.")
    body = client.get(f"/repositories/{repository_id}/releases/", params={"name": value}).json()
    results = body.get("results") if isinstance(body, dict) else body
    if not results:
        raise ResourceNotFoundError(
            f"Could not find release with id or name '{value}' in repository '{repository_id}'."
        )
    return str(results[0]["id"])


def resolve_release_name(client: Any, repository_id: str | None, value: str) -> str:
    """Resolve an apt release name-or-id to its name (pulp_deb's ``distribution``).

    The packages endpoint scopes a change by release *name*, not id, so an id
    has to be turned back into one. A value that isn't an id is already a name
    and is returned as-is. The release list carries no id filter, so the repo's
    releases are matched client-side; this also confirms the release is in the
    repository the caller named.
    """
    if not value or not _looks_like_id(_RELEASE_ID_PREFIX, value):
        return value
    if not repository_id:
        raise RequiredArgumentMissingError("Resolving a release by id requires --repository.")
    for release in iter_results(client, f"/repositories/{repository_id}/releases/"):
        if release.get("id") == value:
            return str(release["distribution"])
    raise ResourceNotFoundError(
        f"Could not find release with id '{value}' in repository '{repository_id}'."
    )


def resolve_release_component(
    client: Any, repository_id: str | None, release_id: str | None, value: str
) -> str:
    """Resolve a release component name-or-id to an id.

    A component name (e.g. main) is only unique within a release, so a name
    lookup is scoped to the release's components:
    GET /repositories/<repo>/releases/<release_id>/components/?component=<value>.
    A value that is already an id is returned as-is.
    """
    if not value or _looks_like_id(_RELEASE_COMPONENT_ID_PREFIX, value):
        return value
    if not repository_id:
        raise RequiredArgumentMissingError(
            "Resolving a release component by name requires --repository."
        )
    if not release_id:
        raise RequiredArgumentMissingError(
            "Resolving a release component by name requires --release."
        )
    body = client.get(
        f"/repositories/{repository_id}/releases/{release_id}/components/",
        params={"component": value},
    ).json()
    results = body.get("results") if isinstance(body, dict) else body
    if not results:
        raise ResourceNotFoundError(
            f"Could not find release component '{value}' in release '{release_id}' "
            f"of repository '{repository_id}'."
        )
    return str(results[0]["id"])
