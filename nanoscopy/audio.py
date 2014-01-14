import pyaudio
import struct
from threading import Thread, Condition
import time
from logging import thread
import socket
from FileEsempio import DataFilesLib as dfl

CHUNK = 2**12
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

class AudioReader(Thread):

    def __init__(self, raw = False, remote = False, dataFile = None, host = 'localhost', port = 9999):
        Thread.__init__(self)
        self.active = False
        self.listeners = []
        self.condition = Condition()
        self.quit = False
        self.raw = raw
        self.remote = remote
        self.host = host
        self.port = port
        self.simul = dataFile is not None
        print self.simul
        if self.simul:
            self.simulFile = dfl.qrtaiFile(dataFile)
           # self.CHUNK = int(self.simulFile.rate/8)
           # self.RATE = float(self.simulFile.rate)
            self.RATE = 40000
            self.CHUNK = 2500
            self.simulCount = 0
        else:
            self.simulFile = None
            self.CHUNK = CHUNK
            self.FORMAT = FORMAT
            self.CHANNELS = CHANNELS
            self.RATE = RATE
        
    def pause(self):
        self.active = False
    
    def play(self):
        self.active = True
        #self.condition.acquire()
        #self.condition.notify()
        #self.condition.release()
    
    def stop(self):
        if not self.active:
            self.play()
        self.active = False
        self.quit = True

    def readData(self):
        
        #self.condition.acquire()
        #self.condition.wait()
        #self.condition.release()
        print 'real'
        
        self.stream = pyaudio.PyAudio().open(format=self.FORMAT, 
            channels=self.CHANNELS, 
            rate=self.RATE, 
            input=True, 
            frames_per_buffer=self.CHUNK)
        
        while self.active:
            data = self.stream.read(self.CHUNK)
            if not self.raw:            
                count = len(data) / 2
                fmt = "%dh" % (count)
                shorts = struct.unpack(fmt, data)
            else:
                shorts = data
            for l in self.listeners:
                l(shorts)
                
        self.stream.close()

    def readRemoteData(self):
        
        self.condition.acquire()
        self.condition.wait()
        self.condition.release()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        buf = []

        while self.active:
            data = self.socket.recv((self.CHUNK*2-len(buf))*2)
            if not self.raw:            
                count = len(data) / 2
                fmt = "%dh" % (count)
                shorts = struct.unpack(fmt, data)
                buf.extend(shorts)
                if len(buf)>=self.CHUNK*2:
                    for l in self.listeners:
                        l(buf)
                    buf=[]
            else:
                for l in self.listeners:
                    l(data)
                
        self.socket.close()
        
    def readSimulatedData(self):
        
        print 'simulate'
        #self.condition.acquire()
        #self.condition.wait()
        #self.condition.release()
        print 'simulate'
        
        while self.active:
            if self.simulCount+self.CHUNK > len(self.simulFile.data):
                self.simulCount = 0
            data = self.simulFile.data[self.simulCount:self.simulCount+self.CHUNK]
            self.simulCount += self.CHUNK
                
            for l in self.listeners:
                l(data)
        

    def run(self):
        print self.simul
        while not self.quit:
            if not self.remote and not self.simul:               
                self.readData()
            elif self.remote and not self.simul:
                self.readRemoteData()
            elif self.simul:
                print 'pippo'
                self.readSimulatedData()
            
            
            