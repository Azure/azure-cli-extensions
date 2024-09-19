# Azure CLI MulticloudConnector Extension #
This is an extension to Azure CLI to manage MulticloudConnector resources.

## How to use ##

### PublicCloudConnector Usage
- Create a PublicCloudConnector
    ```bash
        arc-multicloud public-cloud-connector create --resource-group rgpublicCloud --name advjwoakdusalamomg --aws-cloud-profile "{account-id:snbnuxckevyqpm,excluded-accounts:[rwgqpukglvbqmogqcliqolucp],is-organizational-account:True}" --host-type AWS --tags "{}" --location jpiglusfxynfcewcjwvvnn
    ```

- GenerateAwsTemplate
  ```bash
      arc-multicloud generate-aws-template --connector-id pnxcfjidglabnwxit --solution-types "[{solution-type:hjyownzpfxwiufmd,solution-settings:{}}]"
  ```

- Test allowed permissions of a PublicCloudConnector
    ```bash
        arc-multicloud public-cloud-connector test-permission --resource-group rgpublicCloud --name sjuahmnojgachluzcbhxhwkxwugbsi
    ```

### SolutionConfiguration Usage

- Create a SolutionConfiguration
    ```bash
        arc-multicloud solution-configuration create --connector-id ymuj --name keebwujt --solution-type nmtqllkyohwtsthxaimsye --solution-settings "{}"
    ```