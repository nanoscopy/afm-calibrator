import pyaudio
import struct
from threading import Thread, Condition
import time
from logging import thread
import socket
import pysun

CHUNK = 2**12
FORMAT = pyaudio.paInt16
CHANNELS = 2
audioRATE = 44100
ftdiRATE = 180000
RATE = audioRATE

class AudioReader(Thread):

    def __init__(self, raw = False, remote = False, host = 'localhost', port = 9999, sun = False):
        Thread.__init__(self)
        self.active = False
        self.listeners = []
        self.condition = Condition()
        self.quit = False
        self.raw = raw
        self.remote = remote
        self.host = host
        self.port = port
        self.sun = sun
        if self.sun:
            self.sunDev = pysun.suncard()
        
    def pause(self):
        self.active = False
    
    def play(self):
        if self.sun:
            self.sunDev.open()
        self.active = True
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()
    
    def stop(self):
        if not self.active:
            self.play()
        self.active = False
        self.quit = True
        if self.sun:
            self.sunDev.close()

    def readData(self):
        
        self.condition.acquire()
        self.condition.wait()
        self.condition.release()
        
        self.stream = pyaudio.PyAudio().open(format=FORMAT, 
            channels=CHANNELS, 
            rate=RATE, 
            input=True, 
            frames_per_buffer=CHUNK)
        
        while self.active:
            data = self.stream.read(CHUNK)
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
            data = self.socket.recv((CHUNK*2-len(buf))*2)
            if not self.raw:            
                count = len(data) / 2
                fmt = "%dh" % (count)
                shorts = struct.unpack(fmt, data)
                buf.extend(shorts)
                if len(buf)>=CHUNK*2:
                    for l in self.listeners:
                        l(buf)
                    buf=[]
            else:
                for l in self.listeners:
                    l(data)
                
        self.socket.close()
        
    def readSun(self):
        
        self.condition.acquire()
        self.condition.wait()
        self.condition.release()
        
        
        while self.active:
            data = self.sunDev.read(CHUNK)
            for l in self.listeners:
                l(data)
                
        self.sunDev.close()

    def run(self):
        while not self.quit:
            if not self.remote and not self.sun:               
                self.readData()
            elif self.remote and not self.sun:
                self.readRemoteData()
            elif not self.remote and self.sun:
                self.readSun()
            
            