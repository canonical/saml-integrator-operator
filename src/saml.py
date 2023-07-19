# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Provide the SamlApp class to encapsulate the business logic."""
import hashlib
import logging
import socket
import ssl
import urllib
from functools import cached_property
from typing import List, Optional, Set

from pydantic import AnyHttpUrl, BaseModel, Field

from charm_state import CharmConfigInvalidError, CharmState

logger = logging.getLogger(__name__)


class SamlEndpoint(BaseModel):  # pylint: disable=too-few-public-methods
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


class SamlIntegrator:  # pylint: disable=import-outside-toplevel
    """A class representing the SAML Integrator application.

    Attrs:
        entity_id: Entity ID for SAML.
        metadata_url: URL for the SAML metadata.
        endpoints: SAML endpoints.
        certificates: Public certificates.
    """

    def __init__(self, charm_state: CharmState):
        """Initialize a new instance of the SamlApp class.

        Args:
            charm_state: The state of the charm that the Saml instance belongs to.

        Raises:
            CharmConfigInvalidError: if the certificate validation fails.
        """
        self._charm_state = charm_state
        try:
            if not self._is_certificate_valid:
                raise CharmConfigInvalidError(
                    (
                        f"The certificate from {self._charm_state.metadata_url} "
                        "doesn't match the provided fingerprint"
                    )
                )
        except TimeoutError as ex:
            raise CharmConfigInvalidError(
                f"Error while validating certificate from {self._charm_state.metadata_url}"
            ) from ex

    @property
    def entity_id(self) -> str:
        """Return entity_id config.

        Returns:
            str: entity_id config.
        """
        return self._charm_state.entity_id

    @property
    def metadata_url(self) -> str:
        """Return metadata_url config.

        Returns:
            str: metadata_url config.
        """
        return self._charm_state.metadata_url

    @cached_property
    def _is_certificate_valid(self):
        """Validate the public certificate for the metadata URL.

        Returns:
            True if the certificate matches the one provided.

        Raises:
            TimeoutError: if the connection can't be established.
        """
        if self._charm_state.fingerprint:
            url = urllib.parse.urlparse(self._charm_state.metadata_url)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            context = ssl.create_default_context()
            with socket.create_connection((url.hostname, 443)) as sock, context.wrap_socket(
                sock, server_hostname=url.hostname
            ) as wrapped_socket:
                der_cert = wrapped_socket.getpeercert(True)
                return hashlib.sha256(
                    der_cert
                ).hexdigest() == self._charm_state.fingerprint.replace(":", "").replace(" ", "")
        return True

    @cached_property
    def _tree(self) -> "etree.ElementTree":  # type: ignore
        """Fetch metadata contents.

        Returns:
            The metadata as an XML tree.

        Raises:
            CharmConfigInvalidError: if the metadata URL can't be parsed.
        """
        # Lazy importing. Required deb packages won't be present on charm startup
        from lxml import etree  # nosec

        try:
            with urllib.request.urlopen(
                self._charm_state.metadata_url, timeout=10
            ) as resource:  # nosec
                raw_data = resource.read().decode("utf-8")
                tree = etree.fromstring(raw_data)  # nosec
                return tree
        except urllib.error.URLError as ex:
            raise CharmConfigInvalidError(
                f"Error while retrieving data from {self._charm_state.metadata_url}"
            ) from ex
        except etree.XMLSyntaxError as ex:
            raise CharmConfigInvalidError(
                f"Data from {self._charm_state.metadata_url} can't be parsed"
            ) from ex

    @cached_property
    def certificates(self) -> Set[str]:
        """Return public certificates defined in the metadata.

        Returns:
            List of certificates.
        """
        return {
            node.text
            for node in self._tree.xpath(
                (
                    f"//md:EntityDescriptor[@entityID='{self._charm_state.entity_id}']"
                    "//md:KeyDescriptor//ds:X509Certificate"
                ),
                namespaces=self._tree.nsmap,
            )
        }

    @cached_property
    def endpoints(self) -> List[SamlEndpoint]:
        """Return endpoints defined in the metadata.

        Returns:
            List of endpoints.
        """
        # Lazy importing. Required deb packages won't be present on charm startup
        from lxml import etree  # nosec

        results = self._tree.xpath(
            (
                f"//md:EntityDescriptor[@entityID='{self._charm_state.entity_id}']"
                f"//md:SingleSignOnService | "
                f"//md:EntityDescriptor[@entityID='{self._charm_state.entity_id}']"
                f"//md:SingleLogoutService"
            ),
            namespaces=self._tree.nsmap,
        )
        endpoints = []
        for result in results:
            endpoints.append(
                SamlEndpoint(
                    name=etree.QName(result).localname,
                    url=result.get("Location"),
                    binding=result.get("Binding"),
                    response_url=result.get("ResponseLocation"),
                )
            )
        return endpoints
