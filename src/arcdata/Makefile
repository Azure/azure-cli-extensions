###############################################################################
#
# Copyright (c) Microsoft Corporation.
#
#
# Stop!
#
# This makefile is not intended to aid azure-cli command authoring or
# development. Its intention and existence is only to fit into the arcdata build
# ecosystem for non command authors to use easily via make. If you are building
# azure-cli commands please start by reading the `README.md`.
#
# Quick Start to run Azure CLI with ArcData extension:
# $ make az
# [docker-container]> az --help
#
###############################################################################

include ../../build/common.mk

IMAGE            = azure-arcdata-cli
LABEL            = "org.label-schema.name=Azure CLI with ArcData extension"
TARGET           = build-env
NAMESPACE        = microsoft
BUILD_DATE       = $(shell date)
CLI_ROOT         = $(shell git rev-parse --show-toplevel)/projects/azure-cli-extension
OUTPUT_DIRECTORY = $(CLI_ROOT)/output
DOCKERFILE       = $(CLI_ROOT)/Dockerfile
AZEXT_IMAGE      = $(BUILD_DOCKER_BASE_TEST_IMAGE):$(BUILD_DOCKER_BASE_IMAGE_TAG)
.DEFAULT_GOAL    = help

.PHONY: az
az: install
	@echo "+ $@"
	@docker run -it -v ${HOME}/.kube:/root/.kube \
		-v ${HOME}/.azure:/root/.azure $(NAMESPACE)/$(IMAGE):latest

.PHONY: dev-setup
dev-setup:
	@echo "+ $@"
	@cd $(CLI_ROOT)
	@python3 --version
	@python3 ./scripts/dev_setup.py
	@echo "!!!Remember to activate your venv for development!!! 'source ./env/bin/activate'"

.PHONY: clean
clean: down
	@echo "+ $@"
	@rm -rf $(OUTPUT_DIRECTORY)
	@rm -rf $(CLI_ROOT)/env

.PHONY: dockerclean
dockerclean: down

.PHONY: down
down:
	@echo "+ $@"
	@docker image ls --filter reference="$(NAMESPACE)/$(IMAGE)" --quiet | xargs docker image rm -f || true
	@docker system prune -a -f --filter label=$(LABEL)

.PHONY: version
version:
	@echo "+ $@"
	$(eval CLI_VERSION=$(shell sh -c "$(CLI_ROOT)/scripts/version.sh"))

.PHONY: template
template:
	@echo "+ $@"
	@$(CLI_ROOT)/scripts/generate-role-template.sh

.PHONY: unit-tests
unit-tests: install
	@echo "+ $@"
	@docker run --rm --name unit-tests $(NAMESPACE)/$(IMAGE):latest \
		/bin/bash -c "./azure-cli-extension/scripts/gci/verify-all.sh"

.PHONY: install
install: version template
	@echo "+ $@"
	@echo "azext_arcdata version = $(CLI_VERSION)"
	@echo "BUILD_DATE = $(BUILD_DATE)"
	@echo "AZEXT_IMAGE = $(AZEXT_IMAGE)"

	@sed -e 's%$${CLI_VERSION}%$(CLI_VERSION)%' \
	    -e 's%$${BUILD_DATE}%$(BUILD_DATE)%' \
	    -e 's%$${AZEXT_IMAGE}%$(AZEXT_IMAGE)%' < $(DOCKERFILE) \
		| docker build --label $(LABEL) --target $(TARGET) \
		-f - -t $(NAMESPACE)/$(IMAGE):$(CLI_VERSION) .
	@docker tag $(NAMESPACE)/$(IMAGE):$(CLI_VERSION) $(NAMESPACE)/$(IMAGE):latest
	@docker images --format '{{.Repository}}:{{.Tag}}\t\t Built: {{.CreatedSince}}\t\tSize: {{.Size}}' \
		| grep $(IMAGE):$(CLI_VERSION)

.PHONY: all
all: package-all unit-tests

.PHONY: package-all
package-all: install
	@echo "+ $@"
	@rm -rf $(OUTPUT_DIRECTORY)
	@mkdir -p $(OUTPUT_DIRECTORY)
	$(eval CONTAINER_ID = $(shell docker create $(NAMESPACE)/$(IMAGE):latest))
	@docker cp $(CONTAINER_ID):/azure-cli-extension/output/packages $(OUTPUT_DIRECTORY)
	@docker stop $(CONTAINER_ID)
	@docker rm $(CONTAINER_ID)
	@chmod -R 755 $(OUTPUT_DIRECTORY)/packages

.PHONY: help
help:
	@echo ""
	@echo "Make targets: "
	@echo "   make [help]         - This help text."
	@echo "   make az             - Install the azure-cli ArcData extension and invoke 'docker run -it'."
	@echo "   make dev-setup      - Convenience to prepare a local development environment for ArcData extension."
	@echo "   make unit-tests     - Run all unit-tests, coverage, verify checks, lint, style, formatter."
	@echo "   make install        - Install the azure-cli ArcData extension by building an image with it available."
	@echo "   make package-all    - Build python wheel."
	@echo "   make all            - Build python wheel and run all unit-tests, coverage, verify checks, lint, style, formatter."
	@echo "   make clean          - Remove all build files, docker images, and cached artifacts."
	@echo "   make dockerclean    - Remove all docker images including any cached artifacts."
	@echo "   make down           - Shorthand for 'dockerclean'."
	@echo "   make version        - Display the current azure-cli ArcData extension version from source."
	@echo "   make template       - Generate template files."
	@echo ""
