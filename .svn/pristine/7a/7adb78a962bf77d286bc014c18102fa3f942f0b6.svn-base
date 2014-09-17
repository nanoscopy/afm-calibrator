import scipy as sp
from scipy import optimize as opt
import numpy as np
import kCalcUtils as kc
from FileEsempio import DataFilesLib as dflib # mia libreria per aprire alcuni file di testo particolari, non tenerne conto
from numpy import fft
from matplotlib import pyplot as plt
from matplotlib import figure
import platform
import sys

if __name__ == '__main__':
    
    fileName = 'FileEsempio/data_25e-6_20sec_2'
    
    myFile = dflib.qrtaiFile(fileName)
    
    fig = plt.figure()
    
    ax = fig.add_subplot(1,1,1)
    
    ax.set_yscale('log')
    
    ax.set_xscale('log')

    b = 35*(10**-6) # larghezza cantilever (nell'interfaccia web dovra' essere inserita dall'utente)
    L = 350*(10**-6) # lunghezza cantilever (nell'interfaccia web dovra' essere inserita dall'utente)
    
    grad = np.gradient(np.array(myFile.time))
    
    dt = np.round(np.mean(grad),6) # Intervallo di campionamento
    
    T = np.round(myFile.time[-1],0) # durata misura

    data = myFile.data
    
    NI = kc.buildNI(T,dt)
    
    start = np.nonzero(NI>=5000)[0][0] # indice di inizio della finestra per lo spettro 
    end = np.nonzero(NI>=12000)[0][0] # indice di fine della finestra per lo spettro

    spec = np.abs(fft.fft(data))**2
    
    Pw,Pd,n,q = kc.GETparams(NI[start:end],spec[start:end]) # Ottenimento dei parametri dalla funzione di fitting
    
    print kc.GETk(kc.roAria,b,L,q,n,kc.etaAria) #roAria e etaAria sono la densita' e la viscosita' dell'aria. Nell'interfaccia web l'utente dovra' poter inserire valori di Ro ed eta arbitrari (avendo come default quelli dell'aria)
    
    line, = ax.plot(NI[start:end],spec[start:end],'b.')
    line2, = ax.plot(NI[start:end],kc.PRF(NI[start:end],Pw,Pd,n,q),'r')
    
    plt.show()
    
    