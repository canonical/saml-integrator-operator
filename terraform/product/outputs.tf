# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "metadata" {
  description = "Metadata of the product module deployment."
  value = {
    version = "1.0.0"
    risk    = var.risk
  }
}

output "models" {
  description = "Map of the model key to its model UUID and the components deployed in it."
  value = {
    saml_integrator = {
      model_uuid = var.model_uuid
      components = {
        saml_integrator = module.saml_integrator.application
      }
    }
  }
}

output "offers" {
  description = "Map of the offers exposed by this product module with their URLs."
  value = {
    saml = juju_offer.saml.url
  }
}

output "provides" {
  description = "Map of the provided endpoints exposed by this product module."
  value = {
    saml = {
      kind       = "endpoint"
      name       = module.saml_integrator.application.name
      endpoint   = "saml"
      controller = null
    }
  }
}

output "saml_integrator_app_name" {
  description = "Name of the deployed saml-integrator application."
  value       = module.saml_integrator.application.name
}
