# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Provide the SamlApp class to encapsulate the business logic."""

import base64
import hashlib
import logging
import secrets
from functools import cached_property
from typing import Optional

import signxml
from charms.saml_integrator.v0 import saml

# Bandit classifies this import as vulnerable. For more details, see
# https://github.com/PyCQA/bandit/issues/767
from lxml import etree  # nosec

from charm_state import CharmConfigInvalidError, CharmState

logger = logging.getLogger(__name__)


class SamlIntegrator:  # pylint: disable=import-outside-toplevel
    """A class representing the SAML Integrator application.

    Attrs:
        endpoints: SAML endpoints.
        certificates: public certificates.
        signature: the Signature element in the metadata.
        signing_certificate: signing certificate.
        tree: the element tree for the metadata.
        nsmap: namespaces list.
    """

    def __init__(self, charm_state: CharmState):
        """Initialize a new instance of the SamlApp class.

        Args:
            charm_state: The state of the charm that the Saml instance belongs to.
        """
        self._charm_state = charm_state

    def _read_tree(self) -> "etree.ElementTree":
        """Fetch the metadata contents.

        Returns:
            The metadata as an XML tree.

        Raises:
            CharmConfigInvalidError: if the metadata URL can't be parsed.
        """
        try:
            return etree.fromstring(self._charm_state.metadata)  # nosec
        except etree.XMLSyntaxError as ex:
            raise CharmConfigInvalidError("Metadata can't be parsed") from ex

    @cached_property
    def tree(self) -> "etree.ElementTree":
        """Fetch and validate the metadata contents.

        Returns:
            The metadata as an XML tree.

        Raises:
            CharmConfigInvalidError: if the metadata URL or the metadata itself is invalid.
        """
        if self._charm_state.fingerprint and (
            not self.signing_certificate
            or not secrets.compare_digest(
                hashlib.sha256(base64.b64decode(self.signing_certificate)).hexdigest(),
                self._charm_state.fingerprint.replace(":", "").replace(" ", "").lower(),
            )
        ):
            raise CharmConfigInvalidError(
                "The metadata's signing certificate does not match the provided fingerprint"
            )
        tree = self._read_tree()
        if self.signing_certificate and self.signature:
            # The metadata can be tampered unless the metadata contents used are signed. To prevent
            # this, instead of arbitrarily validating the signature for all fragments that can be
            # shared with the requirer, the whole contents will need to be signed.
            try:
                signxml.XMLVerifier().verify(tree, x509_cert=self.signing_certificate)
            except signxml.exceptions.InvalidSignature as ex:
                raise CharmConfigInvalidError("The metadata has an invalid signature") from ex
        return tree

    @cached_property
    def nsmap(self) -> dict:
        """Get namespaces.

        Returns:
            The namespaces list without None.
        """
        return {
            "md": "urn:oasis:names:tc:SAML:2.0:metadata",
            "ds": "http://www.w3.org/2000/09/xmldsig#",
        }

    @cached_property
    def signing_certificate(self) -> str | None:
        """Return the signing certificate for the metadata, if any."""
        tree = self._read_tree()
        signing_certificates = tree.xpath(
            "//md:KeyDescriptor[@use='signing']//ds:X509Certificate/text()",
            namespaces=self.nsmap,
        )
        return next(iter(signing_certificates), None)

    @cached_property
    def signature(self) -> Optional["etree.ElementTree"]:
        """Check if the metadata has a Signature element."""
        tree = self._read_tree()
        signature = tree.xpath(
            "//ds:Signature",
            namespaces=self.nsmap,
        )
        return signature[0] if signature else None

    @cached_property
    def certificates(self) -> list[str]:
        """Return public certificates defined in the metadata.

        Returns:
            List of certificates.
        """
        tree = self.tree
        return sorted(
            tree.xpath(
                (
                    f"//md:EntityDescriptor[@entityID='{self._charm_state.entity_id}']"
                    "//md:KeyDescriptor//ds:X509Certificate/text()"
                ),
                namespaces=self.nsmap,
            )
        )

    @cached_property
    def endpoints(self) -> list[saml.SamlEndpoint]:
        """Return endpoints defined in the metadata.

        Returns:
            List of endpoints.
        """
        tree = self.tree
        results = tree.xpath(
            (
                f"//md:EntityDescriptor[@entityID='{self._charm_state.entity_id}']"
                f"//md:SingleSignOnService | "
                f"//md:EntityDescriptor[@entityID='{self._charm_state.entity_id}']"
                f"//md:SingleLogoutService"
            ),
            namespaces=self.nsmap,
        )
        endpoints = []
        for result in results:
            endpoints.append(
                saml.SamlEndpoint(
                    name=etree.QName(result).localname,
                    url=result.get("Location"),
                    binding=result.get("Binding"),
                    response_url=result.get("ResponseLocation"),
                )
            )
        return endpoints
