# Ref doc gen #

Scripts for reference documentation generation for Azure CLI Extensions using [sphinx](http://www.sphinx-doc.org/en/master/)

# How to generate the Sphinx help file output #

## Set up environment ##

1. Ensure the CLI is installed in your Python virtual environment.
2. Inside the Python virtual environment, run `pip install sphinx==1.7.0`

## Run Sphinx ##

1. Run the generate script `python scripts/refdoc/generate.py -e PATH_TO_WHL.whl`

## Retrieve output ##

1. By default, the XML output is stored in `ref-doc-out-*/ind.xml`
