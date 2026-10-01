# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model_uuid" {
  description = "UUID of the Juju model to deploy application to."
  type        = string
  nullable    = false
}

variable "risk" {
  description = "Risk level reported in the product module's metadata output. It does not override an explicitly configured saml_integrator.channel."
  type        = string
  default     = "stable"

  validation {
    condition     = contains(["stable", "candidate", "beta", "edge"], var.risk)
    error_message = "risk must be one of: stable, candidate, beta, edge."
  }
}

variable "saml_integrator" {
  type = object({
    app_name    = optional(string, "saml-integrator")
    channel     = optional(string, "latest/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    revision    = optional(number)
    base        = optional(string, "ubuntu@22.04")
    units       = optional(number, 1)
  })
}

variable "saml_offer_consumers" {
  description = "List of consumers for the SAML offer."
  type        = list(string)
}
