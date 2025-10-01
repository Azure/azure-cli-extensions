from pathlib import Path

import pytest

try:
    from mypy import api as mypy_api
except ImportError:
    mypy_api = None


@pytest.fixture(scope="module", autouse=True)
def check_mypy():
    if mypy_api is None:
        pytest.skip("missing mypy import")


AZEXT_ROOT = Path(__file__).resolve().parents[2]
LIB_ROOT = AZEXT_ROOT / "lib"
MYPY_ARGS = [
    "--explicit-package-bases",
]


def _discover_modules() -> list[tuple[str, Path]]:
    modules: list[tuple[str, Path]] = []
    for path in sorted(AZEXT_ROOT.rglob("*.py")):
        if not path.is_file():
            continue
        rel = path.relative_to(AZEXT_ROOT)
        module_name = f"{rel.with_suffix('').as_posix().replace('/', '.')}"
        modules.append((module_name, path))
    return modules


MODULE_PATHS = _discover_modules()


# These files already existed when this test was added and will be fixed incrementally
BAD_MODULES = {
    "__init__",
    "_params",
    "_validators",
    "_help",
    "config",
    "container",
    "cose_proxy",
    "custom",
    "errors",
    "fragment_util",
    "init_checks",
    "kata_proxy",
    "oras_proxy",
    "os_util",
    "rootfs_proxy",
    "security_policy",
    "template_util",
    "tests"
}


@pytest.mark.parametrize(
    "module_name, target_path",
    [pytest.param(name, path, id=name) for name, path in MODULE_PATHS],
)
def test_mypy(module_name: str, target_path: Path):
    assert MODULE_PATHS, f"No Python files discovered under {LIB_ROOT}"

    if any(module_name.startswith(bad_module) for bad_module in BAD_MODULES):
        pytest.skip(f"Skipping mypy test for {module_name} due to known issues")

    stdout, stderr, exit_status = mypy_api.run([*MYPY_ARGS, str(target_path)])
    assert exit_status == 0, (
        f"mypy reported issues for {module_name}\n"
        f"command: mypy {' '.join(MYPY_ARGS + [str(target_path)])}\n"
        f"stdout:\n{stdout}\n"
        f"stderr:\n{stderr}"
    )
