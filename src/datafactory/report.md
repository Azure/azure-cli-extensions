# Azure CLI Module Creation Report

### datafactory activity-run query-by-pipeline-run

query-by-pipeline-run a datafactory activity-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--run-id**|string|The pipeline run identifier.|run_id|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|
|**--filters**|array|List of filters.|filters|
|**--order-by**|array|List of OrderBy option.|order_by|
### datafactory data-flow create

create a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|
|**--properties**|object|Data flow properties.|properties|
|**--if-match**|string|ETag of the data flow entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory data-flow delete

delete a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|
### datafactory data-flow list

list a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory data-flow show

show a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|
|**--if-none-match**|string|ETag of the data flow entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory data-flow update

create a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|
|**--properties**|object|Data flow properties.|properties|
|**--if-match**|string|ETag of the data flow entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory data-flow-debug-session add-data-flow

add-data-flow a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--session-id**|string|The ID of data flow debug session.|session_id|
|**--datasets**|array|List of datasets.|datasets|
|**--linked-services**|array|List of linked services.|linked_services|
|**--debug-settings-source-settings**|array|Source setting for data flow debug.|source_settings|
|**--debug-settings-parameters**|dictionary|Data flow parameters.|parameters_debug_settings_parameters|
|**--debug-settings-dataset-parameters**|any|Parameters for dataset.|dataset_parameters|
|**--staging-folder-path**|string|Folder path for staging blob.|folder_path|
|**--staging-linked-service-reference-name**|string|Reference LinkedService name.|reference_name|
|**--staging-linked-service-parameters**|dictionary|Arguments for LinkedService.|parameters|
|**--data-flow-name**|string|The resource name.|name|
|**--data-flow-properties**|object|Data flow properties.|properties|
### datafactory data-flow-debug-session create

create a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--compute-type**|string|Compute type of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|compute_type|
|**--core-count**|integer|Core count of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|core_count|
|**--time-to-live**|integer|Time to live setting of the cluster in minutes.|time_to_live|
|**--integration-runtime-name**|string|The resource name.|name|
|**--integration-runtime-properties**|object|Integration runtime properties.|properties|
### datafactory data-flow-debug-session delete

delete a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--session-id**|string|The ID of data flow debug session.|session_id|
### datafactory data-flow-debug-session execute-command

execute-command a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--session-id**|string|The ID of data flow debug session.|session_id|
|**--command**|choice|The command type.|command|
|**--command-payload**|object|The command payload object.|command_payload|
### datafactory data-flow-debug-session query-by-factory

query-by-factory a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory dataset amazon-mws-object create

amazon-mws-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|amazon_mws_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|amazon_mws_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazon_mws_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazon_mws_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazon_mws_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazon_mws_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazon_mws_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|amazon_mws_object_table_name|
### datafactory dataset amazon-mws-object update

amazon-mws-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|amazon_mws_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|amazon_mws_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazon_mws_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazon_mws_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazon_mws_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazon_mws_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazon_mws_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|amazon_mws_object_table_name|
### datafactory dataset amazon-redshift-table create

amazon-redshift-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|amazon_redshift_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|amazon_redshift_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazon_redshift_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazon_redshift_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazon_redshift_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazon_redshift_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazon_redshift_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|amazon_redshift_table_table_name|
|**--type-properties-table**|any|The Amazon Redshift table name. Type: string (or Expression with resultType string).|amazon_redshift_table_table|
|**--type-properties-schema**|any|The Amazon Redshift schema name. Type: string (or Expression with resultType string).|amazon_redshift_table_schema_type_properties_schema|
### datafactory dataset amazon-redshift-table update

amazon-redshift-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|amazon_redshift_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|amazon_redshift_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazon_redshift_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazon_redshift_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazon_redshift_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazon_redshift_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazon_redshift_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|amazon_redshift_table_table_name|
|**--type-properties-table**|any|The Amazon Redshift table name. Type: string (or Expression with resultType string).|amazon_redshift_table_table|
|**--type-properties-schema**|any|The Amazon Redshift schema name. Type: string (or Expression with resultType string).|amazon_redshift_table_schema_type_properties_schema|
### datafactory dataset amazon-s3-object create

amazon-s3-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|amazon_s3_object_linked_service_name|
|**--type-properties-bucket-name**|any|The name of the Amazon S3 bucket. Type: string (or Expression with resultType string).|amazon_s3_object_bucket_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|amazon_s3_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazon_s3_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazon_s3_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazon_s3_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazon_s3_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazon_s3_object_folder|
|**--type-properties-key**|any|The key of the Amazon S3 object. Type: string (or Expression with resultType string).|amazon_s3_object_key|
|**--type-properties-prefix**|any|The prefix filter for the S3 object name. Type: string (or Expression with resultType string).|amazon_s3_object_prefix|
|**--type-properties-version**|any|The version for the S3 object. Type: string (or Expression with resultType string).|amazon_s3_object_version|
|**--type-properties-modified-datetime-start**|any|The start of S3 object's modified datetime. Type: string (or Expression with resultType string).|amazon_s3_object_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of S3 object's modified datetime. Type: string (or Expression with resultType string).|amazon_s3_object_modified_datetime_end|
|**--type-properties-format**|object|The format of files.|amazon_s3_object_format|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset amazon-s3-object update

amazon-s3-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|amazon_s3_object_linked_service_name|
|**--type-properties-bucket-name**|any|The name of the Amazon S3 bucket. Type: string (or Expression with resultType string).|amazon_s3_object_bucket_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|amazon_s3_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazon_s3_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazon_s3_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazon_s3_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazon_s3_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazon_s3_object_folder|
|**--type-properties-key**|any|The key of the Amazon S3 object. Type: string (or Expression with resultType string).|amazon_s3_object_key|
|**--type-properties-prefix**|any|The prefix filter for the S3 object name. Type: string (or Expression with resultType string).|amazon_s3_object_prefix|
|**--type-properties-version**|any|The version for the S3 object. Type: string (or Expression with resultType string).|amazon_s3_object_version|
|**--type-properties-modified-datetime-start**|any|The start of S3 object's modified datetime. Type: string (or Expression with resultType string).|amazon_s3_object_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of S3 object's modified datetime. Type: string (or Expression with resultType string).|amazon_s3_object_modified_datetime_end|
|**--type-properties-format**|object|The format of files.|amazon_s3_object_format|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset avro create

avro create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|avro_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|avro_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|avro_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|avro_schema|
|**--parameters**|dictionary|Parameters for dataset.|avro_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|avro_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|avro_folder|
|**--type-properties-location**|object|The location of the avro storage.|avro_location|
|**--type-properties-avro-compression-codec**|choice||avro_avro_compression_codec|
|**--type-properties-avro-compression-level**|integer||avro_avro_compression_level|
### datafactory dataset avro update

avro create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|avro_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|avro_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|avro_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|avro_schema|
|**--parameters**|dictionary|Parameters for dataset.|avro_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|avro_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|avro_folder|
|**--type-properties-location**|object|The location of the avro storage.|avro_location|
|**--type-properties-avro-compression-codec**|choice||avro_avro_compression_codec|
|**--type-properties-avro-compression-level**|integer||avro_avro_compression_level|
### datafactory dataset azure-blob create

azure-blob create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_blob_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_blob_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_blob_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_blob_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_blob_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_blob_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_blob_folder|
|**--type-properties-folder-path**|any|The path of the Azure Blob storage. Type: string (or Expression with resultType string).|azure_blob_folder_path|
|**--type-properties-table-root-location**|any|The root of blob path. Type: string (or Expression with resultType string).|azure_blob_table_root_location|
|**--type-properties-file-name**|any|The name of the Azure Blob. Type: string (or Expression with resultType string).|azure_blob_file_name|
|**--type-properties-modified-datetime-start**|any|The start of Azure Blob's modified datetime. Type: string (or Expression with resultType string).|azure_blob_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of Azure Blob's modified datetime. Type: string (or Expression with resultType string).|azure_blob_modified_datetime_end|
|**--type-properties-format**|object|The format of the Azure Blob storage.|azure_blob_format|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset azure-blob update

azure-blob create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_blob_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_blob_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_blob_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_blob_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_blob_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_blob_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_blob_folder|
|**--type-properties-folder-path**|any|The path of the Azure Blob storage. Type: string (or Expression with resultType string).|azure_blob_folder_path|
|**--type-properties-table-root-location**|any|The root of blob path. Type: string (or Expression with resultType string).|azure_blob_table_root_location|
|**--type-properties-file-name**|any|The name of the Azure Blob. Type: string (or Expression with resultType string).|azure_blob_file_name|
|**--type-properties-modified-datetime-start**|any|The start of Azure Blob's modified datetime. Type: string (or Expression with resultType string).|azure_blob_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of Azure Blob's modified datetime. Type: string (or Expression with resultType string).|azure_blob_modified_datetime_end|
|**--type-properties-format**|object|The format of the Azure Blob storage.|azure_blob_format|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset azure-blob-fs-file create

azure-blob-fs-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_blob_fs_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_blob_fs_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_blob_fs_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_blob_fs_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_blob_fs_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_blob_fs_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_blob_fs_file_folder|
|**--type-properties-folder-path**|any|The path of the Azure Data Lake Storage Gen2 storage. Type: string (or Expression with resultType string).|azure_blob_fs_file_folder_path|
|**--type-properties-file-name**|any|The name of the Azure Data Lake Storage Gen2. Type: string (or Expression with resultType string).|azure_blob_fs_file_file_name|
|**--type-properties-format**|object|The format of the Azure Data Lake Storage Gen2 storage.|azure_blob_fs_file_format|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset azure-blob-fs-file update

azure-blob-fs-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_blob_fs_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_blob_fs_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_blob_fs_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_blob_fs_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_blob_fs_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_blob_fs_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_blob_fs_file_folder|
|**--type-properties-folder-path**|any|The path of the Azure Data Lake Storage Gen2 storage. Type: string (or Expression with resultType string).|azure_blob_fs_file_folder_path|
|**--type-properties-file-name**|any|The name of the Azure Data Lake Storage Gen2. Type: string (or Expression with resultType string).|azure_blob_fs_file_file_name|
|**--type-properties-format**|object|The format of the Azure Data Lake Storage Gen2 storage.|azure_blob_fs_file_format|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset azure-data-explorer-table create

azure-data-explorer-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_data_explorer_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_data_explorer_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_data_explorer_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_data_explorer_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_data_explorer_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_data_explorer_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_data_explorer_table_folder|
|**--type-properties-table**|any|The table name of the Azure Data Explorer database. Type: string (or Expression with resultType string).|azure_data_explorer_table_table|
### datafactory dataset azure-data-explorer-table update

azure-data-explorer-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_data_explorer_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_data_explorer_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_data_explorer_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_data_explorer_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_data_explorer_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_data_explorer_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_data_explorer_table_folder|
|**--type-properties-table**|any|The table name of the Azure Data Explorer database. Type: string (or Expression with resultType string).|azure_data_explorer_table_table|
### datafactory dataset azure-data-lake-store-file create

azure-data-lake-store-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_data_lake_store_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_data_lake_store_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_data_lake_store_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_data_lake_store_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_data_lake_store_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_data_lake_store_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_data_lake_store_file_folder|
|**--type-properties-folder-path**|any|Path to the folder in the Azure Data Lake Store. Type: string (or Expression with resultType string).|azure_data_lake_store_file_folder_path|
|**--type-properties-file-name**|any|The name of the file in the Azure Data Lake Store. Type: string (or Expression with resultType string).|azure_data_lake_store_file_file_name|
|**--type-properties-format**|object|The format of the Data Lake Store.|azure_data_lake_store_file_format|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset azure-data-lake-store-file update

azure-data-lake-store-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_data_lake_store_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_data_lake_store_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_data_lake_store_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_data_lake_store_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_data_lake_store_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_data_lake_store_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_data_lake_store_file_folder|
|**--type-properties-folder-path**|any|Path to the folder in the Azure Data Lake Store. Type: string (or Expression with resultType string).|azure_data_lake_store_file_folder_path|
|**--type-properties-file-name**|any|The name of the file in the Azure Data Lake Store. Type: string (or Expression with resultType string).|azure_data_lake_store_file_file_name|
|**--type-properties-format**|object|The format of the Data Lake Store.|azure_data_lake_store_file_format|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset azure-maria-d-b-table create

azure-maria-d-b-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_maria_d_b_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_maria_d_b_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_maria_d_b_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_maria_d_b_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_maria_d_b_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_maria_d_b_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_maria_d_b_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|azure_maria_d_b_table_table_name|
### datafactory dataset azure-maria-d-b-table update

azure-maria-d-b-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_maria_d_b_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_maria_d_b_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_maria_d_b_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_maria_d_b_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_maria_d_b_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_maria_d_b_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_maria_d_b_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|azure_maria_d_b_table_table_name|
### datafactory dataset azure-my-sql-table create

azure-my-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_my_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_my_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_my_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_my_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_my_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_my_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_my_sql_table_folder|
|**--type-properties-table-name**|any|The Azure MySQL database table name. Type: string (or Expression with resultType string).|azure_my_sql_table_table_name|
|**--type-properties-table**|any|The name of Azure MySQL database table. Type: string (or Expression with resultType string).|azure_my_sql_table_table|
### datafactory dataset azure-my-sql-table update

azure-my-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_my_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_my_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_my_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_my_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_my_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_my_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_my_sql_table_folder|
|**--type-properties-table-name**|any|The Azure MySQL database table name. Type: string (or Expression with resultType string).|azure_my_sql_table_table_name|
|**--type-properties-table**|any|The name of Azure MySQL database table. Type: string (or Expression with resultType string).|azure_my_sql_table_table|
### datafactory dataset azure-postgre-sql-table create

azure-postgre-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_postgre_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_postgre_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_postgre_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_postgre_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_postgre_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_postgre_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_postgre_sql_table_folder|
|**--type-properties-table-name**|any|The table name of the Azure PostgreSQL database which includes both schema and table. Type: string (or Expression with resultType string).|azure_postgre_sql_table_table_name|
|**--type-properties-table**|any|The table name of the Azure PostgreSQL database. Type: string (or Expression with resultType string).|azure_postgre_sql_table_table|
|**--type-properties-schema**|any|The schema name of the Azure PostgreSQL database. Type: string (or Expression with resultType string).|azure_postgre_sql_table_schema_type_properties_schema|
### datafactory dataset azure-postgre-sql-table update

azure-postgre-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_postgre_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_postgre_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_postgre_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_postgre_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_postgre_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_postgre_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_postgre_sql_table_folder|
|**--type-properties-table-name**|any|The table name of the Azure PostgreSQL database which includes both schema and table. Type: string (or Expression with resultType string).|azure_postgre_sql_table_table_name|
|**--type-properties-table**|any|The table name of the Azure PostgreSQL database. Type: string (or Expression with resultType string).|azure_postgre_sql_table_table|
|**--type-properties-schema**|any|The schema name of the Azure PostgreSQL database. Type: string (or Expression with resultType string).|azure_postgre_sql_table_schema_type_properties_schema|
### datafactory dataset azure-search-index create

azure-search-index create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_search_index_linked_service_name|
|**--type-properties-index-name**|any|The name of the Azure Search Index. Type: string (or Expression with resultType string).|azure_search_index_index_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_search_index_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_search_index_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_search_index_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_search_index_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_search_index_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_search_index_folder|
### datafactory dataset azure-search-index update

azure-search-index create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_search_index_linked_service_name|
|**--type-properties-index-name**|any|The name of the Azure Search Index. Type: string (or Expression with resultType string).|azure_search_index_index_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_search_index_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_search_index_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_search_index_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_search_index_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_search_index_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_search_index_folder|
### datafactory dataset azure-sql-dw-table create

azure-sql-dw-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_sql_dw_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_sql_dw_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_sql_dw_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_sql_dw_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_sql_dw_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_sql_dw_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_sql_dw_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azure_sql_dw_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azure_sql_dw_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azure_sql_dw_table_table|
### datafactory dataset azure-sql-dw-table update

azure-sql-dw-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_sql_dw_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_sql_dw_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_sql_dw_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_sql_dw_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_sql_dw_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_sql_dw_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_sql_dw_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azure_sql_dw_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azure_sql_dw_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azure_sql_dw_table_table|
### datafactory dataset azure-sql-mi-table create

azure-sql-mi-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_sql_mi_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_sql_mi_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_sql_mi_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_sql_mi_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_sql_mi_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_sql_mi_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_sql_mi_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azure_sql_mi_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL Managed Instance. Type: string (or Expression with resultType string).|azure_sql_mi_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL Managed Instance dataset. Type: string (or Expression with resultType string).|azure_sql_mi_table_table|
### datafactory dataset azure-sql-mi-table update

azure-sql-mi-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_sql_mi_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_sql_mi_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_sql_mi_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_sql_mi_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_sql_mi_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_sql_mi_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_sql_mi_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azure_sql_mi_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL Managed Instance. Type: string (or Expression with resultType string).|azure_sql_mi_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL Managed Instance dataset. Type: string (or Expression with resultType string).|azure_sql_mi_table_table|
### datafactory dataset azure-sql-table create

azure-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_sql_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azure_sql_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL database. Type: string (or Expression with resultType string).|azure_sql_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL database. Type: string (or Expression with resultType string).|azure_sql_table_table|
### datafactory dataset azure-sql-table update

azure-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_sql_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azure_sql_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL database. Type: string (or Expression with resultType string).|azure_sql_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL database. Type: string (or Expression with resultType string).|azure_sql_table_table|
### datafactory dataset azure-table create

azure-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_table_linked_service_name|
|**--type-properties-table-name**|any|The table name of the Azure Table storage. Type: string (or Expression with resultType string).|azure_table_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_table_folder|
### datafactory dataset azure-table update

azure-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|azure_table_linked_service_name|
|**--type-properties-table-name**|any|The table name of the Azure Table storage. Type: string (or Expression with resultType string).|azure_table_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|azure_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azure_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azure_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azure_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azure_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azure_table_folder|
### datafactory dataset binary create

binary create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|binary_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|binary_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|binary_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|binary_schema|
|**--parameters**|dictionary|Parameters for dataset.|binary_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|binary_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|binary_folder|
|**--type-properties-location**|object|The location of the Binary storage.|binary_location|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset binary update

binary create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|binary_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|binary_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|binary_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|binary_schema|
|**--parameters**|dictionary|Parameters for dataset.|binary_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|binary_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|binary_folder|
|**--type-properties-location**|object|The location of the Binary storage.|binary_location|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset cassandra-table create

cassandra-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|cassandra_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|cassandra_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|cassandra_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|cassandra_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|cassandra_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|cassandra_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|cassandra_table_folder|
|**--type-properties-table-name**|any|The table name of the Cassandra database. Type: string (or Expression with resultType string).|cassandra_table_table_name|
|**--type-properties-keyspace**|any|The keyspace of the Cassandra database. Type: string (or Expression with resultType string).|cassandra_table_keyspace|
### datafactory dataset cassandra-table update

cassandra-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|cassandra_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|cassandra_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|cassandra_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|cassandra_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|cassandra_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|cassandra_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|cassandra_table_folder|
|**--type-properties-table-name**|any|The table name of the Cassandra database. Type: string (or Expression with resultType string).|cassandra_table_table_name|
|**--type-properties-keyspace**|any|The keyspace of the Cassandra database. Type: string (or Expression with resultType string).|cassandra_table_keyspace|
### datafactory dataset common-data-service-for-apps-entity create

common-data-service-for-apps-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|common_data_service_for_apps_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|common_data_service_for_apps_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|common_data_service_for_apps_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|common_data_service_for_apps_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|common_data_service_for_apps_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|common_data_service_for_apps_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|common_data_service_for_apps_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|common_data_service_for_apps_entity_entity_name|
### datafactory dataset common-data-service-for-apps-entity update

common-data-service-for-apps-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|common_data_service_for_apps_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|common_data_service_for_apps_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|common_data_service_for_apps_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|common_data_service_for_apps_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|common_data_service_for_apps_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|common_data_service_for_apps_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|common_data_service_for_apps_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|common_data_service_for_apps_entity_entity_name|
### datafactory dataset concur-object create

concur-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|concur_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|concur_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|concur_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|concur_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|concur_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|concur_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|concur_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|concur_object_table_name|
### datafactory dataset concur-object update

concur-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|concur_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|concur_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|concur_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|concur_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|concur_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|concur_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|concur_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|concur_object_table_name|
### datafactory dataset cosmos-d-b-mongo-d-b-api-collection create

cosmos-d-b-mongo-d-b-api-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|cosmos_d_b_mongo_d_b_api_collection_linked_service_name|
|**--type-properties-collection**|any|The collection name of the CosmosDB (MongoDB API) database. Type: string (or Expression with resultType string).|cosmos_d_b_mongo_d_b_api_collection_collection|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|cosmos_d_b_mongo_d_b_api_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|cosmos_d_b_mongo_d_b_api_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|cosmos_d_b_mongo_d_b_api_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|cosmos_d_b_mongo_d_b_api_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|cosmos_d_b_mongo_d_b_api_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|cosmos_d_b_mongo_d_b_api_collection_folder|
### datafactory dataset cosmos-d-b-mongo-d-b-api-collection update

cosmos-d-b-mongo-d-b-api-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|cosmos_d_b_mongo_d_b_api_collection_linked_service_name|
|**--type-properties-collection**|any|The collection name of the CosmosDB (MongoDB API) database. Type: string (or Expression with resultType string).|cosmos_d_b_mongo_d_b_api_collection_collection|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|cosmos_d_b_mongo_d_b_api_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|cosmos_d_b_mongo_d_b_api_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|cosmos_d_b_mongo_d_b_api_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|cosmos_d_b_mongo_d_b_api_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|cosmos_d_b_mongo_d_b_api_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|cosmos_d_b_mongo_d_b_api_collection_folder|
### datafactory dataset cosmos-d-b-sql-api-collection create

cosmos-d-b-sql-api-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--properties**|object|Dataset properties.|properties|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory dataset cosmos-d-b-sql-api-collection update

cosmos-d-b-sql-api-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--properties**|object|Dataset properties.|properties|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory dataset couchbase-table create

couchbase-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|couchbase_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|couchbase_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|couchbase_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|couchbase_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|couchbase_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|couchbase_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|couchbase_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|couchbase_table_table_name|
### datafactory dataset couchbase-table update

couchbase-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|couchbase_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|couchbase_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|couchbase_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|couchbase_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|couchbase_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|couchbase_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|couchbase_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|couchbase_table_table_name|
### datafactory dataset custom-dataset create

custom-dataset create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|custom_dataset_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|custom_dataset_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|custom_dataset_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|custom_dataset_schema|
|**--parameters**|dictionary|Parameters for dataset.|custom_dataset_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|custom_dataset_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|custom_dataset_folder|
|**--type-properties**|any|Custom dataset properties.|custom_dataset_type_properties|
### datafactory dataset custom-dataset update

custom-dataset create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|custom_dataset_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|custom_dataset_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|custom_dataset_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|custom_dataset_schema|
|**--parameters**|dictionary|Parameters for dataset.|custom_dataset_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|custom_dataset_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|custom_dataset_folder|
|**--type-properties**|any|Custom dataset properties.|custom_dataset_type_properties|
### datafactory dataset db2-table create

db2-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|db2_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|db2_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|db2_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|db2_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|db2_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|db2_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|db2_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|db2_table_table_name|
|**--type-properties-schema**|any|The Db2 schema name. Type: string (or Expression with resultType string).|db2_table_schema_type_properties_schema|
|**--type-properties-table**|any|The Db2 table name. Type: string (or Expression with resultType string).|db2_table_table|
### datafactory dataset db2-table update

db2-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|db2_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|db2_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|db2_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|db2_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|db2_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|db2_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|db2_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|db2_table_table_name|
|**--type-properties-schema**|any|The Db2 schema name. Type: string (or Expression with resultType string).|db2_table_schema_type_properties_schema|
|**--type-properties-table**|any|The Db2 table name. Type: string (or Expression with resultType string).|db2_table_table|
### datafactory dataset delete

delete a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
### datafactory dataset delimited-text create

delimited-text create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|delimited_text_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|delimited_text_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|delimited_text_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|delimited_text_schema|
|**--parameters**|dictionary|Parameters for dataset.|delimited_text_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|delimited_text_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|delimited_text_folder|
|**--type-properties-location**|object|The location of the delimited text storage.|delimited_text_location|
|**--type-properties-column-delimiter**|any|The column delimiter. Type: string (or Expression with resultType string).|delimited_text_column_delimiter|
|**--type-properties-row-delimiter**|any|The row delimiter. Type: string (or Expression with resultType string).|delimited_text_row_delimiter|
|**--type-properties-encoding-name**|any|The code page name of the preferred encoding. If miss, the default value is UTF-8, unless BOM denotes another Unicode encoding. Refer to the name column of the table in the following link to set supported values: https://msdn.microsoft.com/library/system.text.encoding.aspx. Type: string (or Expression with resultType string).|delimited_text_encoding_name|
|**--type-properties-compression-codec**|choice||delimited_text_compression_codec|
|**--type-properties-compression-level**|choice|The data compression method used for DelimitedText.|delimited_text_compression_level|
|**--type-properties-quote-char**|any|The quote character. Type: string (or Expression with resultType string).|delimited_text_quote_char|
|**--type-properties-escape-char**|any|The escape character. Type: string (or Expression with resultType string).|delimited_text_escape_char|
|**--type-properties-first-row-as-header**|any|When used as input, treat the first row of data as headers. When used as output,write the headers into the output as the first row of data. The default value is false. Type: boolean (or Expression with resultType boolean).|delimited_text_first_row_as_header|
|**--type-properties-null-value**|any|The null value string. Type: string (or Expression with resultType string).|delimited_text_null_value|
### datafactory dataset delimited-text update

delimited-text create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|delimited_text_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|delimited_text_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|delimited_text_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|delimited_text_schema|
|**--parameters**|dictionary|Parameters for dataset.|delimited_text_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|delimited_text_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|delimited_text_folder|
|**--type-properties-location**|object|The location of the delimited text storage.|delimited_text_location|
|**--type-properties-column-delimiter**|any|The column delimiter. Type: string (or Expression with resultType string).|delimited_text_column_delimiter|
|**--type-properties-row-delimiter**|any|The row delimiter. Type: string (or Expression with resultType string).|delimited_text_row_delimiter|
|**--type-properties-encoding-name**|any|The code page name of the preferred encoding. If miss, the default value is UTF-8, unless BOM denotes another Unicode encoding. Refer to the name column of the table in the following link to set supported values: https://msdn.microsoft.com/library/system.text.encoding.aspx. Type: string (or Expression with resultType string).|delimited_text_encoding_name|
|**--type-properties-compression-codec**|choice||delimited_text_compression_codec|
|**--type-properties-compression-level**|choice|The data compression method used for DelimitedText.|delimited_text_compression_level|
|**--type-properties-quote-char**|any|The quote character. Type: string (or Expression with resultType string).|delimited_text_quote_char|
|**--type-properties-escape-char**|any|The escape character. Type: string (or Expression with resultType string).|delimited_text_escape_char|
|**--type-properties-first-row-as-header**|any|When used as input, treat the first row of data as headers. When used as output,write the headers into the output as the first row of data. The default value is false. Type: boolean (or Expression with resultType boolean).|delimited_text_first_row_as_header|
|**--type-properties-null-value**|any|The null value string. Type: string (or Expression with resultType string).|delimited_text_null_value|
### datafactory dataset document-d-b-collection create

document-d-b-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|document_d_b_collection_linked_service_name|
|**--type-properties-collection-name**|any|Document Database collection name. Type: string (or Expression with resultType string).|document_d_b_collection_collection_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|document_d_b_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|document_d_b_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|document_d_b_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|document_d_b_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|document_d_b_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|document_d_b_collection_folder|
### datafactory dataset document-d-b-collection update

document-d-b-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|document_d_b_collection_linked_service_name|
|**--type-properties-collection-name**|any|Document Database collection name. Type: string (or Expression with resultType string).|document_d_b_collection_collection_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|document_d_b_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|document_d_b_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|document_d_b_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|document_d_b_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|document_d_b_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|document_d_b_collection_folder|
### datafactory dataset drill-table create

drill-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|drill_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|drill_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|drill_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|drill_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|drill_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|drill_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|drill_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|drill_table_table_name|
|**--type-properties-table**|any|The table name of the Drill. Type: string (or Expression with resultType string).|drill_table_table|
|**--type-properties-schema**|any|The schema name of the Drill. Type: string (or Expression with resultType string).|drill_table_schema_type_properties_schema|
### datafactory dataset drill-table update

drill-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|drill_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|drill_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|drill_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|drill_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|drill_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|drill_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|drill_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|drill_table_table_name|
|**--type-properties-table**|any|The table name of the Drill. Type: string (or Expression with resultType string).|drill_table_table|
|**--type-properties-schema**|any|The schema name of the Drill. Type: string (or Expression with resultType string).|drill_table_schema_type_properties_schema|
### datafactory dataset dynamics-ax-resource create

dynamics-ax-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|dynamics_ax_resource_linked_service_name|
|**--type-properties-path**|any|The path of the Dynamics AX OData entity. Type: string (or Expression with resultType string).|dynamics_ax_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|dynamics_ax_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamics_ax_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamics_ax_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamics_ax_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamics_ax_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamics_ax_resource_folder|
### datafactory dataset dynamics-ax-resource update

dynamics-ax-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|dynamics_ax_resource_linked_service_name|
|**--type-properties-path**|any|The path of the Dynamics AX OData entity. Type: string (or Expression with resultType string).|dynamics_ax_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|dynamics_ax_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamics_ax_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamics_ax_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamics_ax_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamics_ax_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamics_ax_resource_folder|
### datafactory dataset dynamics-crm-entity create

