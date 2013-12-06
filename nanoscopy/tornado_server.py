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

bP = 35*(10**-6) # Valori di default per prova

LP = 350*(10**-6) # Valori di default per prova

port = 8888


class SocketHandler(websocket.WebSocketHandler):
    
    def work_on_d(self, data):
        
        try:
            Pw,Pdc,niR,Q = kcu.GETparams(NI[self.xmin:self.xmax:self.downsampling],data[self.xmin:self.xmax:self.downsampling])
        
            data2 = kcu.PRF(NI[self.xmin:self.xmax:self.downsampling],Pw,Pdc,niR,Q)
        
            kcCalc = kcu.GETk(self.ro,self.b,self.L,Q,niR,kcu.etaAria)

        except:
            data2 = np.zeros(len(data))
            kcCalc = 'Nan'
            niR = 'Nan'
            Q = 'Nan'
        
        return Q,niR,kcCalc,[list(a) for a in zip(r[self.xmin:self.xmax:self.downsampling],data2)]
    
    def data_listener(self, data):
        
        if not self.working:
            self.working = True
            if self.fft:
                data = abs(fft(data))**2
                self.dataSum += data
                self.acqCount += 1
                self.drawFFT = False
                data = self.dataSum/self.acqCount
                if (self.acqCount == self.acqCountMax) and (self.xmin==0 and self.xmax==CHUNK*2):
                    self.acqCount = 0
                    self.dataSum = np.zeros(CHUNK*2)+0.0001
                    self.drawFFT = True
    
            if (self.xmin>0 or self.xmax<CHUNK*2) and self.acqCount == self.acqCountMax:
                self.d2 = []
                self.Q,self.niR,self.kc,self.d2 = self.work_on_d(data)
                self.drawFFT = True
                self.acqCount = 0
                self.dataSum = np.zeros(CHUNK*2)+0.0001
            
            if self.downsampling > 1:
                data = data[::self.downsampling]
            
            d = [[list(a) for a in zip(r[::self.downsampling],data)]]
            
            if self.d2:
                d.append(self.d2)
            
            message = {'draw': self.drawFFT,'Q': self.Q, 'niR':self.niR,'kc':self.kc,'data':d}
            
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
        self.ro = options['ro']
        self.eta = options['eta']
        self.b = options['b']
        self.L = options['L']
        if self.xmin == 0 and self.xmax == CHUNK*2:
            self.d2 = []
            self.kc = 0
            self.niR = 0
            self.Q = 0
        print options
    
    
    def open(self):
        ar.listeners.append(self.data_listener)
        self.working = False
        self.downsampling = 50
        self.fft = False
        self.xmin = 0
        self.xmax = CHUNK*2
        self.ro = kcu.roAria
        self.eta = kcu.etaAria
        self.acqCountMax = 50
        self.acqCount = 0
        self.d2 = []
        self.kc = 0
        self.niR = 0
        self.Q = 0
        self.b = bP
        self.L = LP
        self.drawFFT = False
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
                    niR = 0,
                    Q = 0,
                    eta = kcu.etaAria,
                    ro = kcu.roAria,
                    b=bP,
                    L=LP)

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
