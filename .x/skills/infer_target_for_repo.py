# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Infer an Azure CLI Extensions target from trusted repository structure."""


def infer_target_for_repo(text, pr_files):
    """Resolve sanitized issue text or PR files to a live extension target."""
    extensions = list_repository_directories(
        source_repository="Azure/azure-cli-extensions",
    )

    def normalize(value):
        return "".join(
            character
            for character in str(value or "").casefold()
            if character.isalnum()
        )

    def resolve(candidate):
        candidate_normalized = normalize(candidate)
        for extension in extensions:
            if normalize(extension) == candidate_normalized:
                return {
                    "kind": "extension",
                    "name": extension,
                    "repo": "Azure/azure-cli-extensions",
                }
        return None

    scores = {}
    for path in pr_files or []:
        parts = str(path).replace("\\", "/").split("/")
        if len(parts) > 1 and parts[0].casefold() == "src":
            candidate = parts[1]
            scores[candidate] = scores.get(candidate, 0) + 10
    if pr_files:
        for candidate in sorted(scores, key=lambda item: (-scores[item], item)):
            target = resolve(candidate)
            if target is not None:
                return target
        return {"kind": "none", "name": None, "repo": None}

    cleaned = "".join(
        character if character.isalnum() or character in "-_./" else " "
        for character in str(text or "").casefold()
    )
    words = cleaned.split()
    for index, word in enumerate(words):
        if word == "az" and index + 1 < len(words):
            candidate = words[index + 1]
            scores[candidate] = scores.get(candidate, 0) + 5
        if word.startswith("src/"):
            parts = word.split("/")
            if len(parts) > 1:
                candidate = parts[1]
                scores[candidate] = scores.get(candidate, 0) + 3
        if word.startswith("azext_"):
            candidate = word[len("azext_"):]
            scores[candidate] = scores.get(candidate, 0) + 3
        if word.startswith("azext-"):
            candidate = word[len("azext-"):]
            scores[candidate] = scores.get(candidate, 0) + 3
    for candidate in sorted(scores, key=lambda item: (-scores[item], item)):
        target = resolve(candidate)
        if target is not None:
            return target
    return {"kind": "unknown", "name": None, "repo": None}
