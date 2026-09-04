"""Evaluate Azure CLI Extensions module regression coverage."""


def get_pr_regression_coverage_summary(pr_number):
    """Find changed extension modules without focused tests or recordings."""
    changes = get_pr_file_changes(
        owner=None,
        repo=None,
        pr_number=pr_number,
    )
    files = [
        item.get("filename")
        for item in changes
        if isinstance(item, dict) and item.get("filename")
    ]
    production_files = []
    modules = set()
    for path in files:
        normalized = str(path).replace("\\", "/")
        parts = normalized.split("/")
        name = parts[-1]
        if (
            len(parts) >= 2
            and parts[0].casefold() == "src"
            and normalized.endswith(".py")
            and "/tests/" not in normalized
            and name not in {"__init__.py", "_help.py", "setup.py"}
        ):
            production_files.append(normalized)
            modules.add(parts[1].casefold())

    test_files = []
    recording_files = []
    covered = set()
    for path in files:
        normalized = str(path).replace("\\", "/")
        parts = normalized.split("/")
        if (
            len(parts) < 2
            or parts[0].casefold() != "src"
            or "/tests/" not in normalized
        ):
            continue
        module = parts[1].casefold()
        if module not in modules:
            continue
        name = parts[-1]
        if name.casefold().startswith("test_") and name.casefold().endswith(".py"):
            test_files.append(normalized)
            covered.add(module)
        if "/recordings/" in normalized:
            recording_files.append(normalized)
            covered.add(module)

    uncovered = sorted(modules - covered)
    return {
        "applicable": bool(production_files),
        "gap": bool(uncovered),
        "modules": sorted(modules),
        "uncovered_modules": uncovered,
        "production_files": production_files,
        "test_files": test_files,
        "recording_files": recording_files,
    }
