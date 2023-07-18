#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator Charm service."""
import logging
from typing import List

import ops
from charms.operator_libs_linux.v0 import apt
from charms.saml_integrator.v0 import saml
from ops.main import main

from charm_state import CharmConfigInvalidError, CharmState
from saml import SamlIntegrator

logger = logging.getLogger(__name__)

RELATION_NAME = "saml"


class SamlIntegratorOperatorCharm(ops.CharmBase):
    """Charm for SAML Integrator on kubernetes.

    Attrs:
        relations: List of charm relations.
    """

    def __init__(self, *args):
        """Construct.

        Args:
            args: Arguments passed to the CharmBase parent constructor.
        """
        super().__init__(*args)
        self._charm_state = None
        self._saml_integrator = None
        self.framework.observe(self.on[RELATION_NAME].relation_created, self._on_relation_created)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)

    def _on_upgrade_charm(self, _) -> None:
        """Install needed apt packages."""
        self.unit.status = ops.MaintenanceStatus("Installing packages")
        apt.update()
        apt.add_package(["libxml2"])

    def _on_relation_created(self, event: ops.RelationCreatedEvent) -> None:
        """Handle a change to the saml relation.

        Args:
            event: Event triggering the relation-created hook for the relation.
        """
        if not self.model.unit.is_leader():
            return
        self._update_relation_data(event.relation, self.get_saml_data())

    @property
    def relations(self) -> List[ops.Relation]:
        """The list of Relation instances associated with this relation_name."""
        return list(self.model.relations[RELATION_NAME])

    def _update_relation_data(
        self, relation: ops.Relation, saml_data: saml.SamlRelationData
    ) -> None:
        """Update the relation data.

        Args:
            relation: the relation for which to update the data.
            saml_data: the data.
        """
        relation.data[self.model.app].update(saml_data.to_relation_data())

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
            for relation in self.relations:
                self._update_relation_data(relation, self.get_saml_data())
        self.unit.status = ops.ActiveStatus()

    def get_saml_data(self) -> saml.SamlRelationData:
        """Get relation data.

        Returns:
            SamlRelationData containing the IdP details.
        """
        return saml.SamlRelationData(
            entity_id=self._charm_state.entity_id,
            metadata_url=self._charm_state.metadata_url,
            certificates=self._saml_integrator.certificates,
            endpoints=self._saml_integrator.endpoints,
        )


if __name__ == "__main__":  # pragma: nocover
    main(SamlIntegratorOperatorCharm)
