# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


def add_model_hosting_file_param(c):
    c.argument(
        "file",
        options_list=["--file", "-f"],
        required=True,
        type=str,
        help=f"Local path to the YAML file containing the configuration specification.",
    )


def add_model_param(c):
    c.argument(
        "model",
        options_list=["--model", "-m"],
        required=True,
        type=str,
        help=f"Name of the model.",
    )


def add_publisher_param(c):
    c.argument(
        "publisher",
        options_list=["--publisher", "-p"],
        required=True,
        type=str,
        help=f"Name of the publisher.",
    )


def add_location_param(c):
    c.argument(
        "location",
        options_list=["--location", "-l"],
        required=True,
        type=str,
        help=f"Azure region for the gpu configuration.",
    )


def add_transaction_id_param(c):
    c.argument(
        "transaction_id",
        options_list=["--transaction-id", "-t"],
        required=True,
        type=str,
        help=f"Transaction id for the gpu configuration.",
    )


def add_size_param(c):
    c.argument(
        "size",
        options_list=["--size", "-s"],
        required=False,
        type=int,
        help=f"Number of gpu configuration requests to display.",
    )


def add_page_param(c):
    c.argument(
        "page",
        options_list=["--page"],
        required=False,
        type=int,
        help=f"Page number for pagination.",
    )


def add_display_name_param(c):
    c.argument(
        "name",
        options_list=["--name", "-n"],
        required=False,
        type=str,
        help=f"Display name of publisher",
    )


def add_description_param(c):
    c.argument(
        "description",
        options_list=["--description", "-d"],
        required=False,
        type=str,
        help=f"Description of the publisher.",
    )


def add_website_param(c):
    c.argument(
        "website",
        options_list=["--website", "-w"],
        required=False,
        type=str,
        help=f"Website of the publisher",
    )


def add_offer_id_param(c):
    c.argument(
        "offer_id",
        options_list=["--offer-id", "-of"],
        required=False,
        type=str,
        help=f"Offer id of the plan",
    )


def add_plan_id_param(c):
    c.argument(
        "plan_id",
        options_list=["--plan-id", "-pl"],
        required=False,
        type=str,
        help=f"Plan id of the plan",
    )


def add_version_param(c):
    c.argument(
        "version",
        options_list=["--version", "-v"],
        required=True,
        type=str,
        help=f"Version of the model.",
    )

def add_status_param(c):
    c.argument(
        "status",
        options_list=["--status", "-s"],
        required=True,
        type=str,
        help=f"Model approval status.",
    )

def add_validation_id_param(c):
    c.argument(
        "validation_id",
        options_list=["--validation-id", "-vid"],
        required=True,
        type=str,
        help=f"Id of the validation run.",
    )


def add_file_name_param(c):
    c.argument(
        "file_name",
        options_list=["--file-name", "-fn"],
        required=False,
        type=str,
        help=f"Name of the result file.",
    )


def add_target_path_param(c):
    c.argument(
        "result_path",
        options_list=["--target-path", "-tp"],
        required=False,
        type=str,
        help=f"Target path for the downloaded file.",
    )

def add_model_card_dir_param(c):
    c.argument(
        "model_card_dir",
        options_list=["--model-card-dir", "-dir"],
        required=True,
        type=str,
        help=f"Path to the directory for model card configuration.",
    )

def add_model_id_param(c):
    c.argument(
        "model_id",
        options_list=["--model-id", "-mid"],
        required=True,
        type=str,
        help=f"ID of the model.",
    )

def add_optional_model_hosting_file_param(c):
    c.argument(
        "file",
        options_list=["--file", "-f"],
        required=False,
        type=str,
        help=f"[Depreciated] Local path to the YAML file containing the configuration specification.",
    )


