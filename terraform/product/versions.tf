# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_version = ">= 1.7.2"
  required_providers {
    juju = {
      source  = "juju/juju"
      version = ">= 0.17.1"
    }
  }
}
