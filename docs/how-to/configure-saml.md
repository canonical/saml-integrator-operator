# How to configure SAML

To configure the SAML Integrator integration you'll have to set the following configuration options with the appropriate values for your SAML server by running `juju config [charm_name] [configuration]=[value]`.

Two configuration values are mandatory, the SAML metadata URL that needs to be specified in `metadata_url` and the entity ID, in `entity_id`.

For more details on the configuration options and their default values see the [configuration reference](https://charmhub.io/saml-integrator/configure).