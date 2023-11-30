# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for charm-relation-interfaces tests."""

from unittest import mock

import ops
import pytest
from charms.saml_integrator.v0.saml import SamlEndpoint
from interface_tester.plugin import InterfaceTester
from scenario import State

import saml
from charm import SamlIntegratorOperatorCharm


# Interface tests are centrally hosted at https://github.com/canonical/charm-relation-interfaces.
# this fixture is used by the test runner of charm-relation-interfaces to test saml's compliance
# with the interface specifications.
# DO NOT MOVE OR RENAME THIS FIXTURE! If you need to, you'll need to open a PR on
# https://github.com/canonical/charm-relation-interfaces and change saml's test configuration
# to include the new identifier/location.
@pytest.fixture
def interface_tester(interface_tester: InterfaceTester, monkeypatch: pytest.MonkeyPatch):
    def _on_start_patched(self, _) -> None:
        """Patched start event handler."""
        self.unit.status = ops.ActiveStatus()

    monkeypatch.setattr(SamlIntegratorOperatorCharm, "_on_start", _on_start_patched)

    sso_endpoint = SamlEndpoint(
        name="SingleSignOnService",
        url="https://login.staging.ubuntu.com/saml/",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
    )
    with (
        mock.patch.object(saml.SamlIntegrator, "certificates", ["cert_content"]),
        mock.patch.object(saml.SamlIntegrator, "endpoints", [sso_endpoint]),
    ):
        interface_tester.configure(
            charm_type=SamlIntegratorOperatorCharm,
            state_template=State(
                leader=True,
                config={
                    "entity_id": "https://login.staging.ubuntu.com",
                    "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
                },
            ),
        )
        yield interface_tester
