#!/usr/bin/env python3
__author__ = "Federico Asara"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = ["Federico Asara", "Juan David Gonzalez Cobas"]
__license__ = "GPL2"
__version__ = "1.0.0"
__maintainer__ = "Federico Asara"
__email__ = "federico.asara@gmail.com"
__status__ = "Production"

#from ConfigParser import RawConfigParser
from configparser import RawConfigParser
from numpy import max, abs, sum, sqrt, log10
from time import time                       
import numpy as np               

# timeit decoratr
def timeit(method):
    def timed(*args, **kw):
        ts = time()
        result = method(*args, **kw)
        te = time()

        print ('%r (%r, %r) %2.3f sec' %  (method.__name__, args, kw, te-ts))
        return result

    return timed
    
# db converter
def dB(x): return 20*np.log10(x)

def norm(v):
    m = np.max(np.abs(v))
    w = v/m
    return m * np.sqrt(np.sum(w*w))

# empty generator
def fake(x, y): 
    return (i for i in [])

@timeit
def readFile2(path):
    config = RawConfigParser()
    config.read(path)
    
    nbits = config.getint('SIGNAL', 'nbits')
    rate = config.getint('SIGNAL', 'rate')
    dataString = config.get('SIGNAL', 'data').split('\n')
    
    data = map(int, dataString)
    
    return nbits, rate, data
    
@timeit
def readFile(path):
    config = RawConfigParser()
    config.read(path)
    
    nbits = config.getint('INFO', 'nbits')
    rate = config.getint('INFO', 'rate')
    elements = config.getint('INFO', 'elements')
    
    output = [map(int, config.get('SIGNAL-%d' % i, 'data').split('\n')) for i in xrange(elements)]
    
    return nbits, rate, output
