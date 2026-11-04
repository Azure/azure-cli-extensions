# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Repository-owned validation; execute only in the dedicated job sandbox."""

import ast
import json
import os
from pathlib import Path
import sys
from xml.etree import ElementTree

from x_engineering_agent.tools.copilot.validation import run_command


def python_unit_classes(path):
    tree = ast.parse(path.read_bytes(), filename=str(path))
    selected = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        bases = [base.id if isinstance(base, ast.Name) else base.attr for base in node.bases if isinstance(base, (ast.Name, ast.Attribute))]
        if 'TestCase' in bases and (not any((base.endswith(('ScenarioTest', 'LiveScenarioTest')) for base in bases))):
            selected.append(node.name)
    return selected


def python_unit_files(repository, root, changed):
    selections = set()
    for path in changed:
        parts = path.relative_to(root).parts
        scope = None
        if repository == 'Azure/azure-cli-extensions' and len(parts) > 2 and (parts[0] == 'src'):
            scope = root / 'src' / parts[1]
        if scope is None or path.suffix != '.py':
            continue
        if path.name.startswith('test_') and path.exists():
            selections.add((scope, path, None))
        else:
            stem = path.stem.lstrip('_')
            if stem:
                selections.add((scope, f'test_{stem}.py', path.parent))
    selected = set()
    for scope, target, source_dir in sorted(selections, key=lambda item: tuple(map(str, item))):
        if isinstance(target, Path):
            if (target == scope or scope in target.parents) and python_unit_classes(target):
                selected.add(target)
        else:
            matches = [path for path in scope.rglob(target) if python_unit_classes(path)]
            if not matches:
                matches = [path for path in scope.rglob('test_*.py') if python_unit_classes(path)]
            if not matches:
                continue
            source_parts = source_dir.relative_to(scope).parts if source_dir.is_relative_to(scope) else ()

            def component_distance(path):
                test_parts = path.parent.relative_to(scope).parts
                if 'tests' in test_parts:
                    test_parts = test_parts[:test_parts.index('tests')]
                shared = 0
                for source_part, test_part in zip(source_parts, test_parts):
                    if source_part != test_part:
                        break
                    shared += 1
                return len(source_parts) + len(test_parts) - 2 * shared
            closest = min((component_distance(path) for path in matches))
            selected.update((path for path in matches if component_distance(path) == closest))
    if len(selected) > 100:
        raise RuntimeError('Changed components exceed the bounded unit-test selection budget')
    return sorted(selected)


def python_checks(repository, root, changed, deadline):
    tests = python_unit_files(repository, root, changed)
    if not tests:
        return {'executed': 0, 'skipped': 0, 'coverage': 'none', 'reason': 'No credential-free unittest.TestCase suite in the changed components; repository CI remains required'}
    home = Path(os.environ['HOME'])
    result_path = home / 'foundry-unit-results.xml'
    roots = [root]
    if repository == 'Azure/azure-cli-extensions':
        roots += sorted({root / 'src' / path.relative_to(root).parts[1] for path in tests})
    env = {**os.environ, 'PYTHONPATH': os.pathsep.join(map(str, roots)), 'PYTHONDONTWRITEBYTECODE': '1', 'AZURE_TEST_RUN_LIVE': 'false', 'AZURE_TEST_MODE': 'Playback', 'AZURE_CONFIG_DIR': str(home / '.azure'), 'AZURE_CORE_COLLECT_TELEMETRY': 'false', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1'}
    runner = [sys.executable, '-m', 'pytest']
    nodes = [f'{path}::{name}' for path in tests for name in python_unit_classes(path)]
    run_command([*runner, '-q', '-p', 'no:cacheprovider', '-o', 'addopts=', '--junitxml', str(result_path), *nodes], root=root, deadline=deadline, env=env)
    suites = list(ElementTree.parse(result_path).getroot().iter('testsuite'))
    counts = {name: sum((int(suite.get(name, 0)) for suite in suites)) for name in ('tests', 'failures', 'errors', 'skipped')}
    executed = counts['tests'] - counts['skipped']
    if executed <= 0 or counts['failures'] or counts['errors']:
        raise RuntimeError('Selected unit tests did not execute successfully')
    return {'executed': executed, 'skipped': counts['skipped'], 'coverage': 'selected_component_unit_tests'}


def aaz_checks(root, changed, deadline):
    import aaz_dev
    from command.model.configuration import CMDClientConfig, CMDConfiguration, XMLSerializer
    groups = set()
    models = 0
    full = False
    for path in changed:
        relative = path.relative_to(root)
        if relative.parts[0] == 'Commands':
            if len(relative.parts) > 2 and (root / 'Commands' / relative.parts[1]).is_dir():
                groups.add(relative.parts[1])
            else:
                full = True
        if relative.parts[0] != 'Resources' or path.suffix not in {'.json', '.xml'}:
            continue
        if not path.exists():
            full = True
            continue
        for candidate in (path.with_suffix('.json'), path.with_suffix('.xml')):
            if not candidate.is_file():
                raise ValueError('AAZ resource validation requires both JSON and XML representations')
            model_type = CMDClientConfig if candidate.name.startswith('client') else CMDConfiguration
            model = model_type(json.loads(candidate.read_text())) if candidate.suffix == '.json' else XMLSerializer.from_xml(model_type, candidate.read_text())
            model.validate()
            if model_type is CMDConfiguration:
                model.link()
                groups.update((group.name.split()[0] for group in model.command_groups))
            model.reformat()
            model.validate()
            models += 1
    targets = [None] if full or not groups else sorted(groups)
    for target in targets:
        argv = ['aaz-dev', 'command-model', 'verify', '--aaz-path', str(root)]
        if target is not None:
            if not (root / 'Commands' / target).is_dir():
                raise ValueError('AAZ verification target does not exist')
            argv += ['--target', target]
        run_command(argv, root=root, deadline=deadline)
    return {'schema_models': models, 'metadata_targets': len(targets), 'coverage': 'schema_and_reference_consistency'}


def repository_checks(repository, root, paths, deadline, checks):
    units = python_checks(repository, root, paths, deadline)
    receipt = {'status': 'passed', 'static_checks': checks, 'unit_tests': units, 'repository_ci_required': True, 'live_tests_required': repository in {'Azure/azure-cli-extensions'}, 'csharp_build_or_unit_coverage': False, 'powershell_unit_coverage': False}
    if repository == 'Azure/aaz':
        receipt['aaz'] = aaz_checks(root, paths, deadline)
    return receipt
