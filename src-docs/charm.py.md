<!-- markdownlint-disable -->

<a href="../src/charm.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `charm.py`
SAML Integrator Charm service. 

**Global Variables**
---------------
- **RELATION_NAME**


---

## <kbd>class</kbd> `SamlIntegratorOperatorCharm`
Charm for SAML Integrator. 

<a href="../src/charm.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(*args)
```

Construct. 



**Args:**
 
 - <b>`args`</b>:  Arguments passed to the CharmBase parent constructor. 


---

#### <kbd>property</kbd> app

Application that this unit is part of. 

---

#### <kbd>property</kbd> charm_dir

Root directory of the charm as it is running. 

---

#### <kbd>property</kbd> config

A mapping containing the charm's config and current values. 

---

#### <kbd>property</kbd> meta

Metadata of this charm. 

---

#### <kbd>property</kbd> model

Shortcut for more simple access the model. 

---

#### <kbd>property</kbd> unit

Unit that this execution is responsible for. 



---

<a href="../src/charm.py#L75"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_saml_data`

```python
get_saml_data() → SamlRelationData
```

Get relation data. 



**Returns:**
  SamlRelationData containing the IdP details. 


