Param([Parameter(Mandatory=$true)][string]$script_path)
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
		$result = Invoke-Expression $script_path
		Write-Output $result
	}
} catch {
	Write-Error $error[0].Exception.Message
}