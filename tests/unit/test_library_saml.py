# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML library unit tests"""
import ops
import pytest
from charms.saml_integrator.v0 import saml
from ops.testing import Harness

REQUIRER_METADATA = """
name: saml-consumer
requires:
  saml:
    interface: saml
"""

PROVIDER_METADATA = """
name: saml-producer
provides:
  saml:
    interface: saml
"""


class SamlRequirerCharm(ops.CharmBase):
    """Class for requirer charm testing."""

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


class SamlProviderCharm(ops.CharmBase):
    """Class for provider charm testing."""

    def __init__(self, *args):
        """Init method for the class.

        Args:
            args: Variable list of positional arguments passed to the parent constructor.
        """
        super().__init__(*args)
        self.saml = saml.SamlProvides(self)
        self.events = []
        self.framework.observe(self.on.saml_relation_changed, self._record_event)

    def _record_event(self, event: ops.EventBase) -> None:
        """Record emitted event in the event list.

        Args:
            event: event.
        """
        self.events.append(event)


def test_saml_relation_data_to_relation_data():
    """
    arrange: instantiate a SamlRelationData object.
    act: obtain the relation representation.
    assert: the relation representation is correct.
    """
    sso_endpoint = saml.SamlEndpoint(
        name="SingleSignOnService",
        url="https://login.staging.ubuntu.com/saml/",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
    )
    slo_endpoint = saml.SamlEndpoint(
        name="SingleLogoutService",
        url="https://login.staging.ubuntu.com/+logout",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        response_url="https://login.staging.ubuntu.com/+logout2",
    )
    saml_data = saml.SamlRelationData(
        entity_id="https://login.staging.ubuntu.com",
        metadata_url="https://login.staging.ubuntu.com/saml/metadata",
        certificates=["cert1", "cert2"],
        endpoints=[sso_endpoint, slo_endpoint],
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


def test_requirer_charm_does_not_emit_event_id_no_data():
    """
    arrange: set up a charm with no relation data to be populated.
    act: trigger a relation changed event.
    assert: no events are emitted.
    """
    harness = Harness(SamlRequirerCharm, meta=REQUIRER_METADATA)
    harness.begin()
    harness.set_leader(True)
    relation_id = harness.add_relation("saml", "saml-provider")
    harness.add_relation_unit(relation_id, "saml-provider/0")
    relation = harness.charm.framework.model.get_relation("saml", 0)
    harness.charm.on.saml_relation_changed.emit(relation)
    assert len(harness.charm.events) == 0


@pytest.mark.parametrize("is_leader", [True, False])
def test_requirer_charm_emits_event(is_leader):
    """
    arrange: set up a charm.
    act: trigger a relation changed event.
    assert: a event containing the relation data is emitted.
    """
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

    harness = Harness(SamlRequirerCharm, meta=REQUIRER_METADATA)
    harness.begin()
    harness.set_leader(is_leader)
    relation_id = harness.add_relation("saml", "saml-provider")
    harness.add_relation_unit(relation_id, "saml-provider/0")
    harness.update_relation_data(
        relation_id,
        "saml-provider",
        relation_data,
    )

    slo_endpoint = saml.SamlEndpoint(
        name="SingleLogoutService",
        url="https://login.staging.ubuntu.com/+logout",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
    )
    sso_endpoint = saml.SamlEndpoint(
        name="SingleSignOnService",
        url="https://login.staging.ubuntu.com/saml/",
        binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
    )
    assert len(harness.charm.events) == 1
    assert harness.charm.events[0].entity_id == relation_data["entity_id"]
    assert harness.charm.events[0].metadata_url == relation_data["metadata_url"]
    assert harness.charm.events[0].certificates == tuple(relation_data["x509certs"].split(","))
    assert harness.charm.events[0].endpoints == (slo_endpoint, sso_endpoint)

    retrieved_relation_data = harness.charm.saml.get_relation_data()
    assert retrieved_relation_data.entity_id == relation_data["entity_id"]
    assert retrieved_relation_data.metadata_url == relation_data["metadata_url"]
    assert retrieved_relation_data.certificates == tuple(relation_data["x509certs"].split(","))
    assert retrieved_relation_data.endpoints == (slo_endpoint, sso_endpoint)
