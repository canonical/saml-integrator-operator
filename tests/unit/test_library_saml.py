# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

from charms.saml_integrator.v0 import saml


def test_saml_relation_data_to_relation_data():
    sso_ep = saml.SamlEndpoint(
        name="SingleSignOnService",
        url="https://login.staging.ubuntu.com/saml/",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
    )
    slo_ep = saml.SamlEndpoint(
        name="SingleLogoutService",
        url="https://login.staging.ubuntu.com/+logout",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        response_url="https://login.staging.ubuntu.com/+logout2",
    )
    saml_data = saml.SamlRelationData(
        entity_id="https://login.staging.ubuntu.com",
        metadata_url="https://login.staging.ubuntu.com/saml/metadata",
        certificates=["cert1", "cert2"],
        endpoints=[sso_ep, slo_ep],
    )
    relation_data = saml_data.to_relation_data()
    expected_relation_data = {
        "entity_id": "https://login.staging.ubuntu.com",
        "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
        "x509certs": "cert1,cert2",
        "single_sign_on_service_redirect_url": "https://login.staging.ubuntu.com/saml/",
        "single_sign_on_service_redirect_binding": (
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        ),
        "single_logout_service_redirect_url": "https://login.staging.ubuntu.com/+logout",
        "single_logout_service_redirect_binding": (
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        ),
        "single_logout_service_redirect_response_url": "https://login.staging.ubuntu.com/+logout2",
    }
    assert relation_data == expected_relation_data


def test_saml_relation_data_from_relation_data():
    relation_data = {
        "entity_id": "https://login.staging.ubuntu.com",
        "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
        "x509certs": "cert1,cert2",
        "single_sign_on_service_redirect_url": "https://login.staging.ubuntu.com/saml/",
        "single_sign_on_service_redirect_binding": (
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        ),
        "single_logout_service_redirect_url": "https://login.staging.ubuntu.com/+logout",
        "single_logout_service_redirect_binding": (
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        ),
    }
    saml_data = saml.SamlRelationData.from_relation_data(relation_data)

    slo_ep = saml.SamlEndpoint(
        name="SingleLogoutService",
        url="https://login.staging.ubuntu.com/+logout",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
    )
    sso_ep = saml.SamlEndpoint(
        name="SingleSignOnService",
        url="https://login.staging.ubuntu.com/saml/",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
    )
    expected_saml_data = saml.SamlRelationData(
        entity_id="https://login.staging.ubuntu.com",
        metadata_url="https://login.staging.ubuntu.com/saml/metadata",
        certificates=["cert1", "cert2"],
        endpoints=[slo_ep, sso_ep],
    )
    assert saml_data == expected_saml_data
