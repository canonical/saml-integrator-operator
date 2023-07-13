#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator Charm service."""
import logging
import re
from typing import Dict

import ops
from charms.operator_libs_linux.v0 import apt
from ops.main import main

from charm_state import CharmConfigInvalidError, CharmState
from saml import SamlIntegrator

logger = logging.getLogger(__name__)


class SamlIntegratorOperatorCharm(ops.CharmBase):
    """Charm for SAML Integrator on kubernetes."""

    def __init__(self, *args):
        """Construct.

        Args:
            args: Arguments passed to the CharmBase parent constructor.
        """
        super().__init__(*args)
        self._charm_state = None
        self._saml_integrator = None
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
        self.framework.observe(self.on.saml_relation_created, self._on_saml_relation_created)

    def _on_upgrade_charm(self, _) -> None:
        """Install needed apt packages."""
        self.unit.status = ops.MaintenanceStatus("Installing packages")
        apt.update()
        apt.add_package(["libxml2"])

    def _on_config_changed(self, _) -> None:
        """Handle changes in configuration."""
        self.unit.status = ops.MaintenanceStatus("Configuring charm")
        try:
            self._charm_state = CharmState.from_charm(charm=self)
            self._saml_integrator = SamlIntegrator(charm_state=self._charm_state)
        except CharmConfigInvalidError as exc:
            self.model.unit.status = ops.BlockedStatus(exc.msg)
            return
        if self.model.unit.is_leader():
            for relation in self.model.relations["saml"]:
                relation.data[self.model.app].update(self.dump_saml_data())
        self.unit.status = ops.ActiveStatus()

    def dump_saml_data(self) -> Dict[str, str]:
        """Dump the charm state in the format expected by the relation.

        Returns:
            Dict containing the IdP details.
        """
        result = {
            "entity_id": self._saml_integrator.entity_id,
            "metadata_url": self._saml_integrator.metadata_url,
            "x509certs": ",".join(self._saml_integrator.certificates),
        }
        for endpoint in self._saml_integrator.endpoints:
            http_method = endpoint.binding.split(":")[-1].split("-")[-1].lower()
            lowercase_name = re.sub(r"(?<!^)(?=[A-Z])", "_", endpoint.name).lower()
            prefix = f"{lowercase_name}_{http_method}_"
            result[f"{prefix}url"] = endpoint.url
            result[f"{prefix}binding"] = endpoint.binding
            if endpoint.response_url:
                result[f"{prefix}response_url"] = endpoint.response_url
        return result

    def _on_saml_relation_created(self, event: ops.RelationCreatedEvent):
        """Handle a change to the saml relation.

        Populate the event data.

        Args:
            event: Event triggering the relation-created hook for the relation.
        """
        if not self.model.unit.is_leader():
            return
        event.relation.data[self.model.app].update(self.dump_saml_data())


if __name__ == "__main__":  # pragma: nocover
    main(SamlIntegratorOperatorCharm)
