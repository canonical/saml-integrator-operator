# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator Charm unit tests."""
# pylint: disable=protected-access
from pathlib import Path
from unittest.mock import patch

import ops
from charms.operator_libs_linux.v0 import apt
from ops.testing import Harness

from charm import SamlIntegratorOperatorCharm


@patch.object(apt, "add_package")
def test_libs_installed(apt_add_package_mock):
    """
    arrange: set up a charm.
    act: trigger the install event.
    assert: the charm installs required packages.
    """
    harness = Harness(SamlIntegratorOperatorCharm)
    entity_id = "https://login.staging.ubuntu.com"
    metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
        }
    )
    harness.begin()
    # First confirm no packages have been installed.
    apt_add_package_mock.assert_not_called()
    harness.charm.on.install.emit()
    # And now confirm we've installed the required packages.
    apt_add_package_mock.assert_called_once_with(
        ["libssl-dev", "libxml2", "libxslt1-dev"], update_cache=True
    )


def test_misconfigured_charm_reaches_blocked_status():
    """
    arrange: set up a charm.
    act: trigger a configuration change missing required configs.
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SamlIntegratorOperatorCharm)
    harness.begin()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


@patch.object(apt, "add_package")
def test_config_changed_try_except(apt_add_package_mock):
    """
    arrange: set up a charm.
    act: trigger a config-changed that triggers an ImportError.
    assert: the charm executes _update_relations after installing packages.
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
        # When we call update_relations initially, trigger an ImportError so
        # we attempt to install the packages.
        update_relations_mock.side_effect = [ImportError("Packages not installed"), None]
        harness.charm.on.config_changed.emit()
        # And confirm we've installed the required packages as well.
        apt_add_package_mock.assert_called_once_with(
            ["libssl-dev", "libxml2", "libxslt1-dev"], update_cache=True
        )
        # We've called update_relations twice, once triggering the ImportError
        # and once after installing the packages it requires.
        assert update_relations_mock.call_count == 2


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
