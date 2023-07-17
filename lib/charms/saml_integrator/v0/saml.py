#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# Licensed under the Apache2.0. See LICENSE file in charm source for details.

"""TODO: Add a proper docstring here.

This is a placeholder docstring for this charm library. Docstrings are
presented on Charmhub and updated whenever you push a new version of the
library.

Complete documentation about creating and documenting libraries can be found
in the SDK docs at https://juju.is/docs/sdk/libraries.

See `charmcraft publish-lib` and `charmcraft fetch-lib` for details of how to
share and consume charm libraries. They serve to enhance collaboration
between charmers. Use a charmer's libraries for classes that handle
integration with their charm.

Bear in mind that new revisions of the different major API versions (v0, v1,
v2 etc) are maintained independently.  You can continue to update v0 and v1
after you have pushed v3.

Markdown is supported, following the CommonMark specification.
"""

# The unique Charmhub library identifier, never change it
LIBID = "511cdfa7de3d43568bf9b512f9c9f89d"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1

PYDEPS = ["ops>=2.0.0", "pydantic==1.10.10"]

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import AnyHttpUrl, BaseModel, Field
from ops import (
    CharmBase,
    Object,
    Relation,
    RelationCreatedEvent,
    RelationChangedEvent,
)


class SamlEndpoint(BaseModel):
    """Represent a SAML endpoint.

    Attrs:
        name: Endpoint name.
        url: Endpoint URL.
        binding: Endpoint binding.
        response_url: URL to address the response to.
    """

    name: str = Field(..., min_length=1)
    url: AnyHttpUrl
    binding: str = Field(..., min_length=1)
    response_url: Optional[AnyHttpUrl]

    def to_relation_data(self) -> Dict[str, str]:
        result = {}
        http_method = endpoint.binding.split(":")[-1].split("-")[-1].lower()
        lowercase_name = re.sub(r"(?<!^)(?=[A-Z])", "_", endpoint.name).lower()
        prefix = f"{lowercase_name}_{http_method}_"
        result[f"{prefix}url"] = endpoint.url
        result[f"{prefix}binding"] = endpoint.binding
        if endpoint.response_url:
            result[f"{prefix}response_url"] = endpoint.response_url
        return result
    
    @classmethod
    def from_relation_data(relation_data: Dict[str, str]) -> "SamlEndpoint":
        url_key = ""
        for key, _ in relation_data.keys():
            if key.endswith("_url"):
                url_key = key 
        lowercase_name = url_key.split("_")[:-2]
        name = "".join(x.capitalize() for x in lowercase_name.split("_"))
        http_method = url_key.split("_")[-2]
        prefix = f"{lowercase_name}_{http_method}_"
        return cls(
            name,
            relation_data[f"{prefix}url"],
            relation_data[f"{prefix}binding"],
            relation_data[f"{prefix}response_url"] if f"{prefix}response_url" in relation_data.keys() else None,
        )


class SamlRelationData(BaseModel):
    """Represent the relation data.

    Attrs:
        entity_id: SAML entity ID.
        metadata_url: URL to the metadata.
        certificates: List of SAML certificates.
        endpoints: List of SAML endpoints.
    """
    entity_id: str = Field(..., min_length=1)
    metadata_url: AnyHttpUrl
    certificates: List[str]
    endpoints: List[SamlEndpoint]

    def to_relation_data(self) -> Dict[str, str]:
        result = {
            "entity_id": self.entity_id,
            "metadata_url": self.metadata_url,
            "x509certs": ",".join(self.certificates),
        }
        for endpoint in self.endpoints:
            result = {**result, **endpoint.to_relation_data()}
        return result
    
    @classmethod
    def from_relation_data(relation_data: Dict[str, str]) -> "SamlRelationData":

        endpoints = []
        for key, _ in relation_data.keys():
            if key.endswith("_url"):
                prefix = url_key.split("_")[:-1]
                endpoints.append(
                    SamlEndpoint.from_relation_data(
                        {key: relation_data[key] for key in relation_data.keys() if key.startswith(prefix)}
                    )
                )
        return cls(
            relation_data["entity_id"],
            relation_data["metadata_url"],
            relation_data["certificates"].split(","),
            endpoints
        )



class SamlProvides(Object, ABC):
    
    def __init__(self, charm: CharmBase, relation_name: str) -> None:
        super().__init__(charm, relation_name)
        self.charm = charm
        self.relation_name = relation_name
        self.framework.observe(charm.on[relation_name].relation_created, self._on_relation_created)

    def _on_relation_created(self, event: RelationCreatedEvent) -> None:
        """Handle a change to the saml relation.

        Populate the event data.

        Args:
            event: Event triggering the relation-created hook for the relation.
        """
        if not self.model.unit.is_leader():
            return
        self._update_relation_data(event.relation, self.charm.get_saml_data())

    @property
    def relations(self) -> List[Relation]:
        """The list of Relation instances associated with this relation_name."""
        return list(self.charm.model.relations[self.relation_name])

    def _update_relation_data(self, relation: Relation, saml_data: SamlRelationData) -> None:
        relation.data[self.charm.model.app].update(saml_data.to_relation_data())


class DataRequires(Object, ABC):
    """Requires-side of the relation."""
    def __init__(
        self,
        charm,
        relation_name: str,
    ):
        super().__init__(charm, relation_name)
        self.charm = charm
        self.relation_name = relation_name
        self.framework.observe(
            self.charm.on[relation_name].relation_changed, self._on_relation_changed_event
        )

    @abstractmethod
    def _on_relation_changed_event(self, event: RelationChangedEvent) -> None:
        """Handle the relation changed event."""
        raise NotImplementedError
