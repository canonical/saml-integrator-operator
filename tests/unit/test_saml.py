# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator unit tests."""

# pylint: disable=pointless-statement
from pathlib import Path
from unittest.mock import MagicMock

import pytest  # type: ignore[reportMissingImports]

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
        saml_integrator.certificates  # noqa: B018
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.endpoints  # noqa: B018


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
            "de:ae:84:7b:18:48:ff:02:74:e2:29:48:97:e6:d3:05"
            ":26:ad:d2:87:f0:e0:16:70:ef:d9:fa:7c:6a:67:8a:1f"
        ),
        metadata=metadata,
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    signing_cert = (
        "MIIDTDCCAjSgAwIBAgIUIZ7nkMARZyG69Ss2Rh0EmEXkErswDQYJKoZIhvcNAQELBQAw"
        "RTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoMGEludGVy"
        "bmV0IFdpZGdpdHMgUHR5IEx0ZDAgFw0yMzA4MDkxNDI1NDVaGA8yMDk5MDgwODE0MjU0"
        "NVowRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoMGElu"
        "dGVybmV0IFdpZGdpdHMgUHR5IEx0ZDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC"
        "ggEBANYGsje+fLOPhU55BM8v+0cVqkJbWMgU7PLFcSt7LMO8gQP4HJd0uQfzFF9zFuSn"
        "IDtxFCx6ONcykL4ENDgYvZezPUQZLGucEMP2lMu/YwjBcVcT1Ds7VUKz0M7wKifaDMhd"
        "zE+m40/coFW1/oLeQSPsFXCWnLH0dU8DulzFzvN+UsNe7IZKPGAi/agubMsSme0WOjjT"
        "TEuE66023CRuGZWShfDsFwsHelEJ1xx/1Dd3M8ZD95wCkt6f7LLDEtReVXowj3Lt0vfH"
        "Tpt7kIQpKslcqssZd22fZe+uARgVbOxdEDeGrtUtFiqE/d1EioQmoOYfpfRAnOW7aY5S"
        "YiLO+DUCAwEAAaMyMDAwHQYDVR0OBBYEFJJxYqkZMQ8LxfzpVUvf6VTI78UvMA8GA1Ud"
        "EwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAC769rkYR0+SLBznxmmLT3NHuuB1"
        "EgWlBA0f2pQd6PAGl67z9LG7PsuawgfM6aWAKtN1dkHSx97aDRVSoV/pNXaP9rHZ0KpB"
        "HJqZZkKIbAlEmUFFUUTPOmPTkjgGurni+9OLSchhDGR0E3VJlXMUoK3tHdVhu3HTegdT"
        "WhcfAJDy97Z0ARv6HaNRey8ve6/ORWDZHxQqsYFTgNwjRHxXd7tlW9m1oYOLCkcCupKl"
        "yMObuAZcikRKu33lgFbvXlJiHXuJNlnRabuzysTGbawNn/5m8/tQYgZiG3+kLVX2Kk9F"
        "OqJe+dpjxTjgxJZYae1tYQRrnrEv584w1z6EaJkBn88="
    )
    assert saml_integrator.signing_certificate == signing_cert
    assert saml_integrator.certificates == [signing_cert, "cert1_content"]
    endpoints = saml_integrator.endpoints
    assert len(endpoints) == 2
    assert endpoints[0].name == "SingleLogoutService"
    assert endpoints[0].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    assert str(endpoints[0].url) == "https://login.staging.ubuntu.com/+logout"
    assert str(endpoints[0].response_url) == "https://login.staging.ubuntu.com/example/"
    assert endpoints[1].name == "SingleSignOnService"
    assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    assert str(endpoints[1].url) == "https://login.staging.ubuntu.com/saml/"
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
            "de:ae:84:7b:18:48:ff:02:74:e2:29:48:97:e6:d3:05"
            ":26:ad:d2:87:f0:e0:16:70:ef:d9:fa:7c:6a:67:8a:1f"
        ),
        metadata=metadata,
    )
    saml_integrator = SamlIntegrator(charm_state=charm_state)
    with pytest.raises(CharmConfigInvalidError):
        saml_integrator.tree  # noqa: B018


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
        saml_integrator.tree  # noqa: B018


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
    assert str(endpoints[0].url) == "https://login.staging.ubuntu.com/+logout"
    assert str(endpoints[0].response_url) == "https://login.staging.ubuntu.com/example/"
    assert endpoints[1].name == "SingleSignOnService"
    assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post"
    assert str(endpoints[1].url) == "https://login.staging.ubuntu.com/saml/"
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
    assert str(endpoints[0].url) == "https://accounts.google.com/o/saml2/idp?idpid=C03oypjtr"
    assert endpoints[0].response_url is None
    assert endpoints[1].name == "SingleSignOnService"
    assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    assert str(endpoints[1].url) == "https://accounts.google.com/o/saml2/idp?idpid=C03oypjtr"
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
    assert str(endpoints[0].url) == "https://saml.canonical.test/sso"
    assert endpoints[0].response_url is None
    assert endpoints[1].name == "SingleSignOnService"
    assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    assert str(endpoints[1].url) == "https://saml.canonical.test/sso"
    assert endpoints[1].response_url is None
