set -e
dirname=$(date +%Y%m%d%H%M%S)
mkdir $dirname
cd $dirname
curl -s -S -L -o repair-script-library.tar.gz https://github.com/Azure/repair-script-library/tarball/master/ 
mkdir repair-script-library
tar -xf repair-script-library.tar.gz -C repair-script-library
cd repair-script-library
reponame=$(ls)
cd $reponame
chmod u+x $1
exec $1