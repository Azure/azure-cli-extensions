SET AZURE_EXTENSION_DIR=c:\Users\takamara\.azure\devcliextensions

C:\Python\Python36-32\python setup.py bdist_wheel
C:\Python\Python36-32\scripts\pip install --upgrade --target C:\Users\takamara\.azure\devcliextensions\imagecopyextension C:\dev\azure-cli-extensions\src\image-copy

rem az image copy --help

az image copy --source-resource-group "test-rg" --source-object-name "vm2" --source-type "vm" --target-location uksouth northeurope --target-resource-group "images-repo"

rem az image copy --source-resource-group "test-img-rg" --source-object-name "vm1-image" --target-location uksouth northeurope --target-resource-group "images-repo" --cleanup

rem az vm-image-copy --source-resource-group "test-img-rg" --source-object-name "vm1-image" --source-type "image" --target-location "uksouth, northeurope, westus, eastus, australiaeast, eastasia" --target-resource-group "images-repo" --cleanup "true"