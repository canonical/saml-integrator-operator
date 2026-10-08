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
    channel    = "latest/edge"
    # renovate: depName="saml-integrator"
    revision = 171
  }

  assert {
    condition     = output.application.name == "saml-integrator"
    error_message = "saml-integrator output.application.name did not match expected"
  }
}
