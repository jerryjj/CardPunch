import storage, handlers
import tornado.httpserver
import tornado.ioloop
import tornado.web


class wrapper:
    def __init__(self):
        self.uris = tornado.web.Application
        ([
            (r"/", handlers.MainHandler),
        ])
        self.server = tornado.httpserver.HTTPServer(self.uris)
        self.server.listen(8080)

    def start(self):
        tornado.ioloop.IOLoop.instance().start()

instance = wrapper()
