##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##


import logging
import time
import json

from typing import TYPE_CHECKING

from azure.quantum._client.models import JobDetails
from azure.quantum.job.job_failed_with_results_error import JobFailedWithResultsError
from azure.quantum.job.base_job import BaseJob, ContentType, DEFAULT_TIMEOUT
from azure.quantum.job.filtered_job import FilteredJob

__all__ = ["Job", "JobDetails"]

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from azure.quantum.workspace import Workspace


_log = logging.getLogger(__name__)


class Job(BaseJob, FilteredJob):
    """Azure Quantum Job that is submitted to a given Workspace.

    :param workspace: Workspace instance to submit job to
    :type workspace: Workspace
    :param job_details: Job details model,
            contains Job ID, name and other details
    :type job_details: JobDetails
    """

    _default_poll_wait = 0.2

    def __init__(self, workspace: "Workspace", job_details: JobDetails, **kwargs):
        self.results = None
        super().__init__(
            workspace=workspace,
            details=job_details,
            **kwargs
        )

    def submit(self):
        """Submit a job to Azure Quantum."""
        _log.debug(f"Submitting job with ID {self.id}")
        job = self.workspace.submit_job(self)
        self.details = job.details

    def refresh(self):
        """Refreshes the Job's details by querying the workspace."""
        self.details = self.workspace.get_job(self.id).details

    def has_completed(self) -> bool:
        """Check if the job has completed."""
        return (
            self.details.status == "Succeeded"
            or self.details.status == "Failed"
            or self.details.status == "Cancelled"
        )

    def wait_until_completed(
        self,
        max_poll_wait_secs=30,
        timeout_secs=None,
        print_progress=True
    ) -> None:
        """Keeps refreshing the Job's details
        until it reaches a finished status.

        :param max_poll_wait_secs: Maximum poll wait time, defaults to 30
        :type max_poll_wait_secs: int
        :param timeout_secs: Timeout in seconds, defaults to None
        :type timeout_secs: int
        :param print_progress: Print "." to stdout to display progress
        :type print_progress: bool
        :raises: :class:`TimeoutError` If the total poll time exceeds timeout, raise.
        """
        self.refresh()
        poll_wait = Job._default_poll_wait
        start_time = time.time()
        while not self.has_completed():
            if timeout_secs is not None and (time.time() - start_time) >= timeout_secs:
                raise TimeoutError(f"The wait time has exceeded {timeout_secs} seconds.")

            logger.debug(
                f"Waiting for job {self.id},"
                + f"it is in status '{self.details.status}'"
            )
            if print_progress:
                print(".", end="", flush=True)
            time.sleep(poll_wait)
            self.refresh()
            poll_wait = (
                max_poll_wait_secs
                if poll_wait >= max_poll_wait_secs
                else poll_wait * 1.5
            )

    def get_results(self, timeout_secs: float = DEFAULT_TIMEOUT):
        """Get job results by downloading the results blob from the
        storage container linked via the workspace.
        
        Raises :class:`RuntimeError` if job execution fails.
        
        Raises :class:`ValueError` if job output is malformed or output format is not compatible.

        Raises :class:`azure.quantum.job.JobFailedWithResultsError` if job execution fails, 
                but failure results could still be retrieved (e.g. for jobs submitted against "microsoft.dft" target).

        :param timeout_secs: Timeout in seconds, defaults to 300
        :type timeout_secs: float
        :return: Results dictionary with histogram shots, or raw results if not a json object.
        :rtype: typing.Any
        """
        if self.results is not None:
            return self.results

        if not self.has_completed():
            self.wait_until_completed(timeout_secs=timeout_secs)

        if not self.details.status == "Succeeded":
            if self.details.status == "Failed" and self._allow_failure_results():
                job_blob_properties = self.download_blob_properties(self.details.output_data_uri)
                if job_blob_properties.size > 0:
                    job_failure_data = self.download_data(self.details.output_data_uri)
                    raise JobFailedWithResultsError("An error occurred during job execution.", job_failure_data)

            raise RuntimeError(
                f'{"Cannot retrieve results as job execution failed"}'
                + f"(status: {self.details.status}."
                + f"error: {self.details.error_data})"
            )

        payload = self.download_data(self.details.output_data_uri)
        try:
            payload = payload.decode("utf8")
            results = json.loads(payload)

            if self.details.output_data_format == "microsoft.quantum-results.v1":
                if "Histogram" not in results:
                    raise ValueError(f"\"Histogram\" array was expected to be in the Job results for \"{self.details.output_data_format}\" output format.")
                
                histogram_values = results["Histogram"]

                if len(histogram_values) % 2 == 0:
                    # Re-mapping {'Histogram': ['[0]', 0.50, '[1]', 0.50] } to {'[0]': 0.50, '[1]': 0.50}
                    return {histogram_values[i]: histogram_values[i + 1] for i in range(0, len(histogram_values), 2)}
                else: 
                    raise ValueError(f"\"Histogram\" array has invalid format. Even number of items is expected.")
            elif self.details.output_data_format == "microsoft.quantum-results.v2":
                if "DataFormat" not in results or results["DataFormat"] != "microsoft.quantum-results.v2":
                    raise ValueError(f"\"DataFormat\" was expected to be \"microsoft.quantum-results.v2\" in the Job results for \"{self.details.output_data_format}\" output format.")

                if "Results" not in results:
                    raise ValueError(f"\"Results\" field was expected to be in the Job results for \"{self.details.output_data_format}\" output format.")
                
                if len(results["Results"]) < 1:
                    raise ValueError("\"Results\" array was expected to contain at least one item")
                
                results = results["Results"][0]

                if "Histogram" not in results:
                    raise ValueError(f"\"Histogram\" array was expected to be in the Job results for \"{self.details.output_data_format}\" output format.")

                if "Shots" not in results:
                    raise ValueError(f"\"Shots\" array was expected to be in the Job results for \"{self.details.output_data_format}\" output format.")

                histogram_values = results["Histogram"]

                total_count = len(results["Shots"])

                # Re-mapping object {'Histogram': [{"Outcome": [0], "Display": '[0]', "Count": 500}, {"Outcome": [1], "Display": '[1]', "Count": 500}]} to {'[0]': 0.50, '[1]': 0.50}
                return {outcome["Display"]: outcome["Count"] / total_count for outcome in histogram_values}
            
            return results
        except:
            # If errors decoding the data, return the raw payload:
            return payload

    def get_results_histogram(self, timeout_secs: float = DEFAULT_TIMEOUT):
        """Get job results histogram by downloading the results blob from the storage container linked via the workspace.
        
        Raises :class:`RuntimeError` if job execution fails.
        
        Raises :class:`ValueError` if job output is malformed or output format is not compatible.

        Raises :class:`azure.quantum.job.JobFailedWithResultsError` if job execution fails, 
                but failure results could still be retrieved (e.g. for jobs submitted against "microsoft.dft" target).

        :param timeout_secs: Timeout in seconds, defaults to 300
        :type timeout_secs: float
        :return: Results dictionary with histogram shots, or raw results if not a json object.
        :rtype: typing.Any
        """
        if self.results is not None:
            return self.results

        if not self.has_completed():
            self.wait_until_completed(timeout_secs=timeout_secs)

        if not self.details.status == "Succeeded":
            if self.details.status == "Failed" and self._allow_failure_results():
                job_blob_properties = self.download_blob_properties(self.details.output_data_uri)
                if job_blob_properties.size > 0:
                    job_failure_data = self.download_data(self.details.output_data_uri)
                    raise JobFailedWithResultsError("An error occurred during job execution.", job_failure_data)

            raise RuntimeError(
                f'{"Cannot retrieve results as job execution failed"}'
                + f"(status: {self.details.status}."
                + f"error: {self.details.error_data})"
            )

        payload = self.download_data(self.details.output_data_uri)
        try:
            payload = payload.decode("utf8")
            results = json.loads(payload)

            if self.details.output_data_format == "microsoft.quantum-results.v2":
                if "DataFormat" not in results or results["DataFormat"] != "microsoft.quantum-results.v2":
                    raise ValueError(f"\"DataFormat\" was expected to be \"microsoft.quantum-results.v2\" in the Job results for \"{self.details.output_data_format}\" output format.")
                if "Results" not in results:
                    raise ValueError(f"\"Results\" field was expected to be in the Job results for \"{self.details.output_data_format}\" output format.")
                
                if len(results["Results"]) < 1:
                    raise ValueError("\"Results\" array was expected to contain at least one item")
                
                results = results["Results"]

                if len(results) == 1: 
                    results = results[0]
                    if "Histogram" not in results:
                        raise ValueError(f"\"Histogram\" array was expected to be in the Job results for \"{self.details.output_data_format}\" output format.")

                    histogram_values = results["Histogram"]
                    outcome_keys = self._process_outcome(histogram_values)

                    # Re-mapping object {'Histogram': [{"Outcome": [0], "Display": '[0]', "Count": 500}, {"Outcome": [1], "Display": '[1]', "Count": 500}]} to {'[0]': {"Outcome": [0], "Count": 500}, '[1]': {"Outcome": [1], "Count": 500}}
                    return {hist_val["Display"]: {"outcome": outcome, "count": hist_val["Count"]} for outcome, hist_val in zip(outcome_keys, histogram_values)}

                else:
                    # This is handling the BatchResults edge case
                    resultsArray = []
                    for i, result in enumerate(results):
                        if "Histogram" not in result:
                            raise ValueError(f"\"Histogram\" array was expected to be in the Job results for result {i} for \"{self.details.output_data_format}\" output format.")

                        histogram_values = result["Histogram"]
                        outcome_keys = self._process_outcome(histogram_values)

                        # Re-mapping object {'Histogram': [{"Outcome": [0], "Display": '[0]', "Count": 500}, {"Outcome": [1], "Display": '[1]', "Count": 500}]} to {'[0]': {"Outcome": [0], "Count": 500}, '[1]': {"Outcome": [1], "Count": 500}}
                        resultsArray.append({hist_val["Display"]: {"outcome": outcome, "count": hist_val["Count"]} for outcome, hist_val in zip(outcome_keys, histogram_values)})

                    return resultsArray

            else:
                raise ValueError(f"Getting a results histogram with counts instead of probabilities is not a supported feature for jobs using the \"{self.details.output_data_format}\" output format.")

        except Exception as e:
            raise e

    def get_results_shots(self, timeout_secs: float = DEFAULT_TIMEOUT):
        """Get job results per shot data by downloading the results blob from the
        storage container linked via the workspace.
        
        Raises :class:`RuntimeError` if job execution fails.
        
        Raises :class:`ValueError` if job output is malformed or output format is not compatible.

        Raises :class:`azure.quantum.job.JobFailedWithResultsError` if job execution fails, 
                but failure results could still be retrieved (e.g. for jobs submitted against "microsoft.dft" target).

        :param timeout_secs: Timeout in seconds, defaults to 300
        :type timeout_secs: float
        :return: Results dictionary with histogram shots, or raw results if not a json object.
        :rtype: typing.Any
        """
        if self.results is not None:
            return self.results

        if not self.has_completed():
            self.wait_until_completed(timeout_secs=timeout_secs)

        if not self.details.status == "Succeeded":
            if self.details.status == "Failed" and self._allow_failure_results():
                job_blob_properties = self.download_blob_properties(self.details.output_data_uri)
                if job_blob_properties.size > 0:
                    job_failure_data = self.download_data(self.details.output_data_uri)
                    raise JobFailedWithResultsError("An error occurred during job execution.", job_failure_data)

            raise RuntimeError(
                f'{"Cannot retrieve results as job execution failed"}'
                + f"(status: {self.details.status}."
                + f"error: {self.details.error_data})"
            )

        payload = self.download_data(self.details.output_data_uri)
        try:
            payload = payload.decode("utf8")
            results = json.loads(payload)

            if self.details.output_data_format == "microsoft.quantum-results.v2":
                if "DataFormat" not in results or results["DataFormat"] != "microsoft.quantum-results.v2":
                    raise ValueError(f"\"DataFormat\" was expected to be \"microsoft.quantum-results.v2\" in the Job results for \"{self.details.output_data_format}\" output format.")
                if "Results" not in results:
                    raise ValueError(f"\"Results\" field was expected to be in the Job results for \"{self.details.output_data_format}\" output format.")

                results = results["Results"]

                if len(results) < 1:
                    raise ValueError("\"Results\" array was expected to contain at least one item")

                if len(results) == 1: 
                    result = results[0]
                    if "Shots" not in result:
                        raise ValueError(f"\"Shots\" array was expected to be in the Job results for \"{self.details.output_data_format}\" output format.")
                    
                    return [self._convert_tuples(shot) for shot in result["Shots"]]
                else:
                    # This is handling the BatchResults edge case
                    shotsArray = []
                    for i, result in enumerate(results):
                        if "Shots" not in result:
                            raise ValueError(f"\"Shots\" array was expected to be in the Job results for result {i} of \"{self.details.output_data_format}\" output format.")
                        shotsArray.append([self._convert_tuples(shot) for shot in result["Shots"]])
                    
                    return shotsArray
            else:   
                raise ValueError(f"Individual shot results are not supported for jobs using the \"{self.details.output_data_format}\" output format.")
        except Exception as e:
            raise e

    def _process_outcome(self, histogram_results):
        return [self._convert_tuples(v['Outcome']) for v in histogram_results]

    def _convert_tuples(self, data):
        if isinstance(data, dict):
            # Check if the dictionary represents a tuple
            if all(isinstance(k, str) and k.startswith("Item") for k in data.keys()):
                # Convert the dictionary to a tuple
                return tuple(self._convert_tuples(data[f"Item{i+1}"]) for i in range(len(data)))
            else:
                raise "Malformed tuple output"
        elif isinstance(data, list):
            # Recursively process list elements
            return [self._convert_tuples(item) for item in data]
        else:
            # Return the data as is (int, string, etc.)
            return data

    @classmethod
    def _allow_failure_results(cls) -> bool: 
        """
        Allow to download job results even if the Job status is "Failed".

        This method can be overridden in derived classes to alter the default
        behaviour.

        The default is False.
        """
        return False