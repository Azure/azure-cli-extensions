# Work around for Run-Command Shell Script behavior. Have to use 'ls' call to check if we pulled GitHub already.
if [ $(ls | wc -l) -eq 3 ]; then
	# Try, && added to each line to stop on fail and continue to catch block
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
		# Normal GitHub script scenario
		if [ "$1" != "no-op" ]; then
			chmod u+x $1 &&
			command_string="$*" &&
			bash -e  $command_string >> $logFile
		else # Custom script scenario
			# Call the same script but it will only run the appended custom scripts
			bash -e $0 >> $logFile
		fi &&

		# Add status string to log file
		echo "status string: $?" &&
		if [ $? -eq 0 ]; then
			echo "[STATUS]::SUCCESS" >> $logFile
		else
			echo "[STATUS]::ERROR" >> $logFile
		fi
	} || { # Catch
		errorMessage=$(cat /dev/stderr)
		echo "[Error $(date "+%m/%d/%Y %T")]$errorMessage" >> $logFile
	} 
	# Finally
	echo "[Log-End $(date "+%m/%d/%Y %T")]$logFile" >> $logFile
	echo $(cat $logFile)
	# Exit and don't run appended scripts from run-command
	exit
fi