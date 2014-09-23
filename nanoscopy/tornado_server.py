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
import sys

version = "1.0"

filePath = ""

bP = 35*(10**-6) # Valori di default per prova
LP = 350*(10**-6) # Valori di default per prova

port = 8888

class SocketHandler(websocket.WebSocketHandler):
    
    def work_on_d(self, data, dad):
        '''
        This function fit the data contained in the "data" variables and then calculates the cantilever elastic constant, It is called by "data_listener"
        
        '''
        global r, rs
        global NI, NIs

        mioNI = NI if dad=='real' else NIs
        mioR = r if dad=='real' else rs
        
        print 'fit'

        try:
            #print 'Starting FIT ', self.fitmin, ' ', self.fitmax
            Pw,Pdc,niR,Q = kcu.GETparams(mioNI[self.fitmin:self.fitmax:self.downsampling],data[self.fitmin:self.fitmax:self.downsampling])
        
            data2 = kcu.PRF(mioNI[self.fitmin:self.fitmax:self.downsampling],Pw,Pdc,niR,Q)
       
            kcCalc = kcu.GETk(self.ro,self.b,self.L,Q,niR,kcu.etaAria)

        except Exception, e:
         #   print e
            data2 = np.zeros(len(data))
            kcCalc = 'Nan'
            niR = 'Nan'
            Q = 'Nan'
        
        return Q,niR,kcCalc,[list(a) for a in zip(mioR[self.fitmin:self.fitmax:self.downsampling],data2)]
    
    '''
    def data_listener(self, data):
        global ar
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
                    self.dataSum = np.zeros(ar.CHUNK/2)+0.0001
                    self.drawFFT = True
    
            if (self.xmin>0 or self.xmax<ar.CHUNK*2) and self.acqCount >= self.acqCountMax:
                self.d2 = []
                self.Q,self.niR,self.kc,self.d2 = self.work_on_d(data,'real') # here the server calls the function that performs the data fitting and also caluclates the elastic constant k
                self.drawFFT = True
                self.acqCount = 0
                self.dataSum = np.zeros(ar.CHUNK/2)+0.0001
            
            if self.downsampling > 1:
                data = data[::self.downsampling]
            
            d = [[list(a) for a in zip(r[::self.downsampling],data)]]
            
            if self.d2:
                d.append(self.d2)
            
            if self.autoScale:
                xdatamin = 0
                xdatamax = len(data)/2
            else:
                xdatamin = self.xmin/2
                xdatamax = xdatamin + (self.xmax - self.xmin)/2
                
            message = {'draw': self.drawFFT,'Q': self.Q, 'niR':self.niR,'kc':self.kc,'data':d, 'xmin':xdatamin, 'xmax':xdatamax}
            
            try:  
                self.write_message(message)
            except Exception, e:
                
              #  print e..gs
              #  print e.message
                
                return
            self.working = False
            
        else:
            return
    '''


    def data_listener(self, data):
        global ar
        global r, rs

        if not self.working:
            
            self.working = True
            if self.fft:
                data = abs(fft(data))**2
                self.dataSum += data
                self.acqCount += 1
                self.drawFFT = False
                data = self.dataSum/self.acqCount
                data = data[0:len(data)/2]
                if (self.acqCount >= self.acqCountMax) and (self.xmin==0 and self.xmax==ar.CHUNK*2):
                    #print 'RESETTING to zero'
                    self.acqCount = 0
                    self.dataSum = np.zeros(ar.CHUNK*ar.CHANNELS)+0.0001
                    self.drawFFT = True
                print(self.acqCount),
                sys.stdout.flush()

            if (self.xmin>0 or self.xmax<ar.CHUNK*ar.CHANNELS) and (self.acqCount >= self.acqCountMax):
                print 'Plotting FFT'
                self.d2 = []
                if self.fit:
                    self.Q,self.niR,self.kc,self.d2 = self.work_on_d(data,'real')
                self.drawFFT = True
                self.acqCount = 0
                self.dataSum = np.zeros(ar.CHUNK*ar.CHANNELS)+0.0001
            
            if self.downsampling > 1:
                data = data[::self.downsampling]
            
            d = [[list(a) for a in zip(r[::self.downsampling],data)]]
            
            if self.d2:
                d.append(self.d2)
                
            if self.autoScale and not self.fit:
                xdatamin = 0
                xdatamax = len(data) * self.downsampling
                ydatamin = min(data)
                ydatamax = max(data)
            else:
                if (self.fft):
                    xdatamin = self.xmin
                    xdatamax = self.xmax
                else:
                    xdatamin = self.xmin/2
                    range = (self.xmax - self.xmin)/2
                    xdatamax = xdatamin + range
                ydatamin = self.ymin
                ydatamax = self.ymax
