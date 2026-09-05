# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from unittest import mock

from azext_containerapp._compose_utils import (
    _expand_env_var_substitution,
    resolve_environment_from_service,
)


class TestExpandEnvVarSubstitution(unittest.TestCase):
    """Unit tests for _expand_env_var_substitution()."""

    def _clean_env(self, *var_names):
        """Context manager that removes specified env vars and restores them."""
        return _CleanEnv(*var_names)

    # ------------------------------------------------------------------
    # ${VAR:-default} — use default when unset OR empty
    # ------------------------------------------------------------------

    def test_unset_var_with_colon_dash_default(self):
        """${VAR_C:-bar} → 'bar' when VAR_C is not set (the primary bug scenario)."""
        with _CleanEnv("VAR_C"):
            result = _expand_env_var_substitution("${VAR_C:-bar}")
        self.assertEqual(result, "bar")

    def test_empty_var_with_colon_dash_default(self):
        """${VAR:-default} → 'default' when VAR is set to empty string."""
        with _SetEnv(VAR_C=""):
            result = _expand_env_var_substitution("${VAR_C:-bar}")
        self.assertEqual(result, "bar")

    def test_set_var_with_colon_dash_default(self):
        """${VAR:-default} → actual value when VAR is set to non-empty string."""
        with _SetEnv(VAR_C="world"):
            result = _expand_env_var_substitution("${VAR_C:-bar}")
        self.assertEqual(result, "world")

    # ------------------------------------------------------------------
    # ${VAR-default} — use default only when unset (not when empty)
    # ------------------------------------------------------------------

    def test_unset_var_with_dash_default(self):
        """${VAR-default} → 'default' when VAR is not set."""
        with _CleanEnv("VAR_C"):
            result = _expand_env_var_substitution("${VAR_C-bar}")
        self.assertEqual(result, "bar")

    def test_empty_var_with_dash_default(self):
        """${VAR-default} → '' (empty) when VAR is set to empty string."""
        with _SetEnv(VAR_C=""):
            result = _expand_env_var_substitution("${VAR_C-bar}")
        self.assertEqual(result, "")

    def test_set_var_with_dash_default(self):
        """${VAR-default} → actual value when VAR is set."""
        with _SetEnv(VAR_C="hello"):
            result = _expand_env_var_substitution("${VAR_C-bar}")
        self.assertEqual(result, "hello")

    # ------------------------------------------------------------------
    # ${VAR} — simple substitution
    # ------------------------------------------------------------------

    def test_set_var_simple(self):
        """${VAR} → actual value when VAR is set."""
        with _SetEnv(MY_VAR="hello"):
            result = _expand_env_var_substitution("${MY_VAR}")
        self.assertEqual(result, "hello")

    def test_unset_var_simple(self):
        """${VAR} → empty string when VAR is not set."""
        with _CleanEnv("MY_VAR"):
            result = _expand_env_var_substitution("${MY_VAR}")
        self.assertEqual(result, "")

    # ------------------------------------------------------------------
    # Already-expanded values pass through unchanged
    # ------------------------------------------------------------------

    def test_plain_string_unchanged(self):
        """Plain string with no substitution syntax is returned unchanged."""
        result = _expand_env_var_substitution("hello")
        self.assertEqual(result, "hello")

    def test_already_expanded_value_unchanged(self):
        """A value that was already expanded (e.g. 'bar') is not modified."""
        result = _expand_env_var_substitution("bar")
        self.assertEqual(result, "bar")

    # ------------------------------------------------------------------
    # Non-string values pass through unchanged
    # ------------------------------------------------------------------

    def test_none_passthrough(self):
        result = _expand_env_var_substitution(None)
        self.assertIsNone(result)

    def test_integer_passthrough(self):
        result = _expand_env_var_substitution(42)
        self.assertEqual(result, 42)


class TestResolveEnvironmentFromService(unittest.TestCase):
    """Unit tests for resolve_environment_from_service()."""

    def _make_service(self, env_dict):
        """Create a mock compose service with the given environment dict."""
        service = mock.MagicMock()
        service.resolve_environment_hierarchy.return_value = env_dict
        return service

    def test_unset_var_default_expanded(self):
        """The primary bug: ${VAR_C:-bar} must expand to 'bar' when VAR_C is unset."""
        with _CleanEnv("VAR_C"):
            service = self._make_service({"VAR_C": "${VAR_C:-bar}"})
            result = resolve_environment_from_service(service)
        self.assertEqual(result, ["VAR_C=bar"])

    def test_set_var_uses_actual_value(self):
        """When VAR_C is set, its actual value is used."""
        with _SetEnv(VAR_C="myprod"):
            service = self._make_service({"VAR_C": "${VAR_C:-bar}"})
            result = resolve_environment_from_service(service)
        self.assertEqual(result, ["VAR_C=myprod"])

    def test_mixed_set_and_unset_vars(self):
        """Multiple env vars: set vars keep their values, unset vars use defaults."""
        with _CleanEnv("VAR_C"), _SetEnv(VAR_A="hello", VAR_B="world"):
            service = self._make_service({
                "VAR_A": "${VAR_A}",
                "VAR_B": "${VAR_B:-foo}",
                "VAR_C": "${VAR_C:-bar}",
            })
            result = resolve_environment_from_service(service)
        self.assertEqual(result, ["VAR_A=hello", "VAR_B=world", "VAR_C=bar"])

    def test_already_expanded_values_unchanged(self):
        """Values already expanded by pycomposefile pass through correctly."""
        service = self._make_service({"RACK_ENV": "development", "SHOW": "true"})
        result = resolve_environment_from_service(service)
        self.assertEqual(result, ["RACK_ENV=development", "SHOW=true"])

    def test_none_env_hierarchy_returns_none(self):
        """When resolve_environment_hierarchy() returns None, result is None."""
        service = self._make_service(None)
        result = resolve_environment_from_service(service)
        self.assertIsNone(result)

    def test_none_value_triggers_prompt(self):
        """When a value is None (unset with no default), the user is prompted."""
        service = self._make_service({"LOREM": None})
        with mock.patch("knack.prompting.prompt", return_value="prompted_value") as mock_prompt:
            result = resolve_environment_from_service(service)
        mock_prompt.assert_called_once()
        self.assertEqual(result, ["LOREM=prompted_value"])


# ---------------------------------------------------------------------------
# Helper context managers
# ---------------------------------------------------------------------------

class _CleanEnv:
    """Context manager that temporarily removes named environment variables."""

    def __init__(self, *var_names):
        self._var_names = var_names
        self._saved = {}

    def __enter__(self):
        for name in self._var_names:
            self._saved[name] = os.environ.pop(name, None)
        return self

    def __exit__(self, *_):
        for name, old_val in self._saved.items():
            if old_val is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old_val


class _SetEnv:
    """Context manager that temporarily sets named environment variables."""

    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._saved = {}

    def __enter__(self):
        for name, val in self._kwargs.items():
            self._saved[name] = os.environ.get(name)
            os.environ[name] = val
        return self

    def __exit__(self, *_):
        for name, old_val in self._saved.items():
            if old_val is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old_val


if __name__ == "__main__":
    unittest.main()