def load_model_hosting_params(self):
    with self.argument_context("ml modelpublisher gpu-config create") as c:
        add_model_param(c)
        add_publisher_param(c)
        add_model_hosting_file_param(c)
    with self.argument_context("ml modelpublisher gpu-config show") as c:
        add_model_param(c)
        add_publisher_param(c)
        add_location_param(c)
        add_transaction_id_param(c)
    with self.argument_context("ml modelpublisher gpu-config list") as c:
        add_model_param(c)
        add_publisher_param(c)
        add_location_param(c)
        add_size_param(c)
        add_page_param(c)
    with self.argument_context("ml modelpublisher show") as c:
        add_publisher_param(c)
    with self.argument_context("ml modelpublisher update") as c:
        add_publisher_param(c)
        add_display_name_param(c)
        add_description_param(c)
        add_website_param(c)
    with self.argument_context("ml modelpublisher registry set") as c:
        add_publisher_param(c)
        add_model_hosting_file_param(c)
    with self.argument_context("ml modelpublisher plan create") as c:
        add_publisher_param(c)
        add_model_param(c)
        add_model_hosting_file_param(c)
    with self.argument_context("ml modelpublisher plan list") as c:
        add_model_param(c)
        add_publisher_param(c)
        add_location_param(c)
    with self.argument_context("ml modelpublisher plan show") as c:
        add_model_param(c)
        add_publisher_param(c)
        add_location_param(c)
        add_offer_id_param(c)
        add_plan_id_param(c)
    with self.argument_context("ml modelpublisher plan update") as c:
        add_model_param(c)
        add_publisher_param(c)
        add_location_param(c)
        add_plan_id_param(c)
    with self.argument_context("ml modelpublisher model create") as c:
        add_publisher_param(c)
        add_model_param(c)
        add_optional_model_hosting_file_param(c)
    with self.argument_context("ml modelpublisher model list") as c:
        add_publisher_param(c)
        add_size_param(c)
        add_page_param(c)
    with self.argument_context("ml modelpublisher model show") as c:
        add_model_param(c)
        add_publisher_param(c)
    with self.argument_context("ml modelpublisher model approval") as c:
        add_model_param(c)
        add_publisher_param(c)
        add_version_param(c)
        add_status_param(c)
    with self.argument_context("ml modelpublisher release-candidate create") as c:
        add_publisher_param(c)
        add_model_param(c)
        add_model_hosting_file_param(c)
    with self.argument_context("ml modelpublisher release-candidate list") as c:
        add_publisher_param(c)
        add_model_param(c)
        add_size_param(c)
        add_page_param(c)
    with self.argument_context("ml modelpublisher release-candidate show") as c:
        add_model_param(c)
        add_publisher_param(c)
        add_version_param(c)
    with self.argument_context("ml modelpublisher release-candidate download-validation-result") as c:
        add_publisher_param(c)
        add_model_param(c)
        add_version_param(c)
        add_validation_id_param(c)
        add_file_name_param(c)
        add_target_path_param(c)
    with self.argument_context("ml modelpublisher release-candidate download-deployment-logs") as c:
        add_publisher_param(c)
        add_model_param(c)
        add_version_param(c)
        add_validation_id_param(c)
        add_file_name_param(c)
        add_target_path_param(c)
    with self.argument_context("ml modelpublisher release-candidate promote-to-prod") as c:
        add_model_param(c)
        add_publisher_param(c)
        add_version_param(c)
    with self.argument_context("ml modelpublisher enable-marketplace-integration") as c:
        add_publisher_param(c)
        add_model_hosting_file_param(c)
    with self.argument_context("ml modelpublisher model-card-internal show") as c:
        add_publisher_param(c)
        add_model_param(c)
    with self.argument_context("ml modelpublisher model-card-internal update") as c:
        add_publisher_param(c)
        add_model_param(c)
        add_model_hosting_file_param(c)
    with self.argument_context("ml modelpublisher model-card-internal attach") as c:
        add_publisher_param(c)
        add_model_param(c)
        add_version_param(c)
    with self.argument_context("ml modelpublisher model-card generate-template") as c:
        add_model_card_dir_param(c)
    with self.argument_context("ml modelpublisher model-card validate") as c:
        add_model_card_dir_param(c)
    with self.argument_context("ml modelpublisher model-card apply") as c:
        add_model_id_param(c)
        add_model_card_dir_param(c)
