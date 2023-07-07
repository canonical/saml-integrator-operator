# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Provide the SamlApp class to encapsulate the business logic."""

class SamlApp:
    """A class representing the SAML application."""

    def __init__(self, charm_state: CharmState):
        """Initialize a new instance of the SamlApp class.

        Args:
            charm_state: The state of the charm that the SamlApp instance belongs to.
        """
        self._charm_state = charm_state

    