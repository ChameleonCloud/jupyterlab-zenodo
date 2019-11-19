# jupyterlab-zenodo

A [Zenodo](https://zenodo.org) extension for JupyterLab.

## Installation

This is part of a two-part extension: the JupyterLab extension (UI) and the Notebook server extension (which interfaces with Zenodo). In order to use this extension, both parts must be enabled. The following instructions should be run in your terminal.

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

### `ZenodoConfig.access_token`

You can [create a default Zenodo access token](https://zenodo.org/account/settings/applications/tokens/new/) so that users don't need their own. This token will be used for any user of the Jupyter Notebook, so it should probably be created under a dedicated account for your deployment.

```python
c.ZenodoConfig.access_token = '<your token>'
```

### `ZenodoConfig.upload_redirect_url`

If you want to perform additional processing on the upload after it is published to Zenodo, you can specify a post-create redirect location. By setting `<your-url>` below, users will be redirected to that site (with an added "doi" query parameter for the created Zenodo artifact) when the upload is successfully published.

```python
c.ZenodoConfig.upload_redirect_url = '<your-url>'
```

### `ZenodoConfig.update_redirect_url`

Similar to `upload_redirect_url`, this allows you to redirect users to a custom URL after a new version of an existing artifact is successfully published. A "doi" and "previous_doi" query parameter will be added to the URL for you.

```python
c.ZenodoConfig.update_redirect_url = '<your-url>'
```

### `ZenodoConfig.community`

Set a default [Zenodo community](https://zenodo.org/communities/). All depositions published with this extension will automatically be associated with the community `<your community>`.

```python
c.ZenodoConfig.community = '<your community>'
```

### `ZenodoConfig.database_location`

Information about previous uploads to Zenodo on a user's server will be stored in `<database-location>` in a SQLite database. This defaults to `/work/.zenodo/`.

```python
c.ZenodoConfig.database_location = '<database-location>'
```

### `ZenodoConfig.database_name`

Set a custom SQLite3 database name. This defaults to `zenodo.db`.

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
2. Run `ZENODO_ACCESS_TOKEN=<token> make tests` from the root in your terminal, using the sandbox access token as `<token>`.
