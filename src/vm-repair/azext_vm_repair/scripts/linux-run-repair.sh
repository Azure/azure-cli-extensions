#!/bin/bash
set -e
dirname=$(date +%Y%m%d%H%M%S)
mkdir $dirname
cd $dirname
wget https://github.com/Azure/repair-script-library/tarball/master/ -O repair-script-library.tar.gz 2>&1 | grep -i "failed\|error"
mkdir repair-script-library
tar -xf repair-script-library.tar.gz -C repair-script-library
cd repair-script-library
reponame=$(ls)
cd $reponame
chmod u+x ./src/linux/linux-test.sh
exec ./src/linux/linux-test.sh