# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""CharmState unit tests."""

from unittest.mock import MagicMock

import pytest

from charm_state import CharmConfigInvalidError, CharmState


def test_charm_state_from_charm():
    """
    arrange: set up a configured charm
    act: access the status properties
    assert: the configuration is accessible from the state properties.
    """
    entity_id = "https://login.staging.ubuntu.com"
    metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
    charm = MagicMock(
        config={
            "entity_id": entity_id,
            "metadata_url": metadata_url,
        }
    )
    state = CharmState.from_charm(charm)
    assert state.entity_id == entity_id
    assert state.metadata_url == metadata_url


def test_charm_state_from_charm_with_invalid_config():
    """
    arrange: set up an unconfigured charm
    act: access the status properties
    assert: a CharmConfigInvalidError is raised.
    """
    charm = MagicMock(config={})
    with pytest.raises(CharmConfigInvalidError):
        CharmState.from_charm(charm)