#
            message = {'draw': self.drawFFT,'Q': self.Q, 'niR':self.niR,'kc':self.kc,'data':d, 'xmin':xdatamin, 'xmax':xdatamax, 'ymin':ydatamin, 'ymax':ydatamax}
            
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
        global ar
        global r, rs

        if not self.working:
            
            self.working = True
            if self.fft:
                data = abs(fft(data))**2
                self.dataSum += data
                self.acqCount += 1
                self.drawFFT = False
                data = self.dataSum/self.acqCount
                data = data[0:len(data)/2]
                if (self.acqCount >= self.acqCountMax) and (self.xmin==0 and self.xmax==ar.CHUNKs*2):
                    #print 'RESETTING to zero'
                    self.acqCount = 0
                    self.dataSum = np.zeros(ar.CHUNKs)+0.0001
                    self.drawFFT = True
                print(self.acqCount),
                sys.stdout.flush()

            if (self.xmin>0 or self.xmax<ar.CHUNKs*2) and (self.acqCount >= self.acqCountMax):
                print 'Plotting FFT'
                self.d2 = []
                if self.fit:
                    self.Q,self.niR,self.kc,self.d2 = self.work_on_d(data,'simulate')
                self.drawFFT = True
                self.acqCount = 0
                self.dataSum = np.zeros(ar.CHUNKs)+0.0001
            
            if self.downsampling > 1:
                data = data[::self.downsampling]
            
            d = [[list(a) for a in zip(rs[::self.downsampling],data)]]
            
            if self.d2:
                d.append(self.d2)
                
            if self.autoScale and not self.fit:
                xdatamin = 0
                xdatamax = len(data) * self.downsampling
                ydatamin = min(data)
                ydatamax = max(data)
            else:
                if (self.fft):
                    xdatamin = self.xmin
                    xdatamax = self.xmax
                else:
                    xdatamin = self.xmin/2
                    range = (self.xmax - self.xmin)/2
                    xdatamax = xdatamin + range
                ydatamin = self.ymin
                ydatamax = self.ymax
