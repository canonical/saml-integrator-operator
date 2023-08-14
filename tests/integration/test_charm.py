#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator charm integration tests."""

import ops
import pytest
from pytest_operator.plugin import OpsTest


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_active(ops_test: OpsTest, app: ops.Application):
    """Check that the charm is active.

    Assume that the charm has already been built and is running.
    """
    await app.set_config(  # type: ignore[attr-defined]
        {
            "entity_id": "https://login.staging.ubuntu.com",
            "fingerprint": (
                "1c:73:51:f2:23:55:f8:3d:25:7e:65:56:dd:f1:a9:17:fe"
                ":d4:af:dc:70:d2:a8:11:b3:2f:d2:ea:c4:6d:91:e7"
            ),
            "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
        }
    )
    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
    assert ops_test.model
    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
    assert app.units[0].workload_status == status_name  # type: ignore
