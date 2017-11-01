---

This checklist is used to make sure that common guidelines for a pull request are followed.

### General Guidelines

- [ ] If you modified extension source code, have you run `./scripts/ci/test_static.sh` locally? (`pip install pylint flake8` required)
- [ ] If you modified the index, have you run `python scripts/ci/test_index.py -q` locally?
