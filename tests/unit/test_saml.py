# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator unit tests."""
# pylint: disable=pointless-statement
from pathlib import Path
from unittest.mock import MagicMock

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


def test_saml_with_invalid_metadata():
    """
    arrange: mock the metadata contents so that they are invalid.
    act: access the metadata properties.
    assert: a CharmConfigInvalidError exception is raised when attempting to access the
        properties read from the metadata.
    """
    charm_state = MagicMock(
        entity_id="https://login.staging.ubuntu.com",
        metadata="invalid",
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.certificates
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.endpoints


def test_saml_with_valid_signed_metadata():
    """
    arrange: mock the metadata contents so that they valid.
    act: access the metadata properties.
    assert: the properties are populated as defined in the metadata.
    """
    metadata = Path("tests/unit/files/metadata_signed.xml").read_text(encoding="utf-8")
    entity_id = "https://login.staging.ubuntu.com"
    charm_state = MagicMock(
        entity_id=entity_id,
        fingerprint=(
            "1C:73:51:f2:23:55:f8:3d:25:7e:65:56:dd:f1:a9:17:fe:d4:af"
            ":dc:70:d2:a8:11:b3:2f:d2:ea:c4:6d:91:e7"
        ),
        metadata=metadata,
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    signing_cert = (
        "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"
    )
    assert saml_integrator.signing_certificate == signing_cert
    assert saml_integrator.certificates == [signing_cert, "cert1_content"]
    endpoints = saml_integrator.endpoints
    assert len(endpoints) == 2
    assert endpoints[0].name == "SingleLogoutService"
    assert endpoints[0].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    assert endpoints[0].url == "https://login.staging.ubuntu.com/+logout"
    assert endpoints[0].response_url == "https://login.staging.ubuntu.com/example/"
    assert endpoints[1].name == "SingleSignOnService"
    assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    assert endpoints[1].url == "https://login.staging.ubuntu.com/saml/"
    assert endpoints[1].response_url is None


def test_saml_with_valid_tampered_signed_metadata():
    """
    arrange: mock the metadata contents so that they invalid.
    act: access the metadata properties.
    assert: an exception is raised.
    """
    metadata = Path("tests/unit/files/metadata_signed_tampered.xml").read_text(encoding="utf-8")

    entity_id = "https://login.staging.ubuntu.com"
    charm_state = MagicMock(
        entity_id=entity_id,
        fingerprint=(
            "1c:73:51:f2:23:55:f8:3d:25:7e:65:56:dd:f1:a9:17:fe:d4:af"
            ":dc:70:d2:a8:11:b3:2f:d2:ea:c4:6d:91:e7"
        ),
        metadata=metadata,
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.tree


def test_saml_with_valid_signed_metadata_not_matching_fingerprint():
    """
    arrange: mock the metadata contents so that they invalid and set an invalid fingerprint.
    act: access the metadata properties.
    assert: the properties are po
    pulated as defined in the metadata.
    """
    metadata = Path("tests/unit/files/metadata_signed.xml").read_text(encoding="utf-8")

    entity_id = "https://login.staging.ubuntu.com"
    charm_state = MagicMock(
        entity_id=entity_id,
        fingerprint="invalid_fingerprint",
        metadata=metadata,
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.tree


def test_saml_with_valid_unsigned_metadata():
    """
    arrange: mock the metadata contents so that they invalid.
    act: access the metadata properties.
    assert: the properties are populated as defined in the metadata.
    """
    metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")

    entity_id = "https://login.staging.ubuntu.com"
    charm_state = MagicMock(
        entity_id=entity_id,
        fingerprint="",
        metadata=metadata,
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    assert saml_integrator.certificates == ["cert1_content"]
    endpoints = saml_integrator.endpoints
    assert len(endpoints) == 2
    assert endpoints[0].name == "SingleLogoutService"
    assert endpoints[0].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post"
    assert endpoints[0].url == "https://login.staging.ubuntu.com/+logout"
    assert endpoints[0].response_url == "https://login.staging.ubuntu.com/example/"
    assert endpoints[1].name == "SingleSignOnService"
    assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post"
    assert endpoints[1].url == "https://login.staging.ubuntu.com/saml/"
    assert endpoints[1].response_url is None


def test_saml_with_valid_unsigned_metadata_non_utf8():
    """
    arrange: mock the metadata contents so that they invalid.
    act: access the metadata properties.
    assert: the properties are populated as defined in the metadata.
    """
    metadata = Path("tests/unit/files/non_utf8_metadata_unsigned.xml").read_text(encoding="utf-8")

    entity_id = "https://accounts.google.com/o/saml2?idpid=C03oypjtr"
    charm_state = MagicMock(
        entity_id=entity_id,
        fingerprint="",
        metadata=metadata,
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    certificate = (
        "MIIDdDCCAlygAwIBAgIGAYdLBPyWMA0GCSqGSIb3DQEBCwUAMHsxFDASBgNVBAoTC0dvb2dsZSBJ"
        "bmMuMRYwFAYDVQQHEw1Nb3VudGFpbiBWaWV3MQ8wDQYDVQQDEwZHb29nbGUxGDAWBgNVBAsTD0dv"
        "b2dsZSBGb3IgV29yazELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkNhbGlmb3JuaWEwHhcNMjMwNDA0"
        "MDY0NzA5WhcNMjgwNDAyMDY0NzA5WjB7MRQwEgYDVQQKEwtHb29nbGUgSW5jLjEWMBQGA1UEBxMN"
        "TW91bnRhaW4gVmlldzEPMA0GA1UEAxMGR29vZ2xlMRgwFgYDVQQLEw9Hb29nbGUgRm9yIFdvcmsx"
        "CzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpDYWxpZm9ybmlhMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A"
        "MIIBCgKCAQEApl6vmP6rt86m6I3dojHeT7bodIlDU3UnE2y1Hpqc6xlq0Kxv3ZcVrZX1dX/UC4NY"
        "CTlumUrEoVzERKRU1aGqBuk9QqvMpkf25jiWEetDly7IVJAq8behjq+801KzU3Kn1s830+czzQuH"
        "oVA9KlWwL6FSbCjmNKlAQ8qqcyQ3C1HlVF0x489/kfgZFw6sSX1sTZHgG0vw2E8xGdjRdtVVEgQG"
        "uWzLvcpWAPAK6IqzY5e9xETXN8au04SqnVWfUi19f4w8kCh3T8LIakmvm09lxYajndKCQvYrPnq+"
        "YpVwHiufnHxkVMb4claFFgX+gNDyEWbGDIi8yOQnKeUHnpCKGQIDAQABMA0GCSqGSIb3DQEBCwUA"
        "A4IBAQBZJnZzQilSlH3N2UCoJ1G9Me47NdZIs1HyQZNMtzbXwS+Z5Ek05loKFj75D3R094dtn4RC"
        "1pM5BQjBProMG5UbtQKVKbM8SjQgj23UWuuc6YXDok9lqtWuGwpOSNYUU75K/7vdVCFdG2urtms2"
        "ueZ2D8bA3nDhsgHAhc6YJM3TqatcFHRGTNlwkKl71GYMWYM3JKNEZAfU7zhjicXYhW7t3+Hj6TJC"
        "ChYw2B+hfOv0W324BZyyZW8X3m5CWVlCWxBKfIo3NJ+gg/dGbkuPIbzdV197LSuxkArm/7rMbxwe"
        "KNL8a7w5HN3iCi27GlKpmj4n5uMnDpRDk81hrvyew2Rp"
    )
    assert saml_integrator.certificates == [certificate]
    endpoints = saml_integrator.endpoints
    assert len(endpoints) == 2
    assert endpoints[0].name == "SingleSignOnService"
    assert endpoints[0].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    assert endpoints[0].url == "https://accounts.google.com/o/saml2/idp?idpid=C03oypjtr"
    assert endpoints[0].response_url is None
    assert endpoints[1].name == "SingleSignOnService"
    assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    assert endpoints[1].url == "https://accounts.google.com/o/saml2/idp?idpid=C03oypjtr"
    assert endpoints[1].response_url is None


def test_saml_with_metadata_with_default_namespaces():
    """
    arrange: mock the metadata with XML default namespaces.
    act: access the metadata properties.
    assert: the properties are populated as defined in the metadata.
    """
    metadata = Path("tests/unit/files/metadata_default_namespaces.xml").read_text(encoding="utf-8")

    entity_id = "https://saml.canonical.test/metadata"
    charm_state = MagicMock(
        entity_id=entity_id,
        fingerprint="",
        metadata=metadata,
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    endpoints = saml_integrator.endpoints
    assert len(endpoints) == 2
    assert endpoints[0].name == "SingleSignOnService"
    assert endpoints[0].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    assert endpoints[0].url == "https://saml.canonical.test/sso"
    assert endpoints[0].response_url is None
    assert endpoints[1].name == "SingleSignOnService"
    assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    assert endpoints[1].url == "https://saml.canonical.test/sso"
    assert endpoints[1].response_url is None
