# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the SAML Integrator charm integration tests."""

import json
from pathlib import Path

import jubilant
import yaml
from opcli.pytest_plugin import CharmPathList
from pytest import FixtureRequest, fixture

JUJU_WAIT_TIMEOUT = 10 * 60


@fixture(scope="module", name="app_name")
def app_name_fixture():
    """Provide app name from the metadata."""
    metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
    yield metadata["name"]


@fixture(scope="session")
def charm(charm_paths: dict[str, CharmPathList]) -> str:
    """Provide the packed charm path."""
    return charm_paths["saml-integrator"].path


@fixture(scope="module")
def juju(request: FixtureRequest):
    """Create a temporary model for integration tests."""
    model = request.config.getoption("--model")
    if model:
        juju = jubilant.Juju(model=model)
        juju.wait_timeout = JUJU_WAIT_TIMEOUT
        yield juju
        return

    keep_models = request.config.getoption("--keep-models")
    with jubilant.temp_model(keep=keep_models) as juju:
        juju.wait_timeout = JUJU_WAIT_TIMEOUT
        yield juju


@fixture(scope="module")
def app(juju: jubilant.Juju, charm: str, app_name: str):
    """SAML Integrator charm used for integration testing.

    Build the charm and deploy it along with Anycharm.
    """
    juju.deploy(
        charm=charm,
        app=app_name,
    )
    yield app_name


@fixture(scope="module")
def any_charm(juju: jubilant.Juju):
    """SAML Integrator charm used for integration testing.

    Build the charm and deploy it along with Anycharm.
    """
    path_lib = "lib/charms/saml_integrator/v0/saml.py"
    saml_lib = Path(path_lib).read_text(encoding="utf8")
    any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
    src_overwrite = {
        "saml.py": saml_lib,
        "any_charm.py": any_charm_script,
    }
    app_name = "any"
    juju.deploy(
        "any-charm",
        app=app_name,
        channel="beta",
        config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
    )
    yield app_name
