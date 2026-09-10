import pytest

pytest.importorskip("azure.cli.core")


def test_loader_instantiates():
    from azext_alrs import COMMAND_LOADER_CLS, AlrsCommandsLoader

    assert COMMAND_LOADER_CLS is AlrsCommandsLoader


def test_client_factory_placeholder_raises(monkeypatch):
    from azext_alrs._client_factory import cf_alrs
    from azext_alrs.server import _data_plane

    # a dev build is refused before reaching the placeholder, and this test runs
    # as one for anyone who has registered extension.dev_sources
    monkeypatch.setattr(_data_plane, "is_dev_extension", lambda: False)
    with pytest.raises(NotImplementedError):
        cf_alrs(cli_ctx=None)


def test_command_table_registers_registry_verbs():
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    registered = {k for k in loader.command_table if k.startswith("alrs registry")}
    expected = {
        f"alrs registry {verb}" for verb in ["create", "delete", "show", "list", "update", "wait"]
    }
    assert registered == expected


def test_data_plane_commands_resolve_to_own_module_without_control_plane_factory():
    # Regression guard: every data-plane command group must register with
    # `custom_command_type=<its own type>`. Passing the type positionally (as
    # `command_type`) silently falls back to the loader default, which points at
    # the control-plane `registry` module AND attaches `cf_alrs` — so the command
    # resolves to a nonexistent `registry#<func>` op and dies in the client
    # factory before its handler ever runs.
    from azure.cli.core.mock import DummyCli

    from azext_alrs import AlrsCommandsLoader

    loader = AlrsCommandsLoader(cli_ctx=DummyCli())
    loader.load_command_table(None)

    data_plane = {
        name: cmd
        for name, cmd in loader.command_table.items()
        if name.startswith("alrs ") and not name.startswith("alrs registry")
    }
    assert data_plane, "expected data-plane commands to be registered"
    for name, cmd in data_plane.items():
        kwargs = cmd.command_kwargs
        assert kwargs.get("client_factory") is None, (
            f"{name!r} leaked the control-plane client_factory; register its group "
            f"with custom_command_type=<type>, not a positional command_type"
        )
        assert kwargs["operations_tmpl"] != "azext_alrs.commands.registry#{}", (
            f"{name!r} resolves to the control-plane registry module instead of its "
            f"own data-plane module"
        )

    # Registry commands are generated AAZ management-plane commands rather than
    # custom commands that inherit the data-plane loader's placeholder factory.
    for verb in ["create", "delete", "show", "list", "update", "wait"]:
        cmd = loader.command_table[f"alrs registry {verb}"]
        assert cmd.command_kwargs.get("client_factory") is None
