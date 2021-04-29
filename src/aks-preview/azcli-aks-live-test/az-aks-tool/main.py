import argparse
import glob
import os
from azdev.operations.testtool import _discover_module_tests, run_tests
from azdev.utilities import EXTENSION_PREFIX, get_path_table, get_name_index

from utils import get_test_matrix, decorate_qualified_prefix, check_file_existence

# const
EXTENSION_NAME = "aks-preview"
AKS_PREVIEW_MOD_NAME = EXTENSION_PREFIX + "aks_preview"  # azext_aks_preview


def init_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tests", nargs='+', help="test case names")
    parser.add_argument("-cm", "--cli-matrix",  type=str,
                        help="cli test matrix")
    parser.add_argument("-em", "--ext-matrix",  type=str,
                        help="extension test matrix")
    parser.add_argument("-emf", "--ext-matrix-filter", nargs="+",
                        help="extension test matrix")
    parser.add_argument("-s", "--series", action="store_true",
                        default=False, help="series test")
    parser.add_argument("-l", "--live", action="store_true",
                        default=False, help="live test")
    parser.add_argument("-d", "--discover", action="store_true",
                        default=False, help="discover test index")
    parser.add_argument("--no-exitfirst", action="store_true",
                        default=False, help="no exit first")
    parser.add_argument("--xml-path", type=str,
                        default="azcli_aks_runner.xml", help="junit log path")
    parser.add_argument("-n", "--parallelism", type=str,
                        default="8", help="test parallelism")
    parser.add_argument("-p", "--json-report-path", type=str,
                        required=True, help="json report path")
    parser.add_argument("-f", "--json-report-file", type=str,
                        default="azcli_aks_runner_report.json", help="json report filename")
    parser.add_argument("-r", "--reruns", type=str,
                        default="3", help="rerun times")
    parser.add_argument("-c", "--capture", type=str,
                        default="sys", help="test capture")
    # parser.add_argument("-a", "--pytest-args",
    #                     nargs=argparse.REMAINDER, help="pytest args")
    args = parser.parse_args()
    return args


def get_ext_test_index():
    # path table & name index
    path_table = get_path_table()
    command_modules = path_table['mod']
    extensions = path_table["ext"]
    inverse_name_table = get_name_index(invert=True)

    # import_name & mod_data
    aks_preview_mod_path = extensions[AKS_PREVIEW_MOD_NAME]
    glob_pattern = os.path.normcase(
        os.path.join("{}*".format(EXTENSION_PREFIX)))
    file_path = glob.glob(os.path.join(aks_preview_mod_path, glob_pattern))[0]
    import_name = os.path.basename(file_path)
    mod_data = {
        "alt_name": inverse_name_table[AKS_PREVIEW_MOD_NAME],
        "filepath": os.path.join(file_path, "tests", "latest"),
        "base_path": "{}.tests.{}".format(import_name, "latest"),
        "files": {}
    }

    # azdev hook
    ext_test = _discover_module_tests(import_name, mod_data)
    ext_test_index = ext_test["files"]
    return ext_test_index


def get_ext_test_cases(ext_test_index, ext_matrix):
    ext_test_cases = []
    ext_coverage = ext_matrix["coverage"]
    for fileName, className in ext_coverage.items():
        for c in className:
            ext_test_cases.extend(ext_test_index[fileName][c])
    return ext_test_cases


def get_ext_exclude_test_cases(ext_matrix, ext_matrix_filter):
    ext_exclude_test_cases = []
    ext_exclude = ext_matrix["exclude"]
    if not ext_matrix_filter or "all" in ext_matrix_filter:
        for k, v in ext_exclude.items():
            ext_exclude_test_cases.extend(v)
    else:
        for k, v in ext_exclude.items():
            if k in ext_matrix_filter:
                ext_exclude_test_cases.extend(v)
    return ext_exclude_test_cases


def get_ext_filted_test_cases(ext_test_cases, ext_exclude_test_cases):
    ext_filtered_test_cases = [
        x for x in ext_test_cases if x not in ext_exclude_test_cases]
    return ext_filtered_test_cases


def main():
    args = init_argparse()

    import sys
    print(sys.argv)
    print(args)
    print(os.getcwd())

    # test cases
    test_cases = args.tests
    ext_matrix_file_path = args.ext_matrix
    cli_matrix_file_path = args.cli_matrix
    if not test_cases and not check_file_existence(ext_matrix_file_path) and not check_file_existence(cli_matrix_file_path):
        print("At least one of 'tests', 'cli_matrix' and 'ext_matrix' must be provided!")
        exit(-1)

    # report file
    report_file_full_path = os.path.realpath(os.path.join(
        args.json_report_path, args.json_report_file))
    print("report file full path: {}".format(report_file_full_path))

    # pytest args
    pytest_args = []
    if not args.series and args.parallelism:
        pytest_args.append("-n {}".format(args.parallelism))
    pytest_args.append("--json-report")
    pytest_args.append("--json-report-file {}".format(report_file_full_path))
    pytest_args.append("--reruns {}".format(args.reruns))
    pytest_args.append("--capture {}".format(args.capture))
    pytest_args = [" ".join(pytest_args)]
    print("pytest_args: {}".format(pytest_args))
    print()

    # ext matrix
    if check_file_existence(ext_matrix_file_path):
        ext_test_index = get_ext_test_index()
        ext_matrix = get_test_matrix(ext_matrix_file_path)
        ext_test_cases = get_ext_test_cases(ext_test_index, ext_matrix)
        ext_exclude_test_cases = get_ext_exclude_test_cases(
            ext_matrix, args.ext_matrix_filter)
        ext_filtered_test_cases = get_ext_filted_test_cases(
            ext_test_cases, ext_exclude_test_cases)
        # add prefix
        ext_qualified_test_cases = decorate_qualified_prefix(
            ext_filtered_test_cases, AKS_PREVIEW_MOD_NAME)
        print("According to 'ext_matrix', we get {} cases, need to exclude {} cases, finally get {} cases".format(
            len(ext_test_cases), len(ext_exclude_test_cases), len(ext_filtered_test_cases)))
        print("Perform following tests: {}".format(ext_qualified_test_cases))
        run_tests(ext_qualified_test_cases, xml_path=args.xml_path, discover=args.discover, in_series=args.series,
                  run_live=args.live, no_exit_first=args.no_exitfirst, pytest_args=pytest_args)

    # cli matrix
    if check_file_existence(cli_matrix_file_path):
        print("Currently not support!")
        pass

    # tests
    if test_cases:
        print("Accroding to 'tests', we get {} cases".format(len(test_cases)))
        print("Perform following tets: {}".format(test_cases))
        run_tests(test_cases, xml_path=args.xml_path, discover=args.discover, in_series=args.series,
                  run_live=args.live, no_exit_first=args.no_exitfirst, pytest_args=pytest_args)


if __name__ == "__main__":
    main()
