---

This checklist is used to make sure that common guidelines for a pull request are followed.

### General Guidelines

- [ ] Have you run `azdev style <YOUR_EXT>` locally? (`pip install azdev` required)
- [ ] Have you run `python scripts/ci/test_index.py -q` locally?

For new extensions:

- [ ] My extension description/summary conforms to the [Extension Summary Guidelines](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/extension_summary_guidelines.md).


### About to Publish

There is a pipeline will help you build, upload and publish (update index.json) extension wheel automatically.  
Once your PR is merged into master branch, a new PR will be created to update src/index.json automatically.  
The precondition is put your code inside this repo and src/index.json must not be modified.  