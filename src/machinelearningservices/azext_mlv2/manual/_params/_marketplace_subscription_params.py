from azext_mlv2.manual._params._common_params import (
    add_common_params,
    add_file_param,
    add_lro_param,
    add_max_results_params,
    add_override_param,
)
from azure.ai.ml.constants._common import YAMLRefDocLinks


def add_name_param(c):
    c.argument("name", options_list=["--name", "-n"], type=str, help="Name of the marketplace subscription.")


def load_marketplace_subscription_params(self):
    with self.argument_context("ml marketplace-subscription list") as c:
        add_common_params(c)
        add_max_results_params(c)

    with self.argument_context("ml marketplace-subscription show") as c:
        add_common_params(c)
        add_name_param(c)

    with self.argument_context("ml marketplace-subscription create") as c:
        add_override_param(c)
        add_common_params(c)
        add_name_param(c)
        add_lro_param(c)
        add_file_param(c, "marketplace-subscription", "")

    with self.argument_context("ml marketplace-subscription update") as c:
        add_common_params(c)
        add_name_param(c)
        add_lro_param(c)

    with self.argument_context("ml marketplace-subscription delete") as c:
        add_common_params(c)
        add_name_param(c)
        add_lro_param(c)
