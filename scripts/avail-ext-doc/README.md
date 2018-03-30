# Docker image for automate PRs to https://github.com/azure/azure-docs-cli-python

Automatically create PR to update the document listing the available CLI extensions.

```bash
docker build . -t derekbekoe/az-avail-ext-doc-sync:0.1.2
```

To run locally:
```bash
docker run --rm -e TRAVIS_BUILD_ID=$TRAVIS_BUILD_ID -e TRAVIS_REPO_SLUG=$TRAVIS_REPO_SLUG -e TRAVIS_COMMIT=$TRAVIS_COMMIT -e GH_TOKEN=$GH_TOKEN -e DOC_REPO_SLUG=$DOC_REPO_SLUG -v $PWD:/repo derekbekoe/az-avail-ext-doc-sync:0.1.2
```

For example:
```bash
docker run --rm -e TRAVIS_BUILD_ID=1234 -e TRAVIS_REPO_SLUG='azure/azure-cli-extensions' -e TRAVIS_COMMIT=1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik9ol0p -e GH_TOKEN=qwertyuiopasdfghjklzxcvbnm1234567890 -e DOC_REPO_SLUG='azure/azure-docs-cli-python' -v /Repos/azure-cli-extensions:/repo derekbekoe/az-avail-ext-doc-sync:0.1.2
```
