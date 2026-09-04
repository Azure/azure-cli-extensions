import pydash as _
import re
from azext_arcdata.postgres.constants import (
    API_GROUP,
    RESOURCE_KIND_PLURAL,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.client import KubernetesClient
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.constants import POSTGRES_CRD_NAME
from azext_arcdata.vendored_sdks.kubernetes_sdk.models._models import (
    ComMicrosoftArcdataV1Beta6PostgreSql as PostgresCustomResource,
)


def resolve_postgres_instances(
    namespace,
    name=None,
    field_filter=None,
    label_filter=None,
) -> list:

    client = KubernetesClient.resolve_k8s_client().CustomObjectsApi()

    response = client.list_namespaced_custom_object(
        namespace=namespace,
        field_selector=field_filter,
        label_selector=label_filter,
        group=API_GROUP,
        version=KubernetesClient.get_crd_version(POSTGRES_CRD_NAME),
        plural=RESOURCE_KIND_PLURAL,
    )

    items = response.get("items")

    instances = _.map_(items, PostgresCustomResource.from_dict)

    if name is not None:
        def name_matches(instance):
            return re.match(name, instance.metadata.name)
        instances = _.filter_(instances, name_matches)

    return instances
