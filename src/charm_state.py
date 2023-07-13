#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module defining the CharmState class which represents the state of the SAML Integrator charm."""

import itertools

import ops
from pydantic import AnyHttpUrl, BaseModel, Field, ValidationError

KNOWN_CHARM_CONFIG = (
    "entity_id",
    "metadata_url",
)


class SamlIntegratorConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """Represent charm builtin configuration values.

    Attrs:
        entity_id: Entity ID.
        metadata_url: Metadata URL.
    """

    entity_id: str = Field(..., min_length=1)
    metadata_url: AnyHttpUrl


class CharmConfigInvalidError(Exception):
    """Exception raised when a charm configuration is found to be invalid.

    Attrs:
        msg (str): Explanation of the error.
    """

    def __init__(self, msg: str):
        """Initialize a new instance of the CharmConfigInvalidError exception.

        Args:
            msg (str): Explanation of the error.
        """
        self.msg = msg


class CharmState:
    """Represents the state of the SAML Integrator charm.

    Attrs:
        entity_id: Entity ID for SAML.
        metadata_url: URL for the SAML metadata.
    """

    def __init__(self, *, saml_integrator_config: SamlIntegratorConfig):
        """Initialize a new instance of the CharmState class.

        Args:
            saml_integrator_config: SAML Integrator configuration.
        """
        self._saml_integrator_config = saml_integrator_config

    @property
    def entity_id(self) -> str:
        """Return entity_id config.

        Returns:
            str: entity_id config.
        """
        return self._saml_integrator_config.entity_id

    @property
    def metadata_url(self) -> str:
        """Return metadata_url config.

        Returns:
            str: metadata_url config.
        """
        return self._saml_integrator_config.metadata_url

    @classmethod
    def from_charm(cls, charm: "ops.CharmBase") -> "CharmState":
        """Initialize a new instance of the CharmState class from the associated charm.

        Args:
            charm: The charm instance associated with this state.

        Return:
            The CharmState instance created by the provided charm.

        Raises:
            CharmConfigInvalidError: if the charm configuration is invalid.
        """
        config = {k: v for k, v in charm.config.items() if k in KNOWN_CHARM_CONFIG}
        try:
            # Incompatible with pydantic.AnyHttpUrl
            valid_config = SamlIntegratorConfig(**config)  # type: ignore
        except ValidationError as exc:
            error_fields = set(
                itertools.chain.from_iterable(error["loc"] for error in exc.errors())
            )
            error_field_str = " ".join(str(f) for f in error_fields)
            raise CharmConfigInvalidError(f"invalid configuration: {error_field_str}") from exc
        return cls(saml_integrator_config=valid_config)
