#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator charm integration tests."""

import ops
import pytest


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_active(app: ops.Application):
    """Check that the charm is active.

    Assume that the charm has already been built and is running.
    """
    # Application actually does have units
    entity_id = "https://login.staging.ubuntu.com"
    metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
    app.set_config(
        {
            "entity_id": entity_id,
            "metadata_url": metadata_url,
        }
    )
    assert app.units[0].workload_status == ops.ActiveStatus.name  # type: ignore
