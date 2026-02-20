# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

module "saml_integrator" {
  source      = "../charm"
  app_name    = var.saml_integrator.app_name
  channel     = var.saml_integrator.channel
  config      = var.saml_integrator.config
  model_uuid  = var.model_uuid
  constraints = var.saml_integrator.constraints
  revision    = var.saml_integrator.revision
  base        = var.saml_integrator.base
  units       = var.saml_integrator.units
}

resource "juju_offer" "saml" {
  model_uuid       = var.model_uuid
  application_name = module.saml_integrator.app_name
  endpoint         = "saml"
}

resource "juju_access_offer" "saml" {
  offer_url = juju_offer.saml.url
  admin     = [var.model_uuid]
  consume   = var.saml_offer_consumers
}


