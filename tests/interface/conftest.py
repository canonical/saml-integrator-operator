# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for charm-relation-interfaces tests."""

import pytest
from interface_tester.plugin import InterfaceTester

from charm import SamlIntegratorOperatorCharm


# Interface tests are centrally hosted at https://github.com/canonical/charm-relation-interfaces.
# this fixture is used by the test runner of charm-relation-interfaces to test saml's compliance
# with the interface specifications.
# DO NOT MOVE OR RENAME THIS FIXTURE! If you need to, you'll need to open a PR on
# https://github.com/canonical/charm-relation-interfaces and change saml's test configuration
# to include the new identifier/location.
@pytest.fixture
def interface_tester(interface_tester: InterfaceTester):
    interface_tester.configure(charm_type=SamlIntegratorOperatorCharm)
    yield interface_tester
