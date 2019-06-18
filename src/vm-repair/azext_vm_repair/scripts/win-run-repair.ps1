Param([Parameter(Mandatory=$true)][string]$script_path)
try {
	[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
	Set-ExecutionPolicy Bypass -Scope Process -Force
	$dirname = 'repair-files-' + (Get-Date).toString('yyyyMMddhhmmss')
	mkdir $dirname | Out-Null
	Set-Location $dirname
	(new-object net.webclient).DownloadFile('https://github.com/Azure/repair-script-library/zipball/master/', (Join-Path $pwd 'repair-script-library.zip'))
	Expand-Archive -Path 'repair-script-library.zip' -DestinationPath 'repair-script-library'
	$reponame = dir repair-script-library -n
	$command = './repair-script-library/' + $reponame + '/' + $script_path
	Invoke-Expression $command
} catch {
	$error[0].Exception
}