"""Select changed Azure CLI Extensions live-test files."""


def changed_test_files(pr_files):
    """Return unique changed pytest paths under an extension tests tree."""
    selected = []
    seen = set()
    for path in pr_files or []:
        normalized = str(path).replace("\\", "/")
        lowered = normalized.casefold()
        parts = normalized.split("/")
        name = parts[-1]
        if (
            len(parts) < 2
            or parts[0].casefold() != "src"
            or "/tests/" not in f"/{lowered}"
            or not name.casefold().startswith("test_")
            or not name.casefold().endswith(".py")
        ):
            continue
        if normalized not in seen:
            seen.add(normalized)
            selected.append(normalized)
    return selected
