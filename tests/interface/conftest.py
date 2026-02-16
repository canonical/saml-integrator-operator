# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for charm-relation-interfaces tests."""

from typing import Dict
from unittest import mock

import pytest
from charms.saml_integrator.v0.saml import SamlEndpoint, SamlRelationData
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
    sso_redirect_endpoint = SamlEndpoint(
        name="SingleSignOnService",
        url="https://login.staging.ubuntu.com/saml/",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
    )
    sso_post_endpoint = SamlEndpoint(
        name="SingleSignOnService",
        url="https://login.staging.ubuntu.com/saml/",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
    )
    slo_redirect_endpoint = SamlEndpoint(
        name="SingleLogoutService",
        url="https://login.staging.ubuntu.com/saml/logout",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        response_url="https://login.staging.ubuntu.com/saml/logout/response",
    )
    slo_post_endpoint = SamlEndpoint(
        name="SingleLogoutService",
        url="https://login.staging.ubuntu.com/saml/logout",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        response_url="https://login.staging.ubuntu.com/saml/logout/response",
    )

    # Store the original method
    original_to_relation_data = SamlRelationData.to_relation_data

    # Create a wrapper that adds the missing single_logout_service_url field
    # This is a workaround for a mismatch between the library naming convention
    # and the interface schema expectations
    def patched_to_relation_data(self) -> Dict[str, str]:
        result = original_to_relation_data(self)
        # Add single_logout_service_url if we have logout endpoints
        # The schema expects this field but the library generates method-specific URLs
        if "single_logout_service_redirect_url" in result:
            result["single_logout_service_url"] = result["single_logout_service_redirect_url"]
        return result
    
    with (
        mock.patch.object(saml.SamlIntegrator, "certificates", ["cert_content"]),
        mock.patch.object(
            saml.SamlIntegrator,
            "endpoints",
            [sso_redirect_endpoint, sso_post_endpoint, slo_redirect_endpoint, slo_post_endpoint],
        ),
        mock.patch.object(SamlRelationData, "to_relation_data", patched_to_relation_data),
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
