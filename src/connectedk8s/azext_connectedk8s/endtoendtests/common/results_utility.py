import pytest

from pathlib import Path


# Function to create the test result directory 
def create_results_dir(results_dir):
    print(results_dir)
    try:
        Path(results_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        pytest.fail("Unable to create the results directory: " + str(e))


# Function to append logs from the test run into a result file
def append_result_output(message, result_file_path):
    try:
        with open(result_file_path, "a") as result_file:
            result_file.write(message)
    except Exception as e:
        pytest.fail("Error while appending message '{}' to results file: ".format(message) + str(e))
