<!-- markdownlint-disable -->

<a href="../src/charm_state.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `charm_state.py`
Module defining the CharmState class which represents the state of the SAML Integrator charm. 

**Global Variables**
---------------
- **KNOWN_CHARM_CONFIG**


---

## <kbd>class</kbd> `CharmConfigInvalidError`
Exception raised when a charm configuration is found to be invalid. 

Attrs:  msg (str): Explanation of the error. 

<a href="../src/charm_state.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(msg: str)
```

Initialize a new instance of the CharmConfigInvalidError exception. 



**Args:**
 
 - <b>`msg`</b> (str):  Explanation of the error. 





---

## <kbd>class</kbd> `CharmState`
Represents the state of the SAML Integrator charm. 

Attrs:  entity_id: Entity ID for SAML.  fingerprint: fingerprint to validate the signing certificate against.  metadata_url: URL for the SAML metadata. 

<a href="../src/charm_state.py#L60"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(saml_integrator_config: SamlIntegratorConfig)
```

Initialize a new instance of the CharmState class. 



**Args:**
 
 - <b>`saml_integrator_config`</b>:  SAML Integrator configuration. 


---

#### <kbd>property</kbd> entity_id

Return entity_id config. 



**Returns:**
 
 - <b>`str`</b>:  entity_id config. 

---

#### <kbd>property</kbd> fingerprint

Return certificate config. 



**Returns:**
 
 - <b>`str`</b>:  certificate config. 

---

#### <kbd>property</kbd> metadata_url

Return metadata_url config. 



**Returns:**
 
 - <b>`str`</b>:  metadata_url config. 



---

<a href="../src/charm_state.py#L95"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `from_charm`

```python
from_charm(charm: 'CharmBase') → CharmState
```

Initialize a new instance of the CharmState class from the associated charm. 



**Args:**
 
 - <b>`charm`</b>:  The charm instance associated with this state. 

Return: The CharmState instance created by the provided charm. 



**Raises:**
 
 - <b>`CharmConfigInvalidError`</b>:  if the charm configuration is invalid. 


---

## <kbd>class</kbd> `SamlIntegratorConfig`
Represent charm builtin configuration values. 

Attrs:  entity_id: Entity ID.  fingerprint: fingerprint to validate the signing certificate against.  metadata_url: Metadata URL. 





