# mypy: ignore-errors

import pytest

pytest.importorskip("azure.cli.core")


def test_generated_registry_commands_use_the_expected_api_contract():
    from azext_alrs.aaz.latest.alrs.registry._create import Create
    from azext_alrs.aaz.latest.alrs.registry._delete import Delete
    from azext_alrs.aaz.latest.alrs.registry._list import List
    from azext_alrs.aaz.latest.alrs.registry._show import Show
    from azext_alrs.aaz.latest.alrs.registry._update import Update

    commands = [Create, Delete, Show, Update]
    expected_path = (
        "/subscriptions/{}/resourcegroups/{}/providers/microsoft.packageregistry/registries/{}"
    )
    for command in commands:
        assert command._aaz_info["version"] == "2026-04-01-preview"
        assert command._aaz_info["resources"][0][1] == expected_path

    assert Create.AZ_SUPPORT_NO_WAIT
    # Delete tears down the whole data plane, so it is long-running like create.
    assert Delete.AZ_SUPPORT_NO_WAIT
    assert [resource[1] for resource in List._aaz_info["resources"]] == [
        "/subscriptions/{}/providers/microsoft.packageregistry/registries",
        expected_path.rsplit("/", 1)[0],
    ]


def test_generated_registry_commands_block_dev_builds(monkeypatch):
    from azure.cli.core.azclierror import ValidationError
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader
    from azext_alrs.aaz.latest.alrs.registry._create import Create
    from azext_alrs.aaz.latest.alrs.registry._delete import Delete
    from azext_alrs.aaz.latest.alrs.registry._list import List
    from azext_alrs.aaz.latest.alrs.registry._show import Show
    from azext_alrs.aaz.latest.alrs.registry._update import Update
    from azext_alrs.aaz.latest.alrs.registry._wait import Wait
    from azext_alrs.server import _data_plane

    monkeypatch.setattr(_data_plane, "is_dev_extension", lambda: True)
    commands = [
        Create(cli_ctx=DummyCli()),
        Delete(cli_ctx=DummyCli()),
        Show(cli_ctx=DummyCli()),
        List(cli_ctx=DummyCli()),
        Update(cli_ctx=DummyCli()),
        Wait(AlrsCommandsLoader(cli_ctx=DummyCli())),
    ]
    for command in commands:
        with pytest.raises(ValidationError, match="not available in a local dev build"):
            command.pre_operations()
