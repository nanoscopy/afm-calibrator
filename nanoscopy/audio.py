import pyaudio
import struct
from threading import Thread, Condition
import time
from logging import thread
import socket
from FileEsempio import DataFilesLib as dfl

divC = 1

CHUNK = 2**12
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

class AudioReader(Thread):

    def __init__(self, raw = False, remote = False, dataFile = None, host = 'localhost', port = 9999, chunk = CHUNK, rate = RATE, chunkS = 2500, rateS = 40000):
        Thread.__init__(self)
        self.active = False
        self.listeners = []
        self.simulListeners = []
        self.condition = Condition()
        self.quit = False
        self.raw = raw
        self.remote = remote
        self.host = host
        self.port = port
        self.simul = False
      # self.CHUNK = int(self.simulFile.rate/8)
      # self.RATE = float(self.simulFile.rate)
        self.RATEs = rateS
        self.CHUNKs = chunkS
        self.simulCount = 0
        self.simulFile = dfl.qrtaiFile(dataFile)
        self.CHUNK = chunk
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = rate
        
    def pause(self):
        self.active = False
    
    def play(self):
        self.active = True
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()
    
    def stop(self):
        if not self.active:
            self.play()
        self.active = False
        self.quit = True
        print 'Audio stopping'

    def readData(self):
        
        self.condition.acquire()
        self.condition.wait()
        self.condition.release()
        
        self.stream = pyaudio.PyAudio().open(format=self.FORMAT, 
            channels=self.CHANNELS, 
            rate=self.RATE, 
            input=True, 
            frames_per_buffer=self.CHUNK)
        
        while self.active:
            data = self.stream.read(self.CHUNK)
            
            if self.simulCount+self.CHUNKs+1 > len(self.simulFile.data):
                self.simulCount = 0
            dataS = self.simulFile.data[self.simulCount:self.simulCount+self.CHUNKs/divC]
            self.simulCount += (self.CHUNKs+1)
            #time.sleep((self.CHUNKs/divC)/float(self.RATEs))
            
            if not self.raw:            
                count = len(data) / 2
                fmt = "%dh" % (count)
                shorts = struct.unpack(fmt, data)
            else:
                shorts = data
            for l in self.listeners:
                l(shorts)
            for ls in self.simulListeners:
                ls(dataS)
                
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
        

    def run(self):
        print 'Self.quit: ' + str(self.quit)
        while not self.quit:
            if not self.remote:               
                self.readData()
            else:
                self.readRemoteData()
            
            
            