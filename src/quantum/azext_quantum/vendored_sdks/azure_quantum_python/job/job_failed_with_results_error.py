import json
from typing import Any, Dict, Union

class JobFailedWithResultsError(RuntimeError):
    """Error produced when Job completes with status "Failed" and the Job
    supports producing failure results.

    The failure results can be accessed with get_failure_results() method.
    """

    def __init__(self, message: str, failure_results: Any, *args: object) -> None:
        """Initializes error produced when Job completes with status "Failed" and the Job
        supports producing failure results.

        :param message: Error message.
        :type message: str
        :param failure_results: Failure results produced by the job.
        :type failure_results: Any
        """

        self._set_error_details(message, failure_results)
        super().__init__(message, *args)


    def _set_error_details(self, message: str, failure_results: Any) -> None:
        self._message = message
        try:
            decoded_failure_results = failure_results.decode("utf8")
            self._failure_results: Dict[str, Any] = json.loads(decoded_failure_results)
        except:
            self._failure_results = failure_results


    def get_message(self) -> str:
        """
        Get error message.
        """
        return self._message


    def get_failure_results(self) -> Union[Dict[str, Any], str]:
        """
        Get failure results produced by the job.
        """
        return self._failure_results
    

    def __str__(self) -> str:
        return f"{self._message}\nFailure results: {self._failure_results}"