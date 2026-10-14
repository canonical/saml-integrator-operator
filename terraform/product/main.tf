# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  # Falls back to a channel derived from var.risk when saml_integrator.channel is unset.
  saml_integrator_channel = coalesce(var.saml_integrator.channel, "latest/${var.risk}")
}

module "saml_integrator" {
  source      = "../charm"
  app_name    = var.saml_integrator.app_name
  channel     = local.saml_integrator_channel
  config      = var.saml_integrator.config
  model_uuid  = var.model_uuid
  constraints = var.saml_integrator.constraints
  revision    = var.saml_integrator.revision
  base        = var.saml_integrator.base
  units       = var.saml_integrator.units
}

resource "juju_offer" "saml" {
  model_uuid       = var.model_uuid
  application_name = module.saml_integrator.application.name
  endpoints        = ["saml"]
}

resource "juju_access_offer" "saml" {
  offer_url = juju_offer.saml.url
  consume   = var.saml_offer_consumers
}

