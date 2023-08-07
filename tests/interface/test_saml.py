# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator Charm unit tests."""

from charms.operator_libs_linux.v0 import apt
from interface_tester.plugin import InterfaceTester
from mock import MagicMock, patch

from charm import SamlIntegratorOperatorCharm


@patch("urllib.request.urlopen")
@patch.object(apt, "add_package")
def test_ingress_interface(_, urlopen_mock, interface_tester: InterfaceTester):
    """Run interface tests.

    Args:
        _: apt mock.
        urlopen_mock: requests.urlopen mock.
        interface_tester: interface tester.
    """
    interface_tester.configure(charm_type=SamlIntegratorOperatorCharm, interface_name="saml")
    with open("tests/unit/files/metadata_1.xml", "rb") as metadata:
        urlopen_result_mock = MagicMock()
        urlopen_result_mock.getcode.return_value = 200
        urlopen_result_mock.read.return_value = metadata.read()
        urlopen_result_mock.__enter__.return_value = urlopen_result_mock
        urlopen_mock.return_value = urlopen_result_mock

        interface_tester.run()
