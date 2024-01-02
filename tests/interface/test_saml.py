# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
from interface_tester import InterfaceTester


def test_saml_v0_interface(interface_tester: InterfaceTester):
    interface_tester.configure(
        interface_name="saml",
        interface_version=0,
    )
    interface_tester.run()
