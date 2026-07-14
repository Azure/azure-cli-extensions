# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from knack.help_files import helps


def get_model_hosting_help():
    helps[
        "ml modelpublisher"
    ] = """
        type: group
        short-summary: Manage Azure ML model configurations through the global MPSS endpoints.
    """

    helps[
        "ml modelpublisher gpu-config"
    ] = """
        type: group
        short-summary: Model publishers can use this command to set gpu configuration for their model for Standard pay-per-token and Provisioned offerings on Models as a Service.
    """

    helps[
        "ml modelpublisher gpu-config create"
    ] = """
            type: command
            short-summary: Create gpu configuration request for a model.
    """

    helps[
        "ml modelpublisher gpu-config show"
    ] = """
            type: command
            short-summary: Show gpu configuration for a specific transaction-id.

    """

    helps[
        "ml modelpublisher gpu-config list"
    ] = """
            type: command
            short-summary: List gpu configuration requests raised for a model.

    """
    helps[
        "ml modelpublisher show"
    ] = """
            type: command
            short-summary: Displays publisher details for a given publisher.

    """
    helps[
        "ml modelpublisher update"
    ] = """
            type: command
            short-summary: Updates publisher details for a given publisher.

    """
    helps[
        "ml modelpublisher registry"
    ] = """
            type: group
            short-summary: Source registry details for a given publisher.

    """
    helps[
        "ml modelpublisher registry set"
    ] = """
            type: command
            short-summary: Set source registry details for a given publisher.

    """

    helps[
        "ml modelpublisher plan"
    ] = """
        type: group
        short-summary: Model publishers can use this command to create plan for their model by specifying details in defined yaml and later fetch the existing plan details.
    """

    helps[
        "ml modelpublisher plan create"
    ] = """
            type: command
            short-summary: Create plan details request for a model based on parameters passed in yaml file.
    """

    helps[
        "ml modelpublisher plan list"
    ] = """
            type: command
            short-summary: Lists plan details based on publisher and model name provided

    """
    helps[
        "ml modelpublisher plan show"
    ] = """
            type: command
            short-summary: Shows plan details based on what is provided out of offer_id and plan_id.

    """
    helps[
        "ml modelpublisher plan update"
    ] = """
            type: command
            short-summary: Update plan status for the given publisher model and the plan id.

    """
    helps[
        "ml modelpublisher model"
    ] = """
        type: group
        short-summary: Manage models for a publisher.
    """

    helps[
        "ml modelpublisher model create"
    ] = """
        type: command
        short-summary: Create a new model for a publisher.
    """

    helps[
        "ml modelpublisher model show"
    ] = """
        type: command
        short-summary: Show details of a specific model for a publisher.
    """

    helps[
        "ml modelpublisher model list"
    ] = """
        type: command
        short-summary: List all models for a publisher.
    """

    helps[
        "ml modelpublisher model approval"
    ] = """
        type: command
        short-summary: Approve/Reject a specific model version for publishing on foundry.
    """

    helps[
        "ml modelpublisher release-candidate"
    ] = """
        type: group
        short-summary: Manage model version lifecycle for a model.
    """

    helps[
        "ml modelpublisher release-candidate create"
    ] = """
        type: command
        short-summary: Create a new release candidate for a model by specifying details in yaml file.
    """

    helps[
        "ml modelpublisher release-candidate show"
    ] = """
        type: command
        short-summary: Show details of a specific release candidate for a publisher.
    """

    helps[
        "ml modelpublisher release-candidate list"
    ] = """
        type: command
        short-summary: List all release candidates for a publisher.
    """

    helps[
        "ml modelpublisher release-candidate download-validation-result"
    ] = """
        type: command
        short-summary: Downloads validation results for the specified release candidate for a given validation id.
    """

    helps[
        "ml modelpublisher release-candidate download-deployment-logs"
    ] = """
        type: command
        short-summary: Downloads deployment failure logs for the specified release candidate for a given validation id.
    """

    helps[
        "ml modelpublisher release-candidate promote-to-prod"
    ] = """
        type: command
        short-summary: Promotes to production a specific release candidate of the model.
    """

    helps[
        "ml modelpublisher enable-marketplace-integration"
    ] = """
            type: command
            short-summary: Enable marketplace integration for a given publisher by setting up publisherId in yaml file.
    """

    helps[
        "ml modelpublisher model-card"
    ] = """
        type: group
        short-summary: Model publishers can use this command to create & attach model card to their model.
    """

    helps[
        "ml modelpublisher model-card generate-template"
    ] = """
        type: command
        short-summary: Generate template files for a model card.
    """

    helps[
        "ml modelpublisher model-card validate"
    ] = """
        type: command
        short-summary: Validate model card locally.
    """

    helps[
        "ml modelpublisher model-card apply"
    ] = """
        type: command
        short-summary: Apply model card to a model & preview the model in foundry.
    """

    helps[
        "ml modelpublisher model-card-internal"
    ] = """
        type: group
        short-summary: Used by Microsoft PMs to add system tags to your model.
    """

    helps[
        "ml modelpublisher model-card-internal update"
    ] = """
        type: command
        short-summary: Update system metadata on a model card from the specified YAML file.
    """

    helps[
        "ml modelpublisher model-card-internal show"
    ] = """
        type: command
        short-summary: Show the latest system metadata of a model card.
    """

    helps[
        "ml modelpublisher model-card-internal attach"
    ] = """
        type: command
        short-summary: Attach the model card system metadata to a specific model version.
    """
