# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re
import requests
import json
import sys

from azure.cli.core.azclierror import InvalidArgumentValueError
from collections import defaultdict
from knack.log import get_logger
from knack.util import CLIError
from six.moves.urllib import parse

from .writer import DefaultWriter


logger = get_logger(__name__)


class LogStreamBaseQueryOptions:  # pylint: disable=too-few-public-methods
    def __init__(self, follow, lines, since, limit):
        self.follow = follow
        self.lines = lines
        self.since = since
        self.limit = limit


def attach_logs_query_options(url, queryOptions: LogStreamBaseQueryOptions):
    params = {}
    params["tailLines"] = queryOptions.lines
    params["limitBytes"] = queryOptions.limit
    if queryOptions.since:
        params["sinceSeconds"] = queryOptions.since
    if queryOptions.follow:
        params["follow"] = True

    url += "?{}".format(parse.urlencode(params)) if params else ""
    return url


# pylint: disable=bare-except, too-many-statements
def iter_lines(response, limit=2 ** 20, chunk_size=None):
    '''
    Returns a line iterator from the response content. If no line ending was found and the buffered content size is
    larger than the limit, the buffer will be yielded directly.
    '''
    buffer = []
    total = 0
    for content in response.iter_content(chunk_size=chunk_size):
        if not content:
            if len(buffer) > 0:
                yield b''.join(buffer)
            break

        start = 0
        while start < len(content):
            line_end = content.find(b'\n', start)
            should_print = False
            if line_end < 0:
                next = (content if start == 0 else content[start:])
                buffer.append(next)
                total += len(next)
                start = len(content)
                should_print = total >= limit
            else:
                buffer.append(content[start:line_end + 1])
                start = line_end + 1
                should_print = True

            if should_print:
                yield b''.join(buffer)
                buffer.clear()
                total = 0


def log_stream_from_url(url, auth, format_json, exceptions, writer=DefaultWriter(), chunk_size=None, stderr=False):
    logger_seg_regex = re.compile(r'([^\.])[^\.]+\.')

    def build_log_shortener(length):
        if length <= 0:
            raise InvalidArgumentValueError('Logger length in `logger{length}` should be positive')

        def shortener(record):
            '''
            Try shorten the logger property to the specified length before feeding it to the formatter.
            '''
            logger_name = record.get('logger', None)
            if logger_name is None:
                return record

            # first, try to shorten the package name to one letter, e.g.,
            #     org.springframework.cloud.netflix.eureka.config.DiscoveryClientOptionalArgsConfiguration
            # to: o.s.c.n.e.c.DiscoveryClientOptionalArgsConfiguration
            while len(logger_name) > length:
                logger_name, count = logger_seg_regex.subn(r'\1.', logger_name, 1)
                if count < 1:
                    break

            # then, cut off the leading packages if necessary
            logger_name = logger_name[-length:]
            record['logger'] = logger_name
            return record

        return shortener

    def build_formatter():
        '''
        Build the log line formatter based on the format_json argument.
        '''
        nonlocal format_json

        def identity(o):
            return o

        if format_json is None or len(format_json) == 0:
            return identity

        logger_regex = re.compile(r'\blogger\{(\d+)\}')
        match = logger_regex.search(format_json)
        pre_processor = identity
        if match:
            length = int(match[1])
            pre_processor = build_log_shortener(length)
            format_json = logger_regex.sub('logger', format_json, 1)

        first_exception = True

        def format_line(line):
            nonlocal first_exception
            try:
                log_record = json.loads(line)
                # Add n=\n so that in Windows CMD it's easy to specify customized format with line ending
                # e.g., "{timestamp} {message}{n}"
                # (Windows CMD does not escape \n in string literal.)
                return format_json.format_map(pre_processor(defaultdict(str, n="\n", **log_record)))
            except:
                if first_exception:
                    # enable this format error logging only with --verbose
                    logger.info("Failed to format log line '{}'".format(line), exc_info=sys.exc_info())
                    first_exception = False
                return line

        return format_line

    try:
        with requests.get(url, stream=True, auth=auth) as response:
            try:
                if response.status_code != 200:
                    failure_reason = response.reason
                    if response.content:
                        if isinstance(response.content, bytes):
                            failure_reason = "{}:{}".format(failure_reason, response.content.decode('utf-8'))
                        else:
                            failure_reason = "{}:{}".format(failure_reason, response.content)
                    raise CLIError("Failed to access the url '{}' with status code '{}' and reason '{}'".format(
                        url, response.status_code, failure_reason))
                std_encoding = sys.stdout.encoding

                formatter = build_formatter()

                for line in iter_lines(response, chunk_size=chunk_size):
                    decoded = (line.decode(encoding='utf-8', errors='replace')
                               .encode(std_encoding, errors='replace')
                               .decode(std_encoding, errors='replace'))
                    if stderr:
                        writer.write(formatter(decoded), end='', file=sys.stderr)
                    else:
                        writer.write(formatter(decoded), end='')
            except CLIError as e:
                exceptions.append(e)
    except requests.exceptions.ConnectionError as e:
        try:
            message = str(e)
            if "getaddrinfo failed" in message:
                exceptions.append(CLIError("Failed to connect to \"{}\" due to getaddrinfo failed. "
                                           "For an Azure Spring Apps instance deployed in a custom virtual network, "
                                           "you can access log streaming by default from a private network. "
                                           "But if you want to access real-time app logs from a public network, "
                                           "please make sure 'Dataplane resources on public network' is enabled. "
                                           "Learn more https://aka.ms/asa/component/logstream/vnet"
                                           .format(url)))
            else:
                exceptions.append(CLIError("Failed to connecto to \"{}\" due to \"{}\"".format(url, message)))
        except Exception:
            exceptions.append(CLIError("Failed to connect to '{}'.".format(url)))
