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
import os


ar = AudioReader(dataFile = 'nanoscopy'+os.sep+'FileEsempio'+os.sep+'data_25e-6_20sec_2')

r = range(ar.CHUNK*2)
rs = range(ar.CHUNKs*2)

NI = kcu.buildNI(float(ar.CHUNK)/ar.RATE,1.0/ar.RATE) # Range frequenze creato apposta per le impostazioni della scheda sonora
NIs = kcu.buildNI(float(ar.CHUNKs)/ar.RATEs,1.0/ar.RATEs) # Range frequenze creato apposta per le impostazioni della scheda sonora

bP = 35*(10**-6) # Valori di default per prova

LP = 350*(10**-6) # Valori di default per prova

port = 8888


class SocketHandler(websocket.WebSocketHandler):
    
    def work_on_d(self, data, dad):
        
        mioNI = NI if dad=='real' else NIs
        mioR = r if dad=='real' else rs
        
        try:
            Pw,Pdc,niR,Q = kcu.GETparams(mioNI[self.xmin:self.xmax:self.downsampling],data[self.xmin:self.xmax:self.downsampling])
        
            data2 = kcu.PRF(mioNI[self.xmin:self.xmax:self.downsampling],Pw,Pdc,niR,Q)
        
            kcCalc = kcu.GETk(self.ro,self.b,self.L,Q,niR,kcu.etaAria)

        except Exception, e:
         #   print e
            data2 = np.zeros(len(data))
            kcCalc = 'Nan'
            niR = 'Nan'
            Q = 'Nan'
        
        return Q,niR,kcCalc,[list(a) for a in zip(mioR[self.xmin:self.xmax:self.downsampling],data2)]
    
    def data_listener(self, data):
        
        if not self.working:
            self.working = True
            data = data[0::2]
            if self.fft:
                data = abs(fft(data))**2
                self.dataSum += data
                self.acqCount += 1
                self.drawFFT = False
                data = self.dataSum/self.acqCount
                data = data[0:len(data)/2]
                if (self.acqCount >= self.acqCountMax) and (self.xmin==0 and self.xmax==ar.CHUNK*2):
                    self.acqCount = 0
                    self.dataSum = np.zeros(ar.CHUNK)+0.0001
                    self.drawFFT = True
    
            if (self.xmin>0 or self.xmax<ar.CHUNK*2) and self.acqCount >= self.acqCountMax:
                self.d2 = []
                self.Q,self.niR,self.kc,self.d2 = self.work_on_d(data,'real')
                self.drawFFT = True
                self.acqCount = 0
                self.dataSum = np.zeros(ar.CHUNK)+0.0001
            
            if self.downsampling > 1:
                data = data[::self.downsampling]
            
            d = [[list(a) for a in zip(r[::self.downsampling],data)]]
            
            if self.d2:
                d.append(self.d2)
            
            message = {'draw': self.drawFFT,'Q': self.Q, 'niR':self.niR,'kc':self.kc,'data':d}
            
            try:  
                self.write_message(message)
            except Exception, e:
                
              #  print e.args
              #  print e.message
                
                return
            self.working = False
            
        else:
            return
        
    def data_listener_sim(self, data):
        
        if not self.working:
            
            self.working = True
            if self.fft:
                data = abs(fft(data))**2
                self.dataSum += data
                self.acqCount += 1
                #print self.acqCount
                #print self.acqCountMax
                #print self.acqCount == self.acqCountMax
                #print self.xmax
                #print ar.CHUNKs
                #print self.xmin
                self.drawFFT = False
                data = self.dataSum/self.acqCount
                data = data[0:len(data)/2]
                if (self.acqCount >= self.acqCountMax) and (self.xmin==0 and self.xmax==ar.CHUNKs*2):
                    self.acqCount = 0
                    self.dataSum = np.zeros(ar.CHUNKs)+0.0001
                    self.drawFFT = True
    
            if (self.xmin>0 or self.xmax<ar.CHUNKs*2) and self.acqCount >= self.acqCountMax:
                self.d2 = []
                self.Q,self.niR,self.kc,self.d2 = self.work_on_d(data,'simulate')
                self.drawFFT = True
                self.acqCount = 0
                self.dataSum = np.zeros(ar.CHUNKs)+0.0001
            
            if self.downsampling > 1:
                data = data[::self.downsampling]
            
            d = [[list(a) for a in zip(rs[::self.downsampling],data)]]
            
            if self.d2:
                d.append(self.d2)
            
            message = {'draw': self.drawFFT,'Q': self.Q, 'niR':self.niR,'kc':self.kc,'data':d}
            
            try:  
                self.write_message(message)
            except Exception, e:
                
              #  print e.args
              #  print e.message
                
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
        self.eta = options['eta']/1e+5
        self.b = options['b']/1e+6
        self.L = options['L']/1e+6
        self.avgT = options['avgT']
        if self.simul != options['simul']:
            self.acqCount = 0
            self.dataSum = []
            if options['simul']:
                ar.listeners.remove(self.data_listener)
                ar.simulListeners.append(self.data_listener_sim)
                self.dataSum = np.zeros(ar.CHUNKs)+0.0001
                self.acqCountMax = ar.RATEs/ar.CHUNKs*self.avgT
                self.xmax = ar.CHUNKs*2
                #print self.xmax
            else:
                ar.simulListeners.remove(self.data_listener_sim)
                ar.listeners.append(self.data_listener)
                self.dataSum = np.zeros(ar.CHUNK)+0.0001
                self.acqCountMax = ar.RATE/ar.CHUNK*self.avgT
                self.xmax = ar.CHUNK*2

        self.simul = options['simul']
        if self.simul:
            self.acqCountMax = ar.RATEs/ar.CHUNKs*self.avgT
        else:
            self.acqCountMax = ar.RATE/ar.CHUNK*self.avgT
            
        if self.xmin == 0 and self.xmax == ar.CHUNKs*2 if self.simul else ar.CHUNK*2:
            self.d2 = []
            self.kc = 0
            self.niR = 0
            self.Q = 0
        #print options
    
    
    def open(self):
        self.working = False
        self.downsampling = 50
        self.fft = False
        self.xmin = 0
        self.xmax = ar.CHUNK*2
        self.ro = kcu.roAria
        self.eta = kcu.etaAria
        self.avgT = 2
        self.acqCountMax = ar.RATE/ar.CHUNK*self.avgT
        self.acqCount = 0
        self.d2 = []
        self.kc = 0
        self.niR = 0
        self.Q = 0
        self.b = bP
        self.L = LP
        self.drawFFT = False
        self.dataSum = np.zeros(ar.CHUNK)
        self.simul = False
        ar.listeners.append(self.data_listener)
        print "WS open"
        
        
    def on_close(self):
        for l in ar.listeners:
            ar.listeners.remove(l)
        for ls in ar.simulListeners:
            ar.simulListeners.remove(ls)
            
        print "WS close"

class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        data = [list(a) for a in zip(r,linspace(-5e+4,5e+12,ar.CHUNK*2))]
        self.render("html/index.html", 
                    title="AFM-Calibrator", 
                    data = data,
                    xmax = ar.CHUNK*2,
                    xmaxS = ar.CHUNKs*2,
                    mRate = ar.RATE/2,
                    mRateS = ar.RATEs/2,
                    avgT = 2,
                    kc = 0,
                    niR = 0,
                    Q = 0,
                    eta = kcu.etaAria*1e+5,
                    ro = kcu.roAria,
                    b=bP*1e+6,
                    L=LP*1e+6)

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
    #print 'Stopping'
    ar.stop()
    #print 'Out AR'
    tornado.ioloop.IOLoop.instance().stop()
    #print 'After ioloop stop'
