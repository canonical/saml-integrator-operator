# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

run "setup_tests" {
  module {
    source = "./tests/setup"
  }
}

run "basic_deploy" {
  variables {
    model_uuid = run.setup_tests.model_uuid
    saml_integrator = {
      channel = "latest/edge"
      # renovate: depName="saml-integrator"
      revision = 179
    }
    saml_offer_consumers = []
  }

  assert {
    condition     = output.saml_integrator_app_name == "saml-integrator"
    error_message = "saml-integrator output.saml_integrator_app_name did not match expected"
  }
}

run "channel_derived_from_risk" {
  variables {
    model_uuid = run.setup_tests.model_uuid
    risk       = "edge"
    saml_integrator = {
      # renovate: depName="saml-integrator"
      revision = 171
    }
    saml_offer_consumers = []
  }

  assert {
    condition     = output.metadata.risk == "edge"
    error_message = "output.metadata.risk did not match the configured risk"
  }
}

run "invalid_risk_is_rejected" {
  command = plan

  variables {
    model_uuid           = run.setup_tests.model_uuid
    risk                 = "unstable"
    saml_integrator      = {}
    saml_offer_consumers = []
  }

  expect_failures = [var.risk]
}
