---

This checklist is used to make sure that common guidelines for a pull request are followed.

### Related command
<!--- Please provide the related command with az {command} if you can, so that we can quickly route to the related person to review. --->


### General Guidelines

- [ ] Have you run `azdev style <YOUR_EXT>` locally? (`pip install azdev` required)
- [ ] Have you run `python scripts/ci/test_index.py -q` locally? (`pip install wheel==0.30.0` required)
- [ ] My extension version conforms to the [Extension version schema](https://github.com/Azure/azure-cli/blob/release/doc/extensions/versioning_guidelines.md)

For new extensions:

- [ ] My extension description/summary conforms to the [Extension Summary Guidelines](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/extension_summary_guidelines.md).


### About Extension Publish

There is a pipeline to automatically build, upload and publish extension wheels.  
Once your pull request is merged into main branch, a new pull request will be created to update `src/index.json` automatically.  
You only need to update the version information in file setup.py and historical information in file HISTORY.rst in your PR but do not modify `src/index.json`. 
