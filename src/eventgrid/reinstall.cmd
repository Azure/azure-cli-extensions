cmd /c "az extension remove -n eventgrid"
cmd /c "python setup.py bdist_wheel"
cmd /c "az extension add --source dist\eventgrid-0.4.5-py2.py3-none-any.whl -y"