# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator unit tests."""
import socket
import ssl
import urllib

import pytest
from mock import MagicMock, patch
from ops.testing import Harness

from charm import SamlIntegratorOperatorCharm
from charm_state import CharmConfigInvalidError, CharmState
from saml import SamlIntegrator


@patch("urllib.request.urlopen")
def test_saml_with_invalid_metadata(urlopen_mock):
    """
    arrange: mock the metadata contents so that they are invalid.
    act: access the metadata properties.
    assert: a CharmConfigInvalidError exception is raised when attempting to access the
        properties read from the metadata.
    """
    cm = MagicMock()
    cm.getcode.return_value = 200
    cm.read.return_value = b"invalid"
    cm.__enter__.return_value = cm
    urlopen_mock.return_value = cm

    harness = Harness(SamlIntegratorOperatorCharm)
    harness.begin()
    harness.disable_hooks()
    entity_id = "https://login.staging.ubuntu.com"
    metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
        }
    )
    charm_state = CharmState.from_charm(harness.charm)
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    assert saml_integrator.entity_id == entity_id
    assert saml_integrator.metadata_url == metadata_url
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.certificates
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.endpoints


@patch.object(urllib.request, "urlopen", side_effect=urllib.error.URLError("Error"))
def test_saml_with_invalid_url(urlopen_mock):
    """
    arrange: mock the HTTP request for the metadata so that it fails.
    act: access the metadata properties.
    assert: a CharmConfigInvalidError exception is raised when attempting to access the
        properties read from the metadata.
    """
    harness = Harness(SamlIntegratorOperatorCharm)
    harness.begin()
    harness.disable_hooks()
    entity_id = "https://login.staging.ubuntu.com"
    metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
        }
    )
    charm_state = CharmState.from_charm(harness.charm)
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    assert saml_integrator.entity_id == entity_id
    assert saml_integrator.metadata_url == metadata_url
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.certificates
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.endpoints


@patch("urllib.request.urlopen")
@pytest.mark.parametrize(
    "metadata_file,binding",
    [
        ("metadata_1.xml", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"),
        ("metadata_2.xml", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post"),
    ],
)
def test_saml_with_valid_metadata(urlopen_mock, metadata_file, binding):
    """
    arrange: mock the metadata contents so that they invalid.
    act: access the metadata properties.
    assert: the properties are populated as defined in the metadata.
    """
    with open(f"tests/unit/files/{metadata_file}", "rb") as metadata:
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = metadata.read()
        cm.__enter__.return_value = cm
        urlopen_mock.return_value = cm

        harness = Harness(SamlIntegratorOperatorCharm)
        harness.begin()
        harness.disable_hooks()
        entity_id = "https://login.staging.ubuntu.com"
        metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
        harness.update_config(
            {
                "entity_id": entity_id,
                "metadata_url": metadata_url,
            }
        )
        charm_state = CharmState.from_charm(harness.charm)
        saml_integrator = SamlIntegrator(charm_state=charm_state)
        assert saml_integrator.entity_id == entity_id
        assert saml_integrator.metadata_url == metadata_url
        assert saml_integrator.certificates == {
            (
                "MIIDuzCCAqOgAwIBAgIJALRwYFkmH3k9MA0GCSqGSIb3DQEBCwUAMHQxCzAJBgNVBAYTAkdCMRMwEQYD"
                "VQQIDApTb21lLVN0YXRlMSswKQYDVQQKDCJTU08gU3RhZ2luZyBrZXkgZm9yIEV4cGVuc2lmeSBTQU1M"
                "MSMwIQYDVQQDDBpTU08gU3RhZ2luZyBFeHBlbnNpZnkgU0FNTDAeFw0xNTA5MjUxMDUzNTZaFw0xNjA5"
                "MjQxMDUzNTZaMHQxCzAJBgNVBAYTAkdCMRMwEQYDVQQIDApTb21lLVN0YXRlMSswKQYDVQQKDCJTU08g"
                "U3RhZ2luZyBrZXkgZm9yIEV4cGVuc2lmeSBTQU1MMSMwIQYDVQQDDBpTU08gU3RhZ2luZyBFeHBlbnNp"
                "ZnkgU0FNTDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANyt2LqrD3DSmJMtNUA5xjJpbUNu"
                "iaHFdO0AduOegfM7YnKIp0Y001S07ffEcv/zNo7Gg6wAZwLtW2/+eUkRj8PLEyYDyU2NiwD7stAzhz50"
                "AjTbLojRyZdrEo6xu+f43xFNqf78Ix8mEKFr0ZRVVkkNRifa4niXPDdzIUiv5UZUGjW0ybFKdM3zm6xj"
                "EwMwo8ixu/IbAn74PqC7nypllCvLjKLFeYmYN24oYaVKWIRhQuGL3m98eQWFiVUL40palHtgcy5tffg8"
                "UOyAOqg5OF2kGVeyPZNmjq/jVHYyBUtBaMvrTLUlOKRRC3I+aW9tXs7aqclQytOiFQxq+aEapB8CAwEA"
                "AaNQME4wHQYDVR0OBBYEFA9Ub7RIfw21Qgbnf4IA3n4jUpAlMB8GA1UdIwQYMBaAFA9Ub7RIfw21Qgbn"
                "f4IA3n4jUpAlMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAGBHECvs8V3xBKGRvNfBaTbY"
                "2FpbwLheSm3MUM4/hswvje24oknoHMF3dFNVnosOLXYdaRf8s0rsJfYuoUTap9tKzv0osGoA3mMw18LY"
                "W3a+mUHurx+kJZP+VN3emk84TXiX44CCendMVMxHxDQwg40YxALNc4uew2hlLReB8nC+55OlsIInIqPc"
                "IvtqUZgeNp2iecKnCgZPDaElez52GY5GRFszJd04sAQIrpg2+xfZvLMtvWwb9rpdto5oIdat2gIoMLdr"
                "mJUAYWP2+BLiKVpe9RtzfvqtQrk1lDoTj3adJYutNIPbTGOfI/Vux0HCw9KCrNTspdsfGTIQFJJi01E="
            )
        }
        endpoints = saml_integrator.endpoints
        assert len(endpoints) == 2
        assert endpoints[0].name == "SingleLogoutService"
        assert endpoints[0].binding == binding
        assert endpoints[0].url == "https://login.staging.ubuntu.com/+logout"
        assert endpoints[0].response_url == "https://login.staging.ubuntu.com/example/"
        assert endpoints[1].name == "SingleSignOnService"
        assert endpoints[1].binding == binding
        assert endpoints[1].url == "https://login.staging.ubuntu.com/saml/"
        assert endpoints[1].response_url is None


@patch.object(socket, "create_connection", return_value=MagicMock())
@patch.object(ssl, "create_default_context", return_value=MagicMock())
def test_saml_with_invalid_certificate(context_mock, connection_mock):
    """
    arrange: mock certificate retrieved from the metadata URL.
    act: validate the certificate.
    assert: the certificate is invalid and an exception is raised.
    """
    wrap_socket = context_mock.return_value.wrap_socket
    wrap_socket.return_value.__enter__.return_value.getpeercert.return_value = b"someinvalidcert"

    harness = Harness(SamlIntegratorOperatorCharm)
    harness.begin()
    harness.disable_hooks()
    entity_id = "https://login.staging.ubuntu.com"
    metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
            "fingerprint": "98b228f28eab0b2eb5d03389fb6f8f9733dadcf0c17007fcde4148a4de41db54",
        }
    )
    charm_state = CharmState.from_charm(harness.charm)
    with pytest.raises(CharmConfigInvalidError):
        SamlIntegrator(charm_state=charm_state)


