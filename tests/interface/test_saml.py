# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
from interface_tester import InterfaceTester


def test_saml_v0_interface(interface_tester: InterfaceTester):
    interface_tester.configure(
        repo="https://github.com/arturo-seijas/charm-relation-interfaces",
        branch="add-saml-interface-2",
        interface_name="saml",
        interface_version=0,
    )
    interface_tester.run()
