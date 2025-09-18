from azext_confcom.lib.aci_policy_spec import (
    AciContainerSpec,
    AciContainerProperties,
    AciFragmentSpec,
    AciPolicySpec,
)


def image_ref_to_aci_container_spec(
    image_ref: str,
) -> AciContainerSpec:

    return AciContainerSpec(
        name=image_ref,
        properties=AciContainerProperties(
            image=image_ref,
        )
    )


def image_refs_to_aci_policy_spec(
    image_refs: list[str],
    fragments: list[AciFragmentSpec],
) -> AciPolicySpec:

    return AciPolicySpec(
        fragments=[
            *fragments,
        ],
        containers=[
            image_ref_to_aci_container_spec(image_ref)
            for image_ref in image_refs
        ]
    )