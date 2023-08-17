# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Test fixtures."""

import pytest
from interface_tester.plugin import InterfaceTester

from charm import SamlIntegratorOperatorCharm


@pytest.fixture(name="interface_tester")
def interface_tester_instance(interface_tester: InterfaceTester):
    """Interface tester fixture.

    Args:
        interface_tester: Interface tester.
    """
    interface_tester.configure(charm_type=SamlIntegratorOperatorCharm)
    yield interface_tester
