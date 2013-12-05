import tornado.ioloop
import tornado.web
import tornado
from tornado.web import StaticFileHandler
from audio import AudioReader, CHUNK, RATE
from tornado import websocket
from numpy import linspace, abs
import numpy as np
from numpy.fft import fft
import json
import kCalcUtils as kcu


ar = AudioReader()

r = range(CHUNK*2)

NI = kcu.buildNI(float(CHUNK*2)/RATE,1.0/RATE) # Range frequenze creato apposta per le impostazioni della scheda sonora

b = 35*(10**-6) # Valori di default per prova

L = 350*(10**-6) # Valori di default per prova

port = 8888


class SocketHandler(websocket.WebSocketHandler):
    
    def work_on_d(self, data):
        
        try:
            Pw,Pdc,niR,Q = kcu.GETparams(NI[self.xmin:self.xmax:self.downsampling],data[self.xmin:self.xmax:self.downsampling])
        
            data2 = kcu.PRF(NI[self.xmin:self.xmax:self.downsampling],Pw,Pdc,niR,Q)
        
            kcCalc = kcu.GETk(kcu.roAria,b,L,Q,niR,kcu.etaAria)
            
        except:
            data2 = np.zeros(len(data))
            kcCalc = 0
            niR = NI[self.xmin]
        
        return niR,kcCalc,[list(a) for a in zip(r[self.xmin:self.xmax:self.downsampling],data2)]
    
    def data_listener(self, data):
        
        if not self.working:
            self.working = True
            if self.fft:
                if self.acqCount == self.acqCountMax:
                    self.acqCount = 0
                    self.dataSum = np.zeros(CHUNK*2)+0.0001
                data = abs(fft(data))**2
                self.dataSum += data
                self.acqCount += 1
                data = self.dataSum/self.acqCount
    
            if (self.xmin>0 or self.xmax<CHUNK*2) and self.acqCount == self.acqCountMax:
                self.d2 = []
                self.niR,self.kc,self.d2 = self.work_on_d(data)
                self.acqCount = 0
                self.dataSum = np.zeros(CHUNK*2)+0.0001
            
            if self.downsampling > 1:
                data = data[::self.downsampling]
            
            d = [[list(a) for a in zip(r[::self.downsampling],data)]]
            
            if self.d2:
                d.append(self.d2)
            
            message = {'niR':self.niR,'kc':self.kc,'data':d}
            
            try:  
                self.write_message(message)
            except Exception, e:
                
                print e.args
                print e.message
                
                return
            self.working = False
            
        else:
            return


    def on_message(self, message):
        options = json.loads(message)
        self.downsampling = options['downsampling']
        self.fft = options['fft']
        self.xmin = options['xmin']
        self.xmax = options['xmax']
        if self.xmin == 0 and self.xmax == CHUNK*2:
            self.d2 = []
            self.kc = 0
            self.niR = 0
        print options
    
    
    def open(self):
        ar.listeners.append(self.data_listener)
        self.working = False
        self.downsampling = 10
        self.fft = False
        self.xmin = 0
        self.xmax = CHUNK*2
        self.acqCountMax = 100
        self.acqCount = 0
        self.d2 = []
        self.kc = 0
        self.niR = 0
        self.dataSum = np.zeros(CHUNK*2)
        print "WS open"
        
    def on_close(self):
        ar.listeners.remove(self.data_listener)
        print "WS close"

class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        data = [list(a) for a in zip(r,linspace(-5e+4,5e+12,CHUNK*2))]
        self.render("html/index.html", 
                    title="k Web Calibrator", 
                    data = data,
                    xmax = CHUNK*2,
                    kc = 0,
                    niR = 0)

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
