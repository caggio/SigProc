__author__ = "Federico Asara"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = ["Federico Asara", "Juan David Gonzalez Cobas"]
__license__ = "GPL2"
__version__ = "1.0.0"
__maintainer__ = "Federico Asara"
__email__ = "federico.asara@gmail.com"
__status__ = "Production"

import Waveform
from Utilities import *
from numpy import *
import Pyro4
import Pyro4.util
import sys

class SineWaveform(Waveform.Waveform):
    def get(self, what):
        return self.__getattribute__(what)
    
    def set(self, what, how):
        self.__setattr__(what, how)
    
    _parameters = {'frequency':['Frequency', 'Frequency of the sinewave, in HZ', 1000, float],
                  'amplitude':['Amplitude', 'Amplitude of the sinewave, in Vpp', 1, float],
                  'dc':['DC Compoment', 'DC component of the sinewave, in Vpp', 0, float]}
                  
    def __init__(self, *args, **kwargs):
        Waveform.Waveform.__init__(self, *args, **kwargs)
    
    def generate(self, sampleRate, samples, nbits, fsr):
        f = self.frequency
        A = self.amplitude
        C = self.dc
        
        t = arange(samples, dtype=float)/sampleRate
        s = A*sin(2*pi*f*t) +C
        
        lsb = fsr/(2**nbits)
        
        return (s/lsb).astype(int)
    
    
    def generatePeriod(self, nbits, samples, fsr):
        f = self.frequency
        A = self.amplitude
        C = self.dc
        
        t = arange(samples, dtype=float)/samples
        s = A*sin(2*pi*t) +C
        
        lsb = fsr/(2**nbits)
        
        return (s/lsb).astype(int), f
        
    def scale(self, factor):
        """Multiply the frequency by factor."""
        self.frequency *= factor
        
        return self

name = 'Sine Waveform'
target = SineWaveform

import commands

def launch():
    g = target()
    hn = commands.getoutput('hostname')
    
    daemon=Pyro4.Daemon(host = hn)
    
    myUri = daemon.register(g)
    
    ns=Pyro4.locateNS()
    ns.register("Sine", myUri)
    daemon.requestLoop()

if __name__ == '__main__':
    launch()
