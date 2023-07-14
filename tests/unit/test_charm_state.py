# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""CharmState unit tests."""

import pytest
import yaml
from ops.testing import Harness

from charm import SamlIntegratorOperatorCharm
from charm_state import KNOWN_CHARM_CONFIG, CharmConfigInvalidError, CharmState


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
    with pytest.raises(CharmConfigInvalidError):
        CharmState.from_charm(harness.charm)
