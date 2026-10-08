# Terraform modules

This project contains the [Terraform][Terraform] modules to deploy the 
[SAML integrator charm][SAML integrator charm] with its dependencies.

The modules use the [Terraform Juju provider][Terraform Juju provider] to model
the bundle deployment onto any Kubernetes environment managed by [Juju][Juju].

## Module structure

- **main.tf** - Defines the Juju application to be deployed, plus the SAML offer and its consumers.
- **variables.tf** - Allows customization of the deployment including Juju model name, charm's channel and configuration.
- **outputs.tf** - Responsible for integrating the module with other Terraform modules, primarily by defining the deployed models, metadata and offers.
- **terraform.tf** - Defines the Terraform provider.

## Using `saml-integrator` product module in higher level modules

```text
module "saml_integrator_product" {
  source = "git::https://github.com/canonical/saml-integrator-operator//terraform/product?ref=tf-1.0.0"

  model_uuid            = juju_model.my_model.uuid
  saml_offer_consumers  = ["admin"]
  # (Customize configuration variables here if needed)
}
```

[Terraform]: https://www.terraform.io/
[Terraform Juju provider]: https://registry.terraform.io/providers/juju/juju/latest
[Juju]: https://juju.is
[SAML integrator charm]: https://charmhub.io/saml-integrator

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.12 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | ~> 1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_juju"></a> [juju](#provider\_juju) | ~> 1.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_saml_integrator"></a> [saml\_integrator](#module\_saml\_integrator) | ../charm | n/a |

## Resources

| Name | Type |
|------|------|
| [juju_access_offer.saml](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/access_offer) | resource |
| [juju_offer.saml](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | UUID of the Juju model to deploy application to. | `string` | n/a | yes |
| <a name="input_risk"></a> [risk](#input\_risk) | Risk level reported in the product module's metadata output. It does not override an explicitly configured saml\_integrator.channel. | `string` | `"stable"` | no |
| <a name="input_saml_integrator"></a> [saml\_integrator](#input\_saml\_integrator) | n/a | <pre>object({<br/>    app_name    = optional(string, "saml-integrator")<br/>    channel     = optional(string, "latest/stable")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    revision    = optional(number)<br/>    base        = optional(string, "ubuntu@22.04")<br/>    units       = optional(number, 1)<br/>  })</pre> | n/a | yes |
| <a name="input_saml_offer_consumers"></a> [saml\_offer\_consumers](#input\_saml\_offer\_consumers) | List of consumers for the SAML offer. | `list(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_metadata"></a> [metadata](#output\_metadata) | Metadata of the product module deployment. |
| <a name="output_models"></a> [models](#output\_models) | Map of the model key to its model UUID and the components deployed in it. |
| <a name="output_offers"></a> [offers](#output\_offers) | Map of the offers exposed by this product module with their URLs. |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of the provided endpoints exposed by this product module. |
| <a name="output_saml_integrator_app_name"></a> [saml\_integrator\_app\_name](#output\_saml\_integrator\_app\_name) | Name of the deployed saml-integrator application. |
<!-- END_TF_DOCS -->
