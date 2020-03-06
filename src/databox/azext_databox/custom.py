# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
# pylint: disable=too-many-branches


def create_databox_job(client,
                       resource_group_name,
                       job_name,
                       location,
                       sku,
                       contact_name,
                       phone,
                       city,
                       email_list,
                       street_address1,
                       postal_code,
                       country,
                       state_or_province,
                       destination_account_details,
                       expected_data_size=None,
                       tags=None,
                       mobile=None,
                       street_address2=None,
                       street_address3=None,
                       company_name=None,):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    body.setdefault('sku', {})['name'] = sku  # str
    body.setdefault('details', {})['job_details_type'] = sku
    body.setdefault('details', {})['expected_data_size_in_terabytes'] = expected_data_size
    body.setdefault('details', {}).setdefault('contact_details', {})['contact_name'] = contact_name  # str
    body.setdefault('details', {}).setdefault('contact_details', {})['phone'] = phone  # str
    body.setdefault('details', {}).setdefault('contact_details', {})['mobile'] = mobile  # str
    body.setdefault('details', {}).setdefault('contact_details', {})['email_list'] = email_list
    body.setdefault('details', {}).setdefault('shipping_address', {})['street_address1'] = street_address1  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})['street_address2'] = street_address2  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})['street_address3'] = street_address3  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})['city'] = city  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})['state_or_province'] = state_or_province  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})['country'] = country  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})['postal_code'] = postal_code  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})['company_name'] = company_name  # str

    body.setdefault('details', {})['destination_account_details'] = destination_account_details

    return client.create(resource_group_name=resource_group_name, job_name=job_name, job_resource=body)


def update_databox_job(client,
                       resource_group_name,
                       job_name,
                       contact_name=None,
                       phone=None,
                       email_list=None,
                       street_address1=None,
                       postal_code=None,
                       country=None,
                       mobile=None,
                       city=None,
                       street_address2=None,
                       street_address3=None,
                       state_or_province=None,
                       company_name=None):
    job_resource = get_databox_job(client, resource_group_name, job_name)
    job_details = job_resource.details
    contact_details = job_details.contact_details
    shipping_address = job_details.shipping_address

    body = {}
    body.setdefault('details', {}).setdefault('contact_details', {})[
        'contact_name'] = contact_details.contact_name if contact_name is None else contact_name  # str
    body.setdefault('details', {}).setdefault('contact_details', {})[
        'phone'] = contact_details.phone if phone is None else phone  # str
    body.setdefault('details', {}).setdefault('contact_details', {})[
        'mobile'] = contact_details.mobile if mobile is None else mobile  # str
    body.setdefault('details', {}).setdefault('contact_details', {})[
        'email_list'] = contact_details.email_list if email_list is None else email_list
    body.setdefault('details', {}).setdefault('shipping_address', {})[
        'street_address1'] = shipping_address.street_address1 if street_address1 is None else street_address1  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})[
        'street_address2'] = shipping_address.street_address2 if street_address2 is None else street_address2  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})[
        'street_address3'] = shipping_address.street_address3 if street_address3 is None else street_address3  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})[
        'city'] = shipping_address.city if city is None else city  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})[
        'state_or_province'] = shipping_address.state_or_province if state_or_province is None else state_or_province  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})[
        'country'] = shipping_address.country if country is None else country  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})[
        'postal_code'] = shipping_address.postal_code if postal_code is None else postal_code  # str
    body.setdefault('details', {}).setdefault('shipping_address', {})[
        'company_name'] = shipping_address.company_name if company_name is None else company_name  # str

    return client.update(resource_group_name=resource_group_name, job_name=job_name, job_resource_update_parameter=body)


def delete_databox_job(client,
                       resource_group_name,
                       job_name):
    return client.delete(resource_group_name=resource_group_name, job_name=job_name)


def get_databox_job(client,
                    resource_group_name,
                    job_name):
    return client.get(resource_group_name=resource_group_name, job_name=job_name, expand='details')


def list_databox_job(client,
                     resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list()


def cancel_databox_job(client,
                       resource_group_name,
                       job_name,
                       reason):
    return client.cancel(resource_group_name=resource_group_name, job_name=job_name, reason=reason)


def list_credentials_databox_job(client,
                                 resource_group_name,
                                 job_name):
    return client.list_credentials(resource_group_name=resource_group_name, job_name=job_name)
