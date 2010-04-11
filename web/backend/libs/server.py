import storage, handlers
import tornado.httpserver
import tornado.ioloop
import tornado.web

storage.instance.initialize()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

routes = tornado.web.Application
([
#    (r"/", handlers.MainHandler),
    (r"/", MainHandler),
])


def start():
    http_server = tornado.httpserver.HTTPServer(routes)
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()