#
            message = {'draw': self.drawFFT,'Q': self.Q, 'niR':self.niR,'kc':self.kc,'data':d, 'xmin':xdatamin, 'xmax':xdatamax, 'ymin':ydatamin, 'ymax':ydatamax}
            
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
        global ar
        if message == "fit":
            self.fit()
            return
        else:
            self.setParameters(message)


    def open(self):
        global ar

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
        self.dataSum = np.zeros(ar.CHUNK/2)
        self.simul = False
        self.play = 0
        self.pause = 1
        self.autoScale = False

    def setParameters(self, message):
        global ar
        options = json.loads(message)
        self.autoScale = options['autoScale']
        self.fit = options['fit']
        self.fitmin = options['fitmin']
        self.fitmax = options['fitmax']
        self.downsampling = options['downsampling']
        self.fft = options['fft']
        if self.fft:
            if self.fit:
                self.fitmin = options['fitmin']
                self.fitmax = options['fitmax']
            else:
                self.xmin = options['xmin'] / 2
                self.xmax = options['xmax'] / 2
        else:
            self.xmin = options['xmin']
            self.xmax = options['xmax']
        self.ymin = options['ymin']
        self.ymax = options['ymax']
        self.ro = options['ro']
        self.eta = options['eta']/1e+5
        self.b = options['b']/1e+6
        self.L = options['L']/1e+6
        self.avgT = options['avgT']
        if self.simul != options['simul']:
            self.acqCount = 0
            self.dataSum = []
            self.xmin = 0
            if options['simul']:
                del ar.listeners[:]
                ar.simulListeners.append(self.data_listener_sim)
                self.dataSum = np.zeros(ar.CHUNKs)+0.0001
                self.acqCountMax = ar.RATEs/ar.CHUNKs*self.avgT
                self.xmax = ar.CHUNKs*2
            else:
                del ar.simulListeners[:]
                ar.listeners.append(self.data_listener)
                self.dataSum = np.zeros(ar.CHUNK*ar.CHANNELS)+0.0001
                
                print np.shape(self.dataSum)
                
                self.acqCountMax = ar.RATE/ar.CHUNK*self.avgT
                self.xmax = ar.CHUNK*2

        self.simul = options['simul']
        if self.simul:
            self.acqCountMax = ar.RATEs/ar.CHUNKs*self.avgT
            if ar.simulListeners == [] and ar.listeners == []:
                ar.simulListeners.append(self.data_listener_sim)
                self.dataSum = np.zeros(ar.CHUNKs)+0.0001
                self.acqCountMax = ar.RATEs/ar.CHUNKs*self.avgT
                self.xmax = ar.CHUNKs*2
        else:
            self.acqCountMax = ar.RATE/ar.CHUNK*self.avgT
            if ar.simulListeners == [] and ar.listeners == []:
                ar.listeners.append(self.data_listener)
                self.dataSum = np.zeros(ar.CHUNK*ar.CHANNELS)+0.0001
                self.acqCountMax = ar.RATE/ar.CHUNK*self.avgT
                self.xmax = ar.CHUNK*2
            
        if self.xmin == 0 and self.xmax == ar.CHUNKs*2 if self.simul else ar.CHUNK*2:
            self.d2 = []
            self.kc = 0
            self.niR = 0
            self.Q = 0
        #print 'Set options fitmin/fitmax: ', self.fitmin, ' ', self.fitmax

    def on_close(self):
        for l in ar.listeners:
            ar.listeners.remove(l)
        for ls in ar.simulListeners:
            ar.simulListeners.remove(ls)
        self.play = 1
        self.pause = 0


class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        global ar
        data = [list(a) for a in zip(r,linspace(-5e+4,5e+12,ar.CHUNK*2))]
        data = []
        self.render("html/index.html", 
                    title="AFM-Calibrator V" + version, 
                    data = data,
                    xmax = 1,
                    ymax = 1,
                    xmaxS = 1,
                    ymaxS = 1,
                    mRate = 100,
                    mRateS = 100,
                    play = 1,
                    pause = 0,
                    autoScale = 0,
                    fit = 0,
                    simul = 0,
                    fft = 0,
                    avgT = 2,
                    kc = 0,
                    niR = 0,
                    Q = 0,
                    eta = kcu.etaAria*1e+5,
                    ro = kcu.roAria,
                    b=bP*1e+6,
                    L=LP*1e+6)


def start():
    global r, rs
    global ar
    global NI, NIs
    
    ar = AudioReader(dataFile = filePath+'nanoscopy'+os.sep+'FileEsempio'+os.sep+'data_25e-6_20sec_2')

    r = range(ar.CHUNK*2)
    rs = range(ar.CHUNKs*2)

    NI = kcu.buildNI(float(ar.CHUNK)/ar.RATE,1.0/ar.RATE) # Range frequenze creato apposta per le impostazioni della scheda sonora
                                                          # Frequency range created especially for the settings of the sound card
    NIs = kcu.buildNI(float(ar.CHUNKs)/ar.RATEs,1.0/ar.RATEs) # Range frequenze creato apposta per le impostazioni della scheda sonora
                                                              # Frequency range created especially for the settings of the sound card

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
    global ar
    ar.stop()
    tornado.ioloop.IOLoop.instance().stop()
