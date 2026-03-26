# Confcom Extension Documentation

Welcome to the Azure CLI Confcom (Confidential Computing) extension documentation.
This extension provides tools for generating security policies and fragments for confidential computing workloads in Azure Container Instances (ACI) and Kata Containers.

## Getting Started

If you're new to the confcom extension, we recommend starting with:

1. **Installation**: Follow the main README.md in the parent directory for installation instructions
2. **Core Concepts**: Read `common.md` and `policy_enforcement_points.md` to understand the fundamentals
3. **Choose Your Use Case**:
   - For Azure Container Instances: Start with `acipolicygen.md`
   - For policy fragments: Begin with `acifragmentgen.md`
   - For Kata Containers: Review `katapolicygen.md`
4. **Configuration**: Refer to `v1_json_file_format.md` for input file structures
5. **Testing**: Use `testing.md` to validate your setup and policies

## File Overview

This directory contains comprehensive documentation for all aspects of the confcom extension.
Below is a guide to each file and what you'll find in it:

### Core Concepts Documentation

#### `common.md`

Shared Concepts and Utilities

- Common functionality shared across all confcom commands
- Explains core concepts used throughout the extension
- Covers shared parameters, configuration options, and data structures
- Provides foundational knowledge needed for all other documentation

#### `policy_enforcement_points.md`

Policy Enforcement Architecture

- Deep dive into how security policies are enforced in confidential container environments
- Explains the relationship between policy fragments and enforcement points
- Covers the architecture of policy validation and execution
- Details integration points with Azure confidential computing services

#### `v1_json_file_format.md`

JSON Configuration File Format

- Specification for the v1 JSON file format used by confcom commands
- Defines schema and structure for input configuration files
- Provides examples and validation rules for JSON inputs
- Covers migration from older formats and version compatibility

### Command Documentation

#### `acipolicygen.md`

Azure Container Instances Policy Generator

- Detailed guide for the `az confcom acipolicygen` command
- Explains how to generate confidential computing security policies for ACI workloads
- Covers policy generation from ARM templates, images, and JSON configurations
- Includes examples for CCE policy creation
- Shows how to inject policies into ARM templates and work with parameters
- Contains troubleshooting and best practices for ACI security policies

#### `acifragmentgen.md`

Azure Container Instances Fragment Generator

- Documentation for the `az confcom acifragmentgen` command
- Explains policy fragments and their role in confidential computing security
- Covers two types of fragments: image-attached and standalone fragments
- Provides examples for creating and managing security fragments
- Links to certificate and signing documentation for fragment authentication
- Details ORAS registry integration for fragment storage

#### `katapolicygen.md`

Kata Containers Policy Generator

- Guide for the `az confcom katapolicygen` command
- Focuses on generating security policies specifically for Kata Containers
- Covers Kata-specific security requirements and policy structures
- Includes examples and usage patterns for Kata workloads
- Explains integration with Kubernetes and container runtime security

### Development and Testing

#### `testing.md`

Testing Guidelines and Procedures

- Comprehensive testing documentation for the confcom extension
- Covers unit tests, integration tests, and end-to-end testing scenarios
- Explains test setup, execution, and validation procedures
- Includes guidelines for testing security policies and fragments
- Provides troubleshooting for common testing issues

## Support and Contribution

For issues, feature requests, or contributions, please refer to the main Azure CLI extensions repository. Each command documentation includes troubleshooting sections and common error resolutions.

The confcom extension is actively developed and supports the latest Azure confidential computing features. Check the main README.md for current limitations and supported platforms.