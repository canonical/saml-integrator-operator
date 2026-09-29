#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator charm integration tests."""

import jubilant


def test_active(juju: jubilant.Juju, app: str):
    """Check that the charm is active.

    Assume that the charm has already been built and is running.
    """
    juju.config(
        app,
        {
            "entity_id": "https://login.staging.ubuntu.com",
            "fingerprint": "",
            "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
        },
    )
    juju.wait(lambda status: jubilant.all_active(status, app))
    assert juju.status().apps[app].units[f"{app}/0"].is_active


def test_relation(juju: jubilant.Juju, app: str, any_charm: str):
    """Check that the charm is active once related to another charm.

    Assume that the charm has already been built and is running.
    """
    juju.integrate(f"{any_charm}:require-saml", f"{app}:saml")
    juju.config(
        app,
        {
            "entity_id": "https://login.staging.ubuntu.com",
            "fingerprint": "",
            "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
        },
    )
    juju.wait(lambda status: jubilant.all_active(status, app, any_charm))
    assert juju.status().apps[app].units[f"{app}/0"].is_active
