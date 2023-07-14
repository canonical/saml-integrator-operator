# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the SAML Integrator charm integration tests."""

from pathlib import Path

import pytest_asyncio
import yaml
from pytest import fixture
from pytest_operator.plugin import OpsTest


@fixture(scope="module", name="app_name")
def app_name_fixture():
    """Provide app name from the metadata."""
    metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
    yield metadata["name"]


@pytest_asyncio.fixture(scope="module")
async def app(ops_test: OpsTest, app_name: str):
    """SAML Integrator charm used for integration testing.

    Build the charm and deploys it.
    """
    assert ops_test.model
    charm = await ops_test.build_charm(".")
    application = await ops_test.model.deploy(
        charm,
        application_name=app_name,
        series="focal",
    )
    yield application
