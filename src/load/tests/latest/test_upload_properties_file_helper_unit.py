import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import ANY, Mock


def _load_upload_properties_file_helper():
    utils_file = Path(__file__).resolve().parents[2] / "azext_load" / "data_plane" / "utils" / "utils.py"
    source = utils_file.read_text(encoding="utf-8")
    module = ast.parse(source)
    helper = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "upload_properties_file_helper"
    )
    helper_module = ast.Module(body=[helper], type_ignores=[])
    upload_generic_files_helper = Mock()
    namespace = {
        "AllowedFileTypes": SimpleNamespace(
            USER_PROPERTIES=SimpleNamespace(value="USER_PROPERTIES")
        ),
        "upload_generic_files_helper": upload_generic_files_helper,
    }
    exec(compile(helper_module, str(utils_file), "exec"), namespace)
    return namespace["upload_properties_file_helper"], upload_generic_files_helper


def test_upload_properties_file_helper_handles_null_properties():
    helper, upload_generic_files_helper = _load_upload_properties_file_helper()

    helper(
        client=Mock(),
        test_id="test-id",
        yaml_data={"properties": None},
        load_test_config_file="loadtest.yaml",
        existing_test_files=[],
        wait=True,
    )

    upload_generic_files_helper.assert_not_called()


def test_upload_properties_file_helper_uploads_user_properties_file():
    helper, upload_generic_files_helper = _load_upload_properties_file_helper()

    helper(
        client=Mock(),
        test_id="test-id",
        yaml_data={"properties": {"userPropertyFile": "user.properties"}},
        load_test_config_file="loadtest.yaml",
        existing_test_files=[
            {"fileType": "USER_PROPERTIES"},
            {"fileType": "JMX_FILE"},
        ],
        wait=False,
    )

    upload_generic_files_helper.assert_called_once_with(
        client=ANY,
        test_id="test-id",
        load_test_config_file="loadtest.yaml",
        existing_files=[{"fileType": "USER_PROPERTIES"}],
        file_to_upload="user.properties",
        file_type=SimpleNamespace(value="USER_PROPERTIES"),
        wait=False,
    )
