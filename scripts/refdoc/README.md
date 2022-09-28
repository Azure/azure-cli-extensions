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

## Generating Sphinx output for the latest versions of all extensions in index ##

1. Ensure the CLI is installed in your Python virtual environment.
2. Inside the Python virtual environment, run `pip install sphinx==1.7.0`
3. Set the environment variable `AZ_EXT_REF_DOC_OUT_DIR` to an empty directory that exists.
4. Run the following script to generate sphinx output for the latest versions of all extensions in the index - `python ./scripts/ci/index_ref_doc.py -v`
5. The sphinx output will be in the directory pointed to by the `AZ_EXT_REF_DOC_OUT_DIR` environment variable.
