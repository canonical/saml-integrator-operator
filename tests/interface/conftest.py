# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for charm-relation-interfaces tests."""

import pytest
from unittest import mock
from interface_tester.plugin import InterfaceTester

import ops
from charm import SamlIntegratorOperatorCharm
from saml import SamlIntegrator


# Interface tests are centrally hosted at https://github.com/canonical/charm-relation-interfaces.
# this fixture is used by the test runner of charm-relation-interfaces to test saml's compliance
# with the interface specifications.
# DO NOT MOVE OR RENAME THIS FIXTURE! If you need to, you'll need to open a PR on
# https://github.com/canonical/charm-relation-interfaces and change saml's test configuration
# to include the new identifier/location.
@pytest.fixture
def interface_tester(interface_tester: InterfaceTester, monkeypatch: pytest.MonkeyPatch):

    saml_integrator = mock.MagicMock(spec=SamlIntegrator)
    saml_integrator.certificates = []
    saml_integrator.endpoints = []
    monkeypatch.setattr(SamlIntegrator, "__init__", saml_integrator)
    def _on_start_patched(self, _) -> None:
        self.unit.status = ops.ActiveStatus()
    monkeypatch.setattr(SamlIntegratorOperatorCharm, "_on_start", _on_start_patched)
    interface_tester.configure(charm_type=SamlIntegratorOperatorCharm)
    yield interface_tester
