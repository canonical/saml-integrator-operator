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

# pylint: disable=wrong-import-position
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ops import Object, RelationChangedEvent
from pydantic import AnyHttpUrl, BaseModel, Field
from pydantic.tools import parse_obj_as


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
        """Convert an instance of SamlEndpoint to the relation representation.

        Returns:
            Dict containing the representation.
        """
        result: Dict[str, str] = {}
        http_method = self.binding.split(":")[-1].split("-")[-1].lower()
        lowercase_name = re.sub(r"(?<!^)(?=[A-Z])", "_", self.name).lower()
        prefix = f"{lowercase_name}_{http_method}_"
        result[f"{prefix}url"] = self.url
        result[f"{prefix}binding"] = self.binding
        if self.response_url:
            result[f"{prefix}response_url"] = self.response_url
        return result

    @classmethod
    def from_relation_data(cls, relation_data: Dict[str, str]) -> "SamlEndpoint":
        """Initialize a new instance of the SamlEndpoint class from the relation data.

        Args:
            relation_data: the relation data.

        Returns:
            A SamlEndpoint instance.
        """
        url_key = ""
        for key in relation_data:
            if key.endswith("_redirect_url") or key.endswith("_post_url"):
                url_key = key
        lowercase_name = "_".join(url_key.split("_")[:-2])
        name = "".join(x.capitalize() for x in lowercase_name.split("_"))
        http_method = url_key.split("_")[-2]
        prefix = f"{lowercase_name}_{http_method}_"
        return cls(
            name=name,
            url=parse_obj_as(AnyHttpUrl, relation_data[f"{prefix}url"]),
            binding=relation_data[f"{prefix}binding"],
            response_url=parse_obj_as(AnyHttpUrl, relation_data[f"{prefix}response_url"])
            if f"{prefix}response_url" in relation_data
            else None,
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
        """Convert an instance of SamlRelationData to the relation representation.

        Returns:
            Dict containing the representation.
        """
        result = {
            "entity_id": self.entity_id,
            "metadata_url": self.metadata_url,
            "x509certs": ",".join(self.certificates),
        }
        for endpoint in self.endpoints:
            result = {**result, **endpoint.to_relation_data()}
        return result

    @classmethod
    def from_relation_data(cls, relation_data: Dict[str, str]) -> "SamlRelationData":
        """Initialize a new instance of the SamlRelationData class from the relation data.

        Args:
            relation_data: the relation data.

        Returns:
            A SamlRelationData instance.
        """
        endpoints = []
        for key in relation_data:
            if key.endswith("_redirect_url") or key.endswith("_post_url"):
                prefix = "_".join(key.split("_")[:-1])
                endpoints.append(
                    SamlEndpoint.from_relation_data(
                        {
                            key: relation_data[key]
                            for key in relation_data
                            if key.startswith(prefix)
                        }
                    )
                )
        endpoints.sort(key=lambda ep: ep.name)
        return cls(
            entity_id=relation_data["entity_id"],
            metadata_url=parse_obj_as(AnyHttpUrl, relation_data["metadata_url"]),
            certificates=relation_data["x509certs"].split(","),
            endpoints=endpoints,
        )


class SamlRequires(Object, ABC):
    """Requires-side of the relation.

    Attrs:
        charm: the provider charm.
        relation_name: the relation name.
    """

    def __init__(
        self,
        charm,
        relation_name: str,
    ):
        """Initialize a new instance of the SamlRequires class.

        Args:
            charm: the requirer charm.
            relation_name: the relation name.
        """
        super().__init__(charm, relation_name)
        self.charm = charm
        self.relation_name = relation_name
        self.framework.observe(
            self.charm.on[relation_name].relation_changed, self._on_relation_changed_event
        )

    @abstractmethod
    def _on_relation_changed_event(self, event: RelationChangedEvent) -> None:
        """Handle the relation changed event.

        Args:
            event: The event triggering the handler.

        Raises:
            NotImplementedError: always thrown.
        """
        raise NotImplementedError
