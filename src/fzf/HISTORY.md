# Release History

## 0.1.0
* Initial release.

## 0.1.1
* Added better help, fixed dependency info, added better error handling.

## 0.2.0
* Implemented fzf functionality internally instead of using a module
* Initial unit testing
* Implemented install functionality

## 0.9.0
* Completed unit testing
* Completed pylint

## 0.9.1
* Corrected platform call to get architecture properly on Windows.

## 0.9.2
* Cleaned up unit tests
* Added --no-default/-d parameter to allow use in scripts for finding a subscription/group/location without changing the default.
* Added more error handling to group/location
* Used a better function to get_resource_groups()
* Moved tabulate call to its own function so that it's not repeated.

## 1.0.0
* Initial stable release, some linting cleanup.

## 1.0.1
* Update minimum version to 2.9.0 because we depend on a location format change in that version.

## 1.0.2
* Add experimental flag to indicate lack of support from Microsoft, as this is a side project.

## 1.0.3
* Merge into main azure-cli-extensions repository instead of keeping it separate.
* Added additional documentation in _help.py - closes #3296.
