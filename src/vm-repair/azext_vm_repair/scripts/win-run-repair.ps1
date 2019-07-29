Param([Parameter(Mandatory=$true)][string]$script_path,[Parameter(Mandatory=$false)][string]$params='')
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
	(new-object net.webclient).DownloadFile('https://github.com/Azure/repair-script-library/zipball/master/', (Join-Path $pwd 'repair-script-library.zip'))
	Expand-Archive -Path 'repair-script-library.zip' -DestinationPath 'repair-script-library'
	$reponame = dir repair-script-library -n
	Set-Location (Join-Path 'repair-script-library' $reponame)
	if ($script_path -ne 'no-op')
	{
		# Work around for passing space characters through run-command
		$params = $params.replace('{space}', ' ')
		$logToFile = "Out-File -FilePath $logFile -Append -Encoding Ascii"
		$command = "$script_path $params | $logToFile"
		Invoke-Expression -Command $command 
	}
} catch {
	$errorMessage = $error[0].Exception.Message
	Add-Content -Path $logFile -Value "[Error $(Get-Date)] $errorMessage"
} finally {
	Add-Content -Path $logFile -Value "[Log-End $(Get-Date)]$logFile"
	Write-Output (Get-Content -Path $logFile)
}