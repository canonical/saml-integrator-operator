# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator Charm unit tests."""

# pylint: disable=protected-access
from pathlib import Path
from unittest.mock import patch

import ops
from ops.testing import Harness

from charm import SamlIntegratorOperatorCharm


def test_misconfigured_charm_reaches_blocked_status():
    """
    arrange: set up a charm.
    act: trigger a configuration change missing required configs.
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SamlIntegratorOperatorCharm)
    harness.begin()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_update_status():
    """
    arrange: set up a charm.
    act: trigger an update status with the required configs.
    assert: the charm executes _update_relations.
    """
    metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")
    harness = Harness(SamlIntegratorOperatorCharm)
    entity_id = "https://login.staging.ubuntu.com"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata": metadata,
        }
    )
    harness.begin()
    with patch("charm.SamlIntegratorOperatorCharm._update_relations") as update_relations_mock:
        harness.charm.on.update_status.emit()
        update_relations_mock.assert_called_once()


def test_charm_reaches_active_status():
    """
    arrange: set up a charm.
    act: trigger a configuration change with the required configs.
    assert: the charm reaches ActiveStatus.
    """
    metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")
    harness = Harness(SamlIntegratorOperatorCharm)
    entity_id = "https://login.staging.ubuntu.com"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata": metadata,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    assert harness.model.unit.status == ops.ActiveStatus()


def test_relation_joined_when_leader():
    """
    arrange: set up a configured charm and set leadership for the unit.
    act: add a relation.
    assert: the relation get populated with the SAML data.
    """
    metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")

    harness = Harness(SamlIntegratorOperatorCharm)
    harness.set_leader(True)
    entity_id = "https://login.staging.ubuntu.com"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata": metadata,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    assert harness.model.unit.status == ops.ActiveStatus()
    harness.add_relation("saml", "indico")
    data = harness.model.get_relation("saml").data[harness.model.app]
    assert data["entity_id"] == harness.charm._charm_state.entity_id
    assert data["x509certs"] == ",".join(harness.charm._saml_integrator.certificates)
    endpoints = harness.charm._saml_integrator.endpoints
    sl_re = [
        ep
        for ep in endpoints
        if ep.name == "SingleLogoutService"
        and ep.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    ]
    if sl_re:
        assert data["single_logout_service_redirect_url"] == sl_re[0].url
        assert data["single_logout_service_redirect_binding"] == sl_re[0].binding
        if sl_re[0].response_url:
            assert data["single_logout_service_redirect_response_url"] == sl_re[0].response_url
    sl_post = [
        ep
        for ep in endpoints
        if ep.name == "SingleLogoutService"
        and ep.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post"
    ]
    if sl_post:
        assert data["single_logout_service_post_url"] == sl_post[0].url
        assert data["single_logout_service_post_binding"] == sl_post[0].binding
        if sl_post[0].response_url:
            assert data["single_logout_service_post_response_url"] == sl_post[0].response_url
    sso_re = [
        ep
        for ep in endpoints
        if ep.name == "SingleSignOnService"
        and ep.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    ]
    if sso_re:
        assert data["single_sign_on_service_redirect_url"] == sso_re[0].url
        assert data["single_sign_on_service_redirect_binding"] == sso_re[0].binding
    sso_post = [
        ep
        for ep in endpoints
        if ep.name == "SingleSignOnService"
        and ep.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post"
    ]
    if sso_post:
        assert data["single_sign_on_service_post_url"] == sso_post[0].url
        assert data["single_sign_on_service_post_binding"] == sso_post[0].binding


def test_relation_joined_when_not_leader():
    """
    arrange: set up a charm and unset leadership for the unit.
    act: add a relation.
    assert: the relation get populated with the SAML data.
    """
    metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")

    harness = Harness(SamlIntegratorOperatorCharm)
    harness.set_leader(False)
    entity_id = "https://login.staging.ubuntu.com"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata": metadata,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    assert harness.model.unit.status == ops.ActiveStatus()
    harness.add_relation("saml", "indico")
    data = harness.model.get_relation("saml").data[harness.model.app]
    assert data == {}
