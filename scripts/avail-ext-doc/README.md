# Docker image for automate PRs to https://github.com/azure/azure-docs-cli-python

Automatically create PR to update the document listing the available CLI extensions.

To build locally:

```bash
docker build . -t mcr.microsoft.com/azure-cli-ext/ext-list-publisher:0.3.0
```

To run locally:

```bash
docker run \
    --rm \
    -e TRAVIS_BUILD_ID=$TRAVIS_BUILD_ID \
    -e TRAVIS_REPO_SLUG=$TRAVIS_REPO_SLUG \
    -e TRAVIS_COMMIT=$TRAVIS_COMMIT \
    -e GH_TOKEN=$GH_TOKEN \
    -e DOC_REPO_SLUG=$DOC_REPO_SLUG \
    -e REPO_LOCATION=/repo \
    -v $PWD:/repo \
    mcr.microsoft.com/azure-cli-ext/ext-list-publisher:0.3.0
```

For example:

```bash
docker run \
    --rm \
    -e TRAVIS_BUILD_ID=1234 \
    -e TRAVIS_REPO_SLUG='azure/azure-cli-extensions' \
    -e TRAVIS_COMMIT=abcdef1234 \
    -e GH_TOKEN=$GH_TOKEN \
    -e DOC_REPO_SLUG='azure/azure-docs-cli-python' \
    -e REPO_LOCATION=/repo \
    -v /Repos/azure-cli-extensions:/repo \
    mcr.microsoft.com/azure-cli-ext/ext-list-publisher:0.3.0
```
