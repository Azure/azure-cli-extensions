import ast
import os
import textwrap
import unittest


def _safe_get(mapping, *keys):
    current = mapping
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def _extract_function(file_name, func_name, globals_dict):
    src_path = os.path.join(os.path.dirname(__file__), "..", "..", file_name)
    src_path = os.path.normpath(src_path)
    with open(src_path, "r", encoding="utf-8") as handle:
        source = handle.read()

    tree = ast.parse(source, filename=src_path)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_source = ast.get_source_segment(source, node)
            namespace = dict(globals_dict)
            exec(compile(textwrap.dedent(func_source), src_path, "exec"), namespace)  # pylint: disable=exec-used
            return namespace[func_name]

    raise ValueError(f"Function {func_name!r} not found in {src_path}")


def _to_camel_case(value):
    components = value.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def _convert_object_from_snake_to_camel_case(value):
    if isinstance(value, list):
        return [_convert_object_from_snake_to_camel_case(item) if isinstance(item, (dict, list)) else item for item in value]
    return {
        _to_camel_case(key): _convert_object_from_snake_to_camel_case(item) if isinstance(item, (dict, list)) else item
        for key, item in value.items()
    }


class TestRestoreUserAssignedIdentityResourceIds(unittest.TestCase):

    def test_restores_identity_resource_ids_after_camel_case_normalization(self):
        restore_user_assigned_identity_resource_ids = _extract_function(  # pylint: disable=invalid-name
            "_decorator_utils.py",
            "restore_user_assigned_identity_resource_ids",
            {"safe_get": _safe_get},
        )

        resource_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/"
            "NAME-PARTS-DIVIDED-BY-DASHES-RG_NAME_PARTS_DIVIDED_BY_UNDERSCORES/"
            "providers/Microsoft.ManagedIdentity/userAssignedIdentities/test-identity"
        )
        yaml_containerapp = {
            "identity": {
                "type": "UserAssigned",
                "userAssignedIdentities": {
                    resource_id: {}
                }
            }
        }
        converted_containerapp = _convert_object_from_snake_to_camel_case({
            "identity": {
                "type": "UserAssigned",
                "user_assigned_identities": {
                    resource_id: {}
                }
            }
        })

        self.assertNotIn(resource_id, converted_containerapp["identity"]["userAssignedIdentities"])

        restored_containerapp = restore_user_assigned_identity_resource_ids(yaml_containerapp, converted_containerapp)

        self.assertEqual(
            list(restored_containerapp["identity"]["userAssignedIdentities"].keys()),
            [resource_id],
        )

    def test_leaves_objects_without_user_assigned_identities_unchanged(self):
        restore_user_assigned_identity_resource_ids = _extract_function(  # pylint: disable=invalid-name
            "_decorator_utils.py",
            "restore_user_assigned_identity_resource_ids",
            {"safe_get": _safe_get},
        )

        normalized_containerapp = {"identity": {"type": "SystemAssigned"}}

        self.assertIs(
            restore_user_assigned_identity_resource_ids({"identity": {"type": "SystemAssigned"}}, normalized_containerapp),
            normalized_containerapp,
        )


if __name__ == "__main__":
    unittest.main()
