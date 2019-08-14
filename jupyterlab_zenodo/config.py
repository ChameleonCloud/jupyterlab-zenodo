""" JupyterLab Zenodo : uploads to Zenodo """

from traitlets import Bool, Unicode
from traitlets.config import Configurable

class ZenodoConfig(Configurable):
    """
    A Configurable that declares the configuration options
    for the LatexHandler.
    """
    access_token = Unicode(config=True,
        help='The default Zenodo access token to provide.')
    dev_access_token = Unicode(config=True,
        help='The default Zenodo development access token to provide.')
    dev = Bool(default_value = False, config = True,
        help='Set this to True to publish to Zenodo sandbox while testing')
    upload_redirect_url = Unicode(config=True,
        help='URL to redirect to after upload. Doi will be added as a query parameter.')

    #TEST_API_TOKEN '***REMOVED***'
    #API_TOKEN '***REMOVED***'
