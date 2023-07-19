# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator Charm unit tests."""
import ops
import pytest
from mock import MagicMock, patch
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
    entity_id = "https://login.staging.ubuntu.com"
    harness.update_config({"entity_id": entity_id})
    harness.model.unit.status == ops.BlockedStatus()


@patch("urllib.request.urlopen")
def test_charm_reaches_active_status(mock_urlopen):
    """
    arrange: set up a charm and mock HTTP requests.
    act: trigger a configuration change with the required configs.
    assert: the charm reaches ActiveStatus.
    """
    with open("tests/unit/files/metadata_1.xml", "rb") as metadata:
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = metadata.read()
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        harness = Harness(SamlIntegratorOperatorCharm)
        harness.begin()
        entity_id = "https://login.staging.ubuntu.com"
        metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
        harness.update_config(
            {
                "entity_id": entity_id,
                "metadata_url": metadata_url,
            }
        )
        harness.model.unit.status == ops.ActiveStatus()


@patch("urllib.request.urlopen")
@pytest.mark.parametrize("metadata_file", [("metadata_1.xml"), ("metadata_2.xml")])
def test_relation_joined_when_leader(mock_urlopen, metadata_file):
    """
    arrange: set up a configured charm and set leadership for the unit.
    act: add a relation.
    assert: the relation get populated with the SAML data.
    """
    with open(f"tests/unit/files/{metadata_file}", "rb") as metadata:
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = metadata.read()
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        harness = Harness(SamlIntegratorOperatorCharm)
        harness.begin()
        harness.set_leader(True)
        entity_id = "https://login.staging.ubuntu.com"
        metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
        harness.update_config(
            {
                "entity_id": entity_id,
                "metadata_url": metadata_url,
            }
        )
        harness.add_relation("saml", "indico")
        data = harness.model.get_relation("saml").data[harness.model.app]
        assert data["entity_id"] == harness.charm._saml_integrator.entity_id
        assert data["metadata_url"] == harness.charm._saml_integrator.metadata_url
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


@patch("urllib.request.urlopen")
def test_relation_joined_when_not_leader(mock_urlopen):
    """
    arrange: set up a charm and unset leadership for the unit.
    act: add a relation.
    assert: the relation get populated with the SAML data.
    """
    with open("tests/unit/files/metadata_1.xml", "rb") as metadata:
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = metadata.read()
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        harness = Harness(SamlIntegratorOperatorCharm)
        harness.begin()
        harness.set_leader(False)
        entity_id = "https://login.staging.ubuntu.com"
        metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
        harness.update_config(
            {
                "entity_id": entity_id,
                "metadata_url": metadata_url,
            }
        )
        harness.add_relation("saml", "indico")
        data = harness.model.get_relation("saml").data[harness.model.app]
        assert data == {}


@patch("urllib.request.urlopen")
def test_charm_propagates_config_change(mock_urlopen):
    """
    arrange: set up a charm and mock HTTP requests.
    act: trigger a configuration change with the required configs.
    assert: the charm reaches ActiveStatus.
    """
    with open("tests/unit/files/metadata_1.xml", "rb") as metadata:
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = metadata.read()
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        harness = Harness(SamlIntegratorOperatorCharm)
        harness.begin()
        harness.set_leader(True)
        entity_id = "https://login.staging.ubuntu.com"
        metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
        harness.update_config(
            {
                "entity_id": entity_id,
                "metadata_url": metadata_url,
            }
        )
        harness.model.unit.status == ops.ActiveStatus()
        harness.add_relation("saml", "indico")
        data = harness.model.get_relation("saml").data[harness.model.app]
        assert data["entity_id"] == entity_id
        new_entity_id = "https://login2.staging.ubuntu.com"
        harness.update_config(
            {
                "entity_id": new_entity_id,
                "metadata_url": metadata_url,
            }
        )
        data = harness.model.get_relation("saml").data[harness.model.app]
        assert data["entity_id"] == new_entity_id
