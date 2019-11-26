# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from xml.sax.saxutils import escape as xml_escape
from datetime import date

try:
    from xml.etree import cElementTree as ETree
except ImportError:
    from xml.etree import ElementTree as ETree
from ..common._common_conversion import (
    _encode_base64,
    _str,
)
from ..common._serialization import (
    _to_utc_datetime,
)
from ..common._error import (
    _validate_not_none,
    _ERROR_START_END_NEEDED_FOR_MD5,
    _ERROR_RANGE_TOO_LARGE_FOR_MD5,
)
from ._error import (
    _ERROR_PAGE_BLOB_START_ALIGNMENT,
    _ERROR_PAGE_BLOB_END_ALIGNMENT,
    _ERROR_INVALID_BLOCK_ID,
)
from io import BytesIO

_REQUEST_DELIMITER_PREFIX = "batch_"
_HTTP1_1_IDENTIFIER = "HTTP/1.1"
_HTTP_LINE_ENDING = "\r\n"

def _get_path(container_name=None, blob_name=None):
    '''
    Creates the path to access a blob resource.

    container_name:
        Name of container.
    blob_name:
        The path to the blob.
    '''
    if container_name and blob_name:
        return '/{0}/{1}'.format(
            _str(container_name),
            _str(blob_name))
    elif container_name:
        return '/{0}'.format(_str(container_name))
    else:
        return '/'


def _validate_and_add_cpk_headers(request, encryption_key, protocol):
    if encryption_key is None:
        return

    if protocol.lower() != 'https':
        raise ValueError("Customer provided encryption key must be used over HTTPS.")

    request.headers['x-ms-encryption-key'] = encryption_key.key_value
    request.headers['x-ms-encryption-key-sha256'] = encryption_key.key_hash
    request.headers['x-ms-encryption-algorithm'] = encryption_key.algorithm


def _validate_and_format_range_headers(request, start_range, end_range, start_range_required=True,
                                       end_range_required=True, check_content_md5=False, align_to_page=False,
                                       range_header_name='x-ms-range'):
    # If end range is provided, start range must be provided
    if start_range_required or end_range is not None:
        _validate_not_none('start_range', start_range)
    if end_range_required:
        _validate_not_none('end_range', end_range)

    # Page ranges must be 512 aligned
    if align_to_page:
        if start_range is not None and start_range % 512 != 0:
            raise ValueError(_ERROR_PAGE_BLOB_START_ALIGNMENT)
        if end_range is not None and end_range % 512 != 511:
            raise ValueError(_ERROR_PAGE_BLOB_END_ALIGNMENT)

    # Format based on whether end_range is present
    request.headers = request.headers or {}
    if end_range is not None:
        request.headers[range_header_name] = 'bytes={0}-{1}'.format(start_range, end_range)
    elif start_range is not None:
        request.headers[range_header_name] = "bytes={0}-".format(start_range)

    # Content MD5 can only be provided for a complete range less than 4MB in size
    if check_content_md5:
        if start_range is None or end_range is None:
            raise ValueError(_ERROR_START_END_NEEDED_FOR_MD5)
        if end_range - start_range > 4 * 1024 * 1024:
            raise ValueError(_ERROR_RANGE_TOO_LARGE_FOR_MD5)

        request.headers['x-ms-range-get-content-md5'] = 'true'


def _convert_block_list_to_xml(block_id_list):
    '''
    <?xml version="1.0" encoding="utf-8"?>
    <BlockList>
      <Committed>first-base64-encoded-block-id</Committed>
      <Uncommitted>second-base64-encoded-block-id</Uncommitted>
      <Latest>third-base64-encoded-block-id</Latest>
    </BlockList>

    Convert a block list to xml to send.

    block_id_list:
        A list of BlobBlock containing the block ids and block state that are used in put_block_list.
    Only get block from latest blocks.
    '''
    if block_id_list is None:
        return ''

    block_list_element = ETree.Element('BlockList')

    # Enabled
    for block in block_id_list:
        if block.id is None:
            raise ValueError(_ERROR_INVALID_BLOCK_ID)
        id = xml_escape(_str(format(_encode_base64(block.id))))
        ETree.SubElement(block_list_element, block.state).text = id

    # Add xml declaration and serialize
    try:
        stream = BytesIO()
        ETree.ElementTree(block_list_element).write(stream, xml_declaration=True, encoding='utf-8', method='xml')
    except:
        raise
    finally:
        output = stream.getvalue()
        stream.close()

    # return xml value
    return output


def _convert_delegation_key_info_to_xml(start_time, expiry_time):
    """
    <?xml version="1.0" encoding="utf-8"?>
    <KeyInfo>
        <Start> String, formatted ISO Date </Start>
        <Expiry> String, formatted ISO Date </Expiry>
    </KeyInfo>

    Convert key info to xml to send.
    """
    if start_time is None or expiry_time is None:
        raise ValueError("delegation key start/end times are required")

    key_info_element = ETree.Element('KeyInfo')
    ETree.SubElement(key_info_element, 'Start').text = \
        _to_utc_datetime(start_time) if isinstance(start_time, date) else start_time
    ETree.SubElement(key_info_element, 'Expiry').text = \
        _to_utc_datetime(expiry_time) if isinstance(expiry_time, date) else expiry_time

    # Add xml declaration and serialize
    try:
        stream = BytesIO()
        ETree.ElementTree(key_info_element).write(stream, xml_declaration=True, encoding='utf-8', method='xml')
    finally:
        output = stream.getvalue()
        stream.close()

    # return xml value
    return output


