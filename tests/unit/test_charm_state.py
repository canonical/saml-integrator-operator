# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""CharmState unit tests."""

import os

import yaml
from mock import patch
from ops.testing import Harness

from charm import SamlIntegratorOperatorCharm
from charm_state import KNOWN_CHARM_CONFIG, CharmConfigInvalidError, CharmState, ProxyConfig

PROXY_SETTINGS = {
    "JUJU_CHARM_HTTP_PROXY": "http://proxy.example:3128",
    "JUJU_CHARM_HTTPS_PROXY": "https://proxy.example:3128",
    "JUJU_CHARM_NO_PROXY": "localhost",
}

PROXY_SETTINGS_INVALID = {
    "JUJU_CHARM_NO_PROXY": "localhost",
}


@patch.dict(os.environ, PROXY_SETTINGS)
def test_proxy_config():
    """
    arrange: set JUJU_CHARM proxy env variables.
    act: instantiate the proxy configuration.
    assert: the proxy configuration is loaded correctly.
    """
    proxy_config = ProxyConfig.from_charm_env()
    assert proxy_config.http_proxy == PROXY_SETTINGS["JUJU_CHARM_HTTP_PROXY"]
    assert proxy_config.https_proxy == PROXY_SETTINGS["JUJU_CHARM_HTTPS_PROXY"]
    assert proxy_config.no_proxy == PROXY_SETTINGS["JUJU_CHARM_NO_PROXY"]


@patch.dict(os.environ, PROXY_SETTINGS_INVALID)
def test_proxy_config_invalid():
    """
    arrange: set JUJU_CHARM no proxy env variable.
    act: instantiate the proxy configuration.
    assert: the proxy configuration is none.
    """
    proxy_config = ProxyConfig.from_charm_env()
    assert proxy_config is None


def test_known_charm_config():
    """
    arrange: none
    act: none
    assert: KNOWN_CHARM_CONFIG in the consts module matches the content of config.yaml file.
    """
    with open("config.yaml", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    assert sorted(config["options"].keys()) == sorted(KNOWN_CHARM_CONFIG)


def test_charm_state_from_charm():
    """
    arrange: set up an configured charm
    act: access the status properties
    assert: the configuration is accessible from the state properties.
    """
    harness = Harness(SamlIntegratorOperatorCharm)
    harness.begin()
    harness.disable_hooks()
    entity_id = "https://login.staging.ubuntu.com"
    metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
        }
    )
    state = CharmState.from_charm(harness.charm)
    assert state.entity_id == entity_id
    assert state.metadata_url == metadata_url


def test_charm_state_from_charm_with_invalid_config():
    """
    arrange: set up an unconfigured charm
    act: access the status properties
    assert: a CharmConfigInvalidError is raised.
    """
    harness = Harness(SamlIntegratorOperatorCharm)
    harness.begin()
    try:
        CharmState.from_charm(harness.charm)
        assert False
    except CharmConfigInvalidError:
        assert True
