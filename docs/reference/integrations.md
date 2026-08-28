(reference_integrations)=

# Integrations

## `saml`

_Interface_: `saml`

_Supported charms_: [discourse-k8s](https://charmhub.io/discourse-k8s),
[indico](https://charmhub.io/indico),
[mediawiki-k8s](https://charmhub.io/mediawiki-k8s),
[synapse](https://charmhub.io/synapse)

The `saml` relation provides the requirer charm with SAML configuration details,
such as the identity provider's entity ID, metadata URL, single sign-on
endpoints and x509 signing certificates, so it can authenticate users against
the configured SAML IdP.

Example `saml` integrate command:

```
juju integrate saml-integrator discourse-k8s
```

See [Integrations](https://charmhub.io/saml-integrator/integrations).
