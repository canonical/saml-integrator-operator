# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

# pylint: disable=import-error,consider-using-with,no-member

"""This code snippet is used to be loaded into any-charm which is used for integration tests."""
from any_charm_base import AnyCharmBase

import saml


class AnyCharm(AnyCharmBase):  # pylint: disable=too-few-public-methods
    """Execute a simple charm workload to test the saml relation.

    Attrs:
        saml: The attribute that mimics a real SAML relation.
    """

    def __init__(self, *args, **kwargs):
        """Init function for the class.

        Args:
            args: Variable list of positional arguments passed to the parent constructor.
            kwargs: Variable list of positional keyword arguments passed to the parent constructor.
        """
        super().__init__(*args, **kwargs)
        self.saml = saml.SamlRequires(self)
