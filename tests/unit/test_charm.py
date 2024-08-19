# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator Charm unit tests."""
# pylint: disable=protected-access
from pathlib import Path
from unittest.mock import patch

import ops
import yaml
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
        assert update_relations_mock.called_once()


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


@patch("urllib.request.urlopen")
def test_relation_refresh_on_update_status(urlopen_mock):
    """
    arrange: set up a configured charm and set leadership for the unit.
    act: add a relation.
    assert: the relation get populated with the SAML data.
    """
    metadata = Path("tests/unit/files/metadata_unsigned.xml").read_bytes()
    urlopen_result_mock = MagicMock()
    urlopen_result_mock.getcode.return_value = 200
    urlopen_result_mock.read.return_value = metadata
    urlopen_result_mock.__enter__.return_value = urlopen_result_mock
    urlopen_mock.return_value = urlopen_result_mock

    harness = Harness(SamlIntegratorOperatorCharm)
    harness.set_leader(True)
    entity_id = "https://login.staging.ubuntu.com"
    metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
        }
    )
    harness.begin()
    harness.charm.on.update_status.emit()
    harness.add_relation("saml", "indico")
    data = harness.model.get_relation("saml").data[harness.model.app]
    assert data["entity_id"] == harness.charm._charm_state.entity_id


def test_charmcraft_dependency_in_sync():
    """
    arrange: none.
    act: none.
    assert: the charm-binary-python-packages of charmcraft.yaml charm part is in sync with the
        requirements-binary.txt file.
    """
    root = Path(__file__).parent.parent.parent
    charmcraft_yaml = yaml.safe_load((root / "charmcraft.yaml").read_text())
    requirements = set((root / "requirements-binary.txt").read_text().splitlines())
    assert set(charmcraft_yaml["parts"]["charm"]["charm-binary-python-packages"]) == requirements
