##
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
##
import abc
from azure.quantum.job.session import SessionHost

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import cirq
    from azure.quantum import Job as AzureJob
    from azure.quantum import Workspace
    from azure.quantum.cirq.job import Job as CirqJob

class Target(abc.ABC, SessionHost):
    """Abstract base class for Cirq targets"""
    @abc.abstractstaticmethod
    def _translate_cirq_circuit(circuit):
        """Translate Cirq circuit to native provider format."""
        pass

    @classmethod
    def _translate_circuit(cls, circuit: Any):
        """Translate circuit into native provider format"""
        try:
            return cls._translate_cirq_circuit(circuit)
        except Exception as e:
            raise ValueError(
                f"Cannot translate circuit of type {circuit.__class__}: {e}")

    @abc.abstractstaticmethod
    def _to_cirq_result(result: Any) -> "cirq.Result":
        """Convert native hardware result to cirq.Result"""
        pass

    @abc.abstractmethod
    def _to_cirq_job(self, azure_job: "AzureJob", *args, **kwargs):
        """Convert Azure job to Cirq job"""
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def _get_azure_workspace(self) -> "Workspace":
        raise NotImplementedError

    @abc.abstractmethod
    def _get_azure_target_id(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_azure_provider_id(self) -> str:
        raise NotImplementedError
