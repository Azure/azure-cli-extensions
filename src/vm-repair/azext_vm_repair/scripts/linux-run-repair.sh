# Try
{
	curDate=$(date +%Y%m%d%H%M%S) &&
	dirname="repair-files-$curDate" &&
	mkdir $dirname &&
	cd $dirname &&
	logFileName="logs-$curDate.txt" &&
	logFile="$(pwd)/$line$logFileName" &&
	# Log Start
	echo "[Log-Start  $(date "+%m/%d/%Y %T")]" >> $logFile &&
	curl -s -S -L -o repair-script-library.tar.gz https://github.com/Azure/repair-script-library/tarball/master/ &&
	mkdir repair-script-library &&
	tar -xf repair-script-library.tar.gz -C repair-script-library &&
	cd repair-script-library &&
	reponame=$(ls) &&
	cd $reponame &&
	if [ $1 != "no-op" ]; then
		chmod u+x $1 &&
		# Work around for passing space characters through run-command
		params=$(echo "$2" | sed "s/{space}/ /") &&
		command_string="$1 $params" &&
		bash -e  $command_string >> $logFile &&
		if [ $? -eq 0 ]; then
			echo "[STATUS]::SUCCESS" >> $logFile
		else
			echo "[STATUS]::ERROR" >> $logFile
		fi
	fi
} || { # Catch
	errorMessage=$(cat /dev/stderr)
	echo "[Error $(date "+%m/%d/%Y %T")]$errorMessage" >> $logFile
} && { # Finally
	echo "[Log-End $(date "+%m/%d/%Y %T")]$logFile" >> $logFile
	echo $(cat $logFile)
}