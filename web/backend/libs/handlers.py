import storage
import tornado.web
import time

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
        if t:
            print "Sleeping 2 second, t=%s" % t
            tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 2, lambda: self.wait_for_smth(callback, t-1))
        else:
            callback()

    def on_finish(self):
        print ("inside finish")
        self.write("Long running job complete")
        self.finish()

class exchange(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        # TODO: Use transaction
        entry = storage.midgard.mgdschema.cardpunch_exchange()
        stats_entry = storage.midgard.mgdschema.cardpunch_exchange_statistics()

        stats_entry.fulllat = float(self.get_argument("lat"))
        stats_entry.fulllon = float(self.get_argument("lon"))
        stats_entry.geoaccuracy = self.get_argument("geoaccuracy")
        stats_entry.geoprovider = self.get_argument("geoprovider")
        stats_entry.devicemake = self.get_argument("devicemake")
        stats_entry.devicemodel = self.get_argument("devicemodel")
        stats_entry.devicefirmare = self.get_argument("devicefirmare")

        stats_entry.create()
        if self.stats_entry.id == 0:
            # Bug http://trac.midgard-project.org/ticket/1409
            raise Exception("Hit Midgard bug #1409 when creating stats_entry")

        entry.servertime = int(time.time())
        entry.timedelta = entry.servertime - int(self.get_argument("localtime"))
        entry.vcard = self.get_argument("vcard")
        entry.deviceid = self.get_argument("deviceid")
        entry.lat = stats_entry.fulllat # TODO: round
        entry.lon = stats_entry.fulllon # TODO: round
        entry.initial = bool(self.get_argument("initial"))
        entry.statistics = stats_entry.id

        entry.create()
        if self.entry.id == 0:
            # Bug http://trac.midgard-project.org/ticket/1409
            raise Exception("Hit Midgard bug #1409 when creating entry")

        if entry.initial:
            self.finish()

        # TODO: Register async method to poll for the counterpart every second
        self.finish()
