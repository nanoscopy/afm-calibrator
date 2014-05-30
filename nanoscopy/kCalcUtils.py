import numpy as np
import scipy as sp
from scipy import special as sx
from scipy import optimize as opt

roAria = 1.18
etaAria = 1.86*(10**-5)


def buildNI(T,dt):
    
    # Crea l'array di frequenze a partire dalla durata della misura T e dal tempo di campionamento dt
    '''
    This function creates the frequencies array for the acquired spectrum, using the measurements duration T and the sampling time dt
    
    Input:
    T = measurement duration
    dt = sampling time
    
    Output:
    Frequencies array in Hz
    '''
    
    return np.arange((1/T),(1/dt+1/T),(1/T))


def OMr(Re):
    # Parte reale della funzione di correzione per la funzione gamma circolare applicata a cantilever a sezione rettangolare
    '''
    This function calculates the real part of the correction for the gamma function applied to a cantilever with rectangular section
    
    Input:
    Re = Reynolds number
    
    Output:
    Real part of the correction for the gamma function
    '''

    tau = np.log10(Re)
    num = 0.91324 - 0.48274 * tau + 0.46842 * (tau**2) - 0.12886 * (tau**3) + 0.044055 * (tau**4) - 0.0035117 * (tau**5) + 0.00069085 * (tau**6)
    den= 1 - 0.56964 * tau + 0.48690 * (tau**2) - 0.13444 * (tau**3) + 0.045155 * (tau**4) - 0.0035862 * (tau**5) + 0.00069085 * (tau**6)
    
    return num/den


def OMi(Re):
    # Parte immaginaria della funzione di correzione
    '''
    This function calculates the imaginary part of the correction for the gamma function applied to a cantilever with rectangular section
    
    Input:
    Re = Reynolds number
    
    Output:
    Imaginary part of the correction for the gamma function
    '''
    
    tau = np.log10(Re)
    
    num = -0.024134 - 0.029256 * tau + 0.016294 * (tau**2) - 0.00010961 * (tau**3) + 0.000064577 * (tau**4) - 0.000044510 * (tau**5)
    den = 1 - 0.59702 * tau + 0.55182 * (tau**2) - 0.18357 * (tau**3) + 0.079156 * (tau**4) - 0.014369 * (tau**5) + 0.0028361 * (tau**6)
    
    return num/den


def gammaCirc(ni, Re):
    
    # Funzione idrodinamica per cantilever a sezione circolare
    
    '''
    This function calculates the idrodynamic gamma function for a cantilever with circular section
    
    Input:
    ni = frequency in Hz
    Re = Reynolds number
    
    Output:
    Gamma function value
    '''
    
    Re = np.sqrt(Re/2) - 1j*np.sqrt(Re/2)
    
    num = 4*sx.kv(1,Re)
    den = Re*sx.kv(0,Re)
    
    return (1 + (num/den))


def gamma(ni,Re):
    
    # Funzione idrodinamica per cantilever a sezione rettangolare
    '''
    This function returns the corrected gamma function
    
    Input:
    ni = frequency in Hz
    Re = Reynolds number
    
    Output:
    Corrected gamma function value
    '''
    
    return gammaCirc(ni,Re)*(OMr(Re)+1j*OMi(Re))


def PRF(NI,Pwhite,Pdc,niR,Q):
    
    # Funzione di fit dello spettro (Power Response Function per oscillatore armonico semplice)
    '''
    This is an implementation of the function used to fit the acquired spectrum.
    
    Input:
    NI = frequencies array in Hz
    Pwhite = white noise floor
    Pdc = dc power response
    niR = cantilever resonance frequency
    Q = quality factor
    
    Outpu:
    Fitting function values (array)
    '''
    
    
    num = Pdc*(niR**4)
    den = (NI**2-niR**2)**2+((NI*niR)**2)/(Q**2)
    
    return Pwhite+(num/den)
    
    
def initFit(NI,Spectrum):
    
    # Inizializzazione dei parametri di fit
    '''
    This function initializes the fitting parameters
    
    Input:
    NI = frequencies array in Hz
    Spectrum = data to be fitted
    
    Output:
    PWStart = white noise floor
    PdcStart = dc power response
    niRstart = cantilever resonance frequency
    Qstart = quality factor
    
    '''
    
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

    
def GETparams(NI, Spectrum, T = None):
    
    '''
    Performs the fitting on the acquired spectrum
    
    Input:
    NI = frequencies array in Hz
    Spectrum = data to be fitted
    T = measurements duration, used to correct the measured Q value. If it's none, Q will not be corrected.
    
    Output:
    PW = white noise floor
    Pdc = dc power response
    niR = cantilever resonance frequency
    Q = quality factor
    '''
    # Calcolo dei parametri, necessari per determinare il valore di k, tramite il fit dello spettro 
    # di densita' di potenza
    
    paramsStart = initFit(NI, Spectrum)
    
    fitResult = opt.curve_fit(PRF, NI, Spectrum, paramsStart, maxfev=200000)
    
    PW,Pdc,niR,Q = fitResult[0]
    
    # Questa scelta e' stata aggiunta per permettere di utilizzare o il valore misurato di Q (affetto da problemi riguardanti la risoluzione 
    # finita in frequenza dello spettro) o quello corretto (vedere funzione sottostante)
    if T is not None: Qtrue = GETQtrue(niR,1/T,Q) # T e' la durata totale (in secondi) della misura
    else: Qtrue = Q
    
    return PW,Pdc,niR,Qtrue
    

def GETQtrue(niR,deltaF,Qmeas):
    
    '''
    This function corrects the Q value since it is affected by the finite frequency resolution of the spectrum
    
    Input:
    niR = cantilever resonance frequency
    Qmeas = measured quality factor
    deltaF = spectrum frequency resolution
    
    Output:
    Corrected quality factor
    '''
    # Correzione del fattore di qualita' per ovviare alle limitazioni dovute alla risoluzione finita 
    # in frequenza dello spettro di densita' di potenza 
    
    Qcoeff = (np.pi*niR)/(2*deltaF)
    Qcoeff2 = (4*deltaF)/(np.pi*niR)
    
    return Qcoeff*(1-np.sqrt(1-Qmeas*Qcoeff2))
    

def GETk(roF,b,L,Qtrue,niR,eta):
    
    '''
    This function calculates the elastic constant value
    
    Input:
    roF = medium density
    b = cantilever width
    L = cantilever length
    Qtrue = Corrected quality factor (it doesn't really need to be the corrected one, but for precision sake it's better not to use the measured one)
    niR = cantilever resonance frequency
    eta = medium viscousness
    
    Output:
    k = cantilever elastic constant
    
    '''
    
    # Calcolo del valore di k a partire dai parametri ricavati dal fit dello spettro
    
    Re = (np.pi*roF*niR*(b**2))/(2*eta) # Numero di Reynolds
    
    Gi = np.imag(gamma(niR,Re))
    
    k = 7.5246*roF*(b**2)*L*Qtrue*Gi*(niR**2)
    
    return k

    

if __name__=='__main__':

    print "Not for standalone use." 
    
    