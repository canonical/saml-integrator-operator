# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest
from interface_tester.plugin import InterfaceTester

from charm import SamlIntegratorOperatorCharm


@pytest.fixture
def interface_tester(interface_tester: InterfaceTester):
    interface_tester.configure(charm_type=SamlIntegratorOperatorCharm)
    yield interface_tester
