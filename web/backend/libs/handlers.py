import storage
import tornado.web

storage.instance.initialize()

class hello(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class asyncwait(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.wait_for_smth(callback=self.async_callback(self.on_finish))
        print("Exiting from async.")
        return

    def wait_for_smth(self, callback, t=10):
        import time
        if t:
            print "Sleeping 2 second, t=%s" % t
            tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 2, lambda: self.wait_for_smth(callback, t-1))
        else:
            callback()

    def on_finish(self):
        print ("inside finish")
        self.write("Long running job complete")
        self.finish()