dynamics-crm-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|dynamics_crm_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|dynamics_crm_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamics_crm_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamics_crm_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamics_crm_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamics_crm_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamics_crm_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|dynamics_crm_entity_entity_name|
### datafactory dataset dynamics-crm-entity update

dynamics-crm-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|dynamics_crm_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|dynamics_crm_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamics_crm_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamics_crm_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamics_crm_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamics_crm_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamics_crm_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|dynamics_crm_entity_entity_name|
### datafactory dataset dynamics-entity create

dynamics-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|dynamics_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|dynamics_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamics_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamics_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamics_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamics_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamics_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|dynamics_entity_entity_name|
### datafactory dataset dynamics-entity update

dynamics-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|dynamics_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|dynamics_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamics_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamics_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamics_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamics_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamics_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|dynamics_entity_entity_name|
### datafactory dataset eloqua-object create

eloqua-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|eloqua_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|eloqua_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|eloqua_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|eloqua_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|eloqua_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|eloqua_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|eloqua_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|eloqua_object_table_name|
### datafactory dataset eloqua-object update

eloqua-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|eloqua_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|eloqua_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|eloqua_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|eloqua_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|eloqua_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|eloqua_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|eloqua_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|eloqua_object_table_name|
### datafactory dataset file-share create

file-share create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|file_share_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|file_share_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|file_share_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|file_share_schema|
|**--parameters**|dictionary|Parameters for dataset.|file_share_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|file_share_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|file_share_folder|
|**--type-properties-folder-path**|any|The path of the on-premises file system. Type: string (or Expression with resultType string).|file_share_folder_path|
|**--type-properties-file-name**|any|The name of the on-premises file system. Type: string (or Expression with resultType string).|file_share_file_name|
|**--type-properties-modified-datetime-start**|any|The start of file's modified datetime. Type: string (or Expression with resultType string).|file_share_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of file's modified datetime. Type: string (or Expression with resultType string).|file_share_modified_datetime_end|
|**--type-properties-format**|object|The format of the files.|file_share_format|
|**--type-properties-file-filter**|any|Specify a filter to be used to select a subset of files in the folderPath rather than all files. Type: string (or Expression with resultType string).|file_share_file_filter|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset file-share update

file-share create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|file_share_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|file_share_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|file_share_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|file_share_schema|
|**--parameters**|dictionary|Parameters for dataset.|file_share_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|file_share_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|file_share_folder|
|**--type-properties-folder-path**|any|The path of the on-premises file system. Type: string (or Expression with resultType string).|file_share_folder_path|
|**--type-properties-file-name**|any|The name of the on-premises file system. Type: string (or Expression with resultType string).|file_share_file_name|
|**--type-properties-modified-datetime-start**|any|The start of file's modified datetime. Type: string (or Expression with resultType string).|file_share_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of file's modified datetime. Type: string (or Expression with resultType string).|file_share_modified_datetime_end|
|**--type-properties-format**|object|The format of the files.|file_share_format|
|**--type-properties-file-filter**|any|Specify a filter to be used to select a subset of files in the folderPath rather than all files. Type: string (or Expression with resultType string).|file_share_file_filter|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset google-ad-words-object create

google-ad-words-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|google_ad_words_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|google_ad_words_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|google_ad_words_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|google_ad_words_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|google_ad_words_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|google_ad_words_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|google_ad_words_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|google_ad_words_object_table_name|
### datafactory dataset google-ad-words-object update

google-ad-words-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|google_ad_words_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|google_ad_words_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|google_ad_words_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|google_ad_words_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|google_ad_words_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|google_ad_words_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|google_ad_words_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|google_ad_words_object_table_name|
### datafactory dataset google-big-query-object create

google-big-query-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|google_big_query_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|google_big_query_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|google_big_query_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|google_big_query_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|google_big_query_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|google_big_query_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|google_big_query_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using database + table properties instead.|google_big_query_object_table_name|
|**--type-properties-table**|any|The table name of the Google BigQuery. Type: string (or Expression with resultType string).|google_big_query_object_table|
|**--type-properties-dataset**|any|The database name of the Google BigQuery. Type: string (or Expression with resultType string).|google_big_query_object_dataset|
### datafactory dataset google-big-query-object update

google-big-query-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|google_big_query_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|google_big_query_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|google_big_query_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|google_big_query_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|google_big_query_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|google_big_query_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|google_big_query_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using database + table properties instead.|google_big_query_object_table_name|
|**--type-properties-table**|any|The table name of the Google BigQuery. Type: string (or Expression with resultType string).|google_big_query_object_table|
|**--type-properties-dataset**|any|The database name of the Google BigQuery. Type: string (or Expression with resultType string).|google_big_query_object_dataset|
### datafactory dataset greenplum-table create

greenplum-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|greenplum_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|greenplum_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|greenplum_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|greenplum_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|greenplum_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|greenplum_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|greenplum_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|greenplum_table_table_name|
|**--type-properties-table**|any|The table name of Greenplum. Type: string (or Expression with resultType string).|greenplum_table_table|
|**--type-properties-schema**|any|The schema name of Greenplum. Type: string (or Expression with resultType string).|greenplum_table_schema_type_properties_schema|
### datafactory dataset greenplum-table update

greenplum-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|greenplum_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|greenplum_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|greenplum_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|greenplum_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|greenplum_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|greenplum_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|greenplum_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|greenplum_table_table_name|
|**--type-properties-table**|any|The table name of Greenplum. Type: string (or Expression with resultType string).|greenplum_table_table|
|**--type-properties-schema**|any|The schema name of Greenplum. Type: string (or Expression with resultType string).|greenplum_table_schema_type_properties_schema|
### datafactory dataset h-base-object create

h-base-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|h_base_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|h_base_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|h_base_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|h_base_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|h_base_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|h_base_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|h_base_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|h_base_object_table_name|
### datafactory dataset h-base-object update

h-base-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|h_base_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|h_base_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|h_base_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|h_base_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|h_base_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|h_base_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|h_base_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|h_base_object_table_name|
### datafactory dataset hive-object create

hive-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|hive_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|hive_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|hive_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|hive_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|hive_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|hive_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|hive_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|hive_object_table_name|
|**--type-properties-table**|any|The table name of the Hive. Type: string (or Expression with resultType string).|hive_object_table|
|**--type-properties-schema**|any|The schema name of the Hive. Type: string (or Expression with resultType string).|hive_object_schema_type_properties_schema|
### datafactory dataset hive-object update

hive-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|hive_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|hive_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|hive_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|hive_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|hive_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|hive_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|hive_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|hive_object_table_name|
|**--type-properties-table**|any|The table name of the Hive. Type: string (or Expression with resultType string).|hive_object_table|
|**--type-properties-schema**|any|The schema name of the Hive. Type: string (or Expression with resultType string).|hive_object_schema_type_properties_schema|
### datafactory dataset http-file create

http-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|http_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|http_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|http_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|http_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|http_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|http_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|http_file_folder|
|**--type-properties-relative-url**|any|The relative URL based on the URL in the HttpLinkedService refers to an HTTP file Type: string (or Expression with resultType string).|http_file_relative_url|
|**--type-properties-request-method**|any|The HTTP method for the HTTP request. Type: string (or Expression with resultType string).|http_file_request_method|
|**--type-properties-request-body**|any|The body for the HTTP request. Type: string (or Expression with resultType string).|http_file_request_body|
|**--type-properties-additional-headers**|any|The headers for the HTTP Request. e.g. request-header-name-1:request-header-value-1
...
request-header-name-n:request-header-value-n Type: string (or Expression with resultType string).|http_file_additional_headers|
|**--type-properties-format**|object|The format of files.|http_file_format|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset http-file update

http-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|http_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|http_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|http_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|http_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|http_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|http_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|http_file_folder|
|**--type-properties-relative-url**|any|The relative URL based on the URL in the HttpLinkedService refers to an HTTP file Type: string (or Expression with resultType string).|http_file_relative_url|
|**--type-properties-request-method**|any|The HTTP method for the HTTP request. Type: string (or Expression with resultType string).|http_file_request_method|
|**--type-properties-request-body**|any|The body for the HTTP request. Type: string (or Expression with resultType string).|http_file_request_body|
|**--type-properties-additional-headers**|any|The headers for the HTTP Request. e.g. request-header-name-1:request-header-value-1
...
request-header-name-n:request-header-value-n Type: string (or Expression with resultType string).|http_file_additional_headers|
|**--type-properties-format**|object|The format of files.|http_file_format|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset hubspot-object create

hubspot-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|hubspot_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|hubspot_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|hubspot_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|hubspot_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|hubspot_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|hubspot_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|hubspot_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|hubspot_object_table_name|
### datafactory dataset hubspot-object update

hubspot-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|hubspot_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|hubspot_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|hubspot_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|hubspot_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|hubspot_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|hubspot_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|hubspot_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|hubspot_object_table_name|
### datafactory dataset impala-object create

impala-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|impala_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|impala_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|impala_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|impala_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|impala_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|impala_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|impala_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|impala_object_table_name|
|**--type-properties-table**|any|The table name of the Impala. Type: string (or Expression with resultType string).|impala_object_table|
|**--type-properties-schema**|any|The schema name of the Impala. Type: string (or Expression with resultType string).|impala_object_schema_type_properties_schema|
### datafactory dataset impala-object update

impala-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|impala_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|impala_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|impala_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|impala_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|impala_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|impala_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|impala_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|impala_object_table_name|
|**--type-properties-table**|any|The table name of the Impala. Type: string (or Expression with resultType string).|impala_object_table|
|**--type-properties-schema**|any|The schema name of the Impala. Type: string (or Expression with resultType string).|impala_object_schema_type_properties_schema|
### datafactory dataset informix-table create

informix-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|informix_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|informix_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|informix_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|informix_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|informix_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|informix_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|informix_table_folder|
|**--type-properties-table-name**|any|The Informix table name. Type: string (or Expression with resultType string).|informix_table_table_name|
### datafactory dataset informix-table update

informix-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|informix_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|informix_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|informix_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|informix_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|informix_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|informix_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|informix_table_folder|
|**--type-properties-table-name**|any|The Informix table name. Type: string (or Expression with resultType string).|informix_table_table_name|
### datafactory dataset jira-object create

jira-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|jira_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|jira_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|jira_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|jira_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|jira_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|jira_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|jira_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|jira_object_table_name|
### datafactory dataset jira-object update

jira-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|jira_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|jira_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|jira_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|jira_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|jira_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|jira_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|jira_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|jira_object_table_name|
### datafactory dataset json create

json create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|json_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|json_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|json_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|json_schema|
|**--parameters**|dictionary|Parameters for dataset.|json_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|json_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|json_folder|
|**--type-properties-location**|object|The location of the json data storage.|json_location|
|**--type-properties-encoding-name**|any|The code page name of the preferred encoding. If not specified, the default value is UTF-8, unless BOM denotes another Unicode encoding. Refer to the name column of the table in the following link to set supported values: https://msdn.microsoft.com/library/system.text.encoding.aspx. Type: string (or Expression with resultType string).|json_encoding_name|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset json update

json create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|json_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|json_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|json_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|json_schema|
|**--parameters**|dictionary|Parameters for dataset.|json_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|json_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|json_folder|
|**--type-properties-location**|object|The location of the json data storage.|json_location|
|**--type-properties-encoding-name**|any|The code page name of the preferred encoding. If not specified, the default value is UTF-8, unless BOM denotes another Unicode encoding. Refer to the name column of the table in the following link to set supported values: https://msdn.microsoft.com/library/system.text.encoding.aspx. Type: string (or Expression with resultType string).|json_encoding_name|
|**--dataset-b-zip2-compression**|object|The BZip2 compression method used on a dataset.|dataset_b_zip2_compression|
|**--dataset-g-zip-compression**|object|The GZip compression method used on a dataset.|dataset_g_zip_compression|
|**--dataset-deflate-compression**|object|The Deflate compression method used on a dataset.|dataset_deflate_compression|
|**--dataset-zip-deflate-compression**|object|The ZipDeflate compression method used on a dataset.|dataset_zip_deflate_compression|
### datafactory dataset list

list a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory dataset magento-object create

magento-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|magento_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|magento_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|magento_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|magento_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|magento_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|magento_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|magento_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|magento_object_table_name|
### datafactory dataset magento-object update

magento-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|magento_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|magento_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|magento_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|magento_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|magento_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|magento_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|magento_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|magento_object_table_name|
### datafactory dataset maria-d-b-table create

maria-d-b-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|maria_d_b_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|maria_d_b_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|maria_d_b_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|maria_d_b_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|maria_d_b_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|maria_d_b_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|maria_d_b_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|maria_d_b_table_table_name|
### datafactory dataset maria-d-b-table update

maria-d-b-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|maria_d_b_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|maria_d_b_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|maria_d_b_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|maria_d_b_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|maria_d_b_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|maria_d_b_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|maria_d_b_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|maria_d_b_table_table_name|
### datafactory dataset marketo-object create

marketo-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|marketo_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|marketo_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|marketo_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|marketo_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|marketo_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|marketo_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|marketo_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|marketo_object_table_name|
### datafactory dataset marketo-object update

marketo-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|marketo_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|marketo_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|marketo_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|marketo_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|marketo_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|marketo_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|marketo_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|marketo_object_table_name|
### datafactory dataset microsoft-access-table create

microsoft-access-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|microsoft_access_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|microsoft_access_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|microsoft_access_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|microsoft_access_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|microsoft_access_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|microsoft_access_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|microsoft_access_table_folder|
|**--type-properties-table-name**|any|The Microsoft Access table name. Type: string (or Expression with resultType string).|microsoft_access_table_table_name|
### datafactory dataset microsoft-access-table update

microsoft-access-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|microsoft_access_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|microsoft_access_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|microsoft_access_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|microsoft_access_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|microsoft_access_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|microsoft_access_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|microsoft_access_table_folder|
|**--type-properties-table-name**|any|The Microsoft Access table name. Type: string (or Expression with resultType string).|microsoft_access_table_table_name|
### datafactory dataset mongo-d-b-collection create

mongo-d-b-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|mongo_d_b_collection_linked_service_name|
|**--type-properties-collection-name**|any|The table name of the MongoDB database. Type: string (or Expression with resultType string).|mongo_d_b_collection_collection_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|mongo_d_b_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mongo_d_b_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mongo_d_b_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|mongo_d_b_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mongo_d_b_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mongo_d_b_collection_folder|
### datafactory dataset mongo-d-b-collection update

mongo-d-b-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|mongo_d_b_collection_linked_service_name|
|**--type-properties-collection-name**|any|The table name of the MongoDB database. Type: string (or Expression with resultType string).|mongo_d_b_collection_collection_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|mongo_d_b_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mongo_d_b_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mongo_d_b_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|mongo_d_b_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mongo_d_b_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mongo_d_b_collection_folder|
### datafactory dataset mongo-d-b-v2-collection create

mongo-d-b-v2-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|mongo_d_b_v2_collection_linked_service_name|
|**--type-properties-collection**|any|The collection name of the MongoDB database. Type: string (or Expression with resultType string).|mongo_d_b_v2_collection_collection|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|mongo_d_b_v2_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mongo_d_b_v2_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mongo_d_b_v2_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|mongo_d_b_v2_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mongo_d_b_v2_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mongo_d_b_v2_collection_folder|
### datafactory dataset mongo-d-b-v2-collection update

mongo-d-b-v2-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|mongo_d_b_v2_collection_linked_service_name|
|**--type-properties-collection**|any|The collection name of the MongoDB database. Type: string (or Expression with resultType string).|mongo_d_b_v2_collection_collection|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|mongo_d_b_v2_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mongo_d_b_v2_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mongo_d_b_v2_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|mongo_d_b_v2_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mongo_d_b_v2_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mongo_d_b_v2_collection_folder|
### datafactory dataset my-sql-table create

my-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|my_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|my_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|my_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|my_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|my_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|my_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|my_sql_table_folder|
|**--type-properties-table-name**|any|The MySQL table name. Type: string (or Expression with resultType string).|my_sql_table_table_name|
### datafactory dataset my-sql-table update

my-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|my_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|my_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|my_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|my_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|my_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|my_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|my_sql_table_folder|
|**--type-properties-table-name**|any|The MySQL table name. Type: string (or Expression with resultType string).|my_sql_table_table_name|
### datafactory dataset netezza-table create

netezza-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|netezza_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|netezza_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|netezza_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|netezza_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|netezza_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|netezza_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|netezza_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|netezza_table_table_name|
|**--type-properties-table**|any|The table name of the Netezza. Type: string (or Expression with resultType string).|netezza_table_table|
|**--type-properties-schema**|any|The schema name of the Netezza. Type: string (or Expression with resultType string).|netezza_table_schema_type_properties_schema|
### datafactory dataset netezza-table update

netezza-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|netezza_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|netezza_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|netezza_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|netezza_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|netezza_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|netezza_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|netezza_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|netezza_table_table_name|
|**--type-properties-table**|any|The table name of the Netezza. Type: string (or Expression with resultType string).|netezza_table_table|
|**--type-properties-schema**|any|The schema name of the Netezza. Type: string (or Expression with resultType string).|netezza_table_schema_type_properties_schema|
### datafactory dataset o-data-resource create

o-data-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|o_data_resource_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|o_data_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|o_data_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|o_data_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|o_data_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|o_data_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|o_data_resource_folder|
|**--type-properties-path**|any|The OData resource path. Type: string (or Expression with resultType string).|o_data_resource_path|
### datafactory dataset o-data-resource update

o-data-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|o_data_resource_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|o_data_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|o_data_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|o_data_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|o_data_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|o_data_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|o_data_resource_folder|
|**--type-properties-path**|any|The OData resource path. Type: string (or Expression with resultType string).|o_data_resource_path|
### datafactory dataset odbc-table create

odbc-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|odbc_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|odbc_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|odbc_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|odbc_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|odbc_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|odbc_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|odbc_table_folder|
|**--type-properties-table-name**|any|The ODBC table name. Type: string (or Expression with resultType string).|odbc_table_table_name|
### datafactory dataset odbc-table update

odbc-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|odbc_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|odbc_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|odbc_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|odbc_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|odbc_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|odbc_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|odbc_table_folder|
|**--type-properties-table-name**|any|The ODBC table name. Type: string (or Expression with resultType string).|odbc_table_table_name|
### datafactory dataset office365-table create

office365-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|office365_table_linked_service_name|
|**--type-properties-table-name**|any|Name of the dataset to extract from Office 365. Type: string (or Expression with resultType string).|office365_table_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|office365_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|office365_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|office365_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|office365_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|office365_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|office365_table_folder|
|**--type-properties-predicate**|any|A predicate expression that can be used to filter the specific rows to extract from Office 365. Type: string (or Expression with resultType string).|office365_table_predicate|
### datafactory dataset office365-table update

office365-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|office365_table_linked_service_name|
|**--type-properties-table-name**|any|Name of the dataset to extract from Office 365. Type: string (or Expression with resultType string).|office365_table_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|office365_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|office365_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|office365_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|office365_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|office365_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|office365_table_folder|
|**--type-properties-predicate**|any|A predicate expression that can be used to filter the specific rows to extract from Office 365. Type: string (or Expression with resultType string).|office365_table_predicate|
### datafactory dataset oracle-service-cloud-object create

oracle-service-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|oracle_service_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|oracle_service_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|oracle_service_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|oracle_service_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|oracle_service_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|oracle_service_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|oracle_service_cloud_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|oracle_service_cloud_object_table_name|
### datafactory dataset oracle-service-cloud-object update

oracle-service-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|oracle_service_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|oracle_service_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|oracle_service_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|oracle_service_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|oracle_service_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|oracle_service_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|oracle_service_cloud_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|oracle_service_cloud_object_table_name|
### datafactory dataset oracle-table create

oracle-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|oracle_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|oracle_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|oracle_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|oracle_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|oracle_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|oracle_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|oracle_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|oracle_table_table_name|
|**--type-properties-schema**|any|The schema name of the on-premises Oracle database. Type: string (or Expression with resultType string).|oracle_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the on-premises Oracle database. Type: string (or Expression with resultType string).|oracle_table_table|
### datafactory dataset oracle-table update

oracle-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|oracle_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|oracle_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|oracle_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|oracle_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|oracle_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|oracle_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|oracle_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|oracle_table_table_name|
|**--type-properties-schema**|any|The schema name of the on-premises Oracle database. Type: string (or Expression with resultType string).|oracle_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the on-premises Oracle database. Type: string (or Expression with resultType string).|oracle_table_table|
### datafactory dataset orc create

orc create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|orc_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|orc_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|orc_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|orc_schema|
|**--parameters**|dictionary|Parameters for dataset.|orc_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|orc_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|orc_folder|
|**--type-properties-location**|object|The location of the ORC data storage.|orc_location|
|**--type-properties-orc-compression-codec**|choice||orc_orc_compression_codec|
### datafactory dataset orc update

orc create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|orc_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|orc_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|orc_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|orc_schema|
|**--parameters**|dictionary|Parameters for dataset.|orc_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|orc_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|orc_folder|
|**--type-properties-location**|object|The location of the ORC data storage.|orc_location|
|**--type-properties-orc-compression-codec**|choice||orc_orc_compression_codec|
### datafactory dataset parquet create

parquet create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|parquet_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|parquet_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|parquet_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|parquet_schema|
|**--parameters**|dictionary|Parameters for dataset.|parquet_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|parquet_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|parquet_folder|
|**--type-properties-location**|object|The location of the parquet storage.|parquet_location|
|**--type-properties-compression-codec**|choice||parquet_compression_codec|
### datafactory dataset parquet update

parquet create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|parquet_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|parquet_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|parquet_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|parquet_schema|
|**--parameters**|dictionary|Parameters for dataset.|parquet_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|parquet_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|parquet_folder|
|**--type-properties-location**|object|The location of the parquet storage.|parquet_location|
|**--type-properties-compression-codec**|choice||parquet_compression_codec|
### datafactory dataset paypal-object create

paypal-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|paypal_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|paypal_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|paypal_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|paypal_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|paypal_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|paypal_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|paypal_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|paypal_object_table_name|
### datafactory dataset paypal-object update

paypal-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|paypal_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|paypal_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|paypal_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|paypal_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|paypal_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|paypal_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|paypal_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|paypal_object_table_name|
### datafactory dataset phoenix-object create

phoenix-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|phoenix_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|phoenix_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|phoenix_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|phoenix_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|phoenix_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|phoenix_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|phoenix_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|phoenix_object_table_name|
|**--type-properties-table**|any|The table name of the Phoenix. Type: string (or Expression with resultType string).|phoenix_object_table|
|**--type-properties-schema**|any|The schema name of the Phoenix. Type: string (or Expression with resultType string).|phoenix_object_schema_type_properties_schema|
### datafactory dataset phoenix-object update

phoenix-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|phoenix_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|phoenix_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|phoenix_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|phoenix_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|phoenix_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|phoenix_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|phoenix_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|phoenix_object_table_name|
|**--type-properties-table**|any|The table name of the Phoenix. Type: string (or Expression with resultType string).|phoenix_object_table|
|**--type-properties-schema**|any|The schema name of the Phoenix. Type: string (or Expression with resultType string).|phoenix_object_schema_type_properties_schema|
### datafactory dataset postgre-sql-table create

postgre-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|postgre_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|postgre_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|postgre_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|postgre_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|postgre_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|postgre_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|postgre_sql_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|postgre_sql_table_table_name|
|**--type-properties-table**|any|The PostgreSQL table name. Type: string (or Expression with resultType string).|postgre_sql_table_table|
|**--type-properties-schema**|any|The PostgreSQL schema name. Type: string (or Expression with resultType string).|postgre_sql_table_schema_type_properties_schema|
### datafactory dataset postgre-sql-table update

postgre-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|postgre_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|postgre_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|postgre_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|postgre_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|postgre_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|postgre_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|postgre_sql_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|postgre_sql_table_table_name|
|**--type-properties-table**|any|The PostgreSQL table name. Type: string (or Expression with resultType string).|postgre_sql_table_table|
|**--type-properties-schema**|any|The PostgreSQL schema name. Type: string (or Expression with resultType string).|postgre_sql_table_schema_type_properties_schema|
### datafactory dataset presto-object create

presto-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|presto_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|presto_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|presto_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|presto_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|presto_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|presto_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|presto_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|presto_object_table_name|
|**--type-properties-table**|any|The table name of the Presto. Type: string (or Expression with resultType string).|presto_object_table|
|**--type-properties-schema**|any|The schema name of the Presto. Type: string (or Expression with resultType string).|presto_object_schema_type_properties_schema|
### datafactory dataset presto-object update

presto-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|presto_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|presto_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|presto_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|presto_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|presto_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|presto_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|presto_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|presto_object_table_name|
|**--type-properties-table**|any|The table name of the Presto. Type: string (or Expression with resultType string).|presto_object_table|
|**--type-properties-schema**|any|The schema name of the Presto. Type: string (or Expression with resultType string).|presto_object_schema_type_properties_schema|
### datafactory dataset quick-books-object create

quick-books-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|quick_books_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|quick_books_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|quick_books_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|quick_books_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|quick_books_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|quick_books_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|quick_books_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|quick_books_object_table_name|
### datafactory dataset quick-books-object update

quick-books-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|quick_books_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|quick_books_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|quick_books_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|quick_books_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|quick_books_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|quick_books_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|quick_books_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|quick_books_object_table_name|
### datafactory dataset relational-table create

relational-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|relational_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|relational_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|relational_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|relational_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|relational_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|relational_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|relational_table_folder|
|**--type-properties-table-name**|any|The relational table name. Type: string (or Expression with resultType string).|relational_table_table_name|
### datafactory dataset relational-table update

relational-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|relational_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|relational_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|relational_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|relational_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|relational_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|relational_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|relational_table_folder|
|**--type-properties-table-name**|any|The relational table name. Type: string (or Expression with resultType string).|relational_table_table_name|
### datafactory dataset responsys-object create

responsys-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|responsys_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|responsys_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|responsys_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|responsys_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|responsys_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|responsys_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|responsys_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|responsys_object_table_name|
### datafactory dataset responsys-object update

responsys-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|responsys_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|responsys_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|responsys_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|responsys_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|responsys_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|responsys_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|responsys_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|responsys_object_table_name|
### datafactory dataset rest-resource create

rest-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|rest_resource_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|rest_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|rest_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|rest_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|rest_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|rest_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|rest_resource_folder|
|**--type-properties-relative-url**|any|The relative URL to the resource that the RESTful API provides. Type: string (or Expression with resultType string).|rest_resource_relative_url|
|**--type-properties-request-method**|any|The HTTP method used to call the RESTful API. The default is GET. Type: string (or Expression with resultType string).|rest_resource_request_method|
|**--type-properties-request-body**|any|The HTTP request body to the RESTful API if requestMethod is POST. Type: string (or Expression with resultType string).|rest_resource_request_body|
|**--type-properties-additional-headers**|any|The additional HTTP headers in the request to the RESTful API. Type: string (or Expression with resultType string).|rest_resource_additional_headers|
|**--type-properties-pagination-rules**|any|The pagination rules to compose next page requests. Type: string (or Expression with resultType string).|rest_resource_pagination_rules|
### datafactory dataset rest-resource update

rest-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|rest_resource_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|rest_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|rest_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|rest_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|rest_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|rest_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|rest_resource_folder|
|**--type-properties-relative-url**|any|The relative URL to the resource that the RESTful API provides. Type: string (or Expression with resultType string).|rest_resource_relative_url|
|**--type-properties-request-method**|any|The HTTP method used to call the RESTful API. The default is GET. Type: string (or Expression with resultType string).|rest_resource_request_method|
|**--type-properties-request-body**|any|The HTTP request body to the RESTful API if requestMethod is POST. Type: string (or Expression with resultType string).|rest_resource_request_body|
|**--type-properties-additional-headers**|any|The additional HTTP headers in the request to the RESTful API. Type: string (or Expression with resultType string).|rest_resource_additional_headers|
|**--type-properties-pagination-rules**|any|The pagination rules to compose next page requests. Type: string (or Expression with resultType string).|rest_resource_pagination_rules|
### datafactory dataset salesforce-marketing-cloud-object create

salesforce-marketing-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|salesforce_marketing_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|salesforce_marketing_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforce_marketing_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforce_marketing_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforce_marketing_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforce_marketing_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforce_marketing_cloud_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|salesforce_marketing_cloud_object_table_name|
### datafactory dataset salesforce-marketing-cloud-object update

salesforce-marketing-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|salesforce_marketing_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|salesforce_marketing_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforce_marketing_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforce_marketing_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforce_marketing_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforce_marketing_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforce_marketing_cloud_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|salesforce_marketing_cloud_object_table_name|
### datafactory dataset salesforce-object create

salesforce-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|salesforce_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|salesforce_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforce_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforce_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforce_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforce_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforce_object_folder|
|**--type-properties-object-api-name**|any|The Salesforce object API name. Type: string (or Expression with resultType string).|salesforce_object_object_api_name|
### datafactory dataset salesforce-object update

salesforce-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|salesforce_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|salesforce_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforce_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforce_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforce_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforce_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforce_object_folder|
|**--type-properties-object-api-name**|any|The Salesforce object API name. Type: string (or Expression with resultType string).|salesforce_object_object_api_name|
### datafactory dataset salesforce-service-cloud-object create

salesforce-service-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|salesforce_service_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|salesforce_service_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforce_service_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforce_service_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforce_service_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforce_service_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforce_service_cloud_object_folder|
|**--type-properties-object-api-name**|any|The Salesforce Service Cloud object API name. Type: string (or Expression with resultType string).|salesforce_service_cloud_object_object_api_name|
### datafactory dataset salesforce-service-cloud-object update

