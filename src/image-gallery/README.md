# Azure CLI image-gallery Extension #
This package is for the 'image-gallery' extension, i.e. 'az sig'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name image-gallery
```

### Included Features
#### Image Gallery:
Manage Image Gallery: [more info](https://docs.microsoft.com/en-us/azure/virtual-machines/shared-image-galleries) \
*Examples:*

##### Get a gallery that has been community in the given location.
```
az sig show-community --public-gallery-name publicGalleryName \
    --location myLocation
```

##### Get an image definition in a gallery community in the given location.
```
az sig image-definition show-community --public-gallery-name publicGalleryName \
    --gallery-image-definition myGalleryImageName \
    --location myLocation
```

##### List an image definition in a gallery community.
```
az sig image-definition list-community --public-gallery-name publicGalleryName \
    --location myLocation
```

##### Get an image version in a gallery community in the given location.
```
az sig image-version show-community --public-gallery-name publicGalleryName \
    --gallery-image-definition MyImage \
    --gallery-image-version 1.0.0 \
    --location myLocation
```

##### List an VM Image Versions in a gallery community.
```
az sig image-version list-community --public-gallery-name publicGalleryName \
    --gallery-image-definition MyImage \
    --location myLocation
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
