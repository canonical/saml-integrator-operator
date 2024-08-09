# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""CharmState unit tests."""
import urllib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from charm_state import CharmConfigInvalidError, CharmState


@patch("urllib.request.urlopen")
def test_charm_state_from_charm_with_metadata_url(urlopen_mock):
    """
    arrange: set up a configured charm
    act: access the status properties
    assert: the configuration is accessible from the state properties.
    """
    metadata = Path("tests/unit/files/metadata_unsigned.xml").read_bytes()
    urlopen_result_mock = MagicMock()
    urlopen_result_mock.getcode.return_value = 200
    urlopen_result_mock.read.return_value = metadata
    urlopen_result_mock.__enter__.return_value = urlopen_result_mock
    urlopen_mock.return_value = urlopen_result_mock

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
    assert state.metadata == metadata


def test_charm_state_from_charm_with_metadata():
    """
    arrange: set up a configured charm
    act: access the status properties
    assert: the configuration is accessible from the state properties.
    """
    metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")

    entity_id = "https://login.staging.ubuntu.com"
    charm = MagicMock(
        config={
            "entity_id": entity_id,
            "metadata": metadata,
        }
    )
    state = CharmState.from_charm(charm)
    assert state.entity_id == entity_id
    assert state.metadata_url is None
    assert state.metadata == metadata


def test_charm_state_from_charm_with_invalid_config():
    """
    arrange: set up an unconfigured charm
    act: access the status properties
    assert: a CharmConfigInvalidError is raised.
    """
    entity_id = "https://login.staging.ubuntu.com"
    charm = MagicMock(config={"entity_id": entity_id})
    with pytest.raises(CharmConfigInvalidError):
        CharmState.from_charm(charm)


@patch.object(urllib.request, "urlopen", side_effect=urllib.error.URLError("Error"))
def test_charm_state_from_charm_with_metadata_url_invalid(_):
    """
    arrange: set up a configured charm with a metadata_url returning a 404
    act: access the status properties
    assert: a CharmConfigInvalidError is raised.
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
    with pytest.raises(CharmConfigInvalidError):
        state.metadata  # pylint: disable=pointless-statement
