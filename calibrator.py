import os.path
#!/usr/bin/python
import os
import webbrowser as web

try:
    import numpy, scipy, pyaudio, tornado
except ImportError:
    print "numpy, scipy, pyaudio and tornado are required to run the calibrator"
    pass

import signal, sys, threading, platform, time

from nanoscopy import tornado_server
    
filePath = os.path.dirname(sys.argv[0])
if filePath != "":
    filePath+=os.sep
    
print "AFM tornado server V" + tornado_server.version

try:
    tornado_server.port=int(sys.argv[1])
except:
    pass

try:
    tornado_server.filePath=filePath
except:
    pass      

threading.Thread(target=tornado_server.start).start()

try:
    if sys.argv[3] == 'debug':
        web.open('http://localhost:'+str(tornado_server.port))
except:
    pass

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
