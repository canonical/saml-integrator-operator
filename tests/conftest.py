# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Test fixtures."""

from unittest.mock import MagicMock

import pytest


def pytest_addoption(parser: pytest.Parser):
    """Add test arguments.

    Args:
        parser: pytest parser.
    """
    parser.addoption("--charm-file", action="store")


class Helpers:  # pylint: disable=too-few-public-methods
    """Helper class for testing."""

    @staticmethod
    def get_urlopen_result_mock(code: int, result: bytes) -> MagicMock:
        """Get a MagicMock for the urlopen response.

        Args:
            code: response code.
            result: response content.

        Returns:
            Mock for the response.
        """
        urlopen_result_mock = MagicMock()
        urlopen_result_mock.getcode.return_value = code
        urlopen_result_mock.read.return_value = result
        urlopen_result_mock.__enter__.return_value = urlopen_result_mock
        return urlopen_result_mock


@pytest.fixture
def helpers():
    """Fixture to return the helper class."""
    return Helpers
