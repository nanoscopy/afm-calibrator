afm-calibrator
==============

Motivation
----------

This project provides a very simple architecture to calibrate the spring constant of atomic force microscopy (AFM) cantilevers using the original Sader's method for rectangular cantilevers [ http://dx.doi.org/10.1063/1.1150021 ]. Next releases of the software will support the recent extension of the method to generic shape cantilevers [  http://dx.doi.org/10.1063/1.4757398 ]. 
The provided script implements direct acquisition and conversion of the deflection analog signal coming from the AFM system through the LINE-IN jack (adapters for BNC can be purchased from many providers). The software reads the signal and exposes it through the Internet as a web page.


Usage
-----

Python libraries requirements: numpy, scipy, pyaudio and tornado

after the required libraires are installed, you can run the calibrator running the script 

    ./calibrator.py [port]

then you can connect with a browser to the specified port (default is 8888)
