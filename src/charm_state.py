#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module defining the CharmState class which represents the state of the SAML Integrator charm."""

from pydantic import AnyHttpUrl, BaseModel, Extra, Field
from typing import List, Optional

KNOWN_CHARM_CONFIG = (
    "entity_id",
    "metadata_url",
)

class SamlConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """Represent charm builtin configuration values.

    Attrs:
        server_name: server_name config.
        report_stats: report_stats config.
    """

    entity_id: str | None = Field(..., min_length=2)
    metadata_url: str | None = AnyHttpUrl(None)

    class Config:  # pylint: disable=too-few-public-methods
        """Config class.

        Attrs:
            extra: extra configuration.
        """

        extra = Extra.allow

class Service:
    """Represents the URL and schema for SAML URLs.

    Attrs:
        url: The SAML target URL.
        binding: SAML protocol binding to be used."
    """

    def __init__(
        self,
        url: AnyHttpUrl,
        binding: str
    ):
        """Initialize a new instance of the Service class.

        Args:
            url: The SAML URL.
            binding: The SAML binding.
        """
        self.url = url
        self.binding = binding


class CharmState:
    """Represents the state of the SAML Integrator charm.

    Attrs:
        single_sign_on_service_redirect: Target of the IdP where the Authentication REDIRECT Request Message will be sent.
        single_sign_on_service_post: Target of the IdP where the Authentication POST Request Message will be sent.
        single_logout_service_url: URL location where the <LogoutRequest> from the IdP will be sent (IdP-initiated logout).
        single_logout_service_response_redirect: Location where the REDIRECT <LogoutResponse> from the IdP will sent (SP-initiated logout, reply): only present if different from url parameter.
        single_logout_service_response_post:  Location where the POST <LogoutResponse> from the IdP will sent (SP-initiated logout, reply): only present if different from url parameter.
        x509certs: List of of public X.509 certificates of the IdP.
    """

    def __init__(
        self,
        saml_config: SamlConfig,
        single_sign_on_service_redirect: Optional[Service],
        single_sign_on_service_post: Optional[Service],
        single_logout_service_url: Optional[str],
        single_logout_service_response_redirect: Optional[Service],
        single_logout_service_response_post: Optional[Service],
        x509certs: List[str]
    ):
        """Initialize a new instance of the CharmState class.

        Args:
            single_sign_on_service_redirect: Target of the IdP where the Authentication REDIRECT Request Message will be sent.
            single_sign_on_service_post: Target of the IdP where the Authentication POST Request Message will be sent.
            single_logout_service_url: URL location where the <LogoutRequest> from the IdP will be sent (IdP-initiated logout).
            single_logout_service_response_redirect: Location where the REDIRECT <LogoutResponse> from the IdP will sent (SP-initiated logout, reply): only present if different from url parameter.
            single_logout_service_response_post:  Location where the POST <LogoutResponse> from the IdP will sent (SP-initiated logout, reply): only present if different from url parameter.
            x509certs: List of of public X.509 certificates of the IdP.
        """
        self._saml_config = saml_config
        self.single_sign_on_service_redirect = single_sign_on_service_redirect
        self.single_sign_on_service_post = single_sign_on_service_post
        self.single_logout_service_url = single_logout_service_url
        self.single_logout_service_response_redirect = single_logout_service_response_redirect
        self.single_logout_service_response_post = single_logout_service_response_post
        self.x509certs=x509certs

    @property
    def entity_id(self) -> str:
        """Return entity_id config.

        Returns:
            str: entity_id config.
        """
        return self._saml_config.entity_id

    @property
    def metadata_url(self) -> str:
        """Return metadata_url config.

        Returns:
            str: metadata_url config.
        """
        return self._saml_config.metadata_url

