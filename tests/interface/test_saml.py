# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
import pytest
from interface_tester import InterfaceTester


# https://github.com/canonical/pytest-interface-tester/issues/27
@pytest.mark.skip
def test_saml_v0_interface(interface_tester: InterfaceTester):
    interface_tester.configure(
        interface_name="saml",
        interface_version=0,
    )
    interface_tester.run()
