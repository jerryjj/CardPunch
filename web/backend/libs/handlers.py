import storage
import tornado.web

storage.instance.initialize()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")
