[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;
Set-ExecutionPolicy Bypass -Scope Process -Force;
(new-object net.webclient).DownloadFile('https://github.com/Azure/repair-script-library/zipball/master/', (Join-Path $pwd 'repair-script-library.zip'));
Expand-Archive -Path 'repair-script-library.zip' -DestinationPath 'repair-script-library';
$reponame = dir repair-script-library -n;
$command = './repair-script-library/' + $reponame + '/src/windows/win-test.ps1';
Invoke-Expression $command