# Jupyterlab-Zenodo
A Zenodo extension for JupyterHub

## Installation

This is part of a two-part extension: the lab extension (UI) and the server extension (which interfaces with Zenodo). In order to use this extension, both parts must be enabled. The following instructions should be run in your terminal.

To install the server extension:
```bash
pip install jupyterlab_zenodo
```

To enable the server extension:
```bash
jupyter serverextension enable --py jupyterlab_zenodo
```

To install the lab extension:
```bash
jupyter labextension install @chameleoncloud/jupyterlab_zenodo
```

## Customization
You can add a series of (optional) custom features by adding lines to your `jupyter_notebook_config.py` file.

1. [Create a default Zenodo access token](https://zenodo.org/account/settings/applications/tokens/new/) so that users don't need their own:

```python
c.ZenodoConfig.access_token = '<your token>'
```

2. Set up a post-upload redirect. By setting `<your-url>` below, users will be redirected to that site with an added 'doi' query parameter when they successfully create a new Zenodo upload.

```python
c.ZenodoConfig.upload_redirect_url = '<your-url>'
```

3. Set a default Zenodo community. The below will identify all depositions published with this extension with `<your community>`.

```python
c.ZenodoConfig.community = '<your community>'
```

4. Customize the internal storage database. Information about previous uploads to Zenodo on a user's server will be stored in `<database-location>` in a sqlite database called `<database-name>`. These default to `/work/.zenodo/` and `zenodo.db`, respectively.

```python
c.ZenodoConfig.database_location = '<database-location>'
```
```python
c.ZenodoConfig.database_name = '<database_name>'
```

## Development
To work with the extension without publishing directly to Zenodo, use Zenodo sandbox.
Indicate that you're in a development environment and provide a default sandbox token in `jupyter_notebook_config.py`:

```python
c.ZenodoConfig.dev = True
c.ZenodoConfig.access_token = '<your sandbox token>'
```

## Testing
The server side of this extension comes with a set of integration tests. They can be used as follows:
1. [Create a Zenodo sandbox access token](https://sandbox.zenodo.org/account/settings/applications/tokens/new/)
2. Assign the value TEST_API_TOKEN in `jupyterlab_zenodo/test_init.py` to your access token (as a string)
3. Run `make tests` from the root in your terminal
