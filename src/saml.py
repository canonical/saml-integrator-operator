# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Provide the SamlApp class to encapsulate the business logic."""
import logging
import urllib.request
from functools import cached_property
from typing import List, Set

from charms.saml_integrator.v0 import saml

from charm_state import CharmConfigInvalidError, CharmState

logger = logging.getLogger(__name__)


class SamlIntegrator:  # pylint: disable=import-outside-toplevel
    """A class representing the SAML Integrator application.

    Attrs:
        endpoints: SAML endpoints.
        certificates: Public certificates.
    """

    def __init__(self, charm_state: CharmState):
        """Initialize a new instance of the SamlApp class.

        Args:
            charm_state: The state of the charm that the Saml instance belongs to.
        """
        self._charm_state = charm_state

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
    def endpoints(self) -> List[saml.SamlEndpoint]:
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
                saml.SamlEndpoint(
                    name=etree.QName(result).localname,
                    url=result.get("Location"),
                    binding=result.get("Binding"),
                    response_url=result.get("ResponseLocation"),
                )
            )
        return endpoints
