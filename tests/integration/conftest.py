# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the SAML Integrator charm integration tests."""

import ops
import pytest_asyncio
import yaml
from pathlib import Path
from pytest import fixture
from pytest_operator.plugin import OpsTest


@fixture(scope="module", name="metadata")
def metadata_fixture():
    """Provide charm metadata."""
    yield yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))


@fixture(scope="module", name="app_name")
def app_name_fixture(metadata):
    """Provide app name from the metadata."""
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
    await ops_test.model.wait_for_idle(status=ops.BlockedStatus.name, raise_on_error=False)
    yield application
