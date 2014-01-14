'''
Created on Nov 5, 2013

@author: Ettore
'''
import datetime as dt
import numpy as np


class OscillFile(object):
    
    def __init__(self, filename):
        self.name = filename
        self.time=[]
        self.ch1=[]
        self.ch2=[]
        self.columns=[]
        self.ch1Samples = None
        self.ch1Slot = None
        self.ch2Samples = None
        self.ch2Slot = None
        tempfile = open(self.name,'r')
        timeLine = False
        voltStepLine = False
        dataLines = False
        self.ground = 127
        for line in tempfile:
            if line.find('START: ')!=-1:
                self.start = dt.datetime.strptime(line[7:],'\t%d/%m/%Y\t%H:%M:%S\n')
                continue
            if line.find('TIME STEP:')!=-1: 
                timeLine = True
                continue
            if timeLine:
                splitEqual = line.find('=')
                self.timeSamples = float(line[0:splitEqual-1])
                self.columns.append('Time')
                if line.find('ms') != -1:
                    splitUnit = line.find('ms')
                else:
                    splitUnit = line.find('s')
                self.timeSlot = float(line[splitEqual+1:splitUnit])
                timeLine = False
                continue
            if line.find('VOLTAGE STEP:')!=-1:
                voltStepLine = True
                continue
            if voltStepLine:
                if line.find('CH1: ')!=-1:
                    splitSemi = line.find(':')
                    splitEqual = line.find('=')
                    self.ch1Samples = float(line[splitSemi+1:splitEqual-1])
                    self.columns.append('CH1')
                    if line.find('mV') != -1:
                        splitUnit = line.find('mV')
                        corr = 1e-3
                    else:
                        splitUnit = line.find('V')
                        corr = 1
                    self.ch1Slot = corr * float(line[splitEqual+1:splitUnit])
                    continue
                elif line.find('CH2: ')!=-1:
                    splitSemi = line.find(':')
                    splitEqual = line.find('=')
                    self.ch2Samples = float(line[splitSemi+1:splitEqual-1])
                    self.columns.append('CH2')
                    if line.find('mV') != -1:
                        splitUnit = line.find('mV')
                    else:
                        splitUnit = line.find('V')
                    self.ch2Slot = float(line[splitEqual+1:splitUnit])
                    continue
                else: 
                    voltStepLine = False
                    continue
            if line.find('N\tCH')!=-1:
                dataLines = True
                continue
            if dataLines:
                if line == '\n':
                    continue
                elif line.find('STOP: ')!=-1:
                    self.stop = dt.datetime.strptime(line[6:],'\t%d/%m/%Y\t%H:%M:%S\n')
                    dataLines = False
                else:
                    dataRow = [float(s) for s in line.split('\t')]
                    self.time.append(dataRow[0]*self.timeSlot/self.timeSamples)
                    if self.ch1Samples:
                        self.ch1.append((dataRow[1]-self.ground)*self.ch1Slot/self.ch1Samples)
                    if self.ch2Samples:
                        self.ch2.append((dataRow[1+int(self.ch1Samples!=None)]-self.ground)*self.ch2Slot/self.ch2Samples)
                    continue
    
    def saveTXTtab(self,path):
        new_file = open(path,'w')
        new_file.write('\t'.join(self.columns)+'\n\n')
        if self.ch1Samples and self.ch2Samples:
            data=list(zip(self.time,self.ch1,self.ch2))
        elif self.ch1Samples and self.ch2Samples==None:
            data=list(zip(self.time,self.ch1))
        elif self.ch1Samples==None and self.ch2Samples:
            data=list(zip(self.time,self.ch2))
        for row in data:
            rowS = [str(r) for r in row]
            new_file.write('\t'.join(rowS)+'\n')


class qrtaiFile(object):
    
    def __init__(self, filename):
        
        self.name = filename
        self.time = []
        self.data = []
        
        tempfile = open(self.name, 'r')
        contLine = 0
        
        for line in tempfile:
            
            splitCol = line.find(' ')
            temp1 = float(line[0:splitCol-1])
            temp2 = float(line[splitCol+1:])
            self.data.append(temp2)
            
            if contLine == 0:
                contLine +=1
                self.start = float(line[0:splitCol-1])
                
            self.time.append(temp1-self.start)
        sum = 0
        cont = 0
        for t in range(len(self.time)-1):
            sum += self.time[t+1]-self.time[t]
            cont += 1
            
        self.rate = cont/sum


def movAvg(data,window):
    
    avgData = np.zeros(len(data))
    
    space=window/2
    
    cont = len(range(space,(len(data)-space-1)))
    
    for i in range(space,(len(data)-space-1)):
        avgData[i] = np.average(data[i-space:i+space])
        
        print cont
        cont -= 1
        
    for i in range(space):
        avgData[i] = np.average(data[0:i+space])
    
    cont=1    
    
    for i in range(len(data)-space-1,len(data)):
        avgData[i] = np.average(data[i-space:i+space-cont])
        cont+=1

    return avgData


def movVar(data,window):
    
    varData = np.zeros(len(data))
    
    space=window/2
    
    for i in range(space,(len(data)-space-1)):
        varData[i] = np.var(data[i-space:i+space])
        
    for i in range(space):
        varData[i] = np.var(data[0:i+space])
    
    cont=1    
    
    for i in range(len(data)-space-1,len(data)):
        varData[i] = np.var(data[i-space:i+space-cont])
        cont+=1
    
    return varData


def movStd(data,window):
    
    stdData = np.zeros(len(data))
    
    space=window/2
    
    for i in range(space,(len(data)-space-1)):
        stdData[i] = np.std(data[i-space:i+space])
        
    for i in range(space):
        stdData[i] = np.std(data[0:i+space])
    
    cont=1    
    
    for i in range(len(data)-space-1,len(data)):
        stdData[i] = np.std(data[i-space:i+space-cont])
        cont+=1
    
    return stdData


def averageSignal(data, T, Ttot, dt):
    
    n = len(data)
    m = int(T/dt)
    s = n/m
    
    Data = np.array(data[0:s*m]).reshape(s,m)
    
    return np.mean(Data, 0)
    



if __name__ == '__main__':
    
    print 'Not for standalone use!\n'