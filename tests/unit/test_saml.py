# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator unit tests."""
# pylint: disable=pointless-statement
import urllib
from unittest.mock import MagicMock, patch

import pytest

from charm_state import CharmConfigInvalidError
from saml import SamlIntegrator


def get_urlopen_result_mock(code: int, result: bytes) -> MagicMock:
    """Get a MagicMock for the urlopen response.

    Args:
        code: response code.
        result: response content.

    Returns:
        Mock for the response.
    """
    urlopen_result_mock = MagicMock()
    urlopen_result_mock.getcode.return_value = code
    urlopen_result_mock.read.return_value = result
    return urlopen_result_mock


@patch("urllib.request.urlopen")
def test_saml_with_invalid_metadata(urlopen_mock):
    """
    arrange: mock the metadata contents so that they are invalid.
    act: access the metadata properties.
    assert: a CharmConfigInvalidError exception is raised when attempting to access the
        properties read from the metadata.
    """
    urlopen_result_mock = get_urlopen_result_mock(200, b"invalid")
    urlopen_result_mock.__enter__.return_value = urlopen_result_mock
    urlopen_mock.return_value = urlopen_result_mock
    charm_state = MagicMock(
        entity_id="https://login.staging.ubuntu.com",
        metadata_url="https://login.staging.ubuntu.com/saml/metadata",
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.certificates
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.endpoints


@patch.object(urllib.request, "urlopen", side_effect=urllib.error.URLError("Error"))
def test_saml_with_invalid_url(_):
    """
    arrange: mock the HTTP request for the metadata so that it fails.
    act: access the metadata properties.
    assert: a CharmConfigInvalidError exception is raised when attempting to access the
        properties read from the metadata.
    """
    charm_state = MagicMock(
        entity_id="https://login.staging.ubuntu.com",
        metadata_url="https://login.staging.ubuntu.com/saml/metadata",
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
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
        urlopen_result_mock = get_urlopen_result_mock(200, metadata.read())
        urlopen_result_mock.__enter__.return_value = urlopen_result_mock
        urlopen_mock.return_value = urlopen_result_mock

        entity_id = "https://login.staging.ubuntu.com"
        metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
        charm_state = MagicMock(
            entity_id=entity_id,
            metadata_url=metadata_url,
        )
        saml_integrator = SamlIntegrator(charm_state=charm_state)
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
