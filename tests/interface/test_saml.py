# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
from interface_tester import InterfaceTester


# Interface tests are centrally hosted at https://github.com/canonical/charm-relation-interfaces.
# this fixture is used by the test runner of charm-relation-interfaces to test saml's compliance
# with the interface specifications.
# DO NOT MOVE OR RENAME THIS FIXTURE! If you need to, you'll need to open a PR on
# https://github.com/canonical/charm-relation-interfaces and change saml's test configuration
# to include the new identifier/location.
def test_saml_v0_interface(interface_tester: InterfaceTester):
    interface_tester.configure(
        interface_name="saml",
        interface_version=0,
    )
    interface_tester.run()
