import tornado.ioloop
import tornado.web
from tornado.web import StaticFileHandler
from audio import AudioReader, CHUNK
from tornado import websocket
from numpy import linspace, abs
from numpy.fft import fft
import json


ar = AudioReader()

r = range(CHUNK*2)

port = 8888

class SocketHandler(websocket.WebSocketHandler):
    
    def work_on_d(self, data):
        d2 = [d*2 for d in data[self.xmin:self.xmax:self.downsampling]]
        return [list(a) for a in zip(r[self.xmin:self.xmax:self.downsampling],d2)]
    
    def data_listener(self, data):
        
        d2 = []
        
        if self.fft:
            data = abs(fft(data))

        if self.xmin>0 or self.xmax<CHUNK*2:
            d2 = self.work_on_d(data)
        
        if self.downsampling > 1:
            data = data[::self.downsampling]
        
        d = [[list(a) for a in zip(r[::self.downsampling],data)]]
        
        if d2:
            d.append(d2)
        
        self.write_message(str(d))
    
    def on_message(self, message):
        options = json.loads(message)
        self.downsampling = options['downsampling']
        self.fft = options['fft']
        self.xmin = options['xmin']
        self.xmax = options['xmax']
        print options
    
    def open(self):
        ar.listeners.append(self.data_listener)
        self.downsampling = 1
        self.fft = False
        self.xmin = 0
        self.xmax = CHUNK*2
        print "WS open"
        
    def on_close(self):
        ar.listeners.remove(self.data_listener)
        print "WS close"

class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        data = [list(a) for a in zip(r,linspace(-33000,33000,CHUNK*2))]
        self.render("html/index.html", 
                    title="", 
                    data = data,
                    xmax = CHUNK*2)

def start():
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r'/ws', SocketHandler),
        (r"/static/(.*)", StaticFileHandler, {'path':'nanoscopy/static'})
        ])
    application.listen(port)
    ar.start()
    ar.play()
    tornado.ioloop.IOLoop.instance().start()
    
def stop():
    ar.stop()
    tornado.ioloop.IOLoop.instance().stop()
   