# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Test fixtures."""

import pytest


def pytest_addoption(parser: pytest.Parser):
    """Add test arguments.

    Args:
        parser: pytest parser.
    """
    parser.addoption("--model", action="store", default=None)
    parser.addoption("--keep-models", action="store_true", default=False)
