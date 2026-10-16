# nix-shell config for an AzCLI development environment.
#
# What does this do?
# > Installs Python 3.9
# > creates a python venv named 'env' (if not already created)
# > connects to the virtual env
# > Updates pip 
# > Installs the Azdev from pip (if not already done)
#
# How to use?
# > cd to this dir
# > run: `nix-shell`
#

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [ pkgs.python39 ];

  shellHook = ''
    if [ ! -d "env" ]; then
      python -m venv env --copies
      source ./env/bin/activate
      python3 -m pip install -U pip
      pip install azdev
    else
      source ./env/bin/activate
    fi
  '';
}