salesforce-service-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|salesforce_service_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|salesforce_service_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforce_service_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforce_service_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforce_service_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforce_service_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforce_service_cloud_object_folder|
|**--type-properties-object-api-name**|any|The Salesforce Service Cloud object API name. Type: string (or Expression with resultType string).|salesforce_service_cloud_object_object_api_name|
### datafactory dataset sap-bw-cube create

sap-bw-cube create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_bw_cube_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_bw_cube_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_bw_cube_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_bw_cube_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_bw_cube_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_bw_cube_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_bw_cube_folder|
### datafactory dataset sap-bw-cube update

sap-bw-cube create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_bw_cube_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_bw_cube_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_bw_cube_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_bw_cube_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_bw_cube_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_bw_cube_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_bw_cube_folder|
### datafactory dataset sap-cloud-for-customer-resource create

sap-cloud-for-customer-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_cloud_for_customer_resource_linked_service_name|
|**--type-properties-path**|any|The path of the SAP Cloud for Customer OData entity. Type: string (or Expression with resultType string).|sap_cloud_for_customer_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_cloud_for_customer_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_cloud_for_customer_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_cloud_for_customer_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_cloud_for_customer_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_cloud_for_customer_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_cloud_for_customer_resource_folder|
### datafactory dataset sap-cloud-for-customer-resource update

sap-cloud-for-customer-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_cloud_for_customer_resource_linked_service_name|
|**--type-properties-path**|any|The path of the SAP Cloud for Customer OData entity. Type: string (or Expression with resultType string).|sap_cloud_for_customer_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_cloud_for_customer_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_cloud_for_customer_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_cloud_for_customer_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_cloud_for_customer_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_cloud_for_customer_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_cloud_for_customer_resource_folder|
### datafactory dataset sap-ecc-resource create

sap-ecc-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_ecc_resource_linked_service_name|
|**--type-properties-path**|any|The path of the SAP ECC OData entity. Type: string (or Expression with resultType string).|sap_ecc_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_ecc_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_ecc_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_ecc_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_ecc_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_ecc_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_ecc_resource_folder|
### datafactory dataset sap-ecc-resource update

sap-ecc-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_ecc_resource_linked_service_name|
|**--type-properties-path**|any|The path of the SAP ECC OData entity. Type: string (or Expression with resultType string).|sap_ecc_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_ecc_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_ecc_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_ecc_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_ecc_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_ecc_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_ecc_resource_folder|
### datafactory dataset sap-hana-table create

sap-hana-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_hana_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_hana_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_hana_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_hana_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_hana_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_hana_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_hana_table_folder|
|**--type-properties-schema**|any|The schema name of SAP HANA. Type: string (or Expression with resultType string).|sap_hana_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of SAP HANA. Type: string (or Expression with resultType string).|sap_hana_table_table|
### datafactory dataset sap-hana-table update

sap-hana-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_hana_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_hana_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_hana_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_hana_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_hana_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_hana_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_hana_table_folder|
|**--type-properties-schema**|any|The schema name of SAP HANA. Type: string (or Expression with resultType string).|sap_hana_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of SAP HANA. Type: string (or Expression with resultType string).|sap_hana_table_table|
### datafactory dataset sap-open-hub-table create

sap-open-hub-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_open_hub_table_linked_service_name|
|**--type-properties-open-hub-destination-name**|any|The name of the Open Hub Destination with destination type as Database Table. Type: string (or Expression with resultType string).|sap_open_hub_table_open_hub_destination_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_open_hub_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_open_hub_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_open_hub_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_open_hub_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_open_hub_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_open_hub_table_folder|
|**--type-properties-exclude-last-request**|any|Whether to exclude the records of the last request. The default value is true. Type: boolean (or Expression with resultType boolean).|sap_open_hub_table_exclude_last_request|
|**--type-properties-base-request-id**|any|The ID of request for delta loading. Once it is set, only data with requestId larger than the value of this property will be retrieved. The default value is 0. Type: integer (or Expression with resultType integer ).|sap_open_hub_table_base_request_id|
### datafactory dataset sap-open-hub-table update

sap-open-hub-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_open_hub_table_linked_service_name|
|**--type-properties-open-hub-destination-name**|any|The name of the Open Hub Destination with destination type as Database Table. Type: string (or Expression with resultType string).|sap_open_hub_table_open_hub_destination_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_open_hub_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_open_hub_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_open_hub_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_open_hub_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_open_hub_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_open_hub_table_folder|
|**--type-properties-exclude-last-request**|any|Whether to exclude the records of the last request. The default value is true. Type: boolean (or Expression with resultType boolean).|sap_open_hub_table_exclude_last_request|
|**--type-properties-base-request-id**|any|The ID of request for delta loading. Once it is set, only data with requestId larger than the value of this property will be retrieved. The default value is 0. Type: integer (or Expression with resultType integer ).|sap_open_hub_table_base_request_id|
### datafactory dataset sap-table-resource create

sap-table-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_table_resource_linked_service_name|
|**--type-properties-table-name**|any|The name of the SAP Table. Type: string (or Expression with resultType string).|sap_table_resource_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_table_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_table_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_table_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_table_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_table_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_table_resource_folder|
### datafactory dataset sap-table-resource update

sap-table-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sap_table_resource_linked_service_name|
|**--type-properties-table-name**|any|The name of the SAP Table. Type: string (or Expression with resultType string).|sap_table_resource_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sap_table_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sap_table_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sap_table_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|sap_table_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sap_table_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sap_table_resource_folder|
### datafactory dataset service-now-object create

service-now-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|service_now_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|service_now_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|service_now_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|service_now_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|service_now_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|service_now_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|service_now_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|service_now_object_table_name|
### datafactory dataset service-now-object update

service-now-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|service_now_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|service_now_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|service_now_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|service_now_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|service_now_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|service_now_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|service_now_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|service_now_object_table_name|
### datafactory dataset shopify-object create

shopify-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|shopify_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|shopify_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|shopify_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|shopify_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|shopify_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|shopify_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|shopify_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|shopify_object_table_name|
### datafactory dataset shopify-object update

shopify-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|shopify_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|shopify_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|shopify_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|shopify_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|shopify_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|shopify_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|shopify_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|shopify_object_table_name|
### datafactory dataset show

show a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--if-none-match**|string|ETag of the dataset entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory dataset snowflake-table create

snowflake-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|snowflake_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|snowflake_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|snowflake_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|snowflake_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|snowflake_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|snowflake_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|snowflake_table_folder|
|**--type-properties-schema**|any|The schema name of the Snowflake database. Type: string (or Expression with resultType string).|snowflake_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Snowflake database. Type: string (or Expression with resultType string).|snowflake_table_table|
### datafactory dataset snowflake-table update

snowflake-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|snowflake_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|snowflake_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|snowflake_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|snowflake_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|snowflake_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|snowflake_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|snowflake_table_folder|
|**--type-properties-schema**|any|The schema name of the Snowflake database. Type: string (or Expression with resultType string).|snowflake_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Snowflake database. Type: string (or Expression with resultType string).|snowflake_table_table|
### datafactory dataset spark-object create

spark-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|spark_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|spark_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|spark_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|spark_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|spark_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|spark_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|spark_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|spark_object_table_name|
|**--type-properties-table**|any|The table name of the Spark. Type: string (or Expression with resultType string).|spark_object_table|
|**--type-properties-schema**|any|The schema name of the Spark. Type: string (or Expression with resultType string).|spark_object_schema_type_properties_schema|
### datafactory dataset spark-object update

spark-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|spark_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|spark_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|spark_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|spark_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|spark_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|spark_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|spark_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|spark_object_table_name|
|**--type-properties-table**|any|The table name of the Spark. Type: string (or Expression with resultType string).|spark_object_table|
|**--type-properties-schema**|any|The schema name of the Spark. Type: string (or Expression with resultType string).|spark_object_schema_type_properties_schema|
### datafactory dataset sql-server-table create

sql-server-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sql_server_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sql_server_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sql_server_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sql_server_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sql_server_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sql_server_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sql_server_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|sql_server_table_table_name|
|**--type-properties-schema**|any|The schema name of the SQL Server dataset. Type: string (or Expression with resultType string).|sql_server_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the SQL Server dataset. Type: string (or Expression with resultType string).|sql_server_table_table|
### datafactory dataset sql-server-table update

sql-server-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sql_server_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sql_server_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sql_server_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sql_server_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sql_server_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sql_server_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sql_server_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|sql_server_table_table_name|
|**--type-properties-schema**|any|The schema name of the SQL Server dataset. Type: string (or Expression with resultType string).|sql_server_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the SQL Server dataset. Type: string (or Expression with resultType string).|sql_server_table_table|
### datafactory dataset square-object create

square-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|square_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|square_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|square_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|square_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|square_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|square_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|square_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|square_object_table_name|
### datafactory dataset square-object update

square-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|square_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|square_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|square_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|square_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|square_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|square_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|square_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|square_object_table_name|
### datafactory dataset sybase-table create

sybase-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sybase_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sybase_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sybase_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sybase_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sybase_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sybase_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sybase_table_folder|
|**--type-properties-table-name**|any|The Sybase table name. Type: string (or Expression with resultType string).|sybase_table_table_name|
### datafactory dataset sybase-table update

sybase-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|sybase_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|sybase_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sybase_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sybase_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sybase_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sybase_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sybase_table_folder|
|**--type-properties-table-name**|any|The Sybase table name. Type: string (or Expression with resultType string).|sybase_table_table_name|
### datafactory dataset teradata-table create

teradata-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|teradata_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|teradata_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|teradata_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|teradata_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|teradata_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|teradata_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|teradata_table_folder|
|**--type-properties-database**|any|The database name of Teradata. Type: string (or Expression with resultType string).|teradata_table_database|
|**--type-properties-table**|any|The table name of Teradata. Type: string (or Expression with resultType string).|teradata_table_table|
### datafactory dataset teradata-table update

teradata-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|teradata_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|teradata_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|teradata_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|teradata_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|teradata_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|teradata_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|teradata_table_folder|
|**--type-properties-database**|any|The database name of Teradata. Type: string (or Expression with resultType string).|teradata_table_database|
|**--type-properties-table**|any|The table name of Teradata. Type: string (or Expression with resultType string).|teradata_table_table|
### datafactory dataset vertica-table create

vertica-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|vertica_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|vertica_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|vertica_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|vertica_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|vertica_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|vertica_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|vertica_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|vertica_table_table_name|
|**--type-properties-table**|any|The table name of the Vertica. Type: string (or Expression with resultType string).|vertica_table_table|
|**--type-properties-schema**|any|The schema name of the Vertica. Type: string (or Expression with resultType string).|vertica_table_schema_type_properties_schema|
### datafactory dataset vertica-table update

vertica-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|vertica_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|vertica_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|vertica_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|vertica_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|vertica_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|vertica_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|vertica_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|vertica_table_table_name|
|**--type-properties-table**|any|The table name of the Vertica. Type: string (or Expression with resultType string).|vertica_table_table|
|**--type-properties-schema**|any|The schema name of the Vertica. Type: string (or Expression with resultType string).|vertica_table_schema_type_properties_schema|
### datafactory dataset web-table create

web-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|web_table_linked_service_name|
|**--type-properties-index**|any|The zero-based index of the table in the web page. Type: integer (or Expression with resultType integer), minimum: 0.|web_table_index|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|web_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|web_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|web_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|web_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|web_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|web_table_folder|
|**--type-properties-path**|any|The relative URL to the web page from the linked service URL. Type: string (or Expression with resultType string).|web_table_path|
### datafactory dataset web-table update

web-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|web_table_linked_service_name|
|**--type-properties-index**|any|The zero-based index of the table in the web page. Type: integer (or Expression with resultType integer), minimum: 0.|web_table_index|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|web_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|web_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|web_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|web_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|web_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|web_table_folder|
|**--type-properties-path**|any|The relative URL to the web page from the linked service URL. Type: string (or Expression with resultType string).|web_table_path|
### datafactory dataset xero-object create

xero-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|xero_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|xero_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|xero_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|xero_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|xero_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|xero_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|xero_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|xero_object_table_name|
### datafactory dataset xero-object update

xero-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|xero_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|xero_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|xero_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|xero_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|xero_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|xero_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|xero_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|xero_object_table_name|
### datafactory dataset zoho-object create

zoho-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|zoho_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|zoho_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|zoho_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|zoho_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|zoho_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|zoho_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|zoho_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|zoho_object_table_name|
### datafactory dataset zoho-object update

zoho-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--linked-service-name**|object|Linked service reference.|zoho_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Dataset description.|zoho_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|zoho_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|zoho_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|zoho_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|zoho_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|zoho_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|zoho_object_table_name|
### datafactory exposure-control get-feature-value

get-feature-value a datafactory exposure-control.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location-id**|string|The location identifier.|location_id|
|**--feature-name**|string|The feature name.|feature_name|
|**--feature-type**|string|The feature type.|feature_type|
### datafactory exposure-control get-feature-value-by-factory

get-feature-value-by-factory a datafactory exposure-control.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--feature-name**|string|The feature name.|feature_name|
|**--feature-type**|string|The feature type.|feature_type|
### datafactory factory configure-factory-repo

configure-factory-repo a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location-id**|string|The location identifier.|location_id|
|**--factory-resource-id**|string|The factory resource id.|factory_resource_id|
|**--factory-vsts-configuration**|object|Factory's VSTS repo information.|factory_vsts_configuration|
|**--factory-git-hub-configuration**|object|Factory's GitHub repo information.|factory_git_hub_configuration|
### datafactory factory create

create a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--if-match**|string|ETag of the factory entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--identity**|object|Managed service identity of the factory.|identity|
|**--factory-vsts-configuration**|object|Factory's VSTS repo information.|factory_vsts_configuration|
|**--factory-git-hub-configuration**|object|Factory's GitHub repo information.|factory_git_hub_configuration|
### datafactory factory delete

delete a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory factory get-data-plane-access

get-data-plane-access a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--permissions**|string|The string with permissions for Data Plane access. Currently only 'r' is supported which grants read only access.|permissions|
|**--access-resource-path**|string|The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.|access_resource_path|
|**--profile-name**|string|The name of the profile. Currently only the default is supported. The default value is DefaultProfile.|profile_name|
|**--start-time**|string|Start time for the token. If not specified the current time will be used.|start_time|
|**--expire-time**|string|Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.|expire_time|
### datafactory factory get-git-hub-access-token

get-git-hub-access-token a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--git-hub-access-code**|string|GitHub access code.|git_hub_access_code|
|**--git-hub-access-token-base-url**|string|GitHub access token base URL.|git_hub_access_token_base_url|
|**--git-hub-client-id**|string|GitHub application client ID.|git_hub_client_id|
### datafactory factory list

list a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### datafactory factory show

show a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--if-none-match**|string|ETag of the factory entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory factory update

update a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--tags**|dictionary|The resource tags.|tags|
|**--identity**|object|Managed service identity of the factory.|identity|
### datafactory integration-runtime create-linked-integration-runtime

create-linked-integration-runtime a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--name**|string|The name of the linked integration runtime.|name|
|**--subscription-id**|string|The ID of the subscription that the linked integration runtime belongs to.|subscription_id|
|**--data-factory-name**|string|The name of the data factory that the linked integration runtime belongs to.|data_factory_name|
|**--data-factory-location**|string|The location of the data factory that the linked integration runtime belongs to.|data_factory_location|
### datafactory integration-runtime delete

delete a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime get-connection-info

get-connection-info a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime get-monitoring-data

get-monitoring-data a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime get-status

get-status a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime list

list a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory integration-runtime list-auth-key

list-auth-key a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime managed create

managed create a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--if-match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Integration runtime description.|managed_description|
|**--type-properties-compute-properties**|object|The compute resource for managed integration runtime.|managed_compute_properties|
|**--type-properties-ssis-properties**|object|SSIS properties for managed integration runtime.|managed_ssis_properties|
### datafactory integration-runtime regenerate-auth-key

regenerate-auth-key a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--key-name**|choice|The name of the authentication key to regenerate.|key_name|
### datafactory integration-runtime remove-link

remove-link a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--linked-factory-name**|string|The data factory name for linked integration runtime.|linked_factory_name|
### datafactory integration-runtime self-hosted create

self-hosted create a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--if-match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Integration runtime description.|self_hosted_description|
|**--type-properties-linked-info**|object|The base definition of a linked integration runtime.|self_hosted_linked_info|
### datafactory integration-runtime show

show a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--if-none-match**|string|ETag of the integration runtime entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory integration-runtime start

start a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime stop

stop a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime sync-credentials

sync-credentials a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime update

update a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--auto-update**|choice|Enables or disables the auto-update feature of the self-hosted integration runtime. See https://go.microsoft.com/fwlink/?linkid=854189.|auto_update|
|**--update-delay-offset**|string|The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.|update_delay_offset|
### datafactory integration-runtime upgrade

upgrade a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime-node delete

delete a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|
### datafactory integration-runtime-node get-ip-address

get-ip-address a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|
### datafactory integration-runtime-node show

show a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|
### datafactory integration-runtime-node update

update a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|
|**--concurrent-jobs-limit**|integer|The number of concurrent jobs permitted to run on the integration runtime node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.|concurrent_jobs_limit|
### datafactory integration-runtime-object-metadata get

get a datafactory integration-runtime-object-metadata.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--metadata-path**|string|Metadata path.|metadata_path|
### datafactory integration-runtime-object-metadata refresh

refresh a datafactory integration-runtime-object-metadata.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory linked-service amazon-mws create

amazon-mws create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the Amazon MWS server, (i.e. mws.amazonservices.com)|amazon_mws_endpoint|
|**--type-properties-marketplace-id**|any|The Amazon Marketplace ID you want to retrieve data from. To retrieve data from multiple Marketplace IDs, separate them with a comma (,). (i.e. A2EUQ1WTGCTBG2)|amazon_mws_marketplace_id|
|**--type-properties-seller-id**|any|The Amazon seller ID.|amazon_mws_seller_id|
|**--type-properties-access-key-id**|any|The access key id used to access data.|amazon_mws_access_key_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|amazon_mws_connect_via|
|**--description**|string|Linked service description.|amazon_mws_description|
|**--parameters**|dictionary|Parameters for linked service.|amazon_mws_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazon_mws_annotations|
|**--type-properties-mws-auth-token**|object|The Amazon MWS authentication token.|amazon_mws_mws_auth_token|
|**--type-properties-secret-key**|object|The secret key used to access data.|amazon_mws_secret_key|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|amazon_mws_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|amazon_mws_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|amazon_mws_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazon_mws_encrypted_credential|
### datafactory linked-service amazon-mws update

amazon-mws create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the Amazon MWS server, (i.e. mws.amazonservices.com)|amazon_mws_endpoint|
|**--type-properties-marketplace-id**|any|The Amazon Marketplace ID you want to retrieve data from. To retrieve data from multiple Marketplace IDs, separate them with a comma (,). (i.e. A2EUQ1WTGCTBG2)|amazon_mws_marketplace_id|
|**--type-properties-seller-id**|any|The Amazon seller ID.|amazon_mws_seller_id|
|**--type-properties-access-key-id**|any|The access key id used to access data.|amazon_mws_access_key_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|amazon_mws_connect_via|
|**--description**|string|Linked service description.|amazon_mws_description|
|**--parameters**|dictionary|Parameters for linked service.|amazon_mws_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazon_mws_annotations|
|**--type-properties-mws-auth-token**|object|The Amazon MWS authentication token.|amazon_mws_mws_auth_token|
|**--type-properties-secret-key**|object|The secret key used to access data.|amazon_mws_secret_key|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|amazon_mws_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|amazon_mws_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|amazon_mws_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazon_mws_encrypted_credential|
### datafactory linked-service amazon-redshift create

amazon-redshift create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-server**|any|The name of the Amazon Redshift server. Type: string (or Expression with resultType string).|amazon_redshift_server|
|**--type-properties-database**|any|The database name of the Amazon Redshift source. Type: string (or Expression with resultType string).|amazon_redshift_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|amazon_redshift_connect_via|
|**--description**|string|Linked service description.|amazon_redshift_description|
|**--parameters**|dictionary|Parameters for linked service.|amazon_redshift_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazon_redshift_annotations|
|**--type-properties-username**|any|The username of the Amazon Redshift source. Type: string (or Expression with resultType string).|amazon_redshift_username|
|**--type-properties-password**|object|The password of the Amazon Redshift source.|amazon_redshift_password|
|**--type-properties-port**|any|The TCP port number that the Amazon Redshift server uses to listen for client connections. The default value is 5439. Type: integer (or Expression with resultType integer).|amazon_redshift_port|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazon_redshift_encrypted_credential|
### datafactory linked-service amazon-redshift update

amazon-redshift create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-server**|any|The name of the Amazon Redshift server. Type: string (or Expression with resultType string).|amazon_redshift_server|
|**--type-properties-database**|any|The database name of the Amazon Redshift source. Type: string (or Expression with resultType string).|amazon_redshift_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|amazon_redshift_connect_via|
|**--description**|string|Linked service description.|amazon_redshift_description|
|**--parameters**|dictionary|Parameters for linked service.|amazon_redshift_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazon_redshift_annotations|
|**--type-properties-username**|any|The username of the Amazon Redshift source. Type: string (or Expression with resultType string).|amazon_redshift_username|
|**--type-properties-password**|object|The password of the Amazon Redshift source.|amazon_redshift_password|
|**--type-properties-port**|any|The TCP port number that the Amazon Redshift server uses to listen for client connections. The default value is 5439. Type: integer (or Expression with resultType integer).|amazon_redshift_port|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazon_redshift_encrypted_credential|
### datafactory linked-service amazon-s3 create

amazon-s3 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|amazon_s3_connect_via|
|**--description**|string|Linked service description.|amazon_s3_description|
|**--parameters**|dictionary|Parameters for linked service.|amazon_s3_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazon_s3_annotations|
|**--type-properties-access-key-id**|any|The access key identifier of the Amazon S3 Identity and Access Management (IAM) user. Type: string (or Expression with resultType string).|amazon_s3_access_key_id|
|**--type-properties-secret-access-key**|object|The secret access key of the Amazon S3 Identity and Access Management (IAM) user.|amazon_s3_secret_access_key|
|**--type-properties-service-url**|any|This value specifies the endpoint to access with the S3 Connector. This is an optional property; change it only if you want to try a different service endpoint or want to switch between https and http. Type: string (or Expression with resultType string).|amazon_s3_service_url|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazon_s3_encrypted_credential|
### datafactory linked-service amazon-s3 update

amazon-s3 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|amazon_s3_connect_via|
|**--description**|string|Linked service description.|amazon_s3_description|
|**--parameters**|dictionary|Parameters for linked service.|amazon_s3_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazon_s3_annotations|
|**--type-properties-access-key-id**|any|The access key identifier of the Amazon S3 Identity and Access Management (IAM) user. Type: string (or Expression with resultType string).|amazon_s3_access_key_id|
|**--type-properties-secret-access-key**|object|The secret access key of the Amazon S3 Identity and Access Management (IAM) user.|amazon_s3_secret_access_key|
|**--type-properties-service-url**|any|This value specifies the endpoint to access with the S3 Connector. This is an optional property; change it only if you want to try a different service endpoint or want to switch between https and http. Type: string (or Expression with resultType string).|amazon_s3_service_url|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazon_s3_encrypted_credential|
### datafactory linked-service azure-batch create

azure-batch create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-account-name**|any|The Azure Batch account name. Type: string (or Expression with resultType string).|azure_batch_account_name|
|**--type-properties-batch-uri**|any|The Azure Batch URI. Type: string (or Expression with resultType string).|azure_batch_batch_uri|
|**--type-properties-pool-name**|any|The Azure Batch pool name. Type: string (or Expression with resultType string).|azure_batch_pool_name|
|**--type-properties-linked-service-name**|object|The Azure Storage linked service reference.|azure_batch_linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_batch_connect_via|
|**--description**|string|Linked service description.|azure_batch_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_batch_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_batch_annotations|
|**--type-properties-access-key**|object|The Azure Batch account access key.|azure_batch_access_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_batch_encrypted_credential|
### datafactory linked-service azure-batch update

azure-batch create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-account-name**|any|The Azure Batch account name. Type: string (or Expression with resultType string).|azure_batch_account_name|
|**--type-properties-batch-uri**|any|The Azure Batch URI. Type: string (or Expression with resultType string).|azure_batch_batch_uri|
|**--type-properties-pool-name**|any|The Azure Batch pool name. Type: string (or Expression with resultType string).|azure_batch_pool_name|
|**--type-properties-linked-service-name**|object|The Azure Storage linked service reference.|azure_batch_linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_batch_connect_via|
|**--description**|string|Linked service description.|azure_batch_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_batch_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_batch_annotations|
|**--type-properties-access-key**|object|The Azure Batch account access key.|azure_batch_access_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_batch_encrypted_credential|
### datafactory linked-service azure-blob-fs create

azure-blob-fs create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|Endpoint for the Azure Data Lake Storage Gen2 service. Type: string (or Expression with resultType string).|azure_blob_fs_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_blob_fs_connect_via|
|**--description**|string|Linked service description.|azure_blob_fs_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_blob_fs_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_blob_fs_annotations|
|**--type-properties-account-key**|any|Account key for the Azure Data Lake Storage Gen2 service. Type: string (or Expression with resultType string).|azure_blob_fs_account_key|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Storage Gen2 account. Type: string (or Expression with resultType string).|azure_blob_fs_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Storage Gen2 account.|azure_blob_fs_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_blob_fs_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_blob_fs_encrypted_credential|
### datafactory linked-service azure-blob-fs update

azure-blob-fs create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|Endpoint for the Azure Data Lake Storage Gen2 service. Type: string (or Expression with resultType string).|azure_blob_fs_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_blob_fs_connect_via|
|**--description**|string|Linked service description.|azure_blob_fs_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_blob_fs_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_blob_fs_annotations|
|**--type-properties-account-key**|any|Account key for the Azure Data Lake Storage Gen2 service. Type: string (or Expression with resultType string).|azure_blob_fs_account_key|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Storage Gen2 account. Type: string (or Expression with resultType string).|azure_blob_fs_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Storage Gen2 account.|azure_blob_fs_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_blob_fs_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_blob_fs_encrypted_credential|
### datafactory linked-service azure-blob-storage create

azure-blob-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_blob_storage_connect_via|
|**--description**|string|Linked service description.|azure_blob_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_blob_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_blob_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri, serviceEndpoint property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_blob_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azure_blob_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Blob Storage resource. It is mutually exclusive with connectionString, serviceEndpoint property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_blob_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azure_blob_storage_sas_token|
|**--type-properties-service-endpoint**|string|Blob service endpoint of the Azure Blob Storage resource. It is mutually exclusive with connectionString, sasUri property.|azure_blob_storage_service_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azure_blob_storage_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Data Warehouse.|azure_blob_storage_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_blob_storage_tenant|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_blob_storage_encrypted_credential|
### datafactory linked-service azure-blob-storage update

azure-blob-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_blob_storage_connect_via|
|**--description**|string|Linked service description.|azure_blob_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_blob_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_blob_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri, serviceEndpoint property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_blob_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azure_blob_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Blob Storage resource. It is mutually exclusive with connectionString, serviceEndpoint property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_blob_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azure_blob_storage_sas_token|
|**--type-properties-service-endpoint**|string|Blob service endpoint of the Azure Blob Storage resource. It is mutually exclusive with connectionString, sasUri property.|azure_blob_storage_service_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azure_blob_storage_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Data Warehouse.|azure_blob_storage_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_blob_storage_tenant|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_blob_storage_encrypted_credential|
### datafactory linked-service azure-data-explorer create

