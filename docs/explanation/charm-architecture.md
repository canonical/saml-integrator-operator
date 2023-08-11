# Charm architecture

The SAML Integrator charm fetches SAML metadata details based on the provided configuration and propagates them through a Juju integration.

## Juju events

According to the [Juju SDK](https://juju.is/docs/sdk/event): "an event is a data structure that encapsulates part of the execution context of a charm".

For this charm, the following events are observed:

1. [upgrade-charm](https://juju.is/docs/sdk/upgrade-charm-event): fired on the charms when the unit is undergoing an upgrade. Action: install charm dependencies.
2. [config-changed](https://juju.is/docs/sdk/config-changed-event): usually fired in response to a configuration change using the GUI or CLI. Action: validate the configuration and fetch the SAML details from the metadata URL. If there are relations, update the SAML details in the relation databag.
3. [saml-relation-joined](https://juju.is/docs/sdk/relation-name-relation-joined-event): Custom event for when a new SAML relations joins. Action: write the SAML details in the relation databag.

## Charm code overview

The `src/charm.py` is the default entry point for a charm and has the SamlIntegratorOperatorCharm Python class which inherits from CharmBase.

CharmBase is the base class from which all Charms are formed, defined by [Ops](https://juju.is/docs/sdk/ops) (Python framework for developing charms).

See more information in [Charm](https://juju.is/docs/sdk/constructs#heading--charm).

The `__init__` method guarantees that the charm observes all events relevant to its operation and handles them.
