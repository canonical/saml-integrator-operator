#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator Charm service."""
import logging
import urllib
from lxml import etree
from ops import BlockedStatus, CharmBase, ConfigChangedEvent, RelationCreatedEvent, StoredState

logger = logging.getLogger(__name__)


class SAMLIntegratorOperatorCharm(CharmBase):
    """Charm for SAML Integrator on kubernetes."""

    _stored = StoredState()

    def __init__(self, *args):
        """Construct.

        Args:
            args: Arguments passed to the CharmBase parent constructor.
        """
        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on_saml_relation_created, self._on_saml_relation_created)

    def _on_config_changed(self, event: ConfigChangedEvent) -> None:
        """Handle changes in configuration.

        Args:
            event: Event triggering the configuration change handler.
        """
        raise Exception()
        logger.error("ENTRO")
        logger.error(event)
        if not event.metadata_url or not event.entity_id:
            self.unit.status = BlockedStatus(
                "Configuration fields metadata_url and entity_id must be provided."
            )
            return
        metadata_url = event.metadata_url

        try:
            with urllib.request.urlopen(metadata_url) as resource:  # nosec
                raw_data = resource.read().decode("utf-8")
                etree.fromstring(raw_data)
                entity_node = tree.xpath(f"//md:EntityDescriptor[@entityID='{entity_id}']", namespaces=tree.nsmap)[0]
                xpath_service = lambda node_name, binding: entity_node.xpath(f"//md:{node_name}[@Binding='{binding}']", namespaces=tree.nsmap)
                sso_service_redirect=xpath_service("SingleSignOnService", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect")[0]
                sso_service_redirect=xpath_service("SingleLogoutService", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect")[0]
                sso_service_post=xpath_service("SingleSignOnService", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post")[0]
                sso_service_post=xpath_service("SingleLogoutService", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post")[0]
                certificates=[node.text for node in entity_node.xpath('.//md:KeyDescriptor//ds:X509Certificate', namespaces=tree.nsmap)]

                


                logger.error(data)
        except urllib.URLError as ex:
            logger.error(ex)
            self.unit.status = BlockedStatus(
                "Invalid metadata_url option provided or service not available."
            )

    def _on_saml_relation_created(self, events: RelationCreatedEvent) -> None:
        """Handle the relation created event populating the relation data.

        Args:
            events: Event triggering the configuration handler.
        """
