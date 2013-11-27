import numpy as np
import scipy as sp
from scipy import special as sx
from scipy import optimize as opt

roAria = 1.18
etaAria = 1.86*(10**-5)


def buildNI(T,dt):
    
    # Crea l'array di frequenze a partire dalla durata della misura T e dal tempo di campionamento dt
    
    return np.arange((1/T),(1/dt+1/T),(1/T))


def OMr(Re):
    # Parte reale della funzione di correzione per la funzione gamma circolare applicata a cantilever a sezione rettangolare

    tau = np.log10(Re)
    num = 0.91324 - 0.48274 * tau + 0.46842 * (tau**2) - 0.12886 * (tau**3) + 0.044055 * (tau**4) - 0.0035117 * (tau**5) + 0.00069085 * (tau**6)
    den= 1 - 0.56964 * tau + 0.48690 * (tau**2) - 0.13444 * (tau**3) + 0.045155 * (tau**4) - 0.0035862 * (tau**5) + 0.00069085 * (tau**6)
    
    return num/den


def OMi(Re):
    # Parte immaginaria della funzione di correzione
    
    tau = np.log10(Re)
    
    num = -0.024134 - 0.029256 * tau + 0.016294 * (tau**2) - 0.00010961 * (tau**3) + 0.000064577 * (tau**4) - 0.000044510 * (tau**5)
    den = 1 - 0.59702 * tau + 0.55182 * (tau**2) - 0.18357 * (tau**3) + 0.079156 * (tau**4) - 0.014369 * (tau**5) + 0.0028361 * (tau**6)
    
    return num/den


def gammaCirc(ni, Re):
    
    # Funzione idrodinamica per cantilever a sezione circolare
    
    Re = np.sqrt(Re/2) - 1j*np.sqrt(Re/2)
    
    num = 4*sx.kv(1,Re)
    den = Re*sx.kv(0,Re)
    
    return (1 + (num/den))


def gamma(ni,Re):
    
    # Funzione idrodinamica per cantilever a sezione rettangolare
    
    return gammaCirc(ni,Re)*(OMr(Re)+1j*OMi(Re))


def PRF(NI,Pwhite,Pdc,niR,Q):
    
    # Funzione di fit dello spettro (Power Response Function per oscillatore armonico semplice)
    
    num = Pdc*(niR**4)
    den = (NI**2-niR**2)**2+((NI*niR)**2)/(Q**2)
    
    return Pwhite+(num/den)
    
    
def initFit(NI,Spectrum):
    
    # Inizializzazione dei parametri di fit
    
    indMax = np.argmax(Spectrum)
    niRstart = NI[indMax]
    PwPdcQ = Spectrum[indMax]
    PWstart = Spectrum[0]
    
    PdcQ = PwPdcQ - PWstart
    
    INDniRhalf1, INDniRhalf2 = tuple(np.nonzero(Spectrum>=(PwPdcQ/2))[0][[0,-1]])
    
    deltaNI = NI[INDniRhalf2] - NI[INDniRhalf1] 
    
    Qstart = (niRstart*2*np.sqrt(2))/(deltaNI)
    
    PdcStart = PdcQ/Qstart
    
    return PWstart,PdcStart,niRstart,Qstart

    
def GETparams(NI, T, Spectrum):
    
    # Calcolo dei parametri, necessari per determinare il valore di k, tramite il fit dello spettro 
    # di densita' di potenza
    
    paramsStart = initFit(NI, Spectrum)
    
    fitResult = opt.curve_fit(PRF, NI, Spectrum, paramsStart)
    
    PW,Pdc,niR,Q = fitResult[0]
    
    Qtrue = GETQtrue(niR,1/T,Q)
    
    return PW,Pdc,niR,Qtrue
    

def GETQtrue(niR,deltaF,Qmeas):
    
    # Correzione del fattore di qualita' per ovviare alle limitazioni dovute alla risoluzione finita 
    # in frequenza dello spettro di densita' di potenza 
    
    Qcoeff = (np.pi*niR)/(2*deltaF)
    Qcoeff2 = (4*deltaF)/(np.pi*niR)
    
    return Qcoeff*(1-np.sqrt(1-Qmeas*Qcoeff2))
    

def GETk(roF,b,L,Qtrue,niR,eta):
    
    # Calcolo del valore di k a partire dai parametri ricavati dal fit dello spettro
    
    Re = (np.pi*roF*niR*(b**2))/(2*eta) # Numero di Reynolds
    
    Gi = np.imag(gamma(niR,Re))
    
    k = 7.5246*roF*(b**2)*L*Qtrue*Gi*(niR**2)
    
    return k

    

if __name__=='__main__':

    print "Not for standalone use." 
    
    