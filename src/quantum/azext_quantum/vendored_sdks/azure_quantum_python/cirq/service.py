##
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
##
try:
    import cirq
except ImportError:
    raise ImportError(
    "Missing optional 'cirq' dependencies. \
To install run: pip install azure-quantum[cirq]"
)

from azure.quantum import Workspace
from azure.quantum.job.base_job import DEFAULT_TIMEOUT
from azure.quantum.cirq.targets import * 

from typing import Optional, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.quantum.cirq.targets import Target as CirqTarget
    from azure.quantum.cirq.job import Job as CirqJob
    from cirq_ionq import Job as CirqIonqJob

DEFAULT_JOB_NAME = "cirq-job"
CIRQ_USER_AGENT = "azure-quantum-cirq"


class AzureQuantumService:
    """
    Class for interfacing with the Azure Quantum service
    using Cirq quantum circuits
    """
    def __init__(
        self,
        workspace: Workspace = None,
        default_target: Optional[str] = None,
        **kwargs
    ):
        """AzureQuantumService class

        :param workspace: Azure Quantum workspace. If missing it will create a new Workspace passing `kwargs` to the constructor. Defaults to None. 
        :type workspace: Workspace
        :param default_target: Default target name, defaults to None
        :type default_target: Optional[str]
        """
        if kwargs is not None and len(kwargs) > 0:
            from warnings import warn
            warn(f"""Consider passing \"workspace\" argument explicitly. 
                 The ability to initialize AzureQuantumService with arguments {', '.join(f'"{argName}"' for argName in kwargs)} is going to be deprecated in future versions.""", 
                 DeprecationWarning, 
                 stacklevel=2)

        if workspace is None:
            workspace = Workspace(**kwargs)

        workspace.append_user_agent(CIRQ_USER_AGENT)

        self._workspace = workspace
        self._default_target = default_target

    @property
    def _target_factory(self):
        from azure.quantum.target.target_factory import TargetFactory
        from azure.quantum.cirq.targets import Target, DEFAULT_TARGETS

        target_factory = TargetFactory(
            base_cls=Target,
            workspace=self._workspace,
            default_targets=DEFAULT_TARGETS
        )

        return target_factory

    def targets(
        self,
        name: str = None,
        provider_id: str = None,
        **kwargs
    ) -> Union["CirqTarget", List["CirqTarget"]]:
        """Get all quantum computing targets available in the Azure Quantum Workspace.

        :param name: Target name, defaults to None
        :type name: str
        :return: Target instance or list thereof
        :rtype: typing.Union[Target, typing.List[Target]]
        """
        return self._target_factory.get_targets(
            name=name,
            provider_id=provider_id
        )

    def get_target(self, name: str = None, **kwargs) -> "CirqTarget":
        """Get target with the specified name

        :param name: Target name
        :type name: str
        :return: Cirq target
        :rtype: Target
        """
        if name is None:
            if self._default_target is None:
                raise ValueError("No default target specified for job.")
            return self.targets(name=self._default_target, **kwargs)

        if isinstance(name, str):
            return self.targets(name=name, **kwargs)

    def get_job(self, job_id: str, *args, **kwargs) -> Union["CirqJob", "CirqIonqJob"]:
        """Get Cirq Job by job ID

        :param job_id: Job ID
        :type job_id: str
        :return: Job
        :rtype: azure.quantum.cirq.Job
        """
        job = self._workspace.get_job(job_id=job_id)
        target : CirqTarget = self._target_factory.create_target(
            provider_id=job.details.provider_id,
            name=job.details.target
        )
        return target._to_cirq_job(azure_job=job, *args, **kwargs)

    def create_job(
        self,
        program: cirq.Circuit,
        repetitions: int,
        name: str = DEFAULT_JOB_NAME,
        target: str = None,
        param_resolver: cirq.ParamResolverOrSimilarType = cirq.ParamResolver({})
    ) -> Union["CirqJob", "CirqIonqJob"]:
        """Create job to run the given `cirq` program in Azure Quantum

        :param program: Cirq program or circuit
        :type program: cirq.Circuit
        :param repetitions: Number of measurements 
        :type repetitions: int
        :param name: Program name
        :type name: str
        :param target: Target name
        :type target: str
        :param param_resolver: Parameter resolver for cirq program
        :type param_resolver: cirq.ParamResolverOrSimilarType
        :return: Job
        :rtype: azure.quantum.cirq.Job
        """
        # Get target
        _target = self.get_target(name=target)
        if not _target:
            target_name = target or self._default_target
            raise RuntimeError(f"Could not find target '{target_name}'. \
Please make sure the target name is valid and that the associated provider is added to your Workspace. \
To add a provider to your quantum workspace on the Azure Portal, \
see https://aka.ms/AQ/Docs/AddProvider")
        # Resolve parameters
        resolved_circuit = cirq.resolve_parameters(program, param_resolver)
        # Submit job to Azure
        return _target.submit(
            program=resolved_circuit,
            repetitions=repetitions,
            name=name
        )

    def run(
        self,
        program: cirq.Circuit,
        repetitions: int,
        target: str = None,
        name: str = DEFAULT_JOB_NAME,
        param_resolver: cirq.ParamResolverOrSimilarType = cirq.ParamResolver({}),
        seed: cirq.RANDOM_STATE_OR_SEED_LIKE = None,
        timeout_seconds: int = DEFAULT_TIMEOUT,
    ) -> cirq.Result:
        """Run Cirq circuit on specified target, if target not specified then it runs on the default target

        :param program: Cirq program or circuit
        :type program: cirq.Circuit
        :param repetitions: Number of measurement repetitions
        :type repetitions: int
        :param target: Target name, defaults to default_target
        :type target: str
        :param name: Program name, defaults to "cirq-job"
        :type name: str
        :param param_resolver: Cirq parameters, defaults to `cirq.ParamResolver({})`
        :type param_resolver: cirq.ParamResolverOrSimilarType
        :param seed: Random seed for simulator results, defaults to None
        :type seed: cirq.RANDOM_STATE_OR_SEED_LIKE
        :param timeout_seconds: Timeout in seconds, defaults to None
        :type timeout_seconds: int
        :return: Measurement results
        :rtype: cirq.Result
        """
        job = self.create_job(
            program=program,
            repetitions=repetitions,
            name=name,
            target=target,
            param_resolver=param_resolver
        )
        # Get raw job results
        try:
            result = job.results(timeout_seconds=timeout_seconds)
        except RuntimeError as e:
            # Catch errors from cirq_ionq.Job.results
            if "Job was not completed successful. Instead had status: " in str(e):
                raise TimeoutError(f"The wait time has exceeded {timeout_seconds} seconds. \
Job status: '{job.status()}'.")
            else:
                raise e

        # Convert to Cirq Result
        target = self.get_target(name=target)
        return target._to_cirq_result(
            result=result,
            param_resolver=param_resolver,
            seed=seed
        )
