# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

run "setup_tests" {
  module {
    source = "../tests/setup"
  }
}

run "basic_deploy" {
  variables {
    model_uuid = run.setup_tests.model_uuid
    channel    = "latest/edge"
    # renovate: depName="saml-integrator"
    revision = 121
  }

  assert {
    condition     = output.app_name == "saml-integrator"
    error_message = "saml-integrator app_name did not match expected"
  }
}
