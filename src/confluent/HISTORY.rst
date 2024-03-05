.. :changelog:

Release History
===============
0.6.0
+++++
* Added more commands for user access management
* `az confluent organization environment list --organization-name upntestorg01 --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test` : List of environments in the organization
* `az confluent organization environment cluster list --organization-name upntestorg01 --environment-id env-stgc25p5xq --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test` : List of clusters in the environment 
* `az confluent organization environment schema-registry-cluster list --organization-name upntestorg01 --environment-id env-stgcjzd58q --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test` : List of schema-registry-cluster in the environment 
* `az confluent organization environment cluster create-api-key --organization-name upntestorg01 --environment-id env-stgc25p5xq --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test --cluster-id lsrc-stgcp6kvzk --description cmd-line-apikey-test --name api-key-cmd-0403` : Creates API key in the given cluster
* `az confluent organization api-key delete --api-key-id PQGS27PBBW4LNBRT --organization-name upntestorg01 --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test` : Deletes api key of a cluster
* `az confluent organization create-role-binding --organization-name upntestorg01 --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test --principal User:u-vw7yzn --role-name FlinkAdmin --crn-pattern  /environment=env-jv3wv8` : Creates role binding for a user under a resource (environment, organization, cluster as specified in the crn pattern)
* `az confluent organization role-binding delete --organization-name upntestorg01 --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test --role-binding-id rb-0ePzyz`: Deletes confluent role for the user
* `az confluent organization list-role-binding --organization-name upntestorg01 --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test --search-filters {CRNPattern:/environment=env-jv3wv8}` : List the rolebindings based on the filter params ( filtering can be done at confluent resource level & principal)
* `az confluent organization list-service-accounts --organization-name upntestorg01 --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test` : List of service accounts in the organization
* `az confluent organization list-users --organization-name upntestorg01 --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test --search-filters {pageSize:100}` : List of users in the organization
* `az confluent organization create-user --organization-name upntestorg01 --subscription ff9490e3-e714-4d26-b33b-4deefb0d5ffa --resource-group  deepika-test --invited-email ajaykumar@microsoft.com --auth-type AUTH_TYPE_SSO`: Create a user in the confluent organization

0.5.0
+++++
* Change to GA from experiment

0.4.0
+++++
* `az confluent terms`: Deprecate this command group.

0.3.0
+++++
* `az confluent offer-detail show`: Remove the properties `isRIRequired` and `msrp` from the output.
* `az confluent organization create`: Fix the issue that organization cannot be created with owner/contributor role through a SG assignment.

0.2.0
+++++
* [BREAKING CHANGE] `az confluent organization create`: Remove `--user-detail`, the parameter is now auto-filled by the email address, first name and last name decoded from access token. 
* [BREAKING CHANGE] `az confluent organization create`: Flatten `--offer-detail` to `--offer-id`, `--plan-id`, `--plan-name`, `--publisher-id` and `--term-unit`.
* Add new command `az confluent offer-detail show`.
* `az confluent organization create`: Add Owner or Contributor access check of the subscription before creating the organization.
* `az confluent organization delete`: Customize confirmation message based on plan type. 

0.1.0
++++++
* Initial release.
