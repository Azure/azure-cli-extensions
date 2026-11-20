# Unit Tests

## Run all unit-tests on different versions of Python

Execute the following command from the root directory of this repository:

#### Linux/macOS

```bash
export TOX_ENV=py36
export TOX_ENV=py37
export TOX_ENV=py38

./scripts/ci/unit-tests/pipeline-linux.sh
```

#### Windows

```bash
setx TOX_ENV="py36"
setx TOX_ENV="py37"
setx TOX_ENV="py38"

.\scripts\ci\unit-tests\pipeline-windows.cmd
```
