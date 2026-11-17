# How to configure SAML

To configure the SAML Integrator charm for your identity provider (IdP), set its configuration options with `juju config`:

```bash
juju config saml-integrator <configuration>=<value>
```

`entity_id` is required. You must also provide the IdP metadata through either `metadata_url` or `metadata`; if you set both, `metadata_url` takes precedence. The `fingerprint` option is optional.

## Configure the entity identifier

The `entity_id` option identifies the IdP entity. Set it to the entity ID from the IdP metadata. It must be a URI.

```bash
juju config saml-integrator entity_id=https://login.staging.ubuntu.com
```

## Configure the metadata source

The `metadata_url` option is the URL from which the charm retrieves the IdP metadata. The URL must be reachable from the charm.

```bash
juju config saml-integrator metadata_url=https://login.staging.ubuntu.com/saml/metadata
```

## Configure metadata directly

The `metadata` option contains the IdP metadata as an XML string. Use it when the metadata is not available at a URL or when you want to provide it directly. If you previously configured `metadata_url`, reset it first because `metadata_url` takes precedence.

```bash
juju config saml-integrator --reset metadata_url
juju config saml-integrator metadata="$(cat /path/to/metadata.xml)"
```

`/path/to/metadata.xml` is a file on the machine where you run the command.

## Configure the certificate fingerprint

The optional `fingerprint` option checks the SHA256 fingerprint of the signing certificate in the metadata against a trusted value obtained from your identity provider. If unset, the charm skips this fingerprint comparison.

```bash
juju config saml-integrator fingerprint="<sha256-fingerprint>"
```

Replace the placeholder with the SHA256 fingerprint of your IdP signing certificate.

## Verify the configuration

Check that the charm is active:

```bash
juju status
```

To inspect the current configuration values, run:

```bash
juju config saml-integrator
```

If the charm goes into a blocked state or shows an error, inspect the logs for details:

```bash
juju debug-log --include saml-integrator
```

For more details on the configuration options and their default values, see the [configuration reference](https://charmhub.io/saml-integrator/configure).
