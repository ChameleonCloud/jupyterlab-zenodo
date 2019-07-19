from tornado.testing import AsyncTestCase, gen_test
from tornado.web import Application
from tornado.httpserver import HTTPRequest
from unittest.mock import Mock

from upload import ZenodoUploadHandler

#application = tornado.web.Application([
#    (r"/zenodo/upload", ZenodoUploadHandler)
#])
# z = ZenodoUploadHandler(tornado.web.Application, tornado.httputil.HTTPServerRequest)
#z = ZenodoUploadHandler(application, tornado.httputil.HTTPServerRequest)

#z.zip_dir("tests","temp.zip")
#metadata = z.assemble_metadata("MyTitle",["me","you"], "a thing")
#print(metadata)

class TestZenodoUploadHandler(AsyncTestCase):
    @gen_test
        def test_test():
        print("\n\n\n\nHELLO I AM A TEST\n\n\n\n")
        mock_app = Mock(spec=Application)
    payload_request = HTTPRequest(
        method='GET', uri = '/test', headers=None, body=None
    )
    handler = ZenodoUploadHandler(mock_app, payload_request)
    print(handler.assemble_metadata("Title",["me"],"nope"))
    #with self.assertRaises(ValueError):
        #return handler.get()

print("hi")
test_test()

