Microsoft Azure CLI 'quantum' Extension
==========================================

Azure Quantum is the first open Quantum computing platform. It offers a range of services
from quantum hardware to full-state simulators and quantum inspired optimizations,
providing developers and customers access to the most competitive quantum offering
on the market.

To learn more about azure quantum visit:
https://azure.microsoft.com/en-us/services/quantum/

To learn more about quantum computing and Microsoft's Quantum Development Kit visit:
https://docs.microsoft.com/quantum/


# Using the `az quantum` extension to list and manage jobs in Azure Quantum

1. Log in to Azure using your credentials.
   ```dotnetcli
   az login
   ```
>[!NOTE] In case you have more than one subscription associated with your Azure account you must specify the 
>subscription you want to use. You can do this with the command `az account set -s <Your subscription ID>`.

2. You can see all the Azure Quantum workspaces in your subscription with the `az quantum workspace list` command:
   ```dotnetcli
   az quantum workspace list
   ```

3. You can use `quantum workspace set` to select a default workspace you want to use 
   to list and submit jobs. Note that you also need to specify the resource group.
   ```dotnetcli
    az quantum workspace set -g MyResourceGroup -w MyWorkspace  -o table

    Location     Name                               ResourceGroup
    -----------  ---------------------------------  --------------------------------
    westus       ws-yyyyyy                          rg-yyyyyyyyy
   ```

4. You can check the current default workspace with the command `az quantum workspace show`.

   ```dotnetcli
    az quantum workspace show -o table

    Location     Name                               ResourceGroup
    -----------  ---------------------------------  --------------------------------
    westus       ws-yyyyyy                          rg-yyyyyyyyy
   ```

5. You can see all the jobs submitted a workspace using `az quantum job list`.

   ```dotnetcli
    az quantum job list -o table

    Id                                    State    Target          Submission time
    ------------------------------------  -------  --------------  ---------------------------------
    yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy  Waiting  MyProvider.MyTarget  2020-06-12T14:20:18.6109317+00:00
   ```
   The console will output the information about the job, including the ID of the job.

6. You can use the ID of the job to track its status:
   ```dotnetcli
    az quantum job show -id yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table

    Id                                    State    Target          Submission time
    ------------------------------------  -------  --------------  ---------------------------------
    yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy  Waiting  MyProvider.MyTarget  2020-06-12T14:20:18.6109317+00:00
   ```

7. Once the job finishes you can visualize the job's results with `az quantum job output`:
   ```dotnetcli
    az quantum job output -id yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table
   
    Result    Frequency
    --------  -----------  -------------------------
    [0,0]     0.25000000   ▐█████                  |
    [1,0]     0.25000000   ▐█████                  |
    [0,1]     0.25000000   ▐█████                  |
    [1,1]     0.25000000   ▐█████                  |
   ```



# Submitting Q# programs for execution from the command line

## Prerequisites 

- You need to have an Azure Quantum workspace in your subscription.
- Install the [Quantum Development Kit](https://docs.microsoft.com/quantum/install-guide/standalone), if you haven't already.


## Write your quantum application

First you need to have the Q# quantum application that you want to execute in
Azure Quantum.

>[!TIP] If this is the first time for you to create Q# quantum applications, you can learn
>how in our [Microsoft Learn
>module](https://docs.microsoft.com/en-us/learn/modules/qsharp-create-first-quantum-development-kit/).
>

In this case we will use a simple quantum random bit generator. We create a Q#
project and substitute the content of `Program.qs` with the following code:

```qsharp
namespace RandomBit {

    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Measurement;

    @EntryPoint()
    operation GenerateRandomBit() : Result {
        using (q = Qubit())  {
            H(q);
            return MResetZ(q);
        }
    }
}
```
Note that the `@EntryPoint` attribute tells Q# which operation to run when the program starts.

### Submit the job

In this example we are going to use IonQ as the provider and the
`ionq.simulator` as target. To submit the job to the currently selected
default quantum workspace `az quantum job submit`:

```
az quantum job submit --target-id ionq.simulator --job-name Hello -o table

Name   Id                                    Status    Target          Submission time
-----  ------------------------------------  --------  --------------  ---------------------------------
Hello   yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy  Waiting   ionq.simulator  2020-06-17T17:07:07.3484901+00:00

```

Once the job completes (i.e. it's in a **Successful** state), use `az quantum job output` to see the results:
```
az quantum job output -id yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table

Result    Frequency
--------  -----------  -------------------------
[0,0]     0.25000000   ▐█████                  |
[0,1]     0.75000000   ▐████████████████       |
```
The output shows a histogram with the frequency a specific results was measured. In the example above
the result `[0,1]` was observed 75% of the times.


Finally, you can use `az quantum execute` as a shortcut for both, submitting and getting the results of execution.
```
az quantum execute --target-id ionq.simulator --job-name Hello2 -o table
.....
Result    Frequency
--------  -----------  -------------------------
[0,0]     0.25000000   ▐█████                  |
[0,1]     0.75000000   ▐████████████████       |
```


