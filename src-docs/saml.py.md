<!-- markdownlint-disable -->

<a href="../src/saml.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `saml.py`
Provide the SamlApp class to encapsulate the business logic. 

**Global Variables**
---------------
- **TYPE_CHECKING**


---

## <kbd>class</kbd> `SamlIntegrator`
A class representing the SAML Integrator application. 

Attrs:  endpoints: SAML endpoints.  certificates: public certificates.  signature: the Signature element in the metadata.  signing_certificate: signing certificate.  tree: the element tree for the metadata.  nsmap: namespaces list. 

<a href="../src/saml.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(charm_state: CharmState)
```

Initialize a new instance of the SamlApp class. 



**Args:**
 
 - <b>`charm_state`</b>:  The state of the charm that the Saml instance belongs to. 





