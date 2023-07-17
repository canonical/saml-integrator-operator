#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator Charm service."""
import logging
import re
from typing import Dict

import ops
from charms.operator_libs_linux.v0 import apt
from charms.saml_integrator.v0 import saml
from ops.main import main

from charm_state import CharmConfigInvalidError, CharmState
from saml import SamlIntegrator

logger = logging.getLogger(__name__)

RELATION_NAME = "saml"


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
        self._saml_provides = saml.SamlProvides(self, relation_name=RELATION_NAME)
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
            for relation in self._saml_provides.relations:
                self._saml_provides._update_relation_data(relation, self.get_saml_data())
        self.unit.status = ops.ActiveStatus()

    def get_saml_data(self) -> saml.SamlRelationData:
        """Get relation data.

        Returns:
            SamlRelationData containing the IdP details.
        """
        return SamlRelationData(
            self.charm._charm_state.entity_id,
            self.charm._charm_state.metadata_url,
            self.charm._saml_integrator.certificates,
            self.charm._saml_integrator.endpoints,
        )


if __name__ == "__main__":  # pragma: nocover
    main(SamlIntegratorOperatorCharm)
