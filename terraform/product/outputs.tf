# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed application."
  value       = module.saml_integrator.app_name
}

output "provides" {
  value = {
    saml = "saml"
  }
}
