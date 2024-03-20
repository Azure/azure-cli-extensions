Param([Parameter(Mandatory=$true)][string]$script_path,[Parameter(Mandatory=$false)][string]$repo_fork, [Parameter(Mandatory=$false)][string]$repo_branch, [Parameter(Mandatory=$false)][bool]$init=$true,[Parameter(Mandatory=$false)][string]$params='')
if ($init)
{
	try {
		[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
		Set-ExecutionPolicy Bypass -Scope Process -Force
		$curDate = (Get-Date).toString('yyyyMMddHHmmss')
		$dirname = "repair-files-$curDate"
		mkdir $dirname | Out-Null
		Set-Location $dirname
		$logFileName = "logs-$curDate.txt"
		Set-Content -Path "./$logFileName" -Value "[Log-Start $(Get-Date)]"
		$logFile = (Resolve-Path "./$logFileName").Path
		if($repo_fork -eq $null)
		{
			$repo_fork = 'Azure/repair-script-library'
		}
		if($repo_branch -eq $null)
		{
			$repo_branch = 'master'
		}
		$url = "https://github.com/$repo_fork/repair-script-library/zipball/$repo_branch/"
		(new-object net.webclient).DownloadFile($url, (Join-Path $pwd 'repair-script-library.zip'))
		Expand-Archive -Path 'repair-script-library.zip' -DestinationPath 'repair-script-library'
		$reponame = dir repair-script-library -n
		Set-Location (Join-Path 'repair-script-library' $reponame)
		$logToFile = "Out-File -FilePath $logFile -Append -Encoding Ascii"
		# Normal GitHub script scenario
		if ($script_path -ne 'no-op')
		{
			$command = "$script_path $params | $logToFile"
			Invoke-Expression -Command $command 
		}
		# Custom script scenario
		else
		{
			$curScript = ($MyInvocation.MyCommand).Source
			$command = "$curScript -script_path no-op " + '-init $False ' + "| $logToFile"
			Invoke-Expression -Command $command 
		}
	} catch {
		$errorMessage = $error[0].Exception.Message
		$errorTrace = $error[0].ScriptStackTrace
		Add-Content -Path $logFile -Value "[Error $(Get-Date)] $errorMessage $errorTrace"
	} finally {
		Add-Content -Path $logFile -Value "[Log-End $(Get-Date)]$logFile"
		Write-Output (Get-Content -Path $logFile)
	}
	# End and don't run appended scripts from Run-Command.
	return
}