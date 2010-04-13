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
        print "after self.finish()"

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

        # Register async method to poll for the counterpart every second
        tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 1, lambda:  self.look_for_counterpart_async(entry, 1, 2))

    def look_for_counterpart_async(self, my_entry, iteration, fuzz):
        print "DEBUG: handlers.exchange.look_for_counterpart_async() called for entry #%d, iteration %d" & (my_entry.id, iteration)

        results = []
        
        # TODO: Query for counterpart
        qb = storage.midgard.query_builder('cardpunch_exchange')
        # These are rounded to correct accuracy on before saving so that there is no need for fuzzy logic at this moment
        qb.add_constraint('lat', '=', my_entry.lat)
        qb.add_constraint('lon', '=', my_entry.lon)
        # Allow in total fuzz*2+1 seconds of window
        qb.add_constraint('servertime', '>=', my_entry.servertime - fuzz)
        qb.add_constraint('servertime', '<=', my_entry.servertime + fuzz)

        
        if len(results) == 1:
            # Found match, link the two and reply to client
            eir_entry = results[0]
            eir_entry.counterpart = my_entry.id
            my_entry.counterpart = eir_entry.id
            my_entry.update()
            eir_entry.update()
            self.write("<reply><status>1</status><vcard>%s</vcard></reply>" % eir_entry.vcard)
            return self.finish()

        if len(results) > 1:
            if fuzz > 0:
                # We have fuzz left, narrow it down and recurse
                return self.look_for_counterpart_async(my_entry, iteration+1, fuzz-1)
            # Still multiple results. Tell the client to try again
            self.write("<reply><status>0</status><message>%s</message></reply>" % "Please try again")
            return self.finish()
        
        if (    len(results) == 0
            and (   iteration > 10
                 or int(time.time()) - my_entry.servertime > 5)
            ):
            # No results and ran out of time/iterations. Tell the client to try again
            self.write("<reply><status>0</status><message>%s</message></reply>" % "Please try again")
            return self.finish()

        # No valid replies and no timeouts yet, try again in 1sec
        tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 1, lambda:  self.look_for_counterpart_async(my_entry, iteration+1, fuzz))

