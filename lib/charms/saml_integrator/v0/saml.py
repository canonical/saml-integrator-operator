#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# Licensed under the Apache2.0. See LICENSE file in charm source for details.

"""TODO: Add a proper docstring here.

This is a placeholder docstring for this charm library. Docstrings are
presented on Charmhub and updated whenever you push a new version of the
library.

Complete documentation about creating and documenting libraries can be found
in the SDK docs at https://juju.is/docs/sdk/libraries.

See `charmcraft publish-lib` and `charmcraft fetch-lib` for details of how to
share and consume charm libraries. They serve to enhance collaboration
between charmers. Use a charmer's libraries for classes that handle
integration with their charm.

Bear in mind that new revisions of the different major API versions (v0, v1,
v2 etc) are maintained independently.  You can continue to update v0 and v1
after you have pushed v3.

Markdown is supported, following the CommonMark specification.
"""

# The unique Charmhub library identifier, never change it
LIBID = "511cdfa7de3d43568bf9b512f9c9f89d"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1


class SamlProvides(Object, ABC):
    
    def __init__(self, charm: CharmBase, relation_name: str) -> None:
        super().__init__(charm, relation_name)
        self.charm = charm
        self.local_app = self.charm.model.app
        self.relation_name = relation_name
        self.framework.observe(charm.on[relation_name].relation_created, self._on_relation_created)

    def _on_relation_created(self, event: RelationCreatedEvent) -> None:
        """Handle a change to the saml relation.

        Populate the event data.

        Args:
            event: Event triggering the relation-created hook for the relation.
        """
        if not self.model.unit.is_leader():
            return
        event.relation.data[self.model.app].update(self._dump_saml_data())

    def _dump_saml_data(self) -> Dict[str, str]:
        """Dump the charm state in the format expected by the relation.

        Returns:
            Dict containing the IdP details.
        """
        result = {
            "entity_id": self.charm._saml_integrator.entity_id,
            "metadata_url": self.charm._saml_integrator.metadata_url,
            "x509certs": ",".join(self.charm._saml_integrator.certificates),
        }
        for endpoint in self._saml_integrator.endpoints:
            http_method = endpoint.binding.split(":")[-1].split("-")[-1].lower()
            lowercase_name = re.sub(r"(?<!^)(?=[A-Z])", "_", endpoint.name).lower()
            prefix = f"{lowercase_name}_{http_method}_"
            result[f"{prefix}url"] = endpoint.url
            result[f"{prefix}binding"] = endpoint.binding
            if endpoint.response_url:
                result[f"{prefix}response_url"] = endpoint.response_url
        return result

    @property
    def relations(self) -> List[Relation]:
        """The list of Relation instances associated with this relation_name."""
        return list(self.charm.model.relations[self.relation_name])
