# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "application" {
  description = "Full juju_application object for the deployed SAML integrator application."
  value       = juju_application.saml_integrator
}

output "provides" {
  description = "Provided relations exposed by the module."
  value = {
    saml = {
      kind     = "endpoint"
      name     = juju_application.saml_integrator.name
      endpoint = "saml"
    }
  }
}
