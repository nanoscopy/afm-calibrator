#!/usr/bin/python

try:
    import numpy, scipy, tornado
except ImportError:
    print "numpy, scipy, pyaudio and tornado are required to run the calibrator"

try:
    import pyaudio
except ImportError:
    print "pyaudio is required for use with sound card"

try:
    import libftdi
except ImportError:
    print "libftdi is required for use with FTDI cards"

import signal, sys, threading, platform, time

from nanoscopy import tornado_server

try:
    tornado_server.port=int(sys.argv[1])
except:
    pass

try:
    if len(sys.argv)==3 and sys.argv[2]=='ftdi':
        tornado_server.sunVersion = True
        tornado_server.RATE = tornado_server.ftdiRATE
    else:
        tornado_server.sunVersion = False
        tornado_server.RATE = tornado_server.audioRATE
    
    tornado_server.ar = tornado_server.AudioReader(sun = tornado_server.sunVersion)
    tornado_server.NI = tornado_server.kcu.buildNI(float(tornado_server.CHUNK)/tornado_server.RATE,1.0/tornado_server.RATE) # Range frequenze creato apposta per le impostazioni della scheda sonora
except:
    pass


print tornado_server.sunVersion

threading.Thread(target=tornado_server.start).start()

if platform.system()=='Windows':
    
    c='c'
    try:
        print 'Running on port %d' % tornado_server.port
        print 'Press x and then Enter to stop'
        while c != 'x':
            c = raw_input()
        tornado_server.stop()
        sys.exit()
    except:
        tornado_server.stop()
        sys.exit(0)

else:
    
    def signal_handler(signal, frame):
        print 'exiting'
        tornado_server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    
    print 'Running on port %d' % tornado_server.port
    print 'Press Ctrl+C to stop'
    signal.pause()
