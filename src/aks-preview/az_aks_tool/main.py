# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import os
import sys
import logging

import az_aks_tool.const as const
import az_aks_tool.log as log
import az_aks_tool.utils as utils
import az_aks_tool.cli as cli
import az_aks_tool.ext as ext
import az_aks_tool.index as index
import az_aks_tool.run as run


def init_argparse(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", type=str, default="all",
                        help="test mode ('cli', 'ext', 'all')")
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
    parser.add_argument("-ne", "--no-exitfirst", action="store_true",
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
    parser.add_argument("--log-file", type=str,
                        default="az_aks_tool.log", help="log filename")
    args = parser.parse_args(args)
    return args


def main():
    # parse args
    print("raw args: {}".format(sys.argv))
    args = init_argparse(sys.argv[1:])

    # setup logger
    root_module_name = log.parse_module_name(levels=1)
    log.setup_logging(root_module_name, os.path.join(
        args.report_path, args.log_file))
    logger = logging.getLogger("{}.{}".format(root_module_name, __name__))

    # check test cases
    test_cases = args.tests
    ext_matrix_file_path = args.ext_matrix
    cli_matrix_file_path = args.cli_matrix
    if not test_cases and not utils.check_file_existence(ext_matrix_file_path) and not utils.check_file_existence(cli_matrix_file_path):
        sys.exit(
            "At least one of 'tests', 'cli_matrix' and 'ext_matrix' must be provided!")

    # prepare pytest args
    pytest_args = []
    if not args.series and args.parallelism:
        pytest_args.append("-n {}".format(args.parallelism))
    pytest_args.append("--json-report")
    pytest_args.append("--reruns {}".format(args.reruns))
    pytest_args.append("--capture {}".format(args.capture))
    pytest_args = [" ".join(pytest_args)]
    logger.info("pytest_args: {}".format(pytest_args))

    # check mode & collect module data
    enable_cli = False
    enable_ext = False
    module_data = {}
    if args.mode == "cli" or args.mode == "all":
        enable_cli = True
        module_data[const.ACS_MOD_NAME] = cli.get_cli_mod_data()
        cli_test_index = cli.get_cli_test_index(module_data)

    if args.mode == "ext" or args.mode == "all":
        enable_ext = True
        module_data[const.AKS_PREVIEW_MOD_NAME] = ext.get_ext_mod_data()
        ext_test_index = ext.get_ext_test_index(module_data)

    # build test index
    logger.info("Building test index...")
    test_index = index.build_test_index(module_data)

    # cli matrix test
    if enable_cli:
        cli_qualified_test_cases = utils.get_fully_qualified_test_cases(
            cli_test_index, cli_matrix_file_path, const.ACS_MOD_NAME, args.cli_coverage, args.cli_filter)
        logger.info("Perform following cli tests: {}".format(
            cli_qualified_test_cases))
        exit_code = run.run_tests(cli_qualified_test_cases, test_index, mode="cli", base_path=args.report_path, xml_file=args.xml_file, json_file=args.json_report_file, in_series=args.series,
                                  run_live=args.live, no_exit_first=args.no_exitfirst, pytest_args=pytest_args)
        if exit_code != 0:
            sys.exit("CLI test failed!")

    # ext matrix test
    if enable_ext:
        ext_qualified_test_cases = utils.get_fully_qualified_test_cases(
            ext_test_index, ext_matrix_file_path, const.AKS_PREVIEW_MOD_NAME, args.ext_coverage, args.ext_filter)
        logger.info("Perform following ext tests: {}".format(
            ext_qualified_test_cases))
        exit_code = run.run_tests(ext_qualified_test_cases, test_index, mode="ext", base_path=args.report_path, xml_file=args.xml_file, json_file=args.json_report_file, in_series=args.series,
                                  run_live=args.live, no_exit_first=args.no_exitfirst, pytest_args=pytest_args)
        if exit_code != 0:
            sys.exit("EXT test failed!")

    # raw tests
    if test_cases and len(test_cases) > 0:
        logger.info("Perform following raw tets: {}".format(test_cases))
        exit_code = run_tests(test_cases, test_index, mode="raw", base_path=args.report_path, xml_file=args.xml_file, json_file=args.json_report_file, in_series=args.series,
                              run_live=args.live, no_exit_first=args.no_exitfirst, pytest_args=pytest_args)
        if exit_code != 0:
            sys.exit("Raw test failed!")


if __name__ == "__main__":
    main()
