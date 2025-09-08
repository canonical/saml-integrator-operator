# Terraform modules

This project contains the [Terraform][Terraform] modules to deploy the 
[SAML integrator charm][SAML integrator charm] with its dependencies.

The modules use the [Terraform Juju provider][Terraform Juju provider] to model
the bundle deployment onto any Kubernetes environment managed by [Juju][Juju].

## Module structure

- **main.tf** - Defines the Juju application to be deployed.
- **variables.tf** - Allows customization of the deployment including Juju model name, charm's channel and configuration.
- **output.tf** - Responsible for integrating the module with other Terraform modules, primarily by defining potential integration endpoints (charm integrations).
- **versions.tf** - Defines the Terraform provider.

[Terraform]: https://www.terraform.io/
[Terraform Juju provider]: https://registry.terraform.io/providers/juju/juju/latest
[Juju]: https://juju.is
[SAML integrator charm]: https://charmhub.io/saml-integrator

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.7.2 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >= 0.17.1 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_juju"></a> [juju](#provider\_juju) | >= 0.17.1 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_saml_integrator"></a> [saml\_integrator](#module\_saml\_integrator) | ../charm | n/a |

## Resources

| Name | Type |
|------|------|
| [juju_access_offer.saml](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/access_offer) | resource |
| [juju_offer.saml](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_model.saml_integrator](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/model) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_model"></a> [model](#input\_model) | Reference to the k8s Juju model to deploy application to. | `string` | n/a | yes |
| <a name="input_saml_integrator"></a> [saml\_integrator](#input\_saml\_integrator) | n/a | <pre>object({<br/>    app_name    = optional(string, "saml-integrator")<br/>    channel     = optional(string, "latest/stable")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    revision    = optional(number)<br/>    base        = optional(string, "ubuntu@22.04")<br/>    units       = optional(number, 1)<br/>  })</pre> | n/a | yes |
| <a name="input_saml_offer_consumers"></a> [saml\_offer\_consumers](#input\_saml\_offer\_consumers) | List of consumers for the SAML offer. | `list(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_app_name"></a> [app\_name](#output\_app\_name) | Name of the deployed application. |
| <a name="output_provides"></a> [provides](#output\_provides) | n/a |
<!-- END_TF_DOCS -->