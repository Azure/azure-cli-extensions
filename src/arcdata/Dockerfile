#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#------------------------------------------------------------------------------

ARG AZEXT_IMAGE
ARG CLI_VERSION
ARG BUILD_DATE

FROM ${AZEXT_IMAGE} AS build-env

LABEL maintainer="Microsoft" \
      org.label-schema.schema-version="1.0" \
      org.label-schema.vendor="Microsoft" \
      org.label-schema.name="Azure CLI ArcData extension" \
      org.label-schema.version=${CLI_VERSION} \
      org.label-schema.license="MIT" \
      org.label-schema.description="The Azure CLI ArcData extension." \
      org.label-schema.url="https://docs.microsoft.com/cli/azure/overview" \
      org.label-schema.build-date="${BUILD_DATE}" \
      org.label-schema.docker.cmd="docker run -v \${HOME}/.kube:/root/.kube -v \${HOME}/.azure:/root/.azure -it mcr.microsoft.com/azure-cli:${CLI_VERSION}"

WORKDIR ../../azure-cli-extension
COPY . /azure-cli-extension

# package and install arcdata az ext
RUN ./scripts/install.sh

WORKDIR /
CMD bash