@patch.object(socket, "create_connection", side_effect=TimeoutError())
def test_saml_when_timeout(connection_mock):
    """
    arrange: mock the HTTP call to throw an exception when retrieving the certificate.
    act: validate the certificate.
    assert: an exception is raised.
    """
    harness = Harness(SamlIntegratorOperatorCharm)
    harness.begin()
    harness.disable_hooks()
    entity_id = "https://login.staging.ubuntu.com"
    metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
            "fingerprint": "98b228f28eab0b2eb5d03389fb6f8f9733dadcf0c17007fcde4148a4de41db54",
        }
    )
    charm_state = CharmState.from_charm(harness.charm)
    with pytest.raises(CharmConfigInvalidError):
        SamlIntegrator(charm_state=charm_state)


@patch.object(socket, "create_connection", return_value=MagicMock())
@patch.object(ssl, "create_default_context", return_value=MagicMock())
def test_saml_with_valid_certificate(context_mock, connection_mock):
    """
    arrange: mock certificate retrieved from the metadata URL.
    act: validate the certificate.
    assert: the certificate is valid.
    """
    wrap_socket = context_mock.return_value.wrap_socket
    wrap_socket.return_value.__enter__.return_value.getpeercert.return_value = b"somevalidcert"

    harness = Harness(SamlIntegratorOperatorCharm)
    harness.begin()
    harness.disable_hooks()
    entity_id = "https://login.staging.ubuntu.com"
    metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
            "fingerprint": (
                "98:b2:28:f2:8e:ab:0b:2e:b5:d0:33:89:fb:6f:8f:97:33:da"
                ":dc:f0:c1:70:07:fc:de:41:48:a4:de:41:db:54"
            ),
        }
    )
    charm_state = CharmState.from_charm(harness.charm)
    SamlIntegrator(charm_state=charm_state)

    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
            "fingerprint": (
                "98 b2 28 f2 8e ab 0b 2e b5 d0 33 89 fb 6f 8f 97 33 da"
                " dc f0 c1 70 07 fc de 41 48 a4 de 41 db 54"
            ),
        }
    )
    charm_state = CharmState.from_charm(harness.charm)
    SamlIntegrator(charm_state=charm_state)

    harness.update_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
            "fingerprint": "98b228f28eab0b2eb5d03389fb6f8f9733dadcf0c17007fcde4148a4de41db54",
        }
    )
    charm_state = CharmState.from_charm(harness.charm)
    SamlIntegrator(charm_state=charm_state)
