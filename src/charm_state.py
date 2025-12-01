#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module defining the CharmState class which represents the state of the SAML Integrator charm."""

import itertools
import urllib
from typing import Optional

import ops
from pydantic import AnyHttpUrl, BaseModel, Field, ValidationError


class SamlIntegratorConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """Represent charm builtin configuration values.

    Attrs:
        entity_id: entity ID.
        fingerprint: fingerprint to validate the signing certificate against.
        metadata: metadata.
        metadata_url: metadata URL.
    """

    entity_id: str = Field(..., min_length=1)
    fingerprint: Optional[str]
    metadata: Optional[str]
    metadata_url: Optional[AnyHttpUrl]


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
        fingerprint: fingerprint to validate the signing certificate against.
        metadata: metadata.
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
    def fingerprint(self) -> Optional[str]:
        """Return certificate config.

        Returns:
            str: certificate config.
        """
        return self._saml_integrator_config.fingerprint

    @property
    def metadata_url(self) -> Optional[str]:
        """Return metadata_url config.

        Returns:
            str: metadata_url config.
        """
        return self._saml_integrator_config.metadata_url

    @property
    def metadata(self) -> str:
        """Return metadata config or metadata_url content.

        Returns:
            str: metadata.
        """
        if self._saml_integrator_config.metadata_url:
            try:
                with urllib.request.urlopen(  # noqa: S310
                    self._saml_integrator_config.metadata_url, timeout=10
                ) as resource:  # nosec
                    return resource.read()
            except urllib.error.URLError as ex:
                raise CharmConfigInvalidError(
                    f"Error while retrieving data from {self.metadata_url}"
                ) from ex
        # Config will be identified as invalid is neither metadata_url nor metadata are defined.
        assert self._saml_integrator_config.metadata  # nosec  # noqa: S101
        return self._saml_integrator_config.metadata

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
        try:
            # Incompatible with pydantic.AnyHttpUrl
            valid_config = SamlIntegratorConfig(**dict(charm.config.items()))  # type: ignore
            if not valid_config.metadata_url and not valid_config.metadata:
                raise CharmConfigInvalidError(
                    "Either the metadata_url or the metadata need to be configured."
                )
        except ValidationError as exc:
            error_fields = set(
                itertools.chain.from_iterable(error["loc"] for error in exc.errors())
            )
            error_field_str = " ".join(str(f) for f in error_fields)
            raise CharmConfigInvalidError(f"invalid configuration: {error_field_str}") from exc
        return cls(saml_integrator_config=valid_config)
