# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Azure CLI Extensions implementations of the X Engineering Agent engine hooks."""

from repository_tools.fixer.azure_cli import guidance, targets
from repository_tools.fixer.formatting import guidance as formatting
from repository_tools.reviewer.azure_cli import failures
from repository_tools.reviewer.policy import analysis
from repository_tools.settings import EXECUTION_INSTRUCTIONS, _AAZ_OUTPUT_PATTERN
from repository_tools.tester.azure_cli import live_tests
from x_engineering_agent.tools.reviews.inspection import _verified_generation_source_prs

REPOSITORY = "Azure/azure-cli-extensions"


def infer_target(text=None, pr_files=None):
    return targets.infer_target(text=text, pr_files=pr_files)


def resolve_target(name):
    return targets.resolve_target(name)


def live_test_target(text, pr_files, module=None, target_kind=None):
    return targets._live_test_target(text, pr_files, module, target_kind)


def codegen_guidance(component=None):
    return guidance._codegen_execution_guidance("cli-ext", component)


def execution_instructions():
    return "\n".join(EXECUTION_INSTRUCTIONS)


def pr_title(component=None, issue_number=None, command=None, summary=None, customer_facing=True):
    return formatting.pr_title_for(
        component=component, issue_number=issue_number, command=command,
        summary=summary, customer_facing=customer_facing, style="cli",
    )


def pr_format_guidance(component=None, issue_number=None, customer_facing=True,
                       command=None, issue_repo=None, summary=None):
    return formatting.pr_format_guidance(
        component=component, issue_number=issue_number, customer_facing=customer_facing,
        command=command, issue_repo=issue_repo, summary=summary, style="cli",
    )


def changed_test_files(pr_files):
    return live_tests.changed_test_files(pr_files)


def live_test_plan(pr_files):
    return live_tests._live_test_plan(pr_files)


def regression_coverage(owner, repo, pr_number, pr_files=None, pr=None, file_changes=None,
                        issue_evidence=None, review_feedback=None):
    return live_tests.get_pr_regression_coverage_summary(
        owner, repo, pr_number, pr_files=pr_files, pr=pr, file_changes=file_changes,
        issue_evidence=issue_evidence, review_feedback=review_feedback,
    )


def analyze_review(pr, file_changes, head_repo=None, head_sha=None, generation_source_prs=None):
    return analysis.analyze_review_tools(
        REPOSITORY, pr, file_changes, head_repo=head_repo, head_sha=head_sha,
        generation_source_prs=generation_source_prs,
    )


def classify_test_failures(failed_tests, pr_files, target=None):
    return failures.classify_test_failures(failed_tests, pr_files, target)


def extract_failed_tests(text):
    return failures.extract_failed_tests_from_text(text)


def readiness_policy(pr, file_changes):
    return {"blocked": _ownership_block(pr, file_changes), "validation_required": False}


def _ownership_block(pr, file_changes):
    has_aaz_output = any(
        _AAZ_OUTPUT_PATTERN.search(change.get("filename") or "") for change in file_changes
    )
    sources = _verified_generation_source_prs(pr.get("body") or "") if has_aaz_output else None
    head = pr.get("head") or {}
    findings, _ = analysis._generated_ownership_check(
        REPOSITORY, pr, file_changes, file_changes,
        (head.get("repo") or {}).get("full_name"), head.get("sha"), sources,
    )
    if not findings:
        return None
    return {
        "reason": "codegen ownership preflight failed",
        "findings": [finding["summary"] for finding in findings],
    }