azure-data-explorer create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of Azure Data Explorer (the engine's endpoint). URL will be in the format https://:code:`<clusterName>`.:code:`<regionName>`.kusto.windows.net. Type: string (or Expression with resultType string)|azure_data_explorer_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure Data Explorer. Type: string (or Expression with resultType string).|azure_data_explorer_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Kusto.|azure_data_explorer_service_principal_key|
|**--type-properties-database**|any|Database name for connection. Type: string (or Expression with resultType string).|azure_data_explorer_database|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_data_explorer_tenant|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_data_explorer_connect_via|
|**--description**|string|Linked service description.|azure_data_explorer_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_data_explorer_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_data_explorer_annotations|
### datafactory linked-service azure-data-explorer update

azure-data-explorer create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of Azure Data Explorer (the engine's endpoint). URL will be in the format https://:code:`<clusterName>`.:code:`<regionName>`.kusto.windows.net. Type: string (or Expression with resultType string)|azure_data_explorer_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure Data Explorer. Type: string (or Expression with resultType string).|azure_data_explorer_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Kusto.|azure_data_explorer_service_principal_key|
|**--type-properties-database**|any|Database name for connection. Type: string (or Expression with resultType string).|azure_data_explorer_database|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_data_explorer_tenant|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_data_explorer_connect_via|
|**--description**|string|Linked service description.|azure_data_explorer_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_data_explorer_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_data_explorer_annotations|
### datafactory linked-service azure-data-lake-analytics create

azure-data-lake-analytics create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-account-name**|any|The Azure Data Lake Analytics account name. Type: string (or Expression with resultType string).|azure_data_lake_analytics_account_name|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_data_lake_analytics_tenant|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_data_lake_analytics_connect_via|
|**--description**|string|Linked service description.|azure_data_lake_analytics_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_data_lake_analytics_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_data_lake_analytics_annotations|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Analytics account. Type: string (or Expression with resultType string).|azure_data_lake_analytics_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Analytics account.|azure_data_lake_analytics_service_principal_key|
|**--type-properties-subscription-id**|any|Data Lake Analytics account subscription ID (if different from Data Factory account). Type: string (or Expression with resultType string).|azure_data_lake_analytics_subscription_id|
|**--type-properties-resource-group-name**|any|Data Lake Analytics account resource group name (if different from Data Factory account). Type: string (or Expression with resultType string).|azure_data_lake_analytics_resource_group_name|
|**--type-properties-data-lake-analytics-uri**|any|Azure Data Lake Analytics URI Type: string (or Expression with resultType string).|azure_data_lake_analytics_data_lake_analytics_uri|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_data_lake_analytics_encrypted_credential|
### datafactory linked-service azure-data-lake-analytics update

azure-data-lake-analytics create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-account-name**|any|The Azure Data Lake Analytics account name. Type: string (or Expression with resultType string).|azure_data_lake_analytics_account_name|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_data_lake_analytics_tenant|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_data_lake_analytics_connect_via|
|**--description**|string|Linked service description.|azure_data_lake_analytics_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_data_lake_analytics_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_data_lake_analytics_annotations|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Analytics account. Type: string (or Expression with resultType string).|azure_data_lake_analytics_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Analytics account.|azure_data_lake_analytics_service_principal_key|
|**--type-properties-subscription-id**|any|Data Lake Analytics account subscription ID (if different from Data Factory account). Type: string (or Expression with resultType string).|azure_data_lake_analytics_subscription_id|
|**--type-properties-resource-group-name**|any|Data Lake Analytics account resource group name (if different from Data Factory account). Type: string (or Expression with resultType string).|azure_data_lake_analytics_resource_group_name|
|**--type-properties-data-lake-analytics-uri**|any|Azure Data Lake Analytics URI Type: string (or Expression with resultType string).|azure_data_lake_analytics_data_lake_analytics_uri|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_data_lake_analytics_encrypted_credential|
### datafactory linked-service azure-data-lake-store create

azure-data-lake-store create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-data-lake-store-uri**|any|Data Lake Store service URI. Type: string (or Expression with resultType string).|azure_data_lake_store_data_lake_store_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_data_lake_store_connect_via|
|**--description**|string|Linked service description.|azure_data_lake_store_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_data_lake_store_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_data_lake_store_annotations|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Store account. Type: string (or Expression with resultType string).|azure_data_lake_store_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Store account.|azure_data_lake_store_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_data_lake_store_tenant|
|**--type-properties-account-name**|any|Data Lake Store account name. Type: string (or Expression with resultType string).|azure_data_lake_store_account_name|
|**--type-properties-subscription-id**|any|Data Lake Store account subscription ID (if different from Data Factory account). Type: string (or Expression with resultType string).|azure_data_lake_store_subscription_id|
|**--type-properties-resource-group-name**|any|Data Lake Store account resource group name (if different from Data Factory account). Type: string (or Expression with resultType string).|azure_data_lake_store_resource_group_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_data_lake_store_encrypted_credential|
### datafactory linked-service azure-data-lake-store update

azure-data-lake-store create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-data-lake-store-uri**|any|Data Lake Store service URI. Type: string (or Expression with resultType string).|azure_data_lake_store_data_lake_store_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_data_lake_store_connect_via|
|**--description**|string|Linked service description.|azure_data_lake_store_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_data_lake_store_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_data_lake_store_annotations|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Store account. Type: string (or Expression with resultType string).|azure_data_lake_store_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Store account.|azure_data_lake_store_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_data_lake_store_tenant|
|**--type-properties-account-name**|any|Data Lake Store account name. Type: string (or Expression with resultType string).|azure_data_lake_store_account_name|
|**--type-properties-subscription-id**|any|Data Lake Store account subscription ID (if different from Data Factory account). Type: string (or Expression with resultType string).|azure_data_lake_store_subscription_id|
|**--type-properties-resource-group-name**|any|Data Lake Store account resource group name (if different from Data Factory account). Type: string (or Expression with resultType string).|azure_data_lake_store_resource_group_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_data_lake_store_encrypted_credential|
### datafactory linked-service azure-databricks create

azure-databricks create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-domain**|any|:code:`<REGION>`.azuredatabricks.net, domain name of your Databricks deployment. Type: string (or Expression with resultType string).|azure_databricks_domain|
|**--type-properties-access-token**|object|Access token for databricks REST API. Refer to https://docs.azuredatabricks.net/api/latest/authentication.html. Type: string (or Expression with resultType string).|azure_databricks_access_token|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_databricks_connect_via|
|**--description**|string|Linked service description.|azure_databricks_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_databricks_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_databricks_annotations|
|**--type-properties-existing-cluster-id**|any|The id of an existing interactive cluster that will be used for all runs of this activity. Type: string (or Expression with resultType string).|azure_databricks_existing_cluster_id|
|**--type-properties-instance-pool-id**|any|The id of an existing instance pool that will be used for all runs of this activity. Type: string (or Expression with resultType string).|azure_databricks_instance_pool_id|
|**--type-properties-new-cluster-version**|any|If not using an existing interactive cluster, this specifies the Spark version of a new job cluster or instance pool nodes created for each run of this activity. Required if instancePoolId is specified. Type: string (or Expression with resultType string).|azure_databricks_new_cluster_version|
|**--type-properties-new-cluster-num-of-worker**|any|If not using an existing interactive cluster, this specifies the number of worker nodes to use for the new job cluster or instance pool. For new job clusters, this a string-formatted Int32, like '1' means numOfWorker is 1 or '1:10' means auto-scale from 1 (min) to 10 (max). For instance pools, this is a string-formatted Int32, and can only specify a fixed number of worker nodes, such as '2'. Required if newClusterVersion is specified. Type: string (or Expression with resultType string).|azure_databricks_new_cluster_num_of_worker|
|**--type-properties-new-cluster-node-type**|any|The node type of the new job cluster. This property is required if newClusterVersion is specified and instancePoolId is not specified. If instancePoolId is specified, this property is ignored. Type: string (or Expression with resultType string).|azure_databricks_new_cluster_node_type|
|**--type-properties-new-cluster-spark-conf**|dictionary|A set of optional, user-specified Spark configuration key-value pairs.|azure_databricks_new_cluster_spark_conf|
|**--type-properties-new-cluster-spark-env-vars**|dictionary|A set of optional, user-specified Spark environment variables key-value pairs.|azure_databricks_new_cluster_spark_env_vars|
|**--type-properties-new-cluster-custom-tags**|dictionary|Additional tags for cluster resources. This property is ignored in instance pool configurations.|azure_databricks_new_cluster_custom_tags|
|**--type-properties-new-cluster-driver-node-type**|any|The driver node type for the new job cluster. This property is ignored in instance pool configurations. Type: string (or Expression with resultType string).|azure_databricks_new_cluster_driver_node_type|
|**--type-properties-new-cluster-init-scripts**|any|User-defined initialization scripts for the new cluster. Type: array of strings (or Expression with resultType array of strings).|azure_databricks_new_cluster_init_scripts|
|**--type-properties-new-cluster-enable-elastic-disk**|any|Enable the elastic disk on the new cluster. This property is now ignored, and takes the default elastic disk behavior in Databricks (elastic disks are always enabled). Type: boolean (or Expression with resultType boolean).|azure_databricks_new_cluster_enable_elastic_disk|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_databricks_encrypted_credential|
### datafactory linked-service azure-databricks update

azure-databricks create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-domain**|any|:code:`<REGION>`.azuredatabricks.net, domain name of your Databricks deployment. Type: string (or Expression with resultType string).|azure_databricks_domain|
|**--type-properties-access-token**|object|Access token for databricks REST API. Refer to https://docs.azuredatabricks.net/api/latest/authentication.html. Type: string (or Expression with resultType string).|azure_databricks_access_token|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_databricks_connect_via|
|**--description**|string|Linked service description.|azure_databricks_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_databricks_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_databricks_annotations|
|**--type-properties-existing-cluster-id**|any|The id of an existing interactive cluster that will be used for all runs of this activity. Type: string (or Expression with resultType string).|azure_databricks_existing_cluster_id|
|**--type-properties-instance-pool-id**|any|The id of an existing instance pool that will be used for all runs of this activity. Type: string (or Expression with resultType string).|azure_databricks_instance_pool_id|
|**--type-properties-new-cluster-version**|any|If not using an existing interactive cluster, this specifies the Spark version of a new job cluster or instance pool nodes created for each run of this activity. Required if instancePoolId is specified. Type: string (or Expression with resultType string).|azure_databricks_new_cluster_version|
|**--type-properties-new-cluster-num-of-worker**|any|If not using an existing interactive cluster, this specifies the number of worker nodes to use for the new job cluster or instance pool. For new job clusters, this a string-formatted Int32, like '1' means numOfWorker is 1 or '1:10' means auto-scale from 1 (min) to 10 (max). For instance pools, this is a string-formatted Int32, and can only specify a fixed number of worker nodes, such as '2'. Required if newClusterVersion is specified. Type: string (or Expression with resultType string).|azure_databricks_new_cluster_num_of_worker|
|**--type-properties-new-cluster-node-type**|any|The node type of the new job cluster. This property is required if newClusterVersion is specified and instancePoolId is not specified. If instancePoolId is specified, this property is ignored. Type: string (or Expression with resultType string).|azure_databricks_new_cluster_node_type|
|**--type-properties-new-cluster-spark-conf**|dictionary|A set of optional, user-specified Spark configuration key-value pairs.|azure_databricks_new_cluster_spark_conf|
|**--type-properties-new-cluster-spark-env-vars**|dictionary|A set of optional, user-specified Spark environment variables key-value pairs.|azure_databricks_new_cluster_spark_env_vars|
|**--type-properties-new-cluster-custom-tags**|dictionary|Additional tags for cluster resources. This property is ignored in instance pool configurations.|azure_databricks_new_cluster_custom_tags|
|**--type-properties-new-cluster-driver-node-type**|any|The driver node type for the new job cluster. This property is ignored in instance pool configurations. Type: string (or Expression with resultType string).|azure_databricks_new_cluster_driver_node_type|
|**--type-properties-new-cluster-init-scripts**|any|User-defined initialization scripts for the new cluster. Type: array of strings (or Expression with resultType array of strings).|azure_databricks_new_cluster_init_scripts|
|**--type-properties-new-cluster-enable-elastic-disk**|any|Enable the elastic disk on the new cluster. This property is now ignored, and takes the default elastic disk behavior in Databricks (elastic disks are always enabled). Type: boolean (or Expression with resultType boolean).|azure_databricks_new_cluster_enable_elastic_disk|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_databricks_encrypted_credential|
### datafactory linked-service azure-file-storage create

azure-file-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|Host name of the server. Type: string (or Expression with resultType string).|azure_file_storage_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_file_storage_connect_via|
|**--description**|string|Linked service description.|azure_file_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_file_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_file_storage_annotations|
|**--type-properties-user-id**|any|User ID to logon the server. Type: string (or Expression with resultType string).|azure_file_storage_user_id|
|**--type-properties-password**|object|Password to logon the server.|azure_file_storage_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_file_storage_encrypted_credential|
### datafactory linked-service azure-file-storage update

azure-file-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|Host name of the server. Type: string (or Expression with resultType string).|azure_file_storage_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_file_storage_connect_via|
|**--description**|string|Linked service description.|azure_file_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_file_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_file_storage_annotations|
|**--type-properties-user-id**|any|User ID to logon the server. Type: string (or Expression with resultType string).|azure_file_storage_user_id|
|**--type-properties-password**|object|Password to logon the server.|azure_file_storage_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_file_storage_encrypted_credential|
### datafactory linked-service azure-function create

azure-function create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-function-app-url**|any|The endpoint of the Azure Function App. URL will be in the format https://:code:`<accountName>`.azurewebsites.net.|azure_function_function_app_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_function_connect_via|
|**--description**|string|Linked service description.|azure_function_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_function_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_function_annotations|
|**--type-properties-function-key**|object|Function or Host key for Azure Function App.|azure_function_function_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_function_encrypted_credential|
### datafactory linked-service azure-function update

azure-function create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-function-app-url**|any|The endpoint of the Azure Function App. URL will be in the format https://:code:`<accountName>`.azurewebsites.net.|azure_function_function_app_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_function_connect_via|
|**--description**|string|Linked service description.|azure_function_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_function_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_function_annotations|
|**--type-properties-function-key**|object|Function or Host key for Azure Function App.|azure_function_function_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_function_encrypted_credential|
### datafactory linked-service azure-key-vault create

azure-key-vault create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-base-url**|any|The base URL of the Azure Key Vault. e.g. https://myakv.vault.azure.net Type: string (or Expression with resultType string).|azure_key_vault_base_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_key_vault_connect_via|
|**--description**|string|Linked service description.|azure_key_vault_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_key_vault_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_key_vault_annotations|
### datafactory linked-service azure-key-vault update

azure-key-vault create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-base-url**|any|The base URL of the Azure Key Vault. e.g. https://myakv.vault.azure.net Type: string (or Expression with resultType string).|azure_key_vault_base_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_key_vault_connect_via|
|**--description**|string|Linked service description.|azure_key_vault_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_key_vault_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_key_vault_annotations|
### datafactory linked-service azure-maria-d-b create

azure-maria-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_maria_d_b_connect_via|
|**--description**|string|Linked service description.|azure_maria_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_maria_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_maria_d_b_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_maria_d_b_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|azure_maria_d_b_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_maria_d_b_encrypted_credential|
### datafactory linked-service azure-maria-d-b update

azure-maria-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_maria_d_b_connect_via|
|**--description**|string|Linked service description.|azure_maria_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_maria_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_maria_d_b_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_maria_d_b_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|azure_maria_d_b_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_maria_d_b_encrypted_credential|
### datafactory linked-service azure-ml create

azure-ml create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-ml-endpoint**|any|The Batch Execution REST URL for an Azure ML Studio Web Service endpoint. Type: string (or Expression with resultType string).|azure_ml_ml_endpoint|
|**--type-properties-api-key**|object|The API key for accessing the Azure ML model endpoint.|azure_ml_api_key|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_ml_connect_via|
|**--description**|string|Linked service description.|azure_ml_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_ml_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_ml_annotations|
|**--type-properties-update-resource-endpoint**|any|The Update Resource REST URL for an Azure ML Studio Web Service endpoint. Type: string (or Expression with resultType string).|azure_ml_update_resource_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against the ARM-based updateResourceEndpoint of an Azure ML Studio web service. Type: string (or Expression with resultType string).|azure_ml_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against the ARM-based updateResourceEndpoint of an Azure ML Studio web service.|azure_ml_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_ml_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_ml_encrypted_credential|
### datafactory linked-service azure-ml update

azure-ml create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-ml-endpoint**|any|The Batch Execution REST URL for an Azure ML Studio Web Service endpoint. Type: string (or Expression with resultType string).|azure_ml_ml_endpoint|
|**--type-properties-api-key**|object|The API key for accessing the Azure ML model endpoint.|azure_ml_api_key|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_ml_connect_via|
|**--description**|string|Linked service description.|azure_ml_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_ml_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_ml_annotations|
|**--type-properties-update-resource-endpoint**|any|The Update Resource REST URL for an Azure ML Studio Web Service endpoint. Type: string (or Expression with resultType string).|azure_ml_update_resource_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against the ARM-based updateResourceEndpoint of an Azure ML Studio web service. Type: string (or Expression with resultType string).|azure_ml_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against the ARM-based updateResourceEndpoint of an Azure ML Studio web service.|azure_ml_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_ml_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_ml_encrypted_credential|
### datafactory linked-service azure-ml-service create

azure-ml-service create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-subscription-id**|any|Azure ML Service workspace subscription ID. Type: string (or Expression with resultType string).|azure_ml_service_subscription_id|
|**--type-properties-resource-group-name**|any|Azure ML Service workspace resource group name. Type: string (or Expression with resultType string).|azure_ml_service_resource_group_name|
|**--type-properties-ml-workspace-name**|any|Azure ML Service workspace name. Type: string (or Expression with resultType string).|azure_ml_service_ml_workspace_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_ml_service_connect_via|
|**--description**|string|Linked service description.|azure_ml_service_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_ml_service_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_ml_service_annotations|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against the endpoint of a published Azure ML Service pipeline. Type: string (or Expression with resultType string).|azure_ml_service_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against the endpoint of a published Azure ML Service pipeline.|azure_ml_service_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_ml_service_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_ml_service_encrypted_credential|
### datafactory linked-service azure-ml-service update

azure-ml-service create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-subscription-id**|any|Azure ML Service workspace subscription ID. Type: string (or Expression with resultType string).|azure_ml_service_subscription_id|
|**--type-properties-resource-group-name**|any|Azure ML Service workspace resource group name. Type: string (or Expression with resultType string).|azure_ml_service_resource_group_name|
|**--type-properties-ml-workspace-name**|any|Azure ML Service workspace name. Type: string (or Expression with resultType string).|azure_ml_service_ml_workspace_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_ml_service_connect_via|
|**--description**|string|Linked service description.|azure_ml_service_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_ml_service_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_ml_service_annotations|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against the endpoint of a published Azure ML Service pipeline. Type: string (or Expression with resultType string).|azure_ml_service_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against the endpoint of a published Azure ML Service pipeline.|azure_ml_service_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_ml_service_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_ml_service_encrypted_credential|
### datafactory linked-service azure-my-sql create

azure-my-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_my_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_my_sql_connect_via|
|**--description**|string|Linked service description.|azure_my_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_my_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_my_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azure_my_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_my_sql_encrypted_credential|
### datafactory linked-service azure-my-sql update

azure-my-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_my_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_my_sql_connect_via|
|**--description**|string|Linked service description.|azure_my_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_my_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_my_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azure_my_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_my_sql_encrypted_credential|
### datafactory linked-service azure-postgre-sql create

azure-postgre-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_postgre_sql_connect_via|
|**--description**|string|Linked service description.|azure_postgre_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_postgre_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_postgre_sql_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_postgre_sql_connection_string|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azure_postgre_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_postgre_sql_encrypted_credential|
### datafactory linked-service azure-postgre-sql update

azure-postgre-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_postgre_sql_connect_via|
|**--description**|string|Linked service description.|azure_postgre_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_postgre_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_postgre_sql_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_postgre_sql_connection_string|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azure_postgre_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_postgre_sql_encrypted_credential|
### datafactory linked-service azure-search create

azure-search create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|URL for Azure Search service. Type: string (or Expression with resultType string).|azure_search_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_search_connect_via|
|**--description**|string|Linked service description.|azure_search_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_search_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_search_annotations|
|**--type-properties-key**|object|Admin Key for Azure Search service|azure_search_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_search_encrypted_credential|
### datafactory linked-service azure-search update

azure-search create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|URL for Azure Search service. Type: string (or Expression with resultType string).|azure_search_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_search_connect_via|
|**--description**|string|Linked service description.|azure_search_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_search_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_search_annotations|
|**--type-properties-key**|object|Admin Key for Azure Search service|azure_search_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_search_encrypted_credential|
### datafactory linked-service azure-sql-database create

azure-sql-database create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_sql_database_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_sql_database_connect_via|
|**--description**|string|Linked service description.|azure_sql_database_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_sql_database_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_sql_database_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azure_sql_database_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Database. Type: string (or Expression with resultType string).|azure_sql_database_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Database.|azure_sql_database_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_sql_database_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_sql_database_encrypted_credential|
### datafactory linked-service azure-sql-database update

azure-sql-database create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_sql_database_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_sql_database_connect_via|
|**--description**|string|Linked service description.|azure_sql_database_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_sql_database_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_sql_database_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azure_sql_database_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Database. Type: string (or Expression with resultType string).|azure_sql_database_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Database.|azure_sql_database_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_sql_database_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_sql_database_encrypted_credential|
### datafactory linked-service azure-sql-dw create

azure-sql-dw create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_sql_dw_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_sql_dw_connect_via|
|**--description**|string|Linked service description.|azure_sql_dw_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_sql_dw_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_sql_dw_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azure_sql_dw_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azure_sql_dw_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Data Warehouse.|azure_sql_dw_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_sql_dw_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_sql_dw_encrypted_credential|
### datafactory linked-service azure-sql-dw update

azure-sql-dw create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_sql_dw_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_sql_dw_connect_via|
|**--description**|string|Linked service description.|azure_sql_dw_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_sql_dw_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_sql_dw_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azure_sql_dw_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azure_sql_dw_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Data Warehouse.|azure_sql_dw_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_sql_dw_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_sql_dw_encrypted_credential|
### datafactory linked-service azure-sql-mi create

azure-sql-mi create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_sql_mi_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_sql_mi_connect_via|
|**--description**|string|Linked service description.|azure_sql_mi_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_sql_mi_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_sql_mi_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azure_sql_mi_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Managed Instance. Type: string (or Expression with resultType string).|azure_sql_mi_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Managed Instance.|azure_sql_mi_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_sql_mi_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_sql_mi_encrypted_credential|
### datafactory linked-service azure-sql-mi update

azure-sql-mi create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_sql_mi_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_sql_mi_connect_via|
|**--description**|string|Linked service description.|azure_sql_mi_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_sql_mi_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_sql_mi_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azure_sql_mi_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Managed Instance. Type: string (or Expression with resultType string).|azure_sql_mi_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Managed Instance.|azure_sql_mi_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azure_sql_mi_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_sql_mi_encrypted_credential|
### datafactory linked-service azure-storage create

azure-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_storage_connect_via|
|**--description**|string|Linked service description.|azure_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azure_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Storage resource. It is mutually exclusive with connectionString property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azure_storage_sas_token|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_storage_encrypted_credential|
### datafactory linked-service azure-storage update

azure-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_storage_connect_via|
|**--description**|string|Linked service description.|azure_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azure_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Storage resource. It is mutually exclusive with connectionString property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azure_storage_sas_token|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_storage_encrypted_credential|
### datafactory linked-service azure-table-storage create

azure-table-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_table_storage_connect_via|
|**--description**|string|Linked service description.|azure_table_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_table_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_table_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_table_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azure_table_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Storage resource. It is mutually exclusive with connectionString property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_table_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azure_table_storage_sas_token|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_table_storage_encrypted_credential|
### datafactory linked-service azure-table-storage update

azure-table-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|azure_table_storage_connect_via|
|**--description**|string|Linked service description.|azure_table_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azure_table_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azure_table_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_table_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azure_table_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Storage resource. It is mutually exclusive with connectionString property. Type: string, SecureString or AzureKeyVaultSecretReference.|azure_table_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azure_table_storage_sas_token|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azure_table_storage_encrypted_credential|
### datafactory linked-service cassandra create

cassandra create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|Host name for connection. Type: string (or Expression with resultType string).|cassandra_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|cassandra_connect_via|
|**--description**|string|Linked service description.|cassandra_description|
|**--parameters**|dictionary|Parameters for linked service.|cassandra_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cassandra_annotations|
|**--type-properties-authentication-type**|any|AuthenticationType to be used for connection. Type: string (or Expression with resultType string).|cassandra_authentication_type|
|**--type-properties-port**|any|The port for the connection. Type: integer (or Expression with resultType integer).|cassandra_port|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|cassandra_username|
|**--type-properties-password**|object|Password for authentication.|cassandra_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|cassandra_encrypted_credential|
### datafactory linked-service cassandra update

cassandra create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|Host name for connection. Type: string (or Expression with resultType string).|cassandra_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|cassandra_connect_via|
|**--description**|string|Linked service description.|cassandra_description|
|**--parameters**|dictionary|Parameters for linked service.|cassandra_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cassandra_annotations|
|**--type-properties-authentication-type**|any|AuthenticationType to be used for connection. Type: string (or Expression with resultType string).|cassandra_authentication_type|
|**--type-properties-port**|any|The port for the connection. Type: integer (or Expression with resultType integer).|cassandra_port|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|cassandra_username|
|**--type-properties-password**|object|Password for authentication.|cassandra_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|cassandra_encrypted_credential|
### datafactory linked-service common-data-service-for-apps create

common-data-service-for-apps create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-deployment-type**|choice|The deployment type of the Common Data Service for Apps instance. 'Online' for Common Data Service for Apps Online and 'OnPremisesWithIfd' for Common Data Service for Apps on-premises with Ifd. Type: string (or Expression with resultType string).|common_data_service_for_apps_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Common Data Service for Apps server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario. 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|common_data_service_for_apps_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|common_data_service_for_apps_connect_via|
|**--description**|string|Linked service description.|common_data_service_for_apps_description|
|**--parameters**|dictionary|Parameters for linked service.|common_data_service_for_apps_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|common_data_service_for_apps_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Common Data Service for Apps server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|common_data_service_for_apps_host_name|
|**--type-properties-port**|any|The port of on-premises Common Data Service for Apps server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|common_data_service_for_apps_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Common Data Service for Apps server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|common_data_service_for_apps_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Common Data Service for Apps instance. The property is required for on-prem and required for online when there are more than one Common Data Service for Apps instances associated with the user. Type: string (or Expression with resultType string).|common_data_service_for_apps_organization_name|
|**--type-properties-username**|any|User name to access the Common Data Service for Apps instance. Type: string (or Expression with resultType string).|common_data_service_for_apps_username|
|**--type-properties-password**|object|Password to access the Common Data Service for Apps instance.|common_data_service_for_apps_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|common_data_service_for_apps_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|common_data_service_for_apps_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|common_data_service_for_apps_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|common_data_service_for_apps_encrypted_credential|
### datafactory linked-service common-data-service-for-apps update

common-data-service-for-apps create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-deployment-type**|choice|The deployment type of the Common Data Service for Apps instance. 'Online' for Common Data Service for Apps Online and 'OnPremisesWithIfd' for Common Data Service for Apps on-premises with Ifd. Type: string (or Expression with resultType string).|common_data_service_for_apps_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Common Data Service for Apps server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario. 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|common_data_service_for_apps_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|common_data_service_for_apps_connect_via|
|**--description**|string|Linked service description.|common_data_service_for_apps_description|
|**--parameters**|dictionary|Parameters for linked service.|common_data_service_for_apps_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|common_data_service_for_apps_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Common Data Service for Apps server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|common_data_service_for_apps_host_name|
|**--type-properties-port**|any|The port of on-premises Common Data Service for Apps server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|common_data_service_for_apps_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Common Data Service for Apps server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|common_data_service_for_apps_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Common Data Service for Apps instance. The property is required for on-prem and required for online when there are more than one Common Data Service for Apps instances associated with the user. Type: string (or Expression with resultType string).|common_data_service_for_apps_organization_name|
|**--type-properties-username**|any|User name to access the Common Data Service for Apps instance. Type: string (or Expression with resultType string).|common_data_service_for_apps_username|
|**--type-properties-password**|object|Password to access the Common Data Service for Apps instance.|common_data_service_for_apps_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|common_data_service_for_apps_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|common_data_service_for_apps_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|common_data_service_for_apps_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|common_data_service_for_apps_encrypted_credential|
### datafactory linked-service concur create

concur create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-client-id**|any|Application client_id supplied by Concur App Management.|concur_client_id|
|**--type-properties-username**|any|The user name that you use to access Concur Service.|concur_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|concur_connect_via|
|**--description**|string|Linked service description.|concur_description|
|**--parameters**|dictionary|Parameters for linked service.|concur_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|concur_annotations|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username field.|concur_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|concur_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|concur_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|concur_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|concur_encrypted_credential|
### datafactory linked-service concur update

concur create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-client-id**|any|Application client_id supplied by Concur App Management.|concur_client_id|
|**--type-properties-username**|any|The user name that you use to access Concur Service.|concur_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|concur_connect_via|
|**--description**|string|Linked service description.|concur_description|
|**--parameters**|dictionary|Parameters for linked service.|concur_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|concur_annotations|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username field.|concur_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|concur_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|concur_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|concur_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|concur_encrypted_credential|
### datafactory linked-service cosmos-d-b create

cosmos-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|cosmos_d_b_connect_via|
|**--description**|string|Linked service description.|cosmos_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|cosmos_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cosmos_d_b_annotations|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|cosmos_d_b_connection_string|
|**--type-properties-account-endpoint**|any|The endpoint of the Azure CosmosDB account. Type: string (or Expression with resultType string)|cosmos_d_b_account_endpoint|
|**--type-properties-database**|any|The name of the database. Type: string (or Expression with resultType string)|cosmos_d_b_database|
|**--type-properties-account-key**|object|The account key of the Azure CosmosDB account. Type: SecureString or AzureKeyVaultSecretReference.|cosmos_d_b_account_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|cosmos_d_b_encrypted_credential|
### datafactory linked-service cosmos-d-b update

cosmos-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|cosmos_d_b_connect_via|
|**--description**|string|Linked service description.|cosmos_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|cosmos_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cosmos_d_b_annotations|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|cosmos_d_b_connection_string|
|**--type-properties-account-endpoint**|any|The endpoint of the Azure CosmosDB account. Type: string (or Expression with resultType string)|cosmos_d_b_account_endpoint|
|**--type-properties-database**|any|The name of the database. Type: string (or Expression with resultType string)|cosmos_d_b_database|
|**--type-properties-account-key**|object|The account key of the Azure CosmosDB account. Type: SecureString or AzureKeyVaultSecretReference.|cosmos_d_b_account_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|cosmos_d_b_encrypted_credential|
### datafactory linked-service cosmos-d-b-mongo-d-b-api create

cosmos-d-b-mongo-d-b-api create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The CosmosDB (MongoDB API) connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|cosmos_d_b_mongo_d_b_api_connection_string|
|**--type-properties-database**|any|The name of the CosmosDB (MongoDB API) database that you want to access. Type: string (or Expression with resultType string).|cosmos_d_b_mongo_d_b_api_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|cosmos_d_b_mongo_d_b_api_connect_via|
|**--description**|string|Linked service description.|cosmos_d_b_mongo_d_b_api_description|
|**--parameters**|dictionary|Parameters for linked service.|cosmos_d_b_mongo_d_b_api_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cosmos_d_b_mongo_d_b_api_annotations|
### datafactory linked-service cosmos-d-b-mongo-d-b-api update

cosmos-d-b-mongo-d-b-api create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The CosmosDB (MongoDB API) connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|cosmos_d_b_mongo_d_b_api_connection_string|
|**--type-properties-database**|any|The name of the CosmosDB (MongoDB API) database that you want to access. Type: string (or Expression with resultType string).|cosmos_d_b_mongo_d_b_api_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|cosmos_d_b_mongo_d_b_api_connect_via|
|**--description**|string|Linked service description.|cosmos_d_b_mongo_d_b_api_description|
|**--parameters**|dictionary|Parameters for linked service.|cosmos_d_b_mongo_d_b_api_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cosmos_d_b_mongo_d_b_api_annotations|
### datafactory linked-service couchbase create

couchbase create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|couchbase_connect_via|
|**--description**|string|Linked service description.|couchbase_description|
|**--parameters**|dictionary|Parameters for linked service.|couchbase_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|couchbase_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|couchbase_connection_string|
|**--type-properties-cred-string**|object|The Azure key vault secret reference of credString in connection string.|couchbase_cred_string|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|couchbase_encrypted_credential|
### datafactory linked-service couchbase update

couchbase create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|couchbase_connect_via|
|**--description**|string|Linked service description.|couchbase_description|
|**--parameters**|dictionary|Parameters for linked service.|couchbase_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|couchbase_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|couchbase_connection_string|
|**--type-properties-cred-string**|object|The Azure key vault secret reference of credString in connection string.|couchbase_cred_string|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|couchbase_encrypted_credential|
### datafactory linked-service custom-data-source create

custom-data-source create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties**|any|Custom linked service properties.|custom_data_source_type_properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|custom_data_source_connect_via|
|**--description**|string|Linked service description.|custom_data_source_description|
|**--parameters**|dictionary|Parameters for linked service.|custom_data_source_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|custom_data_source_annotations|
### datafactory linked-service custom-data-source update

custom-data-source create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties**|any|Custom linked service properties.|custom_data_source_type_properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|custom_data_source_connect_via|
|**--description**|string|Linked service description.|custom_data_source_description|
|**--parameters**|dictionary|Parameters for linked service.|custom_data_source_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|custom_data_source_annotations|
### datafactory linked-service db2 create

db2 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|db2_connect_via|
|**--description**|string|Linked service description.|db2_description|
|**--parameters**|dictionary|Parameters for linked service.|db2_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|db2_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with server, database, authenticationType, userName, packageCollection and certificateCommonName property. Type: string, SecureString or AzureKeyVaultSecretReference.|db2_connection_string|
|**--type-properties-server**|any|Server name for connection. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_server|
|**--type-properties-database**|any|Database name for connection. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_database|
|**--type-properties-username**|any|Username for authentication. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_username|
|**--type-properties-password**|object|Password for authentication.|db2_password|
|**--type-properties-package-collection**|any|Under where packages are created when querying database. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_package_collection|
|**--type-properties-certificate-common-name**|any|Certificate Common Name when TLS is enabled. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_certificate_common_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_encrypted_credential|
### datafactory linked-service db2 update

db2 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|db2_connect_via|
|**--description**|string|Linked service description.|db2_description|
|**--parameters**|dictionary|Parameters for linked service.|db2_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|db2_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with server, database, authenticationType, userName, packageCollection and certificateCommonName property. Type: string, SecureString or AzureKeyVaultSecretReference.|db2_connection_string|
|**--type-properties-server**|any|Server name for connection. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_server|
|**--type-properties-database**|any|Database name for connection. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_database|
|**--type-properties-username**|any|Username for authentication. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_username|
|**--type-properties-password**|object|Password for authentication.|db2_password|
|**--type-properties-package-collection**|any|Under where packages are created when querying database. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_package_collection|
|**--type-properties-certificate-common-name**|any|Certificate Common Name when TLS is enabled. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_certificate_common_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_encrypted_credential|
### datafactory linked-service delete

delete a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
### datafactory linked-service drill create

drill create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|drill_connect_via|
|**--description**|string|Linked service description.|drill_description|
|**--parameters**|dictionary|Parameters for linked service.|drill_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|drill_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|drill_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|drill_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|drill_encrypted_credential|
### datafactory linked-service drill update

drill create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|drill_connect_via|
|**--description**|string|Linked service description.|drill_description|
|**--parameters**|dictionary|Parameters for linked service.|drill_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|drill_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|drill_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|drill_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|drill_encrypted_credential|
### datafactory linked-service dynamics create

dynamics create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-deployment-type**|choice|The deployment type of the Dynamics instance. 'Online' for Dynamics Online and 'OnPremisesWithIfd' for Dynamics on-premises with Ifd. Type: string (or Expression with resultType string).|dynamics_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Dynamics server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario, 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|dynamics_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamics_connect_via|
|**--description**|string|Linked service description.|dynamics_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamics_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamics_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Dynamics server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|dynamics_host_name|
|**--type-properties-port**|any|The port of on-premises Dynamics server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|dynamics_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Dynamics server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|dynamics_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Dynamics instance. The property is required for on-prem and required for online when there are more than one Dynamics instances associated with the user. Type: string (or Expression with resultType string).|dynamics_organization_name|
|**--type-properties-username**|any|User name to access the Dynamics instance. Type: string (or Expression with resultType string).|dynamics_username|
|**--type-properties-password**|object|Password to access the Dynamics instance.|dynamics_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|dynamics_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|dynamics_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|dynamics_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamics_encrypted_credential|
### datafactory linked-service dynamics update

dynamics create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-deployment-type**|choice|The deployment type of the Dynamics instance. 'Online' for Dynamics Online and 'OnPremisesWithIfd' for Dynamics on-premises with Ifd. Type: string (or Expression with resultType string).|dynamics_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Dynamics server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario, 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|dynamics_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamics_connect_via|
|**--description**|string|Linked service description.|dynamics_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamics_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamics_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Dynamics server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|dynamics_host_name|
|**--type-properties-port**|any|The port of on-premises Dynamics server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|dynamics_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Dynamics server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|dynamics_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Dynamics instance. The property is required for on-prem and required for online when there are more than one Dynamics instances associated with the user. Type: string (or Expression with resultType string).|dynamics_organization_name|
|**--type-properties-username**|any|User name to access the Dynamics instance. Type: string (or Expression with resultType string).|dynamics_username|
|**--type-properties-password**|object|Password to access the Dynamics instance.|dynamics_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|dynamics_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|dynamics_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|dynamics_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamics_encrypted_credential|
### datafactory linked-service dynamics-ax create

dynamics-ax create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The Dynamics AX (or Dynamics 365 Finance and Operations) instance OData endpoint.|dynamics_ax_url|
|**--type-properties-service-principal-id**|any|Specify the application's client ID. Type: string (or Expression with resultType string).|dynamics_ax_service_principal_id|
|**--type-properties-service-principal-key**|object|Specify the application's key. Mark this field as a SecureString to store it securely in Data Factory, or reference a secret stored in Azure Key Vault. Type: string (or Expression with resultType string).|dynamics_ax_service_principal_key|
|**--type-properties-tenant**|any|Specify the tenant information (domain name or tenant ID) under which your application resides. Retrieve it by hovering the mouse in the top-right corner of the Azure portal. Type: string (or Expression with resultType string).|dynamics_ax_tenant|
|**--type-properties-aad-resource-id**|any|Specify the resource you are requesting authorization. Type: string (or Expression with resultType string).|dynamics_ax_aad_resource_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamics_ax_connect_via|
|**--description**|string|Linked service description.|dynamics_ax_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamics_ax_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamics_ax_annotations|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamics_ax_encrypted_credential|
### datafactory linked-service dynamics-ax update

dynamics-ax create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The Dynamics AX (or Dynamics 365 Finance and Operations) instance OData endpoint.|dynamics_ax_url|
|**--type-properties-service-principal-id**|any|Specify the application's client ID. Type: string (or Expression with resultType string).|dynamics_ax_service_principal_id|
|**--type-properties-service-principal-key**|object|Specify the application's key. Mark this field as a SecureString to store it securely in Data Factory, or reference a secret stored in Azure Key Vault. Type: string (or Expression with resultType string).|dynamics_ax_service_principal_key|
|**--type-properties-tenant**|any|Specify the tenant information (domain name or tenant ID) under which your application resides. Retrieve it by hovering the mouse in the top-right corner of the Azure portal. Type: string (or Expression with resultType string).|dynamics_ax_tenant|
|**--type-properties-aad-resource-id**|any|Specify the resource you are requesting authorization. Type: string (or Expression with resultType string).|dynamics_ax_aad_resource_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamics_ax_connect_via|
|**--description**|string|Linked service description.|dynamics_ax_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamics_ax_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamics_ax_annotations|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamics_ax_encrypted_credential|
### datafactory linked-service dynamics-crm create

dynamics-crm create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-deployment-type**|choice|The deployment type of the Dynamics CRM instance. 'Online' for Dynamics CRM Online and 'OnPremisesWithIfd' for Dynamics CRM on-premises with Ifd. Type: string (or Expression with resultType string).|dynamics_crm_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Dynamics CRM server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario, 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|dynamics_crm_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamics_crm_connect_via|
|**--description**|string|Linked service description.|dynamics_crm_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamics_crm_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamics_crm_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Dynamics CRM server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|dynamics_crm_host_name|
|**--type-properties-port**|any|The port of on-premises Dynamics CRM server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|dynamics_crm_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Dynamics CRM server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|dynamics_crm_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Dynamics CRM instance. The property is required for on-prem and required for online when there are more than one Dynamics CRM instances associated with the user. Type: string (or Expression with resultType string).|dynamics_crm_organization_name|
|**--type-properties-username**|any|User name to access the Dynamics CRM instance. Type: string (or Expression with resultType string).|dynamics_crm_username|
|**--type-properties-password**|object|Password to access the Dynamics CRM instance.|dynamics_crm_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|dynamics_crm_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|dynamics_crm_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|dynamics_crm_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamics_crm_encrypted_credential|
### datafactory linked-service dynamics-crm update

dynamics-crm create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-deployment-type**|choice|The deployment type of the Dynamics CRM instance. 'Online' for Dynamics CRM Online and 'OnPremisesWithIfd' for Dynamics CRM on-premises with Ifd. Type: string (or Expression with resultType string).|dynamics_crm_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Dynamics CRM server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario, 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|dynamics_crm_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamics_crm_connect_via|
|**--description**|string|Linked service description.|dynamics_crm_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamics_crm_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamics_crm_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Dynamics CRM server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|dynamics_crm_host_name|
|**--type-properties-port**|any|The port of on-premises Dynamics CRM server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|dynamics_crm_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Dynamics CRM server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|dynamics_crm_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Dynamics CRM instance. The property is required for on-prem and required for online when there are more than one Dynamics CRM instances associated with the user. Type: string (or Expression with resultType string).|dynamics_crm_organization_name|
|**--type-properties-username**|any|User name to access the Dynamics CRM instance. Type: string (or Expression with resultType string).|dynamics_crm_username|
|**--type-properties-password**|object|Password to access the Dynamics CRM instance.|dynamics_crm_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|dynamics_crm_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|dynamics_crm_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|dynamics_crm_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamics_crm_encrypted_credential|
### datafactory linked-service eloqua create

eloqua create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the Eloqua server. (i.e. eloqua.example.com)|eloqua_endpoint|
|**--type-properties-username**|any|The site name and user name of your Eloqua account in the form: sitename/username. (i.e. Eloqua/Alice)|eloqua_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|eloqua_connect_via|
|**--description**|string|Linked service description.|eloqua_description|
|**--parameters**|dictionary|Parameters for linked service.|eloqua_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|eloqua_annotations|
|**--type-properties-password**|object|The password corresponding to the user name.|eloqua_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|eloqua_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|eloqua_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|eloqua_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|eloqua_encrypted_credential|
### datafactory linked-service eloqua update

eloqua create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the Eloqua server. (i.e. eloqua.example.com)|eloqua_endpoint|
|**--type-properties-username**|any|The site name and user name of your Eloqua account in the form: sitename/username. (i.e. Eloqua/Alice)|eloqua_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|eloqua_connect_via|
|**--description**|string|Linked service description.|eloqua_description|
|**--parameters**|dictionary|Parameters for linked service.|eloqua_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|eloqua_annotations|
|**--type-properties-password**|object|The password corresponding to the user name.|eloqua_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|eloqua_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|eloqua_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|eloqua_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|eloqua_encrypted_credential|
### datafactory linked-service file-server create

file-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|Host name of the server. Type: string (or Expression with resultType string).|file_server_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|file_server_connect_via|
|**--description**|string|Linked service description.|file_server_description|
|**--parameters**|dictionary|Parameters for linked service.|file_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|file_server_annotations|
|**--type-properties-user-id**|any|User ID to logon the server. Type: string (or Expression with resultType string).|file_server_user_id|
|**--type-properties-password**|object|Password to logon the server.|file_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|file_server_encrypted_credential|
### datafactory linked-service file-server update

file-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|Host name of the server. Type: string (or Expression with resultType string).|file_server_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|file_server_connect_via|
|**--description**|string|Linked service description.|file_server_description|
|**--parameters**|dictionary|Parameters for linked service.|file_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|file_server_annotations|
|**--type-properties-user-id**|any|User ID to logon the server. Type: string (or Expression with resultType string).|file_server_user_id|
|**--type-properties-password**|object|Password to logon the server.|file_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|file_server_encrypted_credential|
### datafactory linked-service ftp-server create

ftp-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|Host name of the FTP server. Type: string (or Expression with resultType string).|ftp_server_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|ftp_server_connect_via|
|**--description**|string|Linked service description.|ftp_server_description|
|**--parameters**|dictionary|Parameters for linked service.|ftp_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|ftp_server_annotations|
|**--type-properties-port**|any|The TCP port number that the FTP server uses to listen for client connections. Default value is 21. Type: integer (or Expression with resultType integer), minimum: 0.|ftp_server_port|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the FTP server.|ftp_server_authentication_type|
|**--type-properties-user-name**|any|Username to logon the FTP server. Type: string (or Expression with resultType string).|ftp_server_user_name|
|**--type-properties-password**|object|Password to logon the FTP server.|ftp_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|ftp_server_encrypted_credential|
|**--type-properties-enable-ssl**|any|If true, connect to the FTP server over SSL/TLS channel. Default value is true. Type: boolean (or Expression with resultType boolean).|ftp_server_enable_ssl|
|**--type-properties-enable-server-certificate-validation**|any|If true, validate the FTP server SSL certificate when connect over SSL/TLS channel. Default value is true. Type: boolean (or Expression with resultType boolean).|ftp_server_enable_server_certificate_validation|
### datafactory linked-service ftp-server update

ftp-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|Host name of the FTP server. Type: string (or Expression with resultType string).|ftp_server_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|ftp_server_connect_via|
|**--description**|string|Linked service description.|ftp_server_description|
|**--parameters**|dictionary|Parameters for linked service.|ftp_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|ftp_server_annotations|
|**--type-properties-port**|any|The TCP port number that the FTP server uses to listen for client connections. Default value is 21. Type: integer (or Expression with resultType integer), minimum: 0.|ftp_server_port|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the FTP server.|ftp_server_authentication_type|
|**--type-properties-user-name**|any|Username to logon the FTP server. Type: string (or Expression with resultType string).|ftp_server_user_name|
|**--type-properties-password**|object|Password to logon the FTP server.|ftp_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|ftp_server_encrypted_credential|
|**--type-properties-enable-ssl**|any|If true, connect to the FTP server over SSL/TLS channel. Default value is true. Type: boolean (or Expression with resultType boolean).|ftp_server_enable_ssl|
|**--type-properties-enable-server-certificate-validation**|any|If true, validate the FTP server SSL certificate when connect over SSL/TLS channel. Default value is true. Type: boolean (or Expression with resultType boolean).|ftp_server_enable_server_certificate_validation|
### datafactory linked-service google-ad-words create

google-ad-words create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-client-customer-id**|any|The Client customer ID of the AdWords account that you want to fetch report data for.|google_ad_words_client_customer_id|
|**--type-properties-developer-token**|object|The developer token associated with the manager account that you use to grant access to the AdWords API.|google_ad_words_developer_token|
|**--type-properties-authentication-type**|choice|The OAuth 2.0 authentication mechanism used for authentication. ServiceAuthentication can only be used on self-hosted IR.|google_ad_words_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|google_ad_words_connect_via|
|**--description**|string|Linked service description.|google_ad_words_description|
|**--parameters**|dictionary|Parameters for linked service.|google_ad_words_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|google_ad_words_annotations|
|**--type-properties-refresh-token**|object|The refresh token obtained from Google for authorizing access to AdWords for UserAuthentication.|google_ad_words_refresh_token|
|**--type-properties-client-id**|any|The client id of the google application used to acquire the refresh token. Type: string (or Expression with resultType string).|google_ad_words_client_id|
|**--type-properties-client-secret**|object|The client secret of the google application used to acquire the refresh token.|google_ad_words_client_secret|
|**--type-properties-email**|any|The service account email ID that is used for ServiceAuthentication and can only be used on self-hosted IR.|google_ad_words_email|
|**--type-properties-key-file-path**|any|The full path to the .p12 key file that is used to authenticate the service account email address and can only be used on self-hosted IR.|google_ad_words_key_file_path|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|google_ad_words_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|google_ad_words_use_system_trust_store|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|google_ad_words_encrypted_credential|
### datafactory linked-service google-ad-words update

google-ad-words create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-client-customer-id**|any|The Client customer ID of the AdWords account that you want to fetch report data for.|google_ad_words_client_customer_id|
|**--type-properties-developer-token**|object|The developer token associated with the manager account that you use to grant access to the AdWords API.|google_ad_words_developer_token|
|**--type-properties-authentication-type**|choice|The OAuth 2.0 authentication mechanism used for authentication. ServiceAuthentication can only be used on self-hosted IR.|google_ad_words_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|google_ad_words_connect_via|
|**--description**|string|Linked service description.|google_ad_words_description|
|**--parameters**|dictionary|Parameters for linked service.|google_ad_words_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|google_ad_words_annotations|
|**--type-properties-refresh-token**|object|The refresh token obtained from Google for authorizing access to AdWords for UserAuthentication.|google_ad_words_refresh_token|
|**--type-properties-client-id**|any|The client id of the google application used to acquire the refresh token. Type: string (or Expression with resultType string).|google_ad_words_client_id|
|**--type-properties-client-secret**|object|The client secret of the google application used to acquire the refresh token.|google_ad_words_client_secret|
|**--type-properties-email**|any|The service account email ID that is used for ServiceAuthentication and can only be used on self-hosted IR.|google_ad_words_email|
|**--type-properties-key-file-path**|any|The full path to the .p12 key file that is used to authenticate the service account email address and can only be used on self-hosted IR.|google_ad_words_key_file_path|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|google_ad_words_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|google_ad_words_use_system_trust_store|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|google_ad_words_encrypted_credential|
### datafactory linked-service google-big-query create

google-big-query create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-project**|any|The default BigQuery project to query against.|google_big_query_project|
|**--type-properties-authentication-type**|choice|The OAuth 2.0 authentication mechanism used for authentication. ServiceAuthentication can only be used on self-hosted IR.|google_big_query_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|google_big_query_connect_via|
|**--description**|string|Linked service description.|google_big_query_description|
|**--parameters**|dictionary|Parameters for linked service.|google_big_query_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|google_big_query_annotations|
|**--type-properties-additional-projects**|any|A comma-separated list of public BigQuery projects to access.|google_big_query_additional_projects|
|**--type-properties-request-google-drive-scope**|any|Whether to request access to Google Drive. Allowing Google Drive access enables support for federated tables that combine BigQuery data with data from Google Drive. The default value is false.|google_big_query_request_google_drive_scope|
|**--type-properties-refresh-token**|object|The refresh token obtained from Google for authorizing access to BigQuery for UserAuthentication.|google_big_query_refresh_token|
|**--type-properties-client-id**|any|The client id of the google application used to acquire the refresh token. Type: string (or Expression with resultType string).|google_big_query_client_id|
|**--type-properties-client-secret**|object|The client secret of the google application used to acquire the refresh token.|google_big_query_client_secret|
|**--type-properties-email**|any|The service account email ID that is used for ServiceAuthentication and can only be used on self-hosted IR.|google_big_query_email|
|**--type-properties-key-file-path**|any|The full path to the .p12 key file that is used to authenticate the service account email address and can only be used on self-hosted IR.|google_big_query_key_file_path|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|google_big_query_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|google_big_query_use_system_trust_store|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|google_big_query_encrypted_credential|
### datafactory linked-service google-big-query update

google-big-query create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-project**|any|The default BigQuery project to query against.|google_big_query_project|
|**--type-properties-authentication-type**|choice|The OAuth 2.0 authentication mechanism used for authentication. ServiceAuthentication can only be used on self-hosted IR.|google_big_query_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|google_big_query_connect_via|
|**--description**|string|Linked service description.|google_big_query_description|
|**--parameters**|dictionary|Parameters for linked service.|google_big_query_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|google_big_query_annotations|
|**--type-properties-additional-projects**|any|A comma-separated list of public BigQuery projects to access.|google_big_query_additional_projects|
|**--type-properties-request-google-drive-scope**|any|Whether to request access to Google Drive. Allowing Google Drive access enables support for federated tables that combine BigQuery data with data from Google Drive. The default value is false.|google_big_query_request_google_drive_scope|
|**--type-properties-refresh-token**|object|The refresh token obtained from Google for authorizing access to BigQuery for UserAuthentication.|google_big_query_refresh_token|
|**--type-properties-client-id**|any|The client id of the google application used to acquire the refresh token. Type: string (or Expression with resultType string).|google_big_query_client_id|
|**--type-properties-client-secret**|object|The client secret of the google application used to acquire the refresh token.|google_big_query_client_secret|
|**--type-properties-email**|any|The service account email ID that is used for ServiceAuthentication and can only be used on self-hosted IR.|google_big_query_email|
|**--type-properties-key-file-path**|any|The full path to the .p12 key file that is used to authenticate the service account email address and can only be used on self-hosted IR.|google_big_query_key_file_path|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|google_big_query_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|google_big_query_use_system_trust_store|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|google_big_query_encrypted_credential|
### datafactory linked-service google-cloud-storage create

google-cloud-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|google_cloud_storage_connect_via|
|**--description**|string|Linked service description.|google_cloud_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|google_cloud_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|google_cloud_storage_annotations|
|**--type-properties-access-key-id**|any|The access key identifier of the Google Cloud Storage Identity and Access Management (IAM) user. Type: string (or Expression with resultType string).|google_cloud_storage_access_key_id|
|**--type-properties-secret-access-key**|object|The secret access key of the Google Cloud Storage Identity and Access Management (IAM) user.|google_cloud_storage_secret_access_key|
|**--type-properties-service-url**|any|This value specifies the endpoint to access with the Google Cloud Storage Connector. This is an optional property; change it only if you want to try a different service endpoint or want to switch between https and http. Type: string (or Expression with resultType string).|google_cloud_storage_service_url|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|google_cloud_storage_encrypted_credential|
### datafactory linked-service google-cloud-storage update

google-cloud-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|google_cloud_storage_connect_via|
|**--description**|string|Linked service description.|google_cloud_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|google_cloud_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|google_cloud_storage_annotations|
|**--type-properties-access-key-id**|any|The access key identifier of the Google Cloud Storage Identity and Access Management (IAM) user. Type: string (or Expression with resultType string).|google_cloud_storage_access_key_id|
|**--type-properties-secret-access-key**|object|The secret access key of the Google Cloud Storage Identity and Access Management (IAM) user.|google_cloud_storage_secret_access_key|
|**--type-properties-service-url**|any|This value specifies the endpoint to access with the Google Cloud Storage Connector. This is an optional property; change it only if you want to try a different service endpoint or want to switch between https and http. Type: string (or Expression with resultType string).|google_cloud_storage_service_url|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|google_cloud_storage_encrypted_credential|
### datafactory linked-service greenplum create

greenplum create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|greenplum_connect_via|
|**--description**|string|Linked service description.|greenplum_description|
|**--parameters**|dictionary|Parameters for linked service.|greenplum_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|greenplum_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|greenplum_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|greenplum_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|greenplum_encrypted_credential|
### datafactory linked-service greenplum update

greenplum create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|greenplum_connect_via|
|**--description**|string|Linked service description.|greenplum_description|
|**--parameters**|dictionary|Parameters for linked service.|greenplum_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|greenplum_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|greenplum_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|greenplum_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|greenplum_encrypted_credential|
### datafactory linked-service h-base create

h-base create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The IP address or host name of the HBase server. (i.e. 192.168.222.160)|h_base_host|
|**--type-properties-authentication-type**|choice|The authentication mechanism to use to connect to the HBase server.|h_base_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|h_base_connect_via|
|**--description**|string|Linked service description.|h_base_description|
|**--parameters**|dictionary|Parameters for linked service.|h_base_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|h_base_annotations|
|**--type-properties-port**|any|The TCP port that the HBase instance uses to listen for client connections. The default value is 9090.|h_base_port|
|**--type-properties-http-path**|any|The partial URL corresponding to the HBase server. (i.e. /gateway/sandbox/hbase/version)|h_base_http_path|
|**--type-properties-username**|any|The user name used to connect to the HBase instance.|h_base_username|
|**--type-properties-password**|object|The password corresponding to the user name.|h_base_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|h_base_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|h_base_trusted_cert_path|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|h_base_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|h_base_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|h_base_encrypted_credential|
### datafactory linked-service h-base update

h-base create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The IP address or host name of the HBase server. (i.e. 192.168.222.160)|h_base_host|
|**--type-properties-authentication-type**|choice|The authentication mechanism to use to connect to the HBase server.|h_base_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|h_base_connect_via|
|**--description**|string|Linked service description.|h_base_description|
|**--parameters**|dictionary|Parameters for linked service.|h_base_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|h_base_annotations|
|**--type-properties-port**|any|The TCP port that the HBase instance uses to listen for client connections. The default value is 9090.|h_base_port|
|**--type-properties-http-path**|any|The partial URL corresponding to the HBase server. (i.e. /gateway/sandbox/hbase/version)|h_base_http_path|
|**--type-properties-username**|any|The user name used to connect to the HBase instance.|h_base_username|
|**--type-properties-password**|object|The password corresponding to the user name.|h_base_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|h_base_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|h_base_trusted_cert_path|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|h_base_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|h_base_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|h_base_encrypted_credential|
### datafactory linked-service hd-insight create

hd-insight create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-cluster-uri**|any|HDInsight cluster URI. Type: string (or Expression with resultType string).|hd_insight_cluster_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|hd_insight_connect_via|
|**--description**|string|Linked service description.|hd_insight_description|
|**--parameters**|dictionary|Parameters for linked service.|hd_insight_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hd_insight_annotations|
|**--type-properties-user-name**|any|HDInsight cluster user name. Type: string (or Expression with resultType string).|hd_insight_user_name|
|**--type-properties-password**|object|HDInsight cluster password.|hd_insight_password|
|**--type-properties-linked-service-name**|object|The Azure Storage linked service reference.|hd_insight_linked_service_name|
|**--type-properties-hcatalog-linked-service-name**|object|A reference to the Azure SQL linked service that points to the HCatalog database.|hd_insight_hcatalog_linked_service_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hd_insight_encrypted_credential|
|**--type-properties-is-esp-enabled**|any|Specify if the HDInsight is created with ESP (Enterprise Security Package). Type: Boolean.|hd_insight_is_esp_enabled|
|**--type-properties-file-system**|any|Specify the FileSystem if the main storage for the HDInsight is ADLS Gen2. Type: string (or Expression with resultType string).|hd_insight_file_system|
### datafactory linked-service hd-insight update

hd-insight create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-cluster-uri**|any|HDInsight cluster URI. Type: string (or Expression with resultType string).|hd_insight_cluster_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|hd_insight_connect_via|
|**--description**|string|Linked service description.|hd_insight_description|
|**--parameters**|dictionary|Parameters for linked service.|hd_insight_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hd_insight_annotations|
|**--type-properties-user-name**|any|HDInsight cluster user name. Type: string (or Expression with resultType string).|hd_insight_user_name|
|**--type-properties-password**|object|HDInsight cluster password.|hd_insight_password|
|**--type-properties-linked-service-name**|object|The Azure Storage linked service reference.|hd_insight_linked_service_name|
|**--type-properties-hcatalog-linked-service-name**|object|A reference to the Azure SQL linked service that points to the HCatalog database.|hd_insight_hcatalog_linked_service_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hd_insight_encrypted_credential|
|**--type-properties-is-esp-enabled**|any|Specify if the HDInsight is created with ESP (Enterprise Security Package). Type: Boolean.|hd_insight_is_esp_enabled|
|**--type-properties-file-system**|any|Specify the FileSystem if the main storage for the HDInsight is ADLS Gen2. Type: string (or Expression with resultType string).|hd_insight_file_system|
### datafactory linked-service hd-insight-on-demand create

hd-insight-on-demand create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-cluster-size**|any|Number of worker/data nodes in the cluster. Suggestion value: 4. Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_size|
|**--type-properties-time-to-live**|any|The allowed idle time for the on-demand HDInsight cluster. Specifies how long the on-demand HDInsight cluster stays alive after completion of an activity run if there are no other active jobs in the cluster. The minimum value is 5 mins. Type: string (or Expression with resultType string).|hd_insight_on_demand_time_to_live|
|**--type-properties-version**|any|Version of the HDInsight cluster.  Type: string (or Expression with resultType string).|hd_insight_on_demand_version|
|**--type-properties-linked-service-name**|object|Azure Storage linked service to be used by the on-demand cluster for storing and processing data.|hd_insight_on_demand_linked_service_name|
|**--type-properties-host-subscription-id**|any|The customer’s subscription to host the cluster. Type: string (or Expression with resultType string).|hd_insight_on_demand_host_subscription_id|
|**--type-properties-tenant**|any|The Tenant id/name to which the service principal belongs. Type: string (or Expression with resultType string).|hd_insight_on_demand_tenant|
|**--type-properties-cluster-resource-group**|any|The resource group where the cluster belongs. Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_resource_group|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|hd_insight_on_demand_connect_via|
|**--description**|string|Linked service description.|hd_insight_on_demand_description|
|**--parameters**|dictionary|Parameters for linked service.|hd_insight_on_demand_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hd_insight_on_demand_annotations|
|**--type-properties-service-principal-id**|any|The service principal id for the hostSubscriptionId. Type: string (or Expression with resultType string).|hd_insight_on_demand_service_principal_id|
|**--type-properties-service-principal-key**|object|The key for the service principal id.|hd_insight_on_demand_service_principal_key|
|**--type-properties-cluster-name-prefix**|any|The prefix of cluster name, postfix will be distinct with timestamp. Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_name_prefix|
|**--type-properties-cluster-user-name**|any|The username to access the cluster. Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_user_name|
|**--type-properties-cluster-password**|object|The password to access the cluster.|hd_insight_on_demand_cluster_password|
|**--type-properties-cluster-ssh-user-name**|any|The username to SSH remotely connect to cluster’s node (for Linux). Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_ssh_user_name|
|**--type-properties-cluster-ssh-password**|object|The password to SSH remotely connect cluster’s node (for Linux).|hd_insight_on_demand_cluster_ssh_password|
|**--type-properties-additional-linked-service-names**|array|Specifies additional storage accounts for the HDInsight linked service so that the Data Factory service can register them on your behalf.|hd_insight_on_demand_additional_linked_service_names|
|**--type-properties-hcatalog-linked-service-name**|object|The name of Azure SQL linked service that point to the HCatalog database. The on-demand HDInsight cluster is created by using the Azure SQL database as the metastore.|hd_insight_on_demand_hcatalog_linked_service_name|
|**--type-properties-cluster-type**|any|The cluster type. Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_type|
|**--type-properties-spark-version**|any|The version of spark if the cluster type is 'spark'. Type: string (or Expression with resultType string).|hd_insight_on_demand_spark_version|
|**--type-properties-core-configuration**|any|Specifies the core configuration parameters (as in core-site.xml) for the HDInsight cluster to be created.|hd_insight_on_demand_core_configuration|
|**--type-properties-h-base-configuration**|any|Specifies the HBase configuration parameters (hbase-site.xml) for the HDInsight cluster.|hd_insight_on_demand_h_base_configuration|
|**--type-properties-hdfs-configuration**|any|Specifies the HDFS configuration parameters (hdfs-site.xml) for the HDInsight cluster.|hd_insight_on_demand_hdfs_configuration|
|**--type-properties-hive-configuration**|any|Specifies the hive configuration parameters (hive-site.xml) for the HDInsight cluster.|hd_insight_on_demand_hive_configuration|
|**--type-properties-map-reduce-configuration**|any|Specifies the MapReduce configuration parameters (mapred-site.xml) for the HDInsight cluster.|hd_insight_on_demand_map_reduce_configuration|
|**--type-properties-oozie-configuration**|any|Specifies the Oozie configuration parameters (oozie-site.xml) for the HDInsight cluster.|hd_insight_on_demand_oozie_configuration|
|**--type-properties-storm-configuration**|any|Specifies the Storm configuration parameters (storm-site.xml) for the HDInsight cluster.|hd_insight_on_demand_storm_configuration|
|**--type-properties-yarn-configuration**|any|Specifies the Yarn configuration parameters (yarn-site.xml) for the HDInsight cluster.|hd_insight_on_demand_yarn_configuration|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hd_insight_on_demand_encrypted_credential|
|**--type-properties-head-node-size**|any|Specifies the size of the head node for the HDInsight cluster.|hd_insight_on_demand_head_node_size|
|**--type-properties-data-node-size**|any|Specifies the size of the data node for the HDInsight cluster.|hd_insight_on_demand_data_node_size|
|**--type-properties-zookeeper-node-size**|any|Specifies the size of the Zoo Keeper node for the HDInsight cluster.|hd_insight_on_demand_zookeeper_node_size|
|**--type-properties-script-actions**|array|Custom script actions to run on HDI ondemand cluster once it's up. Please refer to https://docs.microsoft.com/en-us/azure/hdinsight/hdinsight-hadoop-customize-cluster-linux?toc=%2Fen-us%2Fazure%2Fhdinsight%2Fr-server%2FTOC.json&bc=%2Fen-us%2Fazure%2Fbread%2Ftoc.json#understanding-script-actions.|hd_insight_on_demand_script_actions|
|**--type-properties-virtual-network-id**|any|The ARM resource ID for the vNet to which the cluster should be joined after creation. Type: string (or Expression with resultType string).|hd_insight_on_demand_virtual_network_id|
|**--type-properties-subnet-name**|any|The ARM resource ID for the subnet in the vNet. If virtualNetworkId was specified, then this property is required. Type: string (or Expression with resultType string).|hd_insight_on_demand_subnet_name|
### datafactory linked-service hd-insight-on-demand update

hd-insight-on-demand create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-cluster-size**|any|Number of worker/data nodes in the cluster. Suggestion value: 4. Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_size|
|**--type-properties-time-to-live**|any|The allowed idle time for the on-demand HDInsight cluster. Specifies how long the on-demand HDInsight cluster stays alive after completion of an activity run if there are no other active jobs in the cluster. The minimum value is 5 mins. Type: string (or Expression with resultType string).|hd_insight_on_demand_time_to_live|
|**--type-properties-version**|any|Version of the HDInsight cluster.  Type: string (or Expression with resultType string).|hd_insight_on_demand_version|
|**--type-properties-linked-service-name**|object|Azure Storage linked service to be used by the on-demand cluster for storing and processing data.|hd_insight_on_demand_linked_service_name|
|**--type-properties-host-subscription-id**|any|The customer’s subscription to host the cluster. Type: string (or Expression with resultType string).|hd_insight_on_demand_host_subscription_id|
|**--type-properties-tenant**|any|The Tenant id/name to which the service principal belongs. Type: string (or Expression with resultType string).|hd_insight_on_demand_tenant|
|**--type-properties-cluster-resource-group**|any|The resource group where the cluster belongs. Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_resource_group|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|hd_insight_on_demand_connect_via|
|**--description**|string|Linked service description.|hd_insight_on_demand_description|
|**--parameters**|dictionary|Parameters for linked service.|hd_insight_on_demand_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hd_insight_on_demand_annotations|
|**--type-properties-service-principal-id**|any|The service principal id for the hostSubscriptionId. Type: string (or Expression with resultType string).|hd_insight_on_demand_service_principal_id|
|**--type-properties-service-principal-key**|object|The key for the service principal id.|hd_insight_on_demand_service_principal_key|
|**--type-properties-cluster-name-prefix**|any|The prefix of cluster name, postfix will be distinct with timestamp. Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_name_prefix|
|**--type-properties-cluster-user-name**|any|The username to access the cluster. Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_user_name|
|**--type-properties-cluster-password**|object|The password to access the cluster.|hd_insight_on_demand_cluster_password|
|**--type-properties-cluster-ssh-user-name**|any|The username to SSH remotely connect to cluster’s node (for Linux). Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_ssh_user_name|
|**--type-properties-cluster-ssh-password**|object|The password to SSH remotely connect cluster’s node (for Linux).|hd_insight_on_demand_cluster_ssh_password|
|**--type-properties-additional-linked-service-names**|array|Specifies additional storage accounts for the HDInsight linked service so that the Data Factory service can register them on your behalf.|hd_insight_on_demand_additional_linked_service_names|
|**--type-properties-hcatalog-linked-service-name**|object|The name of Azure SQL linked service that point to the HCatalog database. The on-demand HDInsight cluster is created by using the Azure SQL database as the metastore.|hd_insight_on_demand_hcatalog_linked_service_name|
|**--type-properties-cluster-type**|any|The cluster type. Type: string (or Expression with resultType string).|hd_insight_on_demand_cluster_type|
|**--type-properties-spark-version**|any|The version of spark if the cluster type is 'spark'. Type: string (or Expression with resultType string).|hd_insight_on_demand_spark_version|
|**--type-properties-core-configuration**|any|Specifies the core configuration parameters (as in core-site.xml) for the HDInsight cluster to be created.|hd_insight_on_demand_core_configuration|
|**--type-properties-h-base-configuration**|any|Specifies the HBase configuration parameters (hbase-site.xml) for the HDInsight cluster.|hd_insight_on_demand_h_base_configuration|
|**--type-properties-hdfs-configuration**|any|Specifies the HDFS configuration parameters (hdfs-site.xml) for the HDInsight cluster.|hd_insight_on_demand_hdfs_configuration|
|**--type-properties-hive-configuration**|any|Specifies the hive configuration parameters (hive-site.xml) for the HDInsight cluster.|hd_insight_on_demand_hive_configuration|
|**--type-properties-map-reduce-configuration**|any|Specifies the MapReduce configuration parameters (mapred-site.xml) for the HDInsight cluster.|hd_insight_on_demand_map_reduce_configuration|
|**--type-properties-oozie-configuration**|any|Specifies the Oozie configuration parameters (oozie-site.xml) for the HDInsight cluster.|hd_insight_on_demand_oozie_configuration|
|**--type-properties-storm-configuration**|any|Specifies the Storm configuration parameters (storm-site.xml) for the HDInsight cluster.|hd_insight_on_demand_storm_configuration|
|**--type-properties-yarn-configuration**|any|Specifies the Yarn configuration parameters (yarn-site.xml) for the HDInsight cluster.|hd_insight_on_demand_yarn_configuration|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hd_insight_on_demand_encrypted_credential|
|**--type-properties-head-node-size**|any|Specifies the size of the head node for the HDInsight cluster.|hd_insight_on_demand_head_node_size|
|**--type-properties-data-node-size**|any|Specifies the size of the data node for the HDInsight cluster.|hd_insight_on_demand_data_node_size|
|**--type-properties-zookeeper-node-size**|any|Specifies the size of the Zoo Keeper node for the HDInsight cluster.|hd_insight_on_demand_zookeeper_node_size|
|**--type-properties-script-actions**|array|Custom script actions to run on HDI ondemand cluster once it's up. Please refer to https://docs.microsoft.com/en-us/azure/hdinsight/hdinsight-hadoop-customize-cluster-linux?toc=%2Fen-us%2Fazure%2Fhdinsight%2Fr-server%2FTOC.json&bc=%2Fen-us%2Fazure%2Fbread%2Ftoc.json#understanding-script-actions.|hd_insight_on_demand_script_actions|
|**--type-properties-virtual-network-id**|any|The ARM resource ID for the vNet to which the cluster should be joined after creation. Type: string (or Expression with resultType string).|hd_insight_on_demand_virtual_network_id|
|**--type-properties-subnet-name**|any|The ARM resource ID for the subnet in the vNet. If virtualNetworkId was specified, then this property is required. Type: string (or Expression with resultType string).|hd_insight_on_demand_subnet_name|
### datafactory linked-service hdfs create

hdfs create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The URL of the HDFS service endpoint, e.g. http://myhostname:50070/webhdfs/v1 . Type: string (or Expression with resultType string).|hdfs_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|hdfs_connect_via|
|**--description**|string|Linked service description.|hdfs_description|
|**--parameters**|dictionary|Parameters for linked service.|hdfs_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hdfs_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the HDFS. Possible values are: Anonymous and Windows. Type: string (or Expression with resultType string).|hdfs_authentication_type|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hdfs_encrypted_credential|
|**--type-properties-user-name**|any|User name for Windows authentication. Type: string (or Expression with resultType string).|hdfs_user_name|
|**--type-properties-password**|object|Password for Windows authentication.|hdfs_password|
### datafactory linked-service hdfs update

hdfs create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The URL of the HDFS service endpoint, e.g. http://myhostname:50070/webhdfs/v1 . Type: string (or Expression with resultType string).|hdfs_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|hdfs_connect_via|
|**--description**|string|Linked service description.|hdfs_description|
|**--parameters**|dictionary|Parameters for linked service.|hdfs_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hdfs_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the HDFS. Possible values are: Anonymous and Windows. Type: string (or Expression with resultType string).|hdfs_authentication_type|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hdfs_encrypted_credential|
|**--type-properties-user-name**|any|User name for Windows authentication. Type: string (or Expression with resultType string).|hdfs_user_name|
|**--type-properties-password**|object|Password for Windows authentication.|hdfs_password|
### datafactory linked-service hive create

hive create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|IP address or host name of the Hive server, separated by ';' for multiple hosts (only when serviceDiscoveryMode is enable).|hive_host|
|**--type-properties-authentication-type**|choice|The authentication method used to access the Hive server.|hive_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|hive_connect_via|
|**--description**|string|Linked service description.|hive_description|
|**--parameters**|dictionary|Parameters for linked service.|hive_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hive_annotations|
|**--type-properties-port**|any|The TCP port that the Hive server uses to listen for client connections.|hive_port|
|**--type-properties-server-type**|choice|The type of Hive server.|hive_server_type|
|**--type-properties-thrift-transport-protocol**|choice|The transport protocol to use in the Thrift layer.|hive_thrift_transport_protocol|
|**--type-properties-service-discovery-mode**|any|true to indicate using the ZooKeeper service, false not.|hive_service_discovery_mode|
|**--type-properties-zoo-keeper-name-space**|any|The namespace on ZooKeeper under which Hive Server 2 nodes are added.|hive_zoo_keeper_name_space|
|**--type-properties-use-native-query**|any|Specifies whether the driver uses native HiveQL queries,or converts them into an equivalent form in HiveQL.|hive_use_native_query|
|**--type-properties-username**|any|The user name that you use to access Hive Server.|hive_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the Username field|hive_password|
|**--type-properties-http-path**|any|The partial URL corresponding to the Hive server.|hive_http_path|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|hive_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|hive_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|hive_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|hive_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|hive_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hive_encrypted_credential|
### datafactory linked-service hive update

hive create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|IP address or host name of the Hive server, separated by ';' for multiple hosts (only when serviceDiscoveryMode is enable).|hive_host|
|**--type-properties-authentication-type**|choice|The authentication method used to access the Hive server.|hive_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|hive_connect_via|
|**--description**|string|Linked service description.|hive_description|
|**--parameters**|dictionary|Parameters for linked service.|hive_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hive_annotations|
|**--type-properties-port**|any|The TCP port that the Hive server uses to listen for client connections.|hive_port|
|**--type-properties-server-type**|choice|The type of Hive server.|hive_server_type|
|**--type-properties-thrift-transport-protocol**|choice|The transport protocol to use in the Thrift layer.|hive_thrift_transport_protocol|
|**--type-properties-service-discovery-mode**|any|true to indicate using the ZooKeeper service, false not.|hive_service_discovery_mode|
|**--type-properties-zoo-keeper-name-space**|any|The namespace on ZooKeeper under which Hive Server 2 nodes are added.|hive_zoo_keeper_name_space|
|**--type-properties-use-native-query**|any|Specifies whether the driver uses native HiveQL queries,or converts them into an equivalent form in HiveQL.|hive_use_native_query|
|**--type-properties-username**|any|The user name that you use to access Hive Server.|hive_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the Username field|hive_password|
|**--type-properties-http-path**|any|The partial URL corresponding to the Hive server.|hive_http_path|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|hive_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|hive_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|hive_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|hive_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|hive_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hive_encrypted_credential|
### datafactory linked-service http-server create

http-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The base URL of the HTTP endpoint, e.g. http://www.microsoft.com. Type: string (or Expression with resultType string).|http_server_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|http_server_connect_via|
|**--description**|string|Linked service description.|http_server_description|
|**--parameters**|dictionary|Parameters for linked service.|http_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|http_server_annotations|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the HTTP server.|http_server_authentication_type|
|**--type-properties-user-name**|any|User name for Basic, Digest, or Windows authentication. Type: string (or Expression with resultType string).|http_server_user_name|
|**--type-properties-password**|object|Password for Basic, Digest, Windows, or ClientCertificate with EmbeddedCertData authentication.|http_server_password|
|**--type-properties-embedded-cert-data**|any|Base64 encoded certificate data for ClientCertificate authentication. For on-premises copy with ClientCertificate authentication, either CertThumbprint or EmbeddedCertData/Password should be specified. Type: string (or Expression with resultType string).|http_server_embedded_cert_data|
|**--type-properties-cert-thumbprint**|any|Thumbprint of certificate for ClientCertificate authentication. Only valid for on-premises copy. For on-premises copy with ClientCertificate authentication, either CertThumbprint or EmbeddedCertData/Password should be specified. Type: string (or Expression with resultType string).|http_server_cert_thumbprint|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|http_server_encrypted_credential|
|**--type-properties-enable-server-certificate-validation**|any|If true, validate the HTTPS server SSL certificate. Default value is true. Type: boolean (or Expression with resultType boolean).|http_server_enable_server_certificate_validation|
### datafactory linked-service http-server update

http-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The base URL of the HTTP endpoint, e.g. http://www.microsoft.com. Type: string (or Expression with resultType string).|http_server_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|http_server_connect_via|
|**--description**|string|Linked service description.|http_server_description|
|**--parameters**|dictionary|Parameters for linked service.|http_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|http_server_annotations|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the HTTP server.|http_server_authentication_type|
|**--type-properties-user-name**|any|User name for Basic, Digest, or Windows authentication. Type: string (or Expression with resultType string).|http_server_user_name|
|**--type-properties-password**|object|Password for Basic, Digest, Windows, or ClientCertificate with EmbeddedCertData authentication.|http_server_password|
|**--type-properties-embedded-cert-data**|any|Base64 encoded certificate data for ClientCertificate authentication. For on-premises copy with ClientCertificate authentication, either CertThumbprint or EmbeddedCertData/Password should be specified. Type: string (or Expression with resultType string).|http_server_embedded_cert_data|
|**--type-properties-cert-thumbprint**|any|Thumbprint of certificate for ClientCertificate authentication. Only valid for on-premises copy. For on-premises copy with ClientCertificate authentication, either CertThumbprint or EmbeddedCertData/Password should be specified. Type: string (or Expression with resultType string).|http_server_cert_thumbprint|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|http_server_encrypted_credential|
|**--type-properties-enable-server-certificate-validation**|any|If true, validate the HTTPS server SSL certificate. Default value is true. Type: boolean (or Expression with resultType boolean).|http_server_enable_server_certificate_validation|
### datafactory linked-service hubspot create

hubspot create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-client-id**|any|The client ID associated with your Hubspot application.|hubspot_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|hubspot_connect_via|
|**--description**|string|Linked service description.|hubspot_description|
|**--parameters**|dictionary|Parameters for linked service.|hubspot_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hubspot_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your Hubspot application.|hubspot_client_secret|
|**--type-properties-access-token**|object|The access token obtained when initially authenticating your OAuth integration.|hubspot_access_token|
|**--type-properties-refresh-token**|object|The refresh token obtained when initially authenticating your OAuth integration.|hubspot_refresh_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|hubspot_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|hubspot_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|hubspot_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hubspot_encrypted_credential|
### datafactory linked-service hubspot update

hubspot create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-client-id**|any|The client ID associated with your Hubspot application.|hubspot_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|hubspot_connect_via|
|**--description**|string|Linked service description.|hubspot_description|
|**--parameters**|dictionary|Parameters for linked service.|hubspot_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hubspot_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your Hubspot application.|hubspot_client_secret|
|**--type-properties-access-token**|object|The access token obtained when initially authenticating your OAuth integration.|hubspot_access_token|
|**--type-properties-refresh-token**|object|The refresh token obtained when initially authenticating your OAuth integration.|hubspot_refresh_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|hubspot_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|hubspot_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|hubspot_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hubspot_encrypted_credential|
### datafactory linked-service impala create

impala create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The IP address or host name of the Impala server. (i.e. 192.168.222.160)|impala_host|
|**--type-properties-authentication-type**|choice|The authentication type to use.|impala_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|impala_connect_via|
|**--description**|string|Linked service description.|impala_description|
|**--parameters**|dictionary|Parameters for linked service.|impala_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|impala_annotations|
|**--type-properties-port**|any|The TCP port that the Impala server uses to listen for client connections. The default value is 21050.|impala_port|
|**--type-properties-username**|any|The user name used to access the Impala server. The default value is anonymous when using SASLUsername.|impala_username|
|**--type-properties-password**|object|The password corresponding to the user name when using UsernameAndPassword.|impala_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|impala_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|impala_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|impala_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|impala_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|impala_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|impala_encrypted_credential|
### datafactory linked-service impala update

impala create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The IP address or host name of the Impala server. (i.e. 192.168.222.160)|impala_host|
|**--type-properties-authentication-type**|choice|The authentication type to use.|impala_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|impala_connect_via|
|**--description**|string|Linked service description.|impala_description|
|**--parameters**|dictionary|Parameters for linked service.|impala_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|impala_annotations|
|**--type-properties-port**|any|The TCP port that the Impala server uses to listen for client connections. The default value is 21050.|impala_port|
|**--type-properties-username**|any|The user name used to access the Impala server. The default value is anonymous when using SASLUsername.|impala_username|
|**--type-properties-password**|object|The password corresponding to the user name when using UsernameAndPassword.|impala_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|impala_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|impala_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|impala_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|impala_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|impala_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|impala_encrypted_credential|
### datafactory linked-service informix create

informix create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|informix_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|informix_connect_via|
|**--description**|string|Linked service description.|informix_description|
|**--parameters**|dictionary|Parameters for linked service.|informix_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|informix_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the Informix as ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|informix_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|informix_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|informix_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|informix_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|informix_encrypted_credential|
### datafactory linked-service informix update

informix create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|informix_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|informix_connect_via|
|**--description**|string|Linked service description.|informix_description|
|**--parameters**|dictionary|Parameters for linked service.|informix_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|informix_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the Informix as ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|informix_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|informix_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|informix_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|informix_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|informix_encrypted_credential|
### datafactory linked-service jira create

jira create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The IP address or host name of the Jira service. (e.g. jira.example.com)|jira_host|
|**--type-properties-username**|any|The user name that you use to access Jira Service.|jira_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|jira_connect_via|
|**--description**|string|Linked service description.|jira_description|
|**--parameters**|dictionary|Parameters for linked service.|jira_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|jira_annotations|
|**--type-properties-port**|any|The TCP port that the Jira server uses to listen for client connections. The default value is 443 if connecting through HTTPS, or 8080 if connecting through HTTP.|jira_port|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username field.|jira_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|jira_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|jira_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|jira_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|jira_encrypted_credential|
### datafactory linked-service jira update

jira create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The IP address or host name of the Jira service. (e.g. jira.example.com)|jira_host|
|**--type-properties-username**|any|The user name that you use to access Jira Service.|jira_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|jira_connect_via|
|**--description**|string|Linked service description.|jira_description|
|**--parameters**|dictionary|Parameters for linked service.|jira_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|jira_annotations|
|**--type-properties-port**|any|The TCP port that the Jira server uses to listen for client connections. The default value is 443 if connecting through HTTPS, or 8080 if connecting through HTTP.|jira_port|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username field.|jira_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|jira_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|jira_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|jira_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|jira_encrypted_credential|
### datafactory linked-service list

list a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory linked-service magento create

magento create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The URL of the Magento instance. (i.e. 192.168.222.110/magento3)|magento_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|magento_connect_via|
|**--description**|string|Linked service description.|magento_description|
|**--parameters**|dictionary|Parameters for linked service.|magento_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|magento_annotations|
|**--type-properties-access-token**|object|The access token from Magento.|magento_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|magento_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|magento_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|magento_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|magento_encrypted_credential|
### datafactory linked-service magento update

magento create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The URL of the Magento instance. (i.e. 192.168.222.110/magento3)|magento_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|magento_connect_via|
|**--description**|string|Linked service description.|magento_description|
|**--parameters**|dictionary|Parameters for linked service.|magento_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|magento_annotations|
|**--type-properties-access-token**|object|The access token from Magento.|magento_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|magento_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|magento_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|magento_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|magento_encrypted_credential|
### datafactory linked-service maria-d-b create

maria-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|maria_d_b_connect_via|
|**--description**|string|Linked service description.|maria_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|maria_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|maria_d_b_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|maria_d_b_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|maria_d_b_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|maria_d_b_encrypted_credential|
### datafactory linked-service maria-d-b update

maria-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|maria_d_b_connect_via|
|**--description**|string|Linked service description.|maria_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|maria_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|maria_d_b_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|maria_d_b_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|maria_d_b_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|maria_d_b_encrypted_credential|
### datafactory linked-service marketo create

marketo create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the Marketo server. (i.e. 123-ABC-321.mktorest.com)|marketo_endpoint|
|**--type-properties-client-id**|any|The client Id of your Marketo service.|marketo_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|marketo_connect_via|
|**--description**|string|Linked service description.|marketo_description|
|**--parameters**|dictionary|Parameters for linked service.|marketo_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|marketo_annotations|
|**--type-properties-client-secret**|object|The client secret of your Marketo service.|marketo_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|marketo_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|marketo_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|marketo_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|marketo_encrypted_credential|
### datafactory linked-service marketo update

marketo create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the Marketo server. (i.e. 123-ABC-321.mktorest.com)|marketo_endpoint|
|**--type-properties-client-id**|any|The client Id of your Marketo service.|marketo_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|marketo_connect_via|
|**--description**|string|Linked service description.|marketo_description|
|**--parameters**|dictionary|Parameters for linked service.|marketo_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|marketo_annotations|
|**--type-properties-client-secret**|object|The client secret of your Marketo service.|marketo_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|marketo_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|marketo_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|marketo_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|marketo_encrypted_credential|
### datafactory linked-service microsoft-access create

microsoft-access create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|microsoft_access_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|microsoft_access_connect_via|
|**--description**|string|Linked service description.|microsoft_access_description|
|**--parameters**|dictionary|Parameters for linked service.|microsoft_access_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|microsoft_access_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the Microsoft Access as ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|microsoft_access_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|microsoft_access_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|microsoft_access_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|microsoft_access_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|microsoft_access_encrypted_credential|
### datafactory linked-service microsoft-access update

microsoft-access create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|microsoft_access_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|microsoft_access_connect_via|
|**--description**|string|Linked service description.|microsoft_access_description|
|**--parameters**|dictionary|Parameters for linked service.|microsoft_access_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|microsoft_access_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the Microsoft Access as ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|microsoft_access_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|microsoft_access_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|microsoft_access_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|microsoft_access_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|microsoft_access_encrypted_credential|
### datafactory linked-service mongo-d-b create

mongo-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-server**|any|The IP address or server name of the MongoDB server. Type: string (or Expression with resultType string).|mongo_d_b_server|
|**--type-properties-database-name**|any|The name of the MongoDB database that you want to access. Type: string (or Expression with resultType string).|mongo_d_b_database_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|mongo_d_b_connect_via|
|**--description**|string|Linked service description.|mongo_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|mongo_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mongo_d_b_annotations|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the MongoDB database.|mongo_d_b_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|mongo_d_b_username|
|**--type-properties-password**|object|Password for authentication.|mongo_d_b_password|
|**--type-properties-auth-source**|any|Database to verify the username and password. Type: string (or Expression with resultType string).|mongo_d_b_auth_source|
|**--type-properties-port**|any|The TCP port number that the MongoDB server uses to listen for client connections. The default value is 27017. Type: integer (or Expression with resultType integer), minimum: 0.|mongo_d_b_port|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false. Type: boolean (or Expression with resultType boolean).|mongo_d_b_enable_ssl|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false. Type: boolean (or Expression with resultType boolean).|mongo_d_b_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|mongo_d_b_encrypted_credential|
### datafactory linked-service mongo-d-b update

mongo-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-server**|any|The IP address or server name of the MongoDB server. Type: string (or Expression with resultType string).|mongo_d_b_server|
|**--type-properties-database-name**|any|The name of the MongoDB database that you want to access. Type: string (or Expression with resultType string).|mongo_d_b_database_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|mongo_d_b_connect_via|
|**--description**|string|Linked service description.|mongo_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|mongo_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mongo_d_b_annotations|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the MongoDB database.|mongo_d_b_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|mongo_d_b_username|
|**--type-properties-password**|object|Password for authentication.|mongo_d_b_password|
|**--type-properties-auth-source**|any|Database to verify the username and password. Type: string (or Expression with resultType string).|mongo_d_b_auth_source|
|**--type-properties-port**|any|The TCP port number that the MongoDB server uses to listen for client connections. The default value is 27017. Type: integer (or Expression with resultType integer), minimum: 0.|mongo_d_b_port|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false. Type: boolean (or Expression with resultType boolean).|mongo_d_b_enable_ssl|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false. Type: boolean (or Expression with resultType boolean).|mongo_d_b_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|mongo_d_b_encrypted_credential|
### datafactory linked-service mongo-d-b-v2 create

mongo-d-b-v2 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The MongoDB connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|mongo_d_b_v2_connection_string|
|**--type-properties-database**|any|The name of the MongoDB database that you want to access. Type: string (or Expression with resultType string).|mongo_d_b_v2_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|mongo_d_b_v2_connect_via|
|**--description**|string|Linked service description.|mongo_d_b_v2_description|
|**--parameters**|dictionary|Parameters for linked service.|mongo_d_b_v2_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mongo_d_b_v2_annotations|
### datafactory linked-service mongo-d-b-v2 update

mongo-d-b-v2 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The MongoDB connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|mongo_d_b_v2_connection_string|
|**--type-properties-database**|any|The name of the MongoDB database that you want to access. Type: string (or Expression with resultType string).|mongo_d_b_v2_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|mongo_d_b_v2_connect_via|
|**--description**|string|Linked service description.|mongo_d_b_v2_description|
|**--parameters**|dictionary|Parameters for linked service.|mongo_d_b_v2_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mongo_d_b_v2_annotations|
### datafactory linked-service my-sql create

my-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string.|my_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|my_sql_connect_via|
|**--description**|string|Linked service description.|my_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|my_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|my_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|my_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|my_sql_encrypted_credential|
### datafactory linked-service my-sql update

my-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string.|my_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|my_sql_connect_via|
|**--description**|string|Linked service description.|my_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|my_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|my_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|my_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|my_sql_encrypted_credential|
### datafactory linked-service netezza create

netezza create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|netezza_connect_via|
|**--description**|string|Linked service description.|netezza_description|
|**--parameters**|dictionary|Parameters for linked service.|netezza_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|netezza_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|netezza_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|netezza_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|netezza_encrypted_credential|
### datafactory linked-service netezza update

netezza create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|netezza_connect_via|
|**--description**|string|Linked service description.|netezza_description|
|**--parameters**|dictionary|Parameters for linked service.|netezza_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|netezza_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|netezza_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|netezza_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|netezza_encrypted_credential|
### datafactory linked-service o-data create

o-data create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The URL of the OData service endpoint. Type: string (or Expression with resultType string).|o_data_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|o_data_connect_via|
|**--description**|string|Linked service description.|o_data_description|
|**--parameters**|dictionary|Parameters for linked service.|o_data_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|o_data_annotations|
|**--type-properties-authentication-type**|choice|Type of authentication used to connect to the OData service.|o_data_authentication_type|
|**--type-properties-user-name**|any|User name of the OData service. Type: string (or Expression with resultType string).|o_data_user_name|
|**--type-properties-password**|object|Password of the OData service.|o_data_password|
|**--type-properties-tenant**|any|Specify the tenant information (domain name or tenant ID) under which your application resides. Type: string (or Expression with resultType string).|o_data_tenant|
|**--type-properties-service-principal-id**|any|Specify the application id of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|o_data_service_principal_id|
|**--type-properties-aad-resource-id**|any|Specify the resource you are requesting authorization to use Directory. Type: string (or Expression with resultType string).|o_data_aad_resource_id|
|**--type-properties-aad-service-principal-credential-type**|choice|Specify the credential type (key or cert) is used for service principal.|o_data_aad_service_principal_credential_type|
|**--type-properties-service-principal-key**|object|Specify the secret of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|o_data_service_principal_key|
|**--type-properties-service-principal-embedded-cert**|object|Specify the base64 encoded certificate of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|o_data_service_principal_embedded_cert|
|**--type-properties-service-principal-embedded-cert-password**|object|Specify the password of your certificate if your certificate has a password and you are using AadServicePrincipal authentication. Type: string (or Expression with resultType string).|o_data_service_principal_embedded_cert_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|o_data_encrypted_credential|
### datafactory linked-service o-data update

o-data create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The URL of the OData service endpoint. Type: string (or Expression with resultType string).|o_data_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|o_data_connect_via|
|**--description**|string|Linked service description.|o_data_description|
|**--parameters**|dictionary|Parameters for linked service.|o_data_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|o_data_annotations|
|**--type-properties-authentication-type**|choice|Type of authentication used to connect to the OData service.|o_data_authentication_type|
|**--type-properties-user-name**|any|User name of the OData service. Type: string (or Expression with resultType string).|o_data_user_name|
|**--type-properties-password**|object|Password of the OData service.|o_data_password|
|**--type-properties-tenant**|any|Specify the tenant information (domain name or tenant ID) under which your application resides. Type: string (or Expression with resultType string).|o_data_tenant|
|**--type-properties-service-principal-id**|any|Specify the application id of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|o_data_service_principal_id|
|**--type-properties-aad-resource-id**|any|Specify the resource you are requesting authorization to use Directory. Type: string (or Expression with resultType string).|o_data_aad_resource_id|
|**--type-properties-aad-service-principal-credential-type**|choice|Specify the credential type (key or cert) is used for service principal.|o_data_aad_service_principal_credential_type|
|**--type-properties-service-principal-key**|object|Specify the secret of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|o_data_service_principal_key|
|**--type-properties-service-principal-embedded-cert**|object|Specify the base64 encoded certificate of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|o_data_service_principal_embedded_cert|
|**--type-properties-service-principal-embedded-cert-password**|object|Specify the password of your certificate if your certificate has a password and you are using AadServicePrincipal authentication. Type: string (or Expression with resultType string).|o_data_service_principal_embedded_cert_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|o_data_encrypted_credential|
### datafactory linked-service odbc create

odbc create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|odbc_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|odbc_connect_via|
|**--description**|string|Linked service description.|odbc_description|
|**--parameters**|dictionary|Parameters for linked service.|odbc_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|odbc_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|odbc_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|odbc_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|odbc_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|odbc_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|odbc_encrypted_credential|
### datafactory linked-service odbc update

odbc create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|odbc_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|odbc_connect_via|
|**--description**|string|Linked service description.|odbc_description|
|**--parameters**|dictionary|Parameters for linked service.|odbc_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|odbc_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|odbc_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|odbc_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|odbc_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|odbc_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|odbc_encrypted_credential|
### datafactory linked-service office365 create

office365 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-office365tenant-id**|any|Azure tenant ID to which the Office 365 account belongs. Type: string (or Expression with resultType string).|office365_office365_tenant_id|
|**--type-properties-service-principal-tenant-id**|any|Specify the tenant information under which your Azure AD web application resides. Type: string (or Expression with resultType string).|office365_service_principal_tenant_id|
|**--type-properties-service-principal-id**|any|Specify the application's client ID. Type: string (or Expression with resultType string).|office365_service_principal_id|
|**--type-properties-service-principal-key**|object|Specify the application's key.|office365_service_principal_key|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|office365_connect_via|
|**--description**|string|Linked service description.|office365_description|
|**--parameters**|dictionary|Parameters for linked service.|office365_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|office365_annotations|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|office365_encrypted_credential|
### datafactory linked-service office365 update

office365 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-office365tenant-id**|any|Azure tenant ID to which the Office 365 account belongs. Type: string (or Expression with resultType string).|office365_office365_tenant_id|
|**--type-properties-service-principal-tenant-id**|any|Specify the tenant information under which your Azure AD web application resides. Type: string (or Expression with resultType string).|office365_service_principal_tenant_id|
|**--type-properties-service-principal-id**|any|Specify the application's client ID. Type: string (or Expression with resultType string).|office365_service_principal_id|
|**--type-properties-service-principal-key**|object|Specify the application's key.|office365_service_principal_key|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|office365_connect_via|
|**--description**|string|Linked service description.|office365_description|
|**--parameters**|dictionary|Parameters for linked service.|office365_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|office365_annotations|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|office365_encrypted_credential|
### datafactory linked-service oracle create

oracle create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|oracle_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|oracle_connect_via|
|**--description**|string|Linked service description.|oracle_description|
|**--parameters**|dictionary|Parameters for linked service.|oracle_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|oracle_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|oracle_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|oracle_encrypted_credential|
### datafactory linked-service oracle update

oracle create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|oracle_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|oracle_connect_via|
|**--description**|string|Linked service description.|oracle_description|
|**--parameters**|dictionary|Parameters for linked service.|oracle_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|oracle_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|oracle_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|oracle_encrypted_credential|
### datafactory linked-service oracle-service-cloud create

oracle-service-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The URL of the Oracle Service Cloud instance.|oracle_service_cloud_host|
|**--type-properties-username**|any|The user name that you use to access Oracle Service Cloud server.|oracle_service_cloud_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username key.|oracle_service_cloud_password|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|oracle_service_cloud_connect_via|
|**--description**|string|Linked service description.|oracle_service_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|oracle_service_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|oracle_service_cloud_annotations|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|oracle_service_cloud_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|oracle_service_cloud_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|oracle_service_cloud_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|oracle_service_cloud_encrypted_credential|
### datafactory linked-service oracle-service-cloud update

oracle-service-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The URL of the Oracle Service Cloud instance.|oracle_service_cloud_host|
|**--type-properties-username**|any|The user name that you use to access Oracle Service Cloud server.|oracle_service_cloud_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username key.|oracle_service_cloud_password|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|oracle_service_cloud_connect_via|
|**--description**|string|Linked service description.|oracle_service_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|oracle_service_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|oracle_service_cloud_annotations|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|oracle_service_cloud_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|oracle_service_cloud_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|oracle_service_cloud_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|oracle_service_cloud_encrypted_credential|
### datafactory linked-service paypal create

paypal create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The URL of the PayPal instance. (i.e. api.sandbox.paypal.com)|paypal_host|
|**--type-properties-client-id**|any|The client ID associated with your PayPal application.|paypal_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|paypal_connect_via|
|**--description**|string|Linked service description.|paypal_description|
|**--parameters**|dictionary|Parameters for linked service.|paypal_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|paypal_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your PayPal application.|paypal_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|paypal_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|paypal_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|paypal_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|paypal_encrypted_credential|
### datafactory linked-service paypal update

paypal create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The URL of the PayPal instance. (i.e. api.sandbox.paypal.com)|paypal_host|
|**--type-properties-client-id**|any|The client ID associated with your PayPal application.|paypal_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|paypal_connect_via|
|**--description**|string|Linked service description.|paypal_description|
|**--parameters**|dictionary|Parameters for linked service.|paypal_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|paypal_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your PayPal application.|paypal_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|paypal_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|paypal_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|paypal_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|paypal_encrypted_credential|
### datafactory linked-service phoenix create

phoenix create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The IP address or host name of the Phoenix server. (i.e. 192.168.222.160)|phoenix_host|
|**--type-properties-authentication-type**|choice|The authentication mechanism used to connect to the Phoenix server.|phoenix_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|phoenix_connect_via|
|**--description**|string|Linked service description.|phoenix_description|
|**--parameters**|dictionary|Parameters for linked service.|phoenix_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|phoenix_annotations|
|**--type-properties-port**|any|The TCP port that the Phoenix server uses to listen for client connections. The default value is 8765.|phoenix_port|
|**--type-properties-http-path**|any|The partial URL corresponding to the Phoenix server. (i.e. /gateway/sandbox/phoenix/version). The default value is hbasephoenix if using WindowsAzureHDInsightService.|phoenix_http_path|
|**--type-properties-username**|any|The user name used to connect to the Phoenix server.|phoenix_username|
|**--type-properties-password**|object|The password corresponding to the user name.|phoenix_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|phoenix_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|phoenix_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|phoenix_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|phoenix_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|phoenix_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|phoenix_encrypted_credential|
### datafactory linked-service phoenix update

phoenix create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The IP address or host name of the Phoenix server. (i.e. 192.168.222.160)|phoenix_host|
|**--type-properties-authentication-type**|choice|The authentication mechanism used to connect to the Phoenix server.|phoenix_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|phoenix_connect_via|
|**--description**|string|Linked service description.|phoenix_description|
|**--parameters**|dictionary|Parameters for linked service.|phoenix_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|phoenix_annotations|
|**--type-properties-port**|any|The TCP port that the Phoenix server uses to listen for client connections. The default value is 8765.|phoenix_port|
|**--type-properties-http-path**|any|The partial URL corresponding to the Phoenix server. (i.e. /gateway/sandbox/phoenix/version). The default value is hbasephoenix if using WindowsAzureHDInsightService.|phoenix_http_path|
|**--type-properties-username**|any|The user name used to connect to the Phoenix server.|phoenix_username|
|**--type-properties-password**|object|The password corresponding to the user name.|phoenix_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|phoenix_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|phoenix_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|phoenix_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|phoenix_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|phoenix_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|phoenix_encrypted_credential|
### datafactory linked-service postgre-sql create

postgre-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string.|postgre_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|postgre_sql_connect_via|
|**--description**|string|Linked service description.|postgre_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|postgre_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|postgre_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|postgre_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|postgre_sql_encrypted_credential|
### datafactory linked-service postgre-sql update

postgre-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string.|postgre_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|postgre_sql_connect_via|
|**--description**|string|Linked service description.|postgre_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|postgre_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|postgre_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|postgre_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|postgre_sql_encrypted_credential|
### datafactory linked-service presto create

presto create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The IP address or host name of the Presto server. (i.e. 192.168.222.160)|presto_host|
|**--type-properties-server-version**|any|The version of the Presto server. (i.e. 0.148-t)|presto_server_version|
|**--type-properties-catalog**|any|The catalog context for all request against the server.|presto_catalog|
|**--type-properties-authentication-type**|choice|The authentication mechanism used to connect to the Presto server.|presto_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|presto_connect_via|
|**--description**|string|Linked service description.|presto_description|
|**--parameters**|dictionary|Parameters for linked service.|presto_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|presto_annotations|
|**--type-properties-port**|any|The TCP port that the Presto server uses to listen for client connections. The default value is 8080.|presto_port|
|**--type-properties-username**|any|The user name used to connect to the Presto server.|presto_username|
|**--type-properties-password**|object|The password corresponding to the user name.|presto_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|presto_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|presto_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|presto_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|presto_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|presto_allow_self_signed_server_cert|
|**--type-properties-time-zone-id**|any|The local time zone used by the connection. Valid values for this option are specified in the IANA Time Zone Database. The default value is the system time zone.|presto_time_zone_id|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|presto_encrypted_credential|
### datafactory linked-service presto update

presto create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The IP address or host name of the Presto server. (i.e. 192.168.222.160)|presto_host|
|**--type-properties-server-version**|any|The version of the Presto server. (i.e. 0.148-t)|presto_server_version|
|**--type-properties-catalog**|any|The catalog context for all request against the server.|presto_catalog|
|**--type-properties-authentication-type**|choice|The authentication mechanism used to connect to the Presto server.|presto_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|presto_connect_via|
|**--description**|string|Linked service description.|presto_description|
|**--parameters**|dictionary|Parameters for linked service.|presto_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|presto_annotations|
|**--type-properties-port**|any|The TCP port that the Presto server uses to listen for client connections. The default value is 8080.|presto_port|
|**--type-properties-username**|any|The user name used to connect to the Presto server.|presto_username|
|**--type-properties-password**|object|The password corresponding to the user name.|presto_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|presto_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|presto_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|presto_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|presto_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|presto_allow_self_signed_server_cert|
|**--type-properties-time-zone-id**|any|The local time zone used by the connection. Valid values for this option are specified in the IANA Time Zone Database. The default value is the system time zone.|presto_time_zone_id|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|presto_encrypted_credential|
### datafactory linked-service quick-books create

quick-books create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the QuickBooks server. (i.e. quickbooks.api.intuit.com)|quick_books_endpoint|
|**--type-properties-company-id**|any|The company ID of the QuickBooks company to authorize.|quick_books_company_id|
|**--type-properties-consumer-key**|any|The consumer key for OAuth 1.0 authentication.|quick_books_consumer_key|
|**--type-properties-consumer-secret**|object|The consumer secret for OAuth 1.0 authentication.|quick_books_consumer_secret|
|**--type-properties-access-token**|object|The access token for OAuth 1.0 authentication.|quick_books_access_token|
|**--type-properties-access-token-secret**|object|The access token secret for OAuth 1.0 authentication.|quick_books_access_token_secret|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|quick_books_connect_via|
|**--description**|string|Linked service description.|quick_books_description|
|**--parameters**|dictionary|Parameters for linked service.|quick_books_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|quick_books_annotations|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|quick_books_use_encrypted_endpoints|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|quick_books_encrypted_credential|
### datafactory linked-service quick-books update

quick-books create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the QuickBooks server. (i.e. quickbooks.api.intuit.com)|quick_books_endpoint|
|**--type-properties-company-id**|any|The company ID of the QuickBooks company to authorize.|quick_books_company_id|
|**--type-properties-consumer-key**|any|The consumer key for OAuth 1.0 authentication.|quick_books_consumer_key|
|**--type-properties-consumer-secret**|object|The consumer secret for OAuth 1.0 authentication.|quick_books_consumer_secret|
|**--type-properties-access-token**|object|The access token for OAuth 1.0 authentication.|quick_books_access_token|
|**--type-properties-access-token-secret**|object|The access token secret for OAuth 1.0 authentication.|quick_books_access_token_secret|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|quick_books_connect_via|
|**--description**|string|Linked service description.|quick_books_description|
|**--parameters**|dictionary|Parameters for linked service.|quick_books_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|quick_books_annotations|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|quick_books_use_encrypted_endpoints|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|quick_books_encrypted_credential|
### datafactory linked-service responsys create

responsys create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the Responsys server.|responsys_endpoint|
|**--type-properties-client-id**|any|The client ID associated with the Responsys application. Type: string (or Expression with resultType string).|responsys_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|responsys_connect_via|
|**--description**|string|Linked service description.|responsys_description|
|**--parameters**|dictionary|Parameters for linked service.|responsys_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|responsys_annotations|
|**--type-properties-client-secret**|object|The client secret associated with the Responsys application. Type: string (or Expression with resultType string).|responsys_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|responsys_encrypted_credential|
### datafactory linked-service responsys update

responsys create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the Responsys server.|responsys_endpoint|
|**--type-properties-client-id**|any|The client ID associated with the Responsys application. Type: string (or Expression with resultType string).|responsys_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|responsys_connect_via|
|**--description**|string|Linked service description.|responsys_description|
|**--parameters**|dictionary|Parameters for linked service.|responsys_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|responsys_annotations|
|**--type-properties-client-secret**|object|The client secret associated with the Responsys application. Type: string (or Expression with resultType string).|responsys_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|responsys_encrypted_credential|
### datafactory linked-service rest-service create

rest-service create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The base URL of the REST service.|rest_service_url|
|**--type-properties-authentication-type**|choice|Type of authentication used to connect to the REST service.|rest_service_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|rest_service_connect_via|
|**--description**|string|Linked service description.|rest_service_description|
|**--parameters**|dictionary|Parameters for linked service.|rest_service_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|rest_service_annotations|
|**--type-properties-enable-server-certificate-validation**|any|Whether to validate server side SSL certificate when connecting to the endpoint.The default value is true. Type: boolean (or Expression with resultType boolean).|rest_service_enable_server_certificate_validation|
|**--type-properties-user-name**|any|The user name used in Basic authentication type.|rest_service_user_name|
|**--type-properties-password**|object|The password used in Basic authentication type.|rest_service_password|
|**--type-properties-service-principal-id**|any|The application's client ID used in AadServicePrincipal authentication type.|rest_service_service_principal_id|
|**--type-properties-service-principal-key**|object|The application's key used in AadServicePrincipal authentication type.|rest_service_service_principal_key|
|**--type-properties-tenant**|any|The tenant information (domain name or tenant ID) used in AadServicePrincipal authentication type under which your application resides.|rest_service_tenant|
|**--type-properties-aad-resource-id**|any|The resource you are requesting authorization to use.|rest_service_aad_resource_id|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|rest_service_encrypted_credential|
### datafactory linked-service rest-service update

rest-service create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The base URL of the REST service.|rest_service_url|
|**--type-properties-authentication-type**|choice|Type of authentication used to connect to the REST service.|rest_service_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|rest_service_connect_via|
|**--description**|string|Linked service description.|rest_service_description|
|**--parameters**|dictionary|Parameters for linked service.|rest_service_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|rest_service_annotations|
|**--type-properties-enable-server-certificate-validation**|any|Whether to validate server side SSL certificate when connecting to the endpoint.The default value is true. Type: boolean (or Expression with resultType boolean).|rest_service_enable_server_certificate_validation|
|**--type-properties-user-name**|any|The user name used in Basic authentication type.|rest_service_user_name|
|**--type-properties-password**|object|The password used in Basic authentication type.|rest_service_password|
|**--type-properties-service-principal-id**|any|The application's client ID used in AadServicePrincipal authentication type.|rest_service_service_principal_id|
|**--type-properties-service-principal-key**|object|The application's key used in AadServicePrincipal authentication type.|rest_service_service_principal_key|
|**--type-properties-tenant**|any|The tenant information (domain name or tenant ID) used in AadServicePrincipal authentication type under which your application resides.|rest_service_tenant|
|**--type-properties-aad-resource-id**|any|The resource you are requesting authorization to use.|rest_service_aad_resource_id|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|rest_service_encrypted_credential|
### datafactory linked-service salesforce create

salesforce create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforce_connect_via|
|**--description**|string|Linked service description.|salesforce_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforce_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforce_annotations|
|**--type-properties-environment-url**|any|The URL of Salesforce instance. Default is 'https://login.salesforce.com'. To copy data from sandbox, specify 'https://test.salesforce.com'. To copy data from custom domain, specify, for example, 'https://[domain].my.salesforce.com'. Type: string (or Expression with resultType string).|salesforce_environment_url|
|**--type-properties-username**|any|The username for Basic authentication of the Salesforce instance. Type: string (or Expression with resultType string).|salesforce_username|
|**--type-properties-password**|object|The password for Basic authentication of the Salesforce instance.|salesforce_password|
|**--type-properties-security-token**|object|The security token is optional to remotely access Salesforce instance.|salesforce_security_token|
|**--type-properties-api-version**|any|The Salesforce API version used in ADF. Type: string (or Expression with resultType string).|salesforce_api_version|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforce_encrypted_credential|
### datafactory linked-service salesforce update

salesforce create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforce_connect_via|
|**--description**|string|Linked service description.|salesforce_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforce_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforce_annotations|
|**--type-properties-environment-url**|any|The URL of Salesforce instance. Default is 'https://login.salesforce.com'. To copy data from sandbox, specify 'https://test.salesforce.com'. To copy data from custom domain, specify, for example, 'https://[domain].my.salesforce.com'. Type: string (or Expression with resultType string).|salesforce_environment_url|
|**--type-properties-username**|any|The username for Basic authentication of the Salesforce instance. Type: string (or Expression with resultType string).|salesforce_username|
|**--type-properties-password**|object|The password for Basic authentication of the Salesforce instance.|salesforce_password|
|**--type-properties-security-token**|object|The security token is optional to remotely access Salesforce instance.|salesforce_security_token|
|**--type-properties-api-version**|any|The Salesforce API version used in ADF. Type: string (or Expression with resultType string).|salesforce_api_version|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforce_encrypted_credential|
### datafactory linked-service salesforce-marketing-cloud create

salesforce-marketing-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-client-id**|any|The client ID associated with the Salesforce Marketing Cloud application. Type: string (or Expression with resultType string).|salesforce_marketing_cloud_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforce_marketing_cloud_connect_via|
|**--description**|string|Linked service description.|salesforce_marketing_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforce_marketing_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforce_marketing_cloud_annotations|
|**--type-properties-client-secret**|object|The client secret associated with the Salesforce Marketing Cloud application. Type: string (or Expression with resultType string).|salesforce_marketing_cloud_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforce_marketing_cloud_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforce_marketing_cloud_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforce_marketing_cloud_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforce_marketing_cloud_encrypted_credential|
### datafactory linked-service salesforce-marketing-cloud update

salesforce-marketing-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-client-id**|any|The client ID associated with the Salesforce Marketing Cloud application. Type: string (or Expression with resultType string).|salesforce_marketing_cloud_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforce_marketing_cloud_connect_via|
|**--description**|string|Linked service description.|salesforce_marketing_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforce_marketing_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforce_marketing_cloud_annotations|
|**--type-properties-client-secret**|object|The client secret associated with the Salesforce Marketing Cloud application. Type: string (or Expression with resultType string).|salesforce_marketing_cloud_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforce_marketing_cloud_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforce_marketing_cloud_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforce_marketing_cloud_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforce_marketing_cloud_encrypted_credential|
### datafactory linked-service salesforce-service-cloud create

salesforce-service-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforce_service_cloud_connect_via|
|**--description**|string|Linked service description.|salesforce_service_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforce_service_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforce_service_cloud_annotations|
|**--type-properties-environment-url**|any|The URL of Salesforce Service Cloud instance. Default is 'https://login.salesforce.com'. To copy data from sandbox, specify 'https://test.salesforce.com'. To copy data from custom domain, specify, for example, 'https://[domain].my.salesforce.com'. Type: string (or Expression with resultType string).|salesforce_service_cloud_environment_url|
|**--type-properties-username**|any|The username for Basic authentication of the Salesforce instance. Type: string (or Expression with resultType string).|salesforce_service_cloud_username|
|**--type-properties-password**|object|The password for Basic authentication of the Salesforce instance.|salesforce_service_cloud_password|
|**--type-properties-security-token**|object|The security token is optional to remotely access Salesforce instance.|salesforce_service_cloud_security_token|
|**--type-properties-api-version**|any|The Salesforce API version used in ADF. Type: string (or Expression with resultType string).|salesforce_service_cloud_api_version|
|**--type-properties-extended-properties**|any|Extended properties appended to the connection string. Type: string (or Expression with resultType string).|salesforce_service_cloud_extended_properties|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforce_service_cloud_encrypted_credential|
### datafactory linked-service salesforce-service-cloud update

salesforce-service-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforce_service_cloud_connect_via|
|**--description**|string|Linked service description.|salesforce_service_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforce_service_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforce_service_cloud_annotations|
|**--type-properties-environment-url**|any|The URL of Salesforce Service Cloud instance. Default is 'https://login.salesforce.com'. To copy data from sandbox, specify 'https://test.salesforce.com'. To copy data from custom domain, specify, for example, 'https://[domain].my.salesforce.com'. Type: string (or Expression with resultType string).|salesforce_service_cloud_environment_url|
|**--type-properties-username**|any|The username for Basic authentication of the Salesforce instance. Type: string (or Expression with resultType string).|salesforce_service_cloud_username|
|**--type-properties-password**|object|The password for Basic authentication of the Salesforce instance.|salesforce_service_cloud_password|
|**--type-properties-security-token**|object|The security token is optional to remotely access Salesforce instance.|salesforce_service_cloud_security_token|
|**--type-properties-api-version**|any|The Salesforce API version used in ADF. Type: string (or Expression with resultType string).|salesforce_service_cloud_api_version|
|**--type-properties-extended-properties**|any|Extended properties appended to the connection string. Type: string (or Expression with resultType string).|salesforce_service_cloud_extended_properties|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforce_service_cloud_encrypted_credential|
### datafactory linked-service sap-bw create

sap-bw create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-server**|any|Host name of the SAP BW instance. Type: string (or Expression with resultType string).|sap_bw_server|
|**--type-properties-system-number**|any|System number of the BW system. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|sap_bw_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the BW system. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|sap_bw_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_bw_connect_via|
|**--description**|string|Linked service description.|sap_bw_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_bw_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_bw_annotations|
|**--type-properties-user-name**|any|Username to access the SAP BW server. Type: string (or Expression with resultType string).|sap_bw_user_name|
|**--type-properties-password**|object|Password to access the SAP BW server.|sap_bw_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sap_bw_encrypted_credential|
### datafactory linked-service sap-bw update

sap-bw create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-server**|any|Host name of the SAP BW instance. Type: string (or Expression with resultType string).|sap_bw_server|
|**--type-properties-system-number**|any|System number of the BW system. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|sap_bw_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the BW system. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|sap_bw_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_bw_connect_via|
|**--description**|string|Linked service description.|sap_bw_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_bw_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_bw_annotations|
|**--type-properties-user-name**|any|Username to access the SAP BW server. Type: string (or Expression with resultType string).|sap_bw_user_name|
|**--type-properties-password**|object|Password to access the SAP BW server.|sap_bw_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sap_bw_encrypted_credential|
### datafactory linked-service sap-cloud-for-customer create

sap-cloud-for-customer create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The URL of SAP Cloud for Customer OData API. For example, '[https://[tenantname].crm.ondemand.com/sap/c4c/odata/v1]'. Type: string (or Expression with resultType string).|sap_cloud_for_customer_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_cloud_for_customer_connect_via|
|**--description**|string|Linked service description.|sap_cloud_for_customer_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_cloud_for_customer_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_cloud_for_customer_annotations|
|**--type-properties-username**|any|The username for Basic authentication. Type: string (or Expression with resultType string).|sap_cloud_for_customer_username|
|**--type-properties-password**|object|The password for Basic authentication.|sap_cloud_for_customer_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Either encryptedCredential or username/password must be provided. Type: string (or Expression with resultType string).|sap_cloud_for_customer_encrypted_credential|
### datafactory linked-service sap-cloud-for-customer update

sap-cloud-for-customer create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|any|The URL of SAP Cloud for Customer OData API. For example, '[https://[tenantname].crm.ondemand.com/sap/c4c/odata/v1]'. Type: string (or Expression with resultType string).|sap_cloud_for_customer_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_cloud_for_customer_connect_via|
|**--description**|string|Linked service description.|sap_cloud_for_customer_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_cloud_for_customer_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_cloud_for_customer_annotations|
|**--type-properties-username**|any|The username for Basic authentication. Type: string (or Expression with resultType string).|sap_cloud_for_customer_username|
|**--type-properties-password**|object|The password for Basic authentication.|sap_cloud_for_customer_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Either encryptedCredential or username/password must be provided. Type: string (or Expression with resultType string).|sap_cloud_for_customer_encrypted_credential|
### datafactory linked-service sap-ecc create

sap-ecc create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|string|The URL of SAP ECC OData API. For example, '[https://hostname:port/sap/opu/odata/sap/servicename/]'. Type: string (or Expression with resultType string).|sap_ecc_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_ecc_connect_via|
|**--description**|string|Linked service description.|sap_ecc_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_ecc_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_ecc_annotations|
|**--type-properties-username**|string|The username for Basic authentication. Type: string (or Expression with resultType string).|sap_ecc_username|
|**--type-properties-password**|object|The password for Basic authentication.|sap_ecc_password|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Either encryptedCredential or username/password must be provided. Type: string (or Expression with resultType string).|sap_ecc_encrypted_credential|
### datafactory linked-service sap-ecc update

sap-ecc create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-url**|string|The URL of SAP ECC OData API. For example, '[https://hostname:port/sap/opu/odata/sap/servicename/]'. Type: string (or Expression with resultType string).|sap_ecc_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_ecc_connect_via|
|**--description**|string|Linked service description.|sap_ecc_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_ecc_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_ecc_annotations|
|**--type-properties-username**|string|The username for Basic authentication. Type: string (or Expression with resultType string).|sap_ecc_username|
|**--type-properties-password**|object|The password for Basic authentication.|sap_ecc_password|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Either encryptedCredential or username/password must be provided. Type: string (or Expression with resultType string).|sap_ecc_encrypted_credential|
### datafactory linked-service sap-hana create

sap-hana create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_hana_connect_via|
|**--description**|string|Linked service description.|sap_hana_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_hana_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_hana_annotations|
|**--type-properties-connection-string**|any|SAP HANA ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|sap_hana_connection_string|
|**--type-properties-server**|any|Host name of the SAP HANA server. Type: string (or Expression with resultType string).|sap_hana_server|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the SAP HANA server.|sap_hana_authentication_type|
|**--type-properties-user-name**|any|Username to access the SAP HANA server. Type: string (or Expression with resultType string).|sap_hana_user_name|
|**--type-properties-password**|object|Password to access the SAP HANA server.|sap_hana_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sap_hana_encrypted_credential|
### datafactory linked-service sap-hana update

sap-hana create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_hana_connect_via|
|**--description**|string|Linked service description.|sap_hana_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_hana_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_hana_annotations|
|**--type-properties-connection-string**|any|SAP HANA ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|sap_hana_connection_string|
|**--type-properties-server**|any|Host name of the SAP HANA server. Type: string (or Expression with resultType string).|sap_hana_server|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the SAP HANA server.|sap_hana_authentication_type|
|**--type-properties-user-name**|any|Username to access the SAP HANA server. Type: string (or Expression with resultType string).|sap_hana_user_name|
|**--type-properties-password**|object|Password to access the SAP HANA server.|sap_hana_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sap_hana_encrypted_credential|
### datafactory linked-service sap-open-hub create

sap-open-hub create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-server**|any|Host name of the SAP BW instance where the open hub destination is located. Type: string (or Expression with resultType string).|sap_open_hub_server|
|**--type-properties-system-number**|any|System number of the BW system where the open hub destination is located. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|sap_open_hub_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the BW system where the open hub destination is located. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|sap_open_hub_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_open_hub_connect_via|
|**--description**|string|Linked service description.|sap_open_hub_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_open_hub_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_open_hub_annotations|
|**--type-properties-language**|any|Language of the BW system where the open hub destination is located. The default value is EN. Type: string (or Expression with resultType string).|sap_open_hub_language|
|**--type-properties-user-name**|any|Username to access the SAP BW server where the open hub destination is located. Type: string (or Expression with resultType string).|sap_open_hub_user_name|
|**--type-properties-password**|object|Password to access the SAP BW server where the open hub destination is located.|sap_open_hub_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sap_open_hub_encrypted_credential|
### datafactory linked-service sap-open-hub update

sap-open-hub create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-server**|any|Host name of the SAP BW instance where the open hub destination is located. Type: string (or Expression with resultType string).|sap_open_hub_server|
|**--type-properties-system-number**|any|System number of the BW system where the open hub destination is located. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|sap_open_hub_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the BW system where the open hub destination is located. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|sap_open_hub_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_open_hub_connect_via|
|**--description**|string|Linked service description.|sap_open_hub_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_open_hub_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_open_hub_annotations|
|**--type-properties-language**|any|Language of the BW system where the open hub destination is located. The default value is EN. Type: string (or Expression with resultType string).|sap_open_hub_language|
|**--type-properties-user-name**|any|Username to access the SAP BW server where the open hub destination is located. Type: string (or Expression with resultType string).|sap_open_hub_user_name|
|**--type-properties-password**|object|Password to access the SAP BW server where the open hub destination is located.|sap_open_hub_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sap_open_hub_encrypted_credential|
### datafactory linked-service sap-table create

sap-table create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_table_connect_via|
|**--description**|string|Linked service description.|sap_table_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_table_annotations|
|**--type-properties-server**|any|Host name of the SAP instance where the table is located. Type: string (or Expression with resultType string).|sap_table_server|
|**--type-properties-system-number**|any|System number of the SAP system where the table is located. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|sap_table_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the SAP system where the table is located. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|sap_table_client_id|
|**--type-properties-language**|any|Language of the SAP system where the table is located. The default value is EN. Type: string (or Expression with resultType string).|sap_table_language|
|**--type-properties-system-id**|any|SystemID of the SAP system where the table is located. Type: string (or Expression with resultType string).|sap_table_system_id|
|**--type-properties-user-name**|any|Username to access the SAP server where the table is located. Type: string (or Expression with resultType string).|sap_table_user_name|
|**--type-properties-password**|object|Password to access the SAP server where the table is located.|sap_table_password|
|**--type-properties-message-server**|any|The hostname of the SAP Message Server. Type: string (or Expression with resultType string).|sap_table_message_server|
|**--type-properties-message-server-service**|any|The service name or port number of the Message Server. Type: string (or Expression with resultType string).|sap_table_message_server_service|
|**--type-properties-snc-mode**|any|SNC activation indicator to access the SAP server where the table is located. Must be either 0 (off) or 1 (on). Type: string (or Expression with resultType string).|sap_table_snc_mode|
|**--type-properties-snc-my-name**|any|Initiator's SNC name to access the SAP server where the table is located. Type: string (or Expression with resultType string).|sap_table_snc_my_name|
|**--type-properties-snc-partner-name**|any|Communication partner's SNC name to access the SAP server where the table is located. Type: string (or Expression with resultType string).|sap_table_snc_partner_name|
|**--type-properties-snc-library-path**|any|External security product's library to access the SAP server where the table is located. Type: string (or Expression with resultType string).|sap_table_snc_library_path|
|**--type-properties-snc-qop**|any|SNC Quality of Protection. Allowed value include: 1, 2, 3, 8, 9. Type: string (or Expression with resultType string).|sap_table_snc_qop|
|**--type-properties-logon-group**|any|The Logon Group for the SAP System. Type: string (or Expression with resultType string).|sap_table_logon_group|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sap_table_encrypted_credential|
### datafactory linked-service sap-table update

sap-table create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sap_table_connect_via|
|**--description**|string|Linked service description.|sap_table_description|
|**--parameters**|dictionary|Parameters for linked service.|sap_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sap_table_annotations|
|**--type-properties-server**|any|Host name of the SAP instance where the table is located. Type: string (or Expression with resultType string).|sap_table_server|
|**--type-properties-system-number**|any|System number of the SAP system where the table is located. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|sap_table_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the SAP system where the table is located. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|sap_table_client_id|
|**--type-properties-language**|any|Language of the SAP system where the table is located. The default value is EN. Type: string (or Expression with resultType string).|sap_table_language|
|**--type-properties-system-id**|any|SystemID of the SAP system where the table is located. Type: string (or Expression with resultType string).|sap_table_system_id|
|**--type-properties-user-name**|any|Username to access the SAP server where the table is located. Type: string (or Expression with resultType string).|sap_table_user_name|
|**--type-properties-password**|object|Password to access the SAP server where the table is located.|sap_table_password|
|**--type-properties-message-server**|any|The hostname of the SAP Message Server. Type: string (or Expression with resultType string).|sap_table_message_server|
|**--type-properties-message-server-service**|any|The service name or port number of the Message Server. Type: string (or Expression with resultType string).|sap_table_message_server_service|
|**--type-properties-snc-mode**|any|SNC activation indicator to access the SAP server where the table is located. Must be either 0 (off) or 1 (on). Type: string (or Expression with resultType string).|sap_table_snc_mode|
|**--type-properties-snc-my-name**|any|Initiator's SNC name to access the SAP server where the table is located. Type: string (or Expression with resultType string).|sap_table_snc_my_name|
|**--type-properties-snc-partner-name**|any|Communication partner's SNC name to access the SAP server where the table is located. Type: string (or Expression with resultType string).|sap_table_snc_partner_name|
|**--type-properties-snc-library-path**|any|External security product's library to access the SAP server where the table is located. Type: string (or Expression with resultType string).|sap_table_snc_library_path|
|**--type-properties-snc-qop**|any|SNC Quality of Protection. Allowed value include: 1, 2, 3, 8, 9. Type: string (or Expression with resultType string).|sap_table_snc_qop|
|**--type-properties-logon-group**|any|The Logon Group for the SAP System. Type: string (or Expression with resultType string).|sap_table_logon_group|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sap_table_encrypted_credential|
### datafactory linked-service service-now create

service-now create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the ServiceNow server. (i.e. :code:`<instance>`.service-now.com)|service_now_endpoint|
|**--type-properties-authentication-type**|choice|The authentication type to use.|service_now_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|service_now_connect_via|
|**--description**|string|Linked service description.|service_now_description|
|**--parameters**|dictionary|Parameters for linked service.|service_now_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|service_now_annotations|
|**--type-properties-username**|any|The user name used to connect to the ServiceNow server for Basic and OAuth2 authentication.|service_now_username|
|**--type-properties-password**|object|The password corresponding to the user name for Basic and OAuth2 authentication.|service_now_password|
|**--type-properties-client-id**|any|The client id for OAuth2 authentication.|service_now_client_id|
|**--type-properties-client-secret**|object|The client secret for OAuth2 authentication.|service_now_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|service_now_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|service_now_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|service_now_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|service_now_encrypted_credential|
### datafactory linked-service service-now update

service-now create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the ServiceNow server. (i.e. :code:`<instance>`.service-now.com)|service_now_endpoint|
|**--type-properties-authentication-type**|choice|The authentication type to use.|service_now_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|service_now_connect_via|
|**--description**|string|Linked service description.|service_now_description|
|**--parameters**|dictionary|Parameters for linked service.|service_now_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|service_now_annotations|
|**--type-properties-username**|any|The user name used to connect to the ServiceNow server for Basic and OAuth2 authentication.|service_now_username|
|**--type-properties-password**|object|The password corresponding to the user name for Basic and OAuth2 authentication.|service_now_password|
|**--type-properties-client-id**|any|The client id for OAuth2 authentication.|service_now_client_id|
|**--type-properties-client-secret**|object|The client secret for OAuth2 authentication.|service_now_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|service_now_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|service_now_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|service_now_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|service_now_encrypted_credential|
### datafactory linked-service sftp create

sftp create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The SFTP server host name. Type: string (or Expression with resultType string).|sftp_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sftp_connect_via|
|**--description**|string|Linked service description.|sftp_description|
|**--parameters**|dictionary|Parameters for linked service.|sftp_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sftp_annotations|
|**--type-properties-port**|any|The TCP port number that the SFTP server uses to listen for client connections. Default value is 22. Type: integer (or Expression with resultType integer), minimum: 0.|sftp_port|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the FTP server.|sftp_authentication_type|
|**--type-properties-user-name**|any|The username used to log on to the SFTP server. Type: string (or Expression with resultType string).|sftp_user_name|
|**--type-properties-password**|object|Password to logon the SFTP server for Basic authentication.|sftp_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sftp_encrypted_credential|
|**--type-properties-private-key-path**|any|The SSH private key file path for SshPublicKey authentication. Only valid for on-premises copy. For on-premises copy with SshPublicKey authentication, either PrivateKeyPath or PrivateKeyContent should be specified. SSH private key should be OpenSSH format. Type: string (or Expression with resultType string).|sftp_private_key_path|
|**--type-properties-private-key-content**|object|Base64 encoded SSH private key content for SshPublicKey authentication. For on-premises copy with SshPublicKey authentication, either PrivateKeyPath or PrivateKeyContent should be specified. SSH private key should be OpenSSH format.|sftp_private_key_content|
|**--type-properties-pass-phrase**|object|The password to decrypt the SSH private key if the SSH private key is encrypted.|sftp_pass_phrase|
|**--type-properties-skip-host-key-validation**|any|If true, skip the SSH host key validation. Default value is false. Type: boolean (or Expression with resultType boolean).|sftp_skip_host_key_validation|
|**--type-properties-host-key-fingerprint**|any|The host key finger-print of the SFTP server. When SkipHostKeyValidation is false, HostKeyFingerprint should be specified. Type: string (or Expression with resultType string).|sftp_host_key_fingerprint|
### datafactory linked-service sftp update

sftp create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The SFTP server host name. Type: string (or Expression with resultType string).|sftp_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sftp_connect_via|
|**--description**|string|Linked service description.|sftp_description|
|**--parameters**|dictionary|Parameters for linked service.|sftp_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sftp_annotations|
|**--type-properties-port**|any|The TCP port number that the SFTP server uses to listen for client connections. Default value is 22. Type: integer (or Expression with resultType integer), minimum: 0.|sftp_port|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the FTP server.|sftp_authentication_type|
|**--type-properties-user-name**|any|The username used to log on to the SFTP server. Type: string (or Expression with resultType string).|sftp_user_name|
|**--type-properties-password**|object|Password to logon the SFTP server for Basic authentication.|sftp_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sftp_encrypted_credential|
|**--type-properties-private-key-path**|any|The SSH private key file path for SshPublicKey authentication. Only valid for on-premises copy. For on-premises copy with SshPublicKey authentication, either PrivateKeyPath or PrivateKeyContent should be specified. SSH private key should be OpenSSH format. Type: string (or Expression with resultType string).|sftp_private_key_path|
|**--type-properties-private-key-content**|object|Base64 encoded SSH private key content for SshPublicKey authentication. For on-premises copy with SshPublicKey authentication, either PrivateKeyPath or PrivateKeyContent should be specified. SSH private key should be OpenSSH format.|sftp_private_key_content|
|**--type-properties-pass-phrase**|object|The password to decrypt the SSH private key if the SSH private key is encrypted.|sftp_pass_phrase|
|**--type-properties-skip-host-key-validation**|any|If true, skip the SSH host key validation. Default value is false. Type: boolean (or Expression with resultType boolean).|sftp_skip_host_key_validation|
|**--type-properties-host-key-fingerprint**|any|The host key finger-print of the SFTP server. When SkipHostKeyValidation is false, HostKeyFingerprint should be specified. Type: string (or Expression with resultType string).|sftp_host_key_fingerprint|
### datafactory linked-service shopify create

shopify create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The endpoint of the Shopify server. (i.e. mystore.myshopify.com)|shopify_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|shopify_connect_via|
|**--description**|string|Linked service description.|shopify_description|
|**--parameters**|dictionary|Parameters for linked service.|shopify_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|shopify_annotations|
|**--type-properties-access-token**|object|The API access token that can be used to access Shopify’s data. The token won't expire if it is offline mode.|shopify_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|shopify_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|shopify_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|shopify_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|shopify_encrypted_credential|
### datafactory linked-service shopify update

shopify create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The endpoint of the Shopify server. (i.e. mystore.myshopify.com)|shopify_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|shopify_connect_via|
|**--description**|string|Linked service description.|shopify_description|
|**--parameters**|dictionary|Parameters for linked service.|shopify_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|shopify_annotations|
|**--type-properties-access-token**|object|The API access token that can be used to access Shopify’s data. The token won't expire if it is offline mode.|shopify_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|shopify_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|shopify_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|shopify_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|shopify_encrypted_credential|
### datafactory linked-service show

show a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-none-match**|string|ETag of the linked service entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory linked-service snowflake create

snowflake create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string of snowflake. Type: string, SecureString.|snowflake_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|snowflake_connect_via|
|**--description**|string|Linked service description.|snowflake_description|
|**--parameters**|dictionary|Parameters for linked service.|snowflake_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|snowflake_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|snowflake_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|snowflake_encrypted_credential|
### datafactory linked-service snowflake update

snowflake create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string of snowflake. Type: string, SecureString.|snowflake_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|snowflake_connect_via|
|**--description**|string|Linked service description.|snowflake_description|
|**--parameters**|dictionary|Parameters for linked service.|snowflake_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|snowflake_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|snowflake_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|snowflake_encrypted_credential|
### datafactory linked-service spark create

spark create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|IP address or host name of the Spark server|spark_host|
|**--type-properties-port**|any|The TCP port that the Spark server uses to listen for client connections.|spark_port|
|**--type-properties-authentication-type**|choice|The authentication method used to access the Spark server.|spark_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|spark_connect_via|
|**--description**|string|Linked service description.|spark_description|
|**--parameters**|dictionary|Parameters for linked service.|spark_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|spark_annotations|
|**--type-properties-server-type**|choice|The type of Spark server.|spark_server_type|
|**--type-properties-thrift-transport-protocol**|choice|The transport protocol to use in the Thrift layer.|spark_thrift_transport_protocol|
|**--type-properties-username**|any|The user name that you use to access Spark Server.|spark_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the Username field|spark_password|
|**--type-properties-http-path**|any|The partial URL corresponding to the Spark server.|spark_http_path|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|spark_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|spark_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|spark_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|spark_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|spark_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|spark_encrypted_credential|
### datafactory linked-service spark update

spark create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|IP address or host name of the Spark server|spark_host|
|**--type-properties-port**|any|The TCP port that the Spark server uses to listen for client connections.|spark_port|
|**--type-properties-authentication-type**|choice|The authentication method used to access the Spark server.|spark_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|spark_connect_via|
|**--description**|string|Linked service description.|spark_description|
|**--parameters**|dictionary|Parameters for linked service.|spark_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|spark_annotations|
|**--type-properties-server-type**|choice|The type of Spark server.|spark_server_type|
|**--type-properties-thrift-transport-protocol**|choice|The transport protocol to use in the Thrift layer.|spark_thrift_transport_protocol|
|**--type-properties-username**|any|The user name that you use to access Spark Server.|spark_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the Username field|spark_password|
|**--type-properties-http-path**|any|The partial URL corresponding to the Spark server.|spark_http_path|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|spark_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|spark_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|spark_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|spark_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|spark_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|spark_encrypted_credential|
### datafactory linked-service sql-server create

sql-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|sql_server_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sql_server_connect_via|
|**--description**|string|Linked service description.|sql_server_description|
|**--parameters**|dictionary|Parameters for linked service.|sql_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sql_server_annotations|
|**--type-properties-user-name**|any|The on-premises Windows authentication user name. Type: string (or Expression with resultType string).|sql_server_user_name|
|**--type-properties-password**|object|The on-premises Windows authentication password.|sql_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sql_server_encrypted_credential|
### datafactory linked-service sql-server update

sql-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|sql_server_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sql_server_connect_via|
|**--description**|string|Linked service description.|sql_server_description|
|**--parameters**|dictionary|Parameters for linked service.|sql_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sql_server_annotations|
|**--type-properties-user-name**|any|The on-premises Windows authentication user name. Type: string (or Expression with resultType string).|sql_server_user_name|
|**--type-properties-password**|object|The on-premises Windows authentication password.|sql_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sql_server_encrypted_credential|
### datafactory linked-service square create

square create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The URL of the Square instance. (i.e. mystore.mysquare.com)|square_host|
|**--type-properties-client-id**|any|The client ID associated with your Square application.|square_client_id|
|**--type-properties-redirect-uri**|any|The redirect URL assigned in the Square application dashboard. (i.e. http://localhost:2500)|square_redirect_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|square_connect_via|
|**--description**|string|Linked service description.|square_description|
|**--parameters**|dictionary|Parameters for linked service.|square_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|square_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your Square application.|square_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|square_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|square_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|square_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|square_encrypted_credential|
### datafactory linked-service square update

square create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The URL of the Square instance. (i.e. mystore.mysquare.com)|square_host|
|**--type-properties-client-id**|any|The client ID associated with your Square application.|square_client_id|
|**--type-properties-redirect-uri**|any|The redirect URL assigned in the Square application dashboard. (i.e. http://localhost:2500)|square_redirect_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|square_connect_via|
|**--description**|string|Linked service description.|square_description|
|**--parameters**|dictionary|Parameters for linked service.|square_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|square_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your Square application.|square_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|square_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|square_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|square_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|square_encrypted_credential|
### datafactory linked-service sybase create

sybase create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-server**|any|Server name for connection. Type: string (or Expression with resultType string).|sybase_server|
|**--type-properties-database**|any|Database name for connection. Type: string (or Expression with resultType string).|sybase_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sybase_connect_via|
|**--description**|string|Linked service description.|sybase_description|
|**--parameters**|dictionary|Parameters for linked service.|sybase_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sybase_annotations|
|**--type-properties-schema**|any|Schema name for connection. Type: string (or Expression with resultType string).|sybase_schema|
|**--type-properties-authentication-type**|choice|AuthenticationType to be used for connection.|sybase_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|sybase_username|
|**--type-properties-password**|object|Password for authentication.|sybase_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sybase_encrypted_credential|
### datafactory linked-service sybase update

sybase create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-server**|any|Server name for connection. Type: string (or Expression with resultType string).|sybase_server|
|**--type-properties-database**|any|Database name for connection. Type: string (or Expression with resultType string).|sybase_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|sybase_connect_via|
|**--description**|string|Linked service description.|sybase_description|
|**--parameters**|dictionary|Parameters for linked service.|sybase_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sybase_annotations|
|**--type-properties-schema**|any|Schema name for connection. Type: string (or Expression with resultType string).|sybase_schema|
|**--type-properties-authentication-type**|choice|AuthenticationType to be used for connection.|sybase_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|sybase_username|
|**--type-properties-password**|object|Password for authentication.|sybase_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sybase_encrypted_credential|
### datafactory linked-service teradata create

teradata create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|teradata_connect_via|
|**--description**|string|Linked service description.|teradata_description|
|**--parameters**|dictionary|Parameters for linked service.|teradata_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|teradata_annotations|
|**--type-properties-connection-string**|any|Teradata ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|teradata_connection_string|
|**--type-properties-server**|any|Server name for connection. Type: string (or Expression with resultType string).|teradata_server|
|**--type-properties-authentication-type**|choice|AuthenticationType to be used for connection.|teradata_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|teradata_username|
|**--type-properties-password**|object|Password for authentication.|teradata_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|teradata_encrypted_credential|
### datafactory linked-service teradata update

teradata create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|teradata_connect_via|
|**--description**|string|Linked service description.|teradata_description|
|**--parameters**|dictionary|Parameters for linked service.|teradata_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|teradata_annotations|
|**--type-properties-connection-string**|any|Teradata ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|teradata_connection_string|
|**--type-properties-server**|any|Server name for connection. Type: string (or Expression with resultType string).|teradata_server|
|**--type-properties-authentication-type**|choice|AuthenticationType to be used for connection.|teradata_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|teradata_username|
|**--type-properties-password**|object|Password for authentication.|teradata_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|teradata_encrypted_credential|
### datafactory linked-service vertica create

vertica create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|vertica_connect_via|
|**--description**|string|Linked service description.|vertica_description|
|**--parameters**|dictionary|Parameters for linked service.|vertica_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|vertica_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|vertica_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|vertica_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|vertica_encrypted_credential|
### datafactory linked-service vertica update

vertica create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|vertica_connect_via|
|**--description**|string|Linked service description.|vertica_description|
|**--parameters**|dictionary|Parameters for linked service.|vertica_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|vertica_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|vertica_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|vertica_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|vertica_encrypted_credential|
### datafactory linked-service web create

web create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties**|object|Web linked service properties.|web_type_properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|web_connect_via|
|**--description**|string|Linked service description.|web_description|
|**--parameters**|dictionary|Parameters for linked service.|web_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|web_annotations|
### datafactory linked-service web update

web create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties**|object|Web linked service properties.|web_type_properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|web_connect_via|
|**--description**|string|Linked service description.|web_description|
|**--parameters**|dictionary|Parameters for linked service.|web_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|web_annotations|
### datafactory linked-service xero create

xero create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The endpoint of the Xero server. (i.e. api.xero.com)|xero_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|xero_connect_via|
|**--description**|string|Linked service description.|xero_description|
|**--parameters**|dictionary|Parameters for linked service.|xero_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|xero_annotations|
|**--type-properties-consumer-key**|object|The consumer key associated with the Xero application.|xero_consumer_key|
|**--type-properties-private-key**|object|The private key from the .pem file that was generated for your Xero private application. You must include all the text from the .pem file, including the Unix line endings(
).|xero_private_key|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|xero_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|xero_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|xero_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|xero_encrypted_credential|
### datafactory linked-service xero update

xero create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-host**|any|The endpoint of the Xero server. (i.e. api.xero.com)|xero_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|xero_connect_via|
|**--description**|string|Linked service description.|xero_description|
|**--parameters**|dictionary|Parameters for linked service.|xero_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|xero_annotations|
|**--type-properties-consumer-key**|object|The consumer key associated with the Xero application.|xero_consumer_key|
|**--type-properties-private-key**|object|The private key from the .pem file that was generated for your Xero private application. You must include all the text from the .pem file, including the Unix line endings(
).|xero_private_key|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|xero_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|xero_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|xero_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|xero_encrypted_credential|
### datafactory linked-service zoho create

zoho create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the Zoho server. (i.e. crm.zoho.com/crm/private)|zoho_endpoint|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|zoho_connect_via|
|**--description**|string|Linked service description.|zoho_description|
|**--parameters**|dictionary|Parameters for linked service.|zoho_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|zoho_annotations|
|**--type-properties-access-token**|object|The access token for Zoho authentication.|zoho_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|zoho_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|zoho_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|zoho_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|zoho_encrypted_credential|
### datafactory linked-service zoho update

zoho create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--type-properties-endpoint**|any|The endpoint of the Zoho server. (i.e. crm.zoho.com/crm/private)|zoho_endpoint|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--connect-via**|object|The integration runtime reference.|zoho_connect_via|
|**--description**|string|Linked service description.|zoho_description|
|**--parameters**|dictionary|Parameters for linked service.|zoho_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|zoho_annotations|
|**--type-properties-access-token**|object|The access token for Zoho authentication.|zoho_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|zoho_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|zoho_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|zoho_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|zoho_encrypted_credential|
### datafactory pipeline create

create a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|
|**--pipeline**|object|Pipeline resource definition.|pipeline|
|**--if-match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory pipeline create-run

create-run a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|
|**--reference-pipeline-run-id**|string|The pipeline run identifier. If run ID is specified the parameters of the specified run will be used to create a new run.|reference_pipeline_run_id|
|**--is-recovery**|boolean|Recovery mode flag. If recovery mode is set to true, the specified referenced pipeline run and the new run will be grouped under the same groupId.|is_recovery|
|**--start-activity-name**|string|In recovery mode, the rerun will start from this activity. If not specified, all activities will run.|start_activity_name|
|**--start-from-failure**|boolean|In recovery mode, if set to true, the rerun will start from failed activities. The property will be used only if startActivityName is not specified.|start_from_failure|
|**--parameters**|dictionary|Parameters of the pipeline run. These parameters will be used only if the runId is not specified.|parameters|
### datafactory pipeline delete

delete a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|
### datafactory pipeline list

list a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory pipeline show

show a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|
|**--if-none-match**|string|ETag of the pipeline entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory pipeline update

create a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|
|**--pipeline**|object|Pipeline resource definition.|pipeline|
|**--if-match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory pipeline-run cancel

cancel a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--run-id**|string|The pipeline run identifier.|run_id|
|**--is-recursive**|boolean|If true, cancel all the Child pipelines that are triggered by the current pipeline.|is_recursive|
### datafactory pipeline-run query-by-factory

query-by-factory a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|
|**--filters**|array|List of filters.|filters|
|**--order-by**|array|List of OrderBy option.|order_by|
### datafactory pipeline-run show

show a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--run-id**|string|The pipeline run identifier.|run_id|
### datafactory trigger create

create a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
|**--properties**|object|Properties of the trigger.|properties|
|**--if-match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory trigger delete

delete a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger get-event-subscription-status

get-event-subscription-status a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger list

list a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory trigger query-by-factory

query-by-factory a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|
|**--parent-trigger-name**|string|The name of the parent TumblingWindowTrigger to get the child rerun triggers|parent_trigger_name|
### datafactory trigger show

show a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
|**--if-none-match**|string|ETag of the trigger entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory trigger start

start a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger stop

stop a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger subscribe-to-event

subscribe-to-event a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger unsubscribe-from-event

unsubscribe-from-event a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger update

create a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
|**--properties**|object|Properties of the trigger.|properties|
|**--if-match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory trigger-run query-by-factory

query-by-factory a datafactory trigger-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|
|**--filters**|array|List of filters.|filters|
|**--order-by**|array|List of OrderBy option.|order_by|
### datafactory trigger-run rerun

rerun a datafactory trigger-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
|**--run-id**|string|The pipeline run identifier.|run_id|