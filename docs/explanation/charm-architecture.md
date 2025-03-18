# Charm architecture

The SAML Integrator charm fetches SAML metadata details based on the provided configuration and propagates them through a Juju integration.

The SAML Integrator can be deployed in Kubernetes and machine models and is a workloadless charm.

The metadata can be provided directly, through the configuration option `metadata`, or it can be provided through the 
configuration option `metadata_url`. In the latter case, the SAML integrator charm will get the XML SAML metadata document from 
the provided URL. From the metadata information, the `entity_id`, `x509certs` and endpoints information will be extracted and passed
in the SAML integration.

The charm provides a library to facilitate the development of charms that use the SAML integration.

## Juju events

According to the [Juju SDK](https://canonical-juju.readthedocs-hosted.com/en/latest/user/reference/hook/): "an event is a data structure that encapsulates part of the execution context of a charm".

For this charm, the following events are observed:

1. [config-changed](https://canonical-juju.readthedocs-hosted.com/en/latest/user/reference/hook/#config-changed): usually fired in response to a configuration change using the GUI or CLI. Action: validate the configuration and fetch the SAML details from the metadata. If there are relations, update the SAML details in the relation databag.
2. [saml-relation-created](https://canonical-juju.readthedocs-hosted.com/en/latest/user/reference/hook/#endpoint-relation-created): Custom event for when a new SAML relations is created. Action: write the SAML details in the relation databag.
3. [update-status](https://canonical-juju.readthedocs-hosted.com/en/latest/user/reference/hook/#update-status): Fired periodically by Juju. Action: write the SAML details in the relation databag if data has changed.

## Charm code overview

The `src/charm.py` is the default entry point for a charm and has the SamlIntegratorOperatorCharm Python class which inherits from CharmBase.

CharmBase is the base class from which all Charms are formed, defined by [Ops](https://ops.readthedocs.io/en/latest/) (Python framework for developing charms).

See more information in [Ops documentation](https://juju.is/docs/sdk/ops).

The `__init__` method guarantees that the charm observes all events relevant to its operation and handles them.
