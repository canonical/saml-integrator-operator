# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Test fixtures."""

import pytest


def pytest_addoption(parser: pytest.Parser):
    """Add test arguments.

    Args:
        parser: pytest parser.
    """
    parser.addoption("--charm-file", action="store")
