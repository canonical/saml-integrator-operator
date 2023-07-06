[![CharmHub Badge](https://charmhub.io/saml-integrator/badge.svg)](https://charmhub.io/saml-integrator)
[![Release to Edge](https://github.com/canonical/saml-integrator-operator/actions/workflows/test_and_publish_charm.yaml/badge.svg)](https://github.com/canonical/saml-integrator-operator/actions/workflows/test_and_publish_charm.yaml)
[![Promote charm](https://github.com/canonical/saml-integrator-operator/actions/workflows/promote_charm.yaml/badge.svg)](https://github.com/canonical/saml-integrator-operator/actions/workflows/promote_charm.yaml)
[![Discourse Status](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.charmhub.io&style=flat&label=CharmHub%20Discourse)](https://discourse.charmhub.io)

# SAML Integrator Operator

A [Juju](https://juju.is/) [charm](https://juju.is/docs/olm/charmed-operators)
deploying and managing a SAML Integrator on Kubernetes. SAML s an XML-based
open-standard for transferring identity data between two parties: an identity
provider (IdP) and a service provider (SP).

This charm simplifies configuration of SAML SPs by providing a single point
of configuration for all the requirers using the same SAML entity. It can be
deployed on many different Kubernetes platforms, from [MicroK8s](https://microk8s.io)
to [Charmed Kubernetes](https://ubuntu.com/kubernetes) and public cloud Kubernetes
offerings.

As such, the charm makes it easy to manage and propagate SAML configuration, while
giving the freedom to deploy on the Kubernetes platform of their choice.

For DevOps or SRE teams this charm will make operating any charm leveraging SAML
authentication simple and straightforward through Juju's clean interface.

## Project and community

The SAML Integrator Operator is a member of the Ubuntu family. It's an open source
project that warmly welcomes community projects, contributions, suggestions,
fixes and constructive feedback.
* [Code of conduct](https://ubuntu.com/community/code-of-conduct)
* [Get support](https://discourse.charmhub.io/)
* [Join our online chat](https://chat.charmhub.io/charmhub/channels/charm-dev)
* [Contribute](https://charmhub.io/indico/docs/how-to-contribute)
Thinking about using the Indico Operator for your next project? [Get in touch](https://chat.charmhub.io/charmhub/channels/charm-dev)!

---

For further details,
[see the charm's detailed documentation](https://charmhub.io/saml-integrator/docs).
