=======================================
Microsoft Azure CLI 'quantum' Extension
=======================================

Azure Quantum is the first open Quantum computing platform. It offers a range of services
from quantum hardware to full-state simulators and quantum inspired optimizations,
providing developers and customers access to the most competitive quantum offering
on the market.

To learn more about azure quantum, visit:
https://azure.microsoft.com/services/quantum/

To learn more about quantum computing and Microsoft's Quantum Development Kit, visit:
https://learn.microsoft.com/quantum/


Creating Q# programs for execution from the command line
========================================================

Prerequisites
-------------

- You need to have an Azure Quantum workspace in your subscription.
- Install the [Quantum Development Kit](https://learn.microsoft.com/quantum/install-guide/standalone), if you haven't already.


Write your quantum application
------------------------------

First you need to have the Q# quantum application that you want to execute in
Azure Quantum.

.. tip::
   If this is the first time for you to create Q# quantum applications, you can learn how
   in our [Microsoft Learn module](https://learn.microsoft.com/learn/modules/qsharp-create-first-quantum-development-kit/).

In this case we will use a simple quantum random bit generator. We create a Q#
project and substitute the content of `Program.qs` with the following code:

.. code-block::

   namespace RandomBit {

       open Microsoft.Quantum.Canon;
       open Microsoft.Quantum.Intrinsic;
       open Microsoft.Quantum.Measurement;

       @EntryPoint()
       operation GenerateRandomBit() : Result {
           use q = Qubit();
           H(q);
           return MResetZ(q);
       }
   }

Note that the `@EntryPoint` attribute tells Q# which operation to run when the program starts.


Prepare to submit and manage jobs in Azure Quantum using the `az quantum` extension
===================================================================================

1. Log in to Azure using your credentials.

   .. code-block:: 

      az login

   .. note::
      In case you have more than one subscription associated with your Azure account you must specify the 
      subscription you want to use. You can do this with the command `az account set -s <Your subscription ID>`.


2. Install the Quantum extension for the Azure CLI.

   .. code-block::

      az extension add --name quantum


3. You can see all the Azure Quantum workspaces in your subscription with the `az quantum workspace list` command.
   At this time, you need to create and set up your workspaces using the Azure Portal, please refer to the documentation
   for Azure Quantum for details on this and how to choose providers.

   .. code-block::

      az quantum workspace list


4. You can use `quantum workspace set` to select a default workspace you want to use to list and submit jobs.
   Note that you also need to specify the resource group. If you set a default workspace by providing a resource group,
   workspace name and location, you don't need to include those parameters in commands #5 to #8 below.
   Anternatively, you can include them in each call.

   .. code-block::

      az quantum workspace set -g MyResourceGroup -w MyWorkspace -l MyLocation -o table

      Location     Name                               ResourceGroup
      -----------  ---------------------------------  --------------------------------
      westus       ws-yyyyyy                          rg-yyyyyyyyy


.. note:
   Commands below assume that a default workspace has been set. If you prefer to specify it
   for each call, include the following parameters with commands below:
   `-g MyResourceGroup -w MyWorkspace -l MyLocation`


5. You can check the current default workspace with command `az quantum workspace show`.

   .. code-block::

      az quantum workspace show -o table

      Location     Name                               ResourceGroup
      -----------  ---------------------------------  --------------------------------
      westus       ws-yyyyyy                          rg-yyyyyyyyy


6. For this example we are going to use IonQ as the provider and the `ionq.simulator` as target.
   To submit the job to the currently selected default quantum workspace, run the following from the directory
   where you have the project created previously.

   .. code-block::

      az quantum job submit --target-id ionq.simulator --job-name Hello -o table

      Name   Id                                    Status    Target          Submission time
      -----  ------------------------------------  --------  --------------  ---------------------------------
      Hello   yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy  Waiting   ionq.simulator  2020-06-17T17:07:07.3484901+00:00


7. You can see all the jobs submitted to a workspace using `az quantum job list`.

   .. code-block::

      az quantum job list -o table

      Id                                    State    Target          Submission time
      ------------------------------------  -------  --------------  ---------------------------------
      yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy  Waiting  MyProvider.MyTarget  2020-06-12T14:20:18.6109317+00:00

   The console will output the information about the job, including the ID of the job.


8. You can use the ID of the job to track its status.

   .. code-block::

      az quantum job show -id yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table

      Id                                    State    Target          Submission time
      ------------------------------------  -------  --------------  ---------------------------------
      yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy  Waiting  MyProvider.MyTarget  2020-06-12T14:20:18.6109317+00:00


9. Once the job finishes (i.e. it's in a **Successful** state) you can visualize the job's results.

   .. code-block::

      az quantum job output -id yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table
   
      Result    Frequency
      --------  -----------  -------------------------
      [0,0]     0.25000000   ▐█████                  |
      [1,0]     0.25000000   ▐█████                  |
      [0,1]     0.25000000   ▐█████                  |
      [1,1]     0.25000000   ▐█████                  |


   The output shows a histogram with the frequency a specific result was measured. In the example above,
   the result `[0,1]` was observed 25% of the times.


10. Alternatively, you can run a job synchronously and wait for it to complete.

    .. code-block::

       az quantum execute --target-id ionq.simulator --job-name Hello2 -o table
   
       Result    Frequency
       --------  -----------  -------------------------
       [0,0]     0.25000000   ▐█████                  |
       [0,1]     0.75000000   ▐████████████████       |


