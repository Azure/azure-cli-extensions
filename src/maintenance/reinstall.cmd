cmd /c "az extension remove -n maintenance"
cmd /c "python setup.py bdist_wheel"
cmd /c "az extension add --source dist\maintenance-1.0.1-py2.py3-none-any.whl -y"