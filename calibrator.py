#!/usr/bin/python

import signal, sys, threading


from nanoscopy import tornado_server

try:
    tornado_server.port=int(sys.argv[1])
except:
    pass
 
def signal_handler(signal, frame):
        print 'exiting'
        tornado_server.stop()
        sys.exit(0)
        
threading.Thread(target=tornado_server.start).start()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)

print 'Running on port %d' % tornado_server.port
print 'Press Ctrl+C to stop'
signal.pause()
