# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import os
import sys
import logging
from azdev.operations.testtool import run_tests
from azdev.utilities import EXTENSION_PREFIX

import azcli_aks_live_test.az_aks_tool.utils as utils
import azcli_aks_live_test.az_aks_tool.ext as ext
from azcli_aks_live_test.az_aks_tool.log import setup_logging

# const
AKS_PREVIEW_MOD_NAME = EXTENSION_PREFIX + "aks_preview"  # azext_aks_preview


def init_argparse(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tests", nargs='+', help="test case names")
    parser.add_argument("-cm", "--cli-matrix",  type=str,
                        help="full path to cli test matrix")
    parser.add_argument("-cc", "--cli-coverage", nargs="+",
                        help="cli test extra coverage")
    parser.add_argument("-cf", "--cli-filter", nargs="+",
                        help="cli test filter")
    parser.add_argument("-em", "--ext-matrix",  type=str,
                        help="full path to extension test matrix")
    parser.add_argument("-ec", "--ext-coverage", nargs="+",
                        help="extension test extra coverage")
    parser.add_argument("-ef", "--ext-filter", nargs="+",
                        help="extension test filter")
    parser.add_argument("-s", "--series", action="store_true",
                        default=False, help="series test")
    parser.add_argument("-l", "--live", action="store_true",
                        default=False, help="live test")
    parser.add_argument("-d", "--discover", action="store_true",
                        default=False, help="discover test index")
    parser.add_argument("--no-exitfirst", action="store_true",
                        default=False, help="no exit first")
    parser.add_argument("--xml-file", type=str,
                        default="azcli_aks_runner.xml", help="junit/xml report filename")
    parser.add_argument("-n", "--parallelism", type=str,
                        default="8", help="test parallelism")
    parser.add_argument("-p", "--report-path", type=str,
                        required=True, help="report path")
    parser.add_argument("-f", "--json-report-file", type=str,
                        default="azcli_aks_runner_report.json", help="json report filename")
    parser.add_argument("-r", "--reruns", type=str,
                        default="3", help="rerun times")
    parser.add_argument("-c", "--capture", type=str,
                        default="sys", help="test capture")
    # parser.add_argument("-a", "--pytest-args",
    #                     nargs=argparse.REMAINDER, help="pytest args")
    args = parser.parse_args(args)
    return args


def main():
    # setup logger
    setup_logging()
    logger = logging.getLogger(__name__)

    # parse args
    logger.info("raw args: {}".format(sys.argv))
    args = init_argparse(sys.argv[1:])
    
    # test cases
    test_cases = args.tests
    ext_matrix_file_path = args.ext_matrix
    cli_matrix_file_path = args.cli_matrix
    if not test_cases and not utils.check_file_existence(ext_matrix_file_path) and not utils.check_file_existence(cli_matrix_file_path):
        sys.exit(
            "At least one of 'tests', 'cli_matrix' and 'ext_matrix' must be provided!")

    # report file
    json_report_file_full_path = os.path.realpath(os.path.join(
        args.report_path, args.json_report_file))
    logger.info("json report file full path: {}".format(json_report_file_full_path))
    xml_path = os.path.realpath(os.path.join(args.report_path, args.xml_file))
    logger.info("junit/xml report file full path: {}".format(xml_path))

    # pytest args
    pytest_args = []
    if not args.series and args.parallelism:
        pytest_args.append("-n {}".format(args.parallelism))
    pytest_args.append("--json-report")
    pytest_args.append("--json-report-file {}".format(json_report_file_full_path))
    pytest_args.append("--reruns {}".format(args.reruns))
    pytest_args.append("--capture {}".format(args.capture))
    pytest_args = [" ".join(pytest_args)]
    logger.info("pytest_args: {}".format(pytest_args))

    # ext matrix
    if utils.check_file_existence(ext_matrix_file_path):
        ext_test_index = ext.get_ext_test_index(AKS_PREVIEW_MOD_NAME)
        ext_matrix = utils.get_test_matrix(ext_matrix_file_path)
        ext_test_cases = ext.get_ext_test_cases(
            ext_test_index, ext_matrix, args.ext_coverage)
        ext_exclude_test_cases = ext.get_ext_exclude_test_cases(ext_test_index,
                                                                ext_matrix, args.ext_filter)
        ext_filtered_test_cases = utils.get_filted_test_cases(
            ext_test_cases, ext_exclude_test_cases)
        # add prefix
        ext_qualified_test_cases = utils.decorate_qualified_prefix(
            ext_filtered_test_cases, AKS_PREVIEW_MOD_NAME)
        logger.info("According to 'ext_matrix' and filters, we get {} cases, need to exclude {} cases, finally get {} cases!".format(
            len(ext_test_cases), len(ext_exclude_test_cases), len(ext_filtered_test_cases)))
        logger.info("Perform following tests: {}".format(ext_qualified_test_cases))
        run_tests(ext_qualified_test_cases, xml_path=xml_path, discover=args.discover, in_series=args.series,
                  run_live=args.live, no_exit_first=args.no_exitfirst, pytest_args=pytest_args)

    # cli matrix
    if utils.check_file_existence(cli_matrix_file_path):
        logger.warning("Currently not support!")
        pass

    # tests
    if test_cases:
        logger.info("Accroding to 'tests', we get {} cases".format(len(test_cases)))
        logger.info("Perform following tets: {}".format(test_cases))
        run_tests(test_cases, xml_path=xml_path, discover=args.discover, in_series=args.series,
                  run_live=args.live, no_exit_first=args.no_exitfirst, pytest_args=pytest_args)


if __name__ == "__main__":
    main()
