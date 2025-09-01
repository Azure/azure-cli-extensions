.. :changelog:

Release History
===============

Guidance
++++++++
If there is no rush to release a new version, please just add a description of the modification under the *Pending* section.

To release a new version, please select a new version number (usually plus 1 to last patch version, X.Y.Z -> Major.Minor.Patch, more details in `\doc <https://semver.org/>`_), and then add a new section named as the new version number in this file, the content should include the new modifications and everything from the *Pending* section. Finally, update the `VERSION` variable in `setup.py` with this new version number.

Pending
+++++++

1.0.0b1
+++++++
* Add interactive AI-powered debugging tool `az aks agent`.