def _serialize_batch_body(requests, batch_id):
    """
    --<delimiter>
    <subrequest>
    --<delimiter>
    <subrequest>    (repeated as needed)
    --<delimiter>--

    Serializes the requests in this batch to a single HTTP mixed/multipart body.

    :param list(class:`~..common._http.HTTPRequest`) requests:
        a list of sub-request for the batch request
    :param str batch_id:
        to be embedded in batch sub-request delimiter
    :return: The body bytes for this batch.
    """

    if requests is None or len(requests) is 0:
        raise ValueError('Please provide sub-request(s) for this batch request')

    delimiter_bytes = (_get_batch_request_delimiter(batch_id, True, False) + _HTTP_LINE_ENDING).encode('utf-8')
    newline_bytes = _HTTP_LINE_ENDING.encode('utf-8')
    batch_body = list()

    for request in requests:
        batch_body.append(delimiter_bytes)
        batch_body.append(_make_body_from_sub_request(request))
        batch_body.append(newline_bytes)

    batch_body.append(_get_batch_request_delimiter(batch_id, True, True).encode('utf-8'))
    # final line of body MUST have \r\n at the end, or it will not be properly read by the service
    batch_body.append(newline_bytes)

    return bytes().join(batch_body)


def _get_batch_request_delimiter(batch_id, is_prepend_dashes=False, is_append_dashes=False):
    """
    Gets the delimiter used for this batch request's mixed/multipart HTTP format.

    :param batch_id Randomly generated id
    :param is_prepend_dashes Whether to include the starting dashes. Used in the body, but non on defining the delimiter.
    :param is_append_dashes  Whether to include the ending dashes. Used in the body on the closing delimiter only.
    :return: The delimiter, WITHOUT a trailing newline.
    """

    prepend_dashes = '--' if is_prepend_dashes else ''
    append_dashes = '--' if is_append_dashes else ''

    return prepend_dashes + _REQUEST_DELIMITER_PREFIX + batch_id + append_dashes


def _make_body_from_sub_request(sub_request):
    """
     Content-Type: application/http
     Content-ID: <sequential int ID>
     Content-Transfer-Encoding: <value> (if present)

     <verb> <path><query> HTTP/<version>
     <header key>: <header value> (repeated as necessary)
     Content-Length: <value>
     (newline if content length > 0)
     <body> (if content length > 0)

     Serializes an http request.

     :param :class:`~..common._http.HTTPRequest` sub_request Request to serialize.
     :return: The serialized sub-request in bytes
     """

    # put the sub-request's headers into a list for efficient str concatenation
    sub_request_body = list()

    # get headers for ease of manipulation; remove headers as they are used
    headers = sub_request.headers

    # append opening headers
    sub_request_body.append("Content-Type: application/http")
    sub_request_body.append(_HTTP_LINE_ENDING)

    sub_request_body.append("Content-ID: ")
    sub_request_body.append(headers.pop("Content-ID", ""))
    sub_request_body.append(_HTTP_LINE_ENDING)

    sub_request_body.append("Content-Transfer-Encoding: ")
    sub_request_body.append(headers.pop("Content-Transfer-Encoding", ""))
    sub_request_body.append(_HTTP_LINE_ENDING)

    # append blank line
    sub_request_body.append(_HTTP_LINE_ENDING)

    # append HTTP verb and path and query and HTTP version
    sub_request_body.append(sub_request.method)
    sub_request_body.append(' ')
    sub_request_body.append(sub_request.path)
    sub_request_body.append("" if sub_request.query is None else '?' + _serialize_query(sub_request.query))
    sub_request_body.append(' ')
    sub_request_body.append(_HTTP1_1_IDENTIFIER)
    sub_request_body.append(_HTTP_LINE_ENDING)

    # append remaining headers (this will set the Content-Length, as it was set on `sub-request`)
    for header_name, header_value in headers.items():
        if header_value is not None:
            sub_request_body.append(header_name)
            sub_request_body.append(": ")
            sub_request_body.append(header_value)
            sub_request_body.append(_HTTP_LINE_ENDING)

    # finished if no body
    if sub_request.body is None:
        return sub_request_body.encode('utf-8')

    # append blank line
    sub_request_body.append(_HTTP_LINE_ENDING)

    sub_request_body.append(sub_request.body)

    return ''.join(sub_request_body).encode('utf-8')


def _serialize_query(query):
    serialized_query = []
    for query_key, query_value in query.items():
        if query_value is not None:
            serialized_query.append(query_key)
            serialized_query.append("=")
            serialized_query.append(query_value)
            serialized_query.append("&")

    if len(serialized_query) is not 0:
        del serialized_query[-1]

    return ''.join(serialized_query)


# TODO to be removed after service update
def _add_file_or_directory_properties_header(properties_dict, request):
    if properties_dict:
        if not request.headers:
            request.headers = {}
        request.headers['x-ms-properties'] = \
            ",".join(["{}={}".format(str(name), _encode_base64(value)) for name, value in properties_dict.items()])
