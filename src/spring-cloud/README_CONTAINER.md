Added the following arguments:
```
    --container-args               : The arguments of the container image.
    --container-command            : The command of the container image.
    --container-image              : The container image tag.
    --container-registry           : The registry of the container image.  Default: docker.io.
    --registry-password            : The password of the container registry.
    --registry-username            : The username of the container registry.
```

Use `az spring-cloud app deploy`

Deploy a container image on Docker Hub to an app.
```
az spring-cloud app deploy -n MyApp -s MyCluster -g MyResourceGroup --container-image contoso/your-app:v1
```
 
Deploy a container image on a private registry to an app.
```
az spring-cloud app deploy -n MyApp -s MyCluster -g MyResourceGroup --container-image contoso/your-app:v1 --container-registry myacr.azurecr.io --registry-username <username> --registry-password <password>
```

Or `az spring-cloud app deployment create`
 
Deploy a container image on Docker Hub to an app.
```
az spring-cloud app deployment create -n green-deployment --app MyApp -s MyCluster -g MyResourceGroup --container-image contoso/your-app:v1
```

Deploy a container image on a private registry to an app.
```
az spring-cloud app deployment create -n green-deployment --app MyApp -s MyCluster -g MyResourceGroup --container-image contoso/your-app:v1 --container-registry myacr.azurecr.io --registry-username <username> --registry-password <password>
```