import pylibftdi as ftdi
import struct
import sys
import time

#suncard specific definitions
#FTDI:FT245R USB FIFO:AD021LOS

CMD_QUERY_FIRMWARE = 0x00
CMD_GET_NBYTES     = 0x01
CMD_CONVERT        = 0x02   
CMD_SETNDATA       = 0x03
CMD_ACQUIRE_NDATA  = 0x04   
CMD_SEND_NDATA     = 0x05   

READ_TIMEOUT       = 3.0
HWRANGE            = 2.048
BITSTEP            = HWRANGE/65536.0

FTDIDEVICE         = 'AD021LOS'

RATE = 22050

logging = False

class suncard():
    def __init__(self):
        try:
            self.device = ftdi.Device(device_id=FTDIDEVICE)
        except:
            print "Error opening the card AD021LOS"
            print "Remember to verify your rights to open the device."            
            if logging: 
                print sys.exc_info()[0]
                
    def open(self):
        # remember to add the support for re-opening by ID for multiple FTDI devices
        if self.device.closed:
            self.device.open()
                
    def close(self):
        return self.device.close()
        
    def __del__(self):
        self.close()
        
    def get_firmware(self):
        r = self.device.write(chr(CMD_QUERY_FIRMWARE))
        buf = struct.unpack('<BB',self.device.read(2))
        
        if buf[0] != CMD_QUERY_FIRMWARE:
            print('Suncard error')
            return False
        major   = int( float(buf[1]) / 16.0)
        minor = buf[1] - major * 16;        
        print ('Firmware version {0}.{1}'.format(major,minor))
        return [major,minor]
    
    def _getVolt(self,msb,lsb=None):
        if lsb == None:
            (msb,lsb)=msb
        word = msb * 256 + lsb
        if (msb >= 0x80) :
            volt = (HWRANGE/2.0) - (BITSTEP * (word - 32768))
        else:
            volt = -BITSTEP * word
        return volt
    
    def get_value(self):
        r = self.device.write(chr(CMD_CONVERT))
        buf = struct.unpack('<BBB',self.device.read(3))
        if buf[0] != CMD_CONVERT:
            print('Suncard error')
            return False
        return self._getVolt(buf[1],buf[2])
    
    def flush(self):
        allbuf=''
        s = self.device.read(1)
        while (s!='') :
            allbuf+=s
            s = self.device.read(1)
        print "Flushed {0} bytes from the board".format(len(allbuf))
        return allbuf
    
    def read(self,nData):
        return self.get_values(nData)
    
    def get_values(self,nData):
        
        msb = (nData & 0xFF00) >> 8;
        lsb = nData & 0xFF; 
        
        # 1-Tell the board how many data we are interested in
        r = self.device.write(chr(CMD_SETNDATA ))
        r = self.device.write(chr(lsb ))
        r = self.device.write(chr(msb ))
        
        buf = struct.unpack('<B',self.device.read(1))
        
        if buf[0] != CMD_SETNDATA:
            print('Suncard error')
            return False
        
        # 2-Send the start acquisition command            
        r = self.device.write(chr(CMD_ACQUIRE_NDATA ))        
        buf = struct.unpack('<B',self.device.read(1))
        
        if buf[0] != CMD_ACQUIRE_NDATA:
            print('Suncard error')
            return False
        
        # 3-retrieve the data from the board
        r = self.device.write(chr(CMD_SEND_NDATA ))
        
        i = 0
        voltarray = []
        start = time.time()
        while(len(voltarray)<nData):
            buf = self.device.read(2)
            if buf != '':
                if len(buf)==1:
                    print 'Suncard error! Requested buffer was too high'
                    break
                try:
                    buf = struct.unpack('<BB',buf)
                    voltarray.append(self._getVolt(buf[0],buf[1]))
                except:
                    print 'Unexpected result at N={0}'.format(len(voltarray))
                    break
            elif len(voltarray)>0:
                ora = time.time()
                if (ora-start)>READ_TIMEOUT:
                    print "Timeout of the acquisition at {0} data".format(len(voltarray))                        
                    break
        return voltarray
