#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Generates role template from what's defined in the helm chart.
#
# Usage:
#
# $ generate-role-template.sh

set -e

# -- position to repository base root location --
: "${EXTSION_ROOT_DIR:=`cd $(dirname $0); cd ../; pwd`}"

DEST_FILE=${EXTSION_ROOT_DIR}/arcdata/azext_arcdata/kubernetes_sdk/dc/templates/bootstrap/role-bootstrapper.yaml.tmpl
cp ${EXTSION_ROOT_DIR}/../helm/arcdataservices/templates/role-bootstrapper.yaml ${DEST_FILE}

# Removing Helm templating to make it a regular yaml
#
sed -i "s/\.Release\.Namespace/model\.namespace/g" ${DEST_FILE}
sed -i "/^{{ if and (not \.Values\.Azure\.LeastPrivilegeSettings\.RuntimeServiceAccount).*/d" ${DEST_FILE}
sed -i "/^{{ end }}/d" ${DEST_FILE}
sed -i "/^  labels\:$/d" ${DEST_FILE}
sed -i "/^    helm\.sh\/chart\:/d" ${DEST_FILE}