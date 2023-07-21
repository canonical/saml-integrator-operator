# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

import ops
from charms.saml_integrator.v0 import saml
from ops.testing import Harness

METADATA = """
name: saml-consumer
requires:
  saml:
    interface: saml
"""


class SamlConsumerCharm(ops.CharmBase):
    """Class for consumer charm testing."""

    def __init__(self, *args):
        """Init method for the class.

        Args:
            args: Variable list of positional arguments passed to the parent constructor.
        """
        super().__init__(*args)
        self.saml = saml.SamlRequires(self)
        self.events = []
        self.framework.observe(self.saml.on.saml_data_available, self._record_event)

    def _record_event(self, event: ops.EventBase) -> None:
        """Rececord emitted event in the event list.

        Args:
            event: event.
        """
        self.events.append(event)


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


def test_consumer_charm_does_not_emit_event_id_no_leader():
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
    harness = Harness(SamlConsumerCharm, meta=METADATA)
    harness.begin()
    harness.set_leader(False)
    relation_id = harness.add_relation("saml", "saml-provider")
    harness.add_relation_unit(relation_id, "saml-provider/0")
    harness.update_relation_data(
        relation_id,
        "saml-provider",
        relation_data,
    )
    assert len(harness.charm.events) == 0


def test_consumer_charm_emits_event_when_leader():
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

    harness = Harness(SamlConsumerCharm, meta=METADATA)
    harness.begin()
    harness.set_leader(True)
    relation_id = harness.add_relation("saml", "saml-provider")
    harness.add_relation_unit(relation_id, "saml-provider/0")
    harness.update_relation_data(
        relation_id,
        "saml-provider",
        relation_data,
    )

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
    assert len(harness.charm.events) == 1
    assert harness.charm.events[0].entity_id == relation_data["entity_id"]
    assert harness.charm.events[0].metadata_url == relation_data["metadata_url"]
    assert harness.charm.events[0].certificates == relation_data["x509certs"].split(",")
    assert harness.charm.events[0].endpoints == [slo_ep, sso_ep]
