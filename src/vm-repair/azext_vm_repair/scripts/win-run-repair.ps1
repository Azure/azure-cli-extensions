Param([Parameter(Mandatory=$true)][string]$script_path,[Parameter(Mandatory=$false)][string]$params='')
try {
	[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
	Set-ExecutionPolicy Bypass -Scope Process -Force
	$dirname = 'repair-files-' + (Get-Date).toString('yyyyMMddHHmmss')
	mkdir $dirname | Out-Null
	Set-Location $dirname
	(new-object net.webclient).DownloadFile('https://github.com/Azure/repair-script-library/zipball/master/', (Join-Path $pwd 'repair-script-library.zip'))
	Expand-Archive -Path 'repair-script-library.zip' -DestinationPath 'repair-script-library'
	$reponame = dir repair-script-library -n
	Set-Location (Join-Path 'repair-script-library' $reponame)
	If ($script_path -ne 'no-op')
	{
		# Work around for passing space characters through run-command
		$params = $params.replace('{space}', ' ')
		$command = $script_path + ' ' + $params
		$result = Invoke-Expression $command
		Write-Output $result
	}
} catch {
	Write-Error $error[0].Exception.Message
}