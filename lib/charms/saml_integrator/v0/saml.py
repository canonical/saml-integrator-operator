#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# Licensed under the Apache2.0. See LICENSE file in charm source for details.

"""Library to manage the relation data for the SAML Integrator charm.

This library contains the SamlRelationData class to encapsulate the relation
data, providing an improved user experience for the requirer charms developers.
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
from typing import Dict, List, Optional

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
