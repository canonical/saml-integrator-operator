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
      revision = 161
    }
    saml_offer_consumers = []
  }

  assert {
    condition     = output.app_name == "saml-integrator"
    error_message = "saml-integrator output.app_name did not match expected"
  }
}
