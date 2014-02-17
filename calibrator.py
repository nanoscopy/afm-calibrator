#!/usr/bin/python

try:
    import numpy, scipy, pyaudio, tornado
except ImportError:
    print "numpy, scipy, pyaudio and tornado are required to run the calibrator"
    pass

import signal, sys, threading, platform, time

 
from nanoscopy import tornado_server

try:
    tornado_server.port=int(sys.argv[1])
except:
    pass
        
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
        print 'before exit'
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    
    print 'Running on port %d' % tornado_server.port
    print 'Press Ctrl+C to stop'
    signal.pause()
