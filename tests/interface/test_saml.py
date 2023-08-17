# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator Charm unit tests."""

from pathlib import Path
from unittest.mock import patch

from charms.operator_libs_linux.v0 import apt
from interface_tester.plugin import InterfaceTester

from charm import SamlIntegratorOperatorCharm


@patch("urllib.request.urlopen")
@patch.object(apt, "add_package")
def test_ingress_interface(_, urlopen_mock, interface_tester: InterfaceTester, helpers):
    """
    arrange: mock the metadata contents so that they are valid.
    act: run the interface tester.
    assert: nothing, the tester will take care of the rest.
    """
    interface_tester.configure(charm_type=SamlIntegratorOperatorCharm, interface_name="saml")
    metadata = Path("tests/unit/files/metadata_unsigned.xml").read_bytes()
    urlopen_result_mock = helpers.get_urlopen_result_mock(200, metadata)
    urlopen_mock.return_value = urlopen_result_mock

    interface_tester.run()
