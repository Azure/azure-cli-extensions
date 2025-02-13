##
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
##
from typing import TYPE_CHECKING, Any, Dict, Union, Optional

try:
    import cirq
    from cirq_ionq import Job as CirqIonqJob
    from cirq_ionq.results import QPUResult, SimulatorResult
except ImportError:
    raise ImportError(
        "Missing optional 'cirq_ionq' dependency. \
To install run: pip install azure-quantum[cirq]")

from azure.quantum.target import IonQ
from azure.quantum.cirq.targets.target import Target as CirqTarget

if TYPE_CHECKING:
    from azure.quantum import Workspace
    from azure.quantum.job import Job as AzureJob


class _IonQClient:
    """Thin wrapper around Workspace to support cirq_ionq.Job"""
    def __init__(self, workspace: "Workspace"):
        self._workspace = workspace
    
    @staticmethod
    def _to_ionq_status(status: str):
        from azure.quantum._client.models._enums import JobStatus
        _STATUS_DICT = {
            JobStatus.SUCCEEDED: 'completed',
            JobStatus.CANCELLED: 'canceled',
            JobStatus.FAILED: 'failed',
            JobStatus.EXECUTING: 'running',
            JobStatus.WAITING: 'ready'
        }
        return _STATUS_DICT.get(status, 'submitted')
    
    def _create_job_dict(self, azure_job: "AzureJob"):
        metadata = azure_job.details.input_params.copy()
        metadata.update(azure_job.details.metadata or {})

        if azure_job.has_completed():
            results = azure_job.get_results()
        else:
            results = None

        job_dict = {
            "id": azure_job.id,
            "name": azure_job.details.name,
            "status": self._to_ionq_status(azure_job.details.status),
            "data": results,
            "metadata": metadata,
            "target": azure_job.details.target,
            "qubits": metadata.get("qubits"),
            "failure": azure_job.details.error_data or ""
        }

        return job_dict
    
    def get_job(self, job_id: str):
        azure_job = self._workspace.get_job(job_id)
        return self._create_job_dict(azure_job)

    def cancel_job(self, job_id: str):
        azure_job = self._workspace.get_job(job_id)
        self._workspace.cancel_job(azure_job)

    def delete_job(self, job_id: str):
        azure_job = self._workspace.get_job(job_id)
        self._workspace.cancel_job(azure_job)
    
    def get_results(
        self, job_id: str, sharpen: Optional[bool] = None, extra_query_params: Optional[dict] = None
    ):
        azure_job = self._workspace.get_job(job_id)
        job_result = azure_job.get_results()
        return job_result["histogram"]
        


class IonQTarget(IonQ, CirqTarget):
    """Base class for interfacing with an IonQ backend in Azure Quantum"""

    def __init__(
        self,
        workspace: "Workspace",
        name: str,
        input_data_format: str = "ionq.circuit.v1",
        output_data_format: str = "ionq.quantum-results.v1",
        provider_id: str = "IonQ",
        content_type: str = "application/json",
        encoding: str = "",
        **kwargs
    ):
        self._client = _IonQClient(workspace)
        super().__init__(
            workspace=workspace,
            name=name,
            input_data_format=input_data_format,
            output_data_format=output_data_format,
            provider_id=provider_id,
            content_type=content_type,
            encoding=encoding,
            **kwargs
        )

    @staticmethod
    def _translate_cirq_circuit(circuit) -> Dict[str, Any]:
        """Translate Cirq circuit to IonQ JSON. If dependencies \
are not installed, throw error with installation instructions."""
        from cirq_ionq import Serializer
        return Serializer().serialize(circuit)

    def _to_cirq_job(self, azure_job: "AzureJob") -> "CirqIonqJob":
        """Convert Azure job to Cirq job"""
        job_dict = self._client._create_job_dict(azure_job)
        return CirqIonqJob(client=self._client, job_dict=job_dict)

    def submit(
        self,
        program: "cirq.Circuit",
        name: str = "cirq-job",
        repetitions: int = 500,
        **kwargs
    ) -> "CirqIonqJob":
        """Submit a Cirq quantum circuit

        :param program: Cirq circuit
        :type program: cirq.Circuit
        :param name: Job name
        :type name: str
        :param repetitions: Number of shots, defaults to 
            provider default value
        :type repetitions: int
        :return: Azure Quantum job
        :rtype: Job
        """
        serialized_program = self._translate_cirq_circuit(program)
        metadata = serialized_program.metadata or {}
        metadata["qubits"] = serialized_program.body["qubits"]
        # Override metadata with value from kwargs
        metadata.update(kwargs.get("metadata", {}))
        azure_job = super().submit(
            circuit=serialized_program.body,
            name=name,
            num_shots=repetitions,
            metadata=metadata,
            **kwargs
        )
        # Get Job shim to process results using cirq.Result
        return self._to_cirq_job(azure_job=azure_job)
    
    @staticmethod
    def _to_cirq_result(
        result: Union[QPUResult, SimulatorResult],
        param_resolver: cirq.ParamResolverOrSimilarType = cirq.ParamResolver({}),
        seed: cirq.RANDOM_STATE_OR_SEED_LIKE = None,
    ) -> "cirq.Result":
        if isinstance(result, QPUResult):
            return result.to_cirq_result(params=cirq.ParamResolver(param_resolver))
        elif isinstance(result, SimulatorResult):
            return result.to_cirq_result(params=cirq.ParamResolver(param_resolver), seed=seed)

        raise ValueError("Result {result} not supported. \
            Expecting either a cirq_ionq.results.QPUResult \
                or cirq_ionq.results.SimulatorResult.")
 