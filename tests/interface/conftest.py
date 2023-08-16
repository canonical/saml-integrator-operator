# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Test fixtures."""

import pytest
from interface_tester.plugin import InterfaceTester

from charm import SamlIntegratorOperatorCharm


@pytest.fixture
def interface_tester(interface_tester_instance: InterfaceTester):
    """Interface tester fixture.

    Args:
        interface_tester_instance: Interface tester.
    """
    interface_tester_instance.configure(charm_type=SamlIntegratorOperatorCharm)
    yield interface_tester_instance
