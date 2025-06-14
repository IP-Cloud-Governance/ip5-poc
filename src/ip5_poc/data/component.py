from ip5_poc.model import (
    Model,
    Model3,
    OscalCompleteOscalComponentDefinitionComponentDefinition,
    OscalCompleteOscalMetadataMetadata,
    OscalCompleteOscalMetadataLastModified,
    OscalCompleteOscalMetadataVersion,
    OscalCompleteOscalMetadataOscalVersion,
    Party,
    UUIDDatatype,
    StringDatatype,
    OscalCompleteOscalComponentDefinitionDefinedComponent,
    OscalCompleteOscalMetadataResponsibleRole,
    TokenDatatype,
    OscalCompleteOscalComponentDefinitionControlImplementation,
    OscalCompleteOscalComponentDefinitionImplementedRequirement,
)


def get_aks_definition() -> Model:
    return Model3(
        component_definition=OscalCompleteOscalComponentDefinitionComponentDefinition(
            uuid=UUIDDatatype(root="e46eee83-a457-42d9-9cc4-96b00e64c638"),
            metadata=OscalCompleteOscalMetadataMetadata(
                title="Azure Kubernetes Service (AKS) Component Definition",
                last_modified=OscalCompleteOscalMetadataLastModified(
                    root="2025-05-21T13:23:00.000000-00:00"
                ),
                version=OscalCompleteOscalMetadataVersion(root="1.0"),
                oscal_version=OscalCompleteOscalMetadataOscalVersion(root="1.1.0"),
                parties=[
                    Party(
                        uuid=UUIDDatatype(root="ee47836c-877c-4007-bbf3-c9d9bd805a9a"),
                        name=StringDatatype(
                            root="Bundesamt für Informatik und Telekommunikation BIT"
                        ),
                        type=StringDatatype(root="organization"),
                    )
                ],
            ),
            components=[
                OscalCompleteOscalComponentDefinitionDefinedComponent(
                    uuid=UUIDDatatype(root="190eb8f2-0bd0-49b1-b378-8a2f072a1419"),
                    type=StringDatatype(root="service"),
                    title="Azure Kubernetes Service (AKS)",
                    description="Managed Kubernetes service in Microsoft Azure.",
                    responsible_roles=[
                        OscalCompleteOscalMetadataResponsibleRole(
                            role_id=TokenDatatype(root="provider"),
                            party_uuids=[
                                UUIDDatatype(
                                    root="ee47836c-877c-4007-bbf3-c9d9bd805a9a"
                                )
                            ],
                        )
                    ],
                    control_implementations=[
                        OscalCompleteOscalComponentDefinitionControlImplementation(
                            uuid=UUIDDatatype(
                                root="6c7e9b15-6d9c-4b61-a8a0-74ae51540efa"
                            ),
                            source="https://ip5-poc-webapp.azurewebsites.net/catalogs/si001.json",
                            description="Si001 - IKT-Grundschutz in der Bundesverwaltung",
                            implemented_requirements=[
                                OscalCompleteOscalComponentDefinitionImplementedRequirement(
                                    uuid=UUIDDatatype(
                                        root="d1016df0-9b5c-4839-86cd-f9c1d113077b"
                                    ),
                                    control_id=TokenDatatype(root="t6.1"),
                                    description="Account management for AKS cluster access.",
                                ),
                                OscalCompleteOscalComponentDefinitionImplementedRequirement(
                                    uuid=UUIDDatatype(
                                        root="65e30b37-0640-4844-9f42-b2a7ae944bb1"
                                    ),
                                    control_id=TokenDatatype(root="t8.1"),
                                    description="Cryptographic key management for AKS nodes.",
                                ),
                            ],
                        )
                    ],
                )
            ],
        )
    )
