#!/usr/bin/env python2.5

# Setup our import paths
import os, sys
local_module_dir = os.path.join(os.path.dirname(sys.argv[0]),  'libs')
if os.path.isdir(local_module_dir):                                       
    sys.path.append(local_module_dir)

from libs import handlers

import tornado.httpserver
import tornado.ioloop
import tornado.web

application = tornado.web.Application([
    (r"/", handlers.hello),
    (r"/async", handlers.asyncwait),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

