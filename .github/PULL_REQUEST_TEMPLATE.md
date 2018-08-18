---

This checklist is used to make sure that common guidelines for a pull request are followed.

### General Guidelines

- [ ] Have you run `./scripts/ci/test_static.sh` locally? (`pip install pylint flake8` required)
- [ ] Have you run `python scripts/ci/test_index.py -q` locally?

For new extensions:

- [ ] My extension description/summary conforms to the [Extension Summary Guidelines](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/extension_summary_guidelines.md).
