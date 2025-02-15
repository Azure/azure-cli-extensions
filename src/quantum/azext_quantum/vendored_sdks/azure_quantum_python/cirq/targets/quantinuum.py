##
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
##
import numpy as np

from typing import TYPE_CHECKING, Any, Dict, Sequence

from azure.quantum.cirq.targets.target import Target as CirqTarget
from azure.quantum.cirq.job import Job as CirqJob
from azure.quantum.target.quantinuum import Quantinuum

if TYPE_CHECKING:
    import cirq
    from azure.quantum import Workspace
    from azure.quantum import Job as AzureJob


class QuantinuumTarget(Quantinuum, CirqTarget):
    """Base class for interfacing with an Quantinuum backend in Azure Quantum"""

    def __init__(
        self,
        workspace: "Workspace",
        name: str,
        input_data_format: str = "honeywell.openqasm.v1",
        output_data_format: str = "honeywell.quantum-results.v1",
        provider_id: str = "quantinuum",
        content_type: str = "application/qasm",
        encoding: str = "",
        **kwargs
    ):
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
    def _translate_cirq_circuit(circuit) -> str:
        """Translate `cirq` circuit to OpenQASM 2.0."""
        return circuit.to_qasm()

    @staticmethod
    def _to_cirq_result(result: Dict[str, Any], param_resolver, **kwargs):
        from cirq import ResultDict
        measurements = {
            key.lstrip("m_"): np.array([[int(_v)] for _v in value])
            for key, value in result.items()
            if key.startswith("m_")
        }
        return ResultDict(params=param_resolver, measurements=measurements)

    def _to_cirq_job(self, azure_job: "AzureJob", program: "cirq.Circuit" = None):
        """Convert Azure job to Cirq job"""
        if "measurement_dict" not in azure_job.details.metadata and program is None:
            raise ValueError("Parameter 'measurement_dict' not found in job metadata.")
        measurement_dict = azure_job.details.metadata.get("measurement_dict")
        return CirqJob(azure_job=azure_job, program=program, measurement_dict=measurement_dict)

    @staticmethod
    def _measurement_dict(program) -> Dict[str, Sequence[int]]:
        """Returns a dictionary of measurement keys to target qubit index."""
        from cirq import MeasurementGate
        measurements = [
            op for op in program.all_operations() if isinstance(op.gate, MeasurementGate)
        ]
        return {
            meas.gate.key: [q.x for q in meas.qubits] for meas in measurements
        }

    def submit(
        self,
        program: "cirq.Circuit",
        name: str = "cirq-job",
        repetitions: int = 500,
        **kwargs
    ) -> "CirqJob":
        """Submit a Cirq quantum circuit

        :param program: Quantum program
        :type program: cirq.Circuit
        :param name: Job name
        :type name: str
        :param repetitions: Number of shots, defaults to
            provider default value
        :type repetitions: int
        :return: Azure Quantum job
        :rtype: Job
        """
        serialized_program = self._translate_circuit(program)
        metadata = {
            "qubits": len(program.all_qubits()),
            "repetitions": repetitions,
            "measurement_dict": self._measurement_dict(program)
        }
        # Override metadata with value from kwargs
        metadata.update(kwargs.get("metadata", {}))
        azure_job = super().submit(
            circuit=serialized_program,
            name=name,
            num_shots=repetitions,
            metadata=metadata,
            **kwargs
        )
        return self._to_cirq_job(azure_job=azure_job)
