# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Provide the SamlApp class to encapsulate the business logic."""
import base64
import hashlib
import logging
import secrets
import urllib.request
from functools import cached_property
from typing import TYPE_CHECKING, Optional

from charms.saml_integrator.v0 import saml

from charm_state import CharmConfigInvalidError, CharmState

if TYPE_CHECKING:  # pragma: nocover
    # Bandit classifies this import as vulnerable. For more details, see
    # https://github.com/PyCQA/bandit/issues/767
    from lxml import etree  # nosec


logger = logging.getLogger(__name__)


class SamlIntegrator:  # pylint: disable=import-outside-toplevel
    """A class representing the SAML Integrator application.

    Attrs:
        endpoints: SAML endpoints.
        certificates: public certificates.
        signature: the Signature element in the metadata.
        signing_certificate: signing certificate.
        tree: the element tree for the metadata.
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
    def tree(self) -> "etree.ElementTree":
        """Fetch and validate the metadata contents.

        Returns:
            The metadata as an XML tree.

        Raises:
            CharmConfigInvalidError: if the metadata URL or the metadata itself is invalid.
        """
        # Lazy importing. Required deb packages won't be present on charm startup
        import signxml

        if self._charm_state.fingerprint and (
            not self.signing_certificate
            or not secrets.compare_digest(
                hashlib.sha256(base64.b64decode(self.signing_certificate)).hexdigest(),
                self._charm_state.fingerprint.replace(":", "").replace(" ", ""),
            )
        ):
            raise CharmConfigInvalidError("The metadata signature does not match the provided one")
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
    def signing_certificate(self) -> str | None:
        """Return the signing certificate for the metadata, if any."""
        tree = self._read_tree()
        signing_certificates = tree.xpath(
            "//md:KeyDescriptor[@use='signing']//ds:X509Certificate/text()",
            namespaces=tree.nsmap,
        )
        return next(iter(signing_certificates), None)

    @cached_property
    def signature(self) -> Optional["etree.ElementTree"]:
        """Check if the metadata has a Signature element."""
        tree = self._read_tree()
        signature = tree.xpath(
            "//ds:Signature",
            namespaces=tree.nsmap,
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
                namespaces=tree.nsmap,
            )
        )

    @cached_property
    def endpoints(self) -> list[saml.SamlEndpoint]:
        """Return endpoints defined in the metadata.

        Returns:
            List of endpoints.
        """
        # Lazy importing. Required deb packages won't be present on charm startup
        from lxml import etree  # nosec

        tree = self.tree
        results = tree.xpath(
            (
                f"//md:EntityDescriptor[@entityID='{self._charm_state.entity_id}']"
                f"//md:SingleSignOnService | "
                f"//md:EntityDescriptor[@entityID='{self._charm_state.entity_id}']"
                f"//md:SingleLogoutService"
            ),
            namespaces=tree.nsmap,
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
