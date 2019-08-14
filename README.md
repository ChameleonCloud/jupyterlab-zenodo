# Zenodo extension for JupyterHub

## Customization

Create a default Zenodo access token so that users do not need their own
To set this, customize your `jupyter_notebook_config.py` file:

```python
c.ZenodoConfig.access_token = '<your token>'
```

For testing, use Zenodo sandbox. 
Indicate that you're in a development environment and provide a default sandbox token in the same file:

```python
c.ZenodoConfig.dev = True
c.ZenodoConfig.dev_access_token = '<your sandbox token>'
```

