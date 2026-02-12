# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------
import pydash as _


class CustomResourceDefinition(object):
    """
    Internal Custom Resource Definition object to be used for deployments.
    """

    def __init__(self, crd_object):
        """
        Initializes a CRD object with the given json.
        :param crd_object:
        """
        self.body = crd_object

    @property
    def body(self):
        """
        Gets the crd json body used for deployments.
        """
        return self._body

    @body.setter
    def body(self, crd_body):
        """
        Sets the crd body used for deployments.
        :param crd_body: The crd json.
        """
        self._body = crd_body

    @property
    def metadata(self):
        """
        Returns the metadata of the crd.
        :return:
        """
        return _.get(self, "body.metadata")

    @property
    def name(self):
        """
        Returns the name of the crd.
        :return:
        """
        return _.get(self, "body.metadata.name")

    @property
    def kind(self):
        """
        Returns the kind of the crd.
        :return:
        """
        return _.get(self, "names.kind")

    @property
    def spec(self):
        """
        Gets the spec of this crd.
        :return:
        """
        return _.get(self, "body.spec")

    @property
    def group(self):
        """
        Gets the API group of this CRD
        :return:
        """
        return _.get(self, "body.spec.group")

    @property
    def versions(self):
        """
        Gets the API version of this CRD
        :return:
        """
        return _.get(self, "body.spec.versions")

    @property
    def stored_version(self):
        """
        Gets the stored version of this CRD
        :return:
        """
        for version in _.get(self, "body.spec.versions"):
            if _.get(version, "storage"):
                return _.get(version, "name")
        raise ValueError(
            "CRD of kind '{}' does not have a persisted version".format(
                self.kind
            )
        )

    @property
    def names(self):
        """
        Gets the names of this crd.
        :return:
        """
        return _.get(self, "body.spec.names")

    @property
    def plural(self):
        """
        Gets the plural form of this crd.
        :return:
        """
        return _.get(self, "body.spec.names.plural")
