# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import os
import sys
import sysconfig
import unittest


class DependencyDeclarationTests(unittest.TestCase):
    """Keep setup.py's DEPENDENCIES in sync with what the shipped code actually imports.

    Extensions are installed with ``pip install --target``, so the declared list is
    vendored wholesale into the extension folder: an unused entry drags its whole
    transitive tree along (this is what broke 32-bit installs via opencensus ->
    google-api-core -> google-auth -> cryptography), and a missing entry only works
    by accident for as long as the CLI happens to ship that package.

    This is a static, dependency-free scan so it runs anywhere without network access.
    """

    PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    SETUP_PY = os.path.join(os.path.dirname(PACKAGE_ROOT), 'setup.py')

    # Top-level modules azure-cli-core guarantees, so the extension must not vendor them:
    # 'azure'/'knack' are the CLI framework itself and 'requests' is required by msal/msrest.
    CLI_PROVIDED = {'azure', 'knack', 'requests'}

    # Distribution name -> imported module name, where the two differ.
    DIST_TO_MODULE = {}

    def _declared_distributions(self):
        with open(self.SETUP_PY, encoding='utf-8') as handle:
            tree = ast.parse(handle.read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == 'DEPENDENCIES' for t in node.targets):
                continue
            declared = set()
            for element in node.value.elts:
                requirement = element.value
                name = requirement.split('~=')[0].split('==')[0].split('>=')[0].split('<')[0]
                declared.add(name.strip().lower().replace('-', '_'))
            return declared
        self.fail('Could not find a DEPENDENCIES assignment in setup.py')

    def _imported_modules(self):
        modules = set()
        for root, _, files in os.walk(self.PACKAGE_ROOT):
            if 'tests' in root.split(os.sep):
                continue
            for name in files:
                if not name.endswith('.py'):
                    continue
                with open(os.path.join(root, name), encoding='utf-8') as handle:
                    tree = ast.parse(handle.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        modules.update(alias.name.split('.')[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                        modules.add(node.module.split('.')[0])
        return modules

    @staticmethod
    def _stdlib_module_names():
        # sys.stdlib_module_names is 3.10+, and setup.py still advertises 3.9.
        names = getattr(sys, 'stdlib_module_names', None)
        if names is not None:
            return set(names)

        names = set(sys.builtin_module_names)
        paths = sysconfig.get_paths()
        directories = [paths.get('stdlib'), paths.get('platstdlib')]
        directories = [d for d in directories if d]
        # Extension modules live outside the stdlib root: DLLs on Windows, lib-dynload elsewhere.
        directories += [os.path.join(d, 'lib-dynload') for d in list(directories)]
        # base_prefix differs from prefix inside a virtualenv, which is how CI runs.
        directories += [os.path.join(p, 'DLLs') for p in {sys.prefix, sys.base_prefix}]

        for directory in directories:
            if not os.path.isdir(directory):
                continue
            for entry in os.listdir(directory):
                if entry.startswith('.'):
                    continue
                if entry.endswith(('.py', '.pyd', '.so')):
                    names.add(entry.split('.')[0])
                elif os.path.isfile(os.path.join(directory, entry, '__init__.py')):
                    names.add(entry)
        return names

    def _third_party_imports(self):
        modules = self._imported_modules()
        stdlib = self._stdlib_module_names()
        return {
            module for module in modules
            if module not in stdlib
            and module not in self.CLI_PROVIDED
            and module != 'azext_vm_repair'
        }

    def test_every_third_party_import_is_declared(self):
        declared = self._declared_distributions()
        declared_modules = {self.DIST_TO_MODULE.get(dist, dist) for dist in declared}
        undeclared = sorted(self._third_party_imports() - declared_modules)
        self.assertEqual(
            undeclared, [],
            'Shipped code imports packages that setup.py does not declare: {}. They resolve '
            'only while the Azure CLI happens to ship them.'.format(', '.join(undeclared))
        )

    def test_no_declared_dependency_is_unused(self):
        imported = self._third_party_imports()
        unused = sorted(
            dist for dist in self._declared_distributions()
            if self.DIST_TO_MODULE.get(dist, dist) not in imported
        )
        self.assertEqual(
            unused, [],
            'setup.py declares dependencies that no shipped module imports: {}. Because '
            'extensions install with pip --target, each one vendors its full transitive '
            'tree into the extension folder.'.format(', '.join(unused))
        )


if __name__ == '__main__':
    unittest.main()
