import json

from notebook.base.handlers import APIHandler


class ZenodoBaseHandler(APIHandler):
    """
    A base handler for the Zenodo extension
    """

    def return_error(self, error_message):
        """Set 400 status and error message, return from request

        Parameters
        ----------
        error_message : string
            Message to be returned as reason for error

        Returns
        -------
        none
        """

        info = {
            'status':'failure',
            'message': error_message,
            'doi' : None
        }
        self.set_status(400)
        self.write(json.dumps(info))
        self.finish()
        return

