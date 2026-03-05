# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model_uuid" {
  description = "UUID of the Juju model to deploy application to."
  type        = string
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
