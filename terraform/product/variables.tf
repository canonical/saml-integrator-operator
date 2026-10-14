# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model_uuid" {
  description = "UUID of the Juju model to deploy application to."
  type        = string
  nullable    = false
}

variable "risk" {
  description = "Risk level used to build the default saml_integrator.channel (\"latest/<risk>\") when saml_integrator.channel is not explicitly set, and reported in the product module's metadata output."
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
    channel     = optional(string)
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
