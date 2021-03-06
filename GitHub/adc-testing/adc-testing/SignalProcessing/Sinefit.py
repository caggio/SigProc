__author__ = "Federico Asara"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = ["Federico Asara", "Juan David Gonzalez Cobas"]
__license__ = "GPL2"
__version__ = "1.0.0"
__maintainer__ = "Federico Asara"
__email__ = "federico.asara@gmail.com"
__status__ = "Production"

from numpy import *
from scipy import optimize

def sineguess(dft, rate, nsamples):
    w0index = argmax(dft)
    w0 = w0index * (2 * pi * rate) / nsamples

    return w0, w0index

def doubleSinefit3(samples, sample_t, w0, w1):
    """fit a sampled wave to a sine of kwnown frequency
        
        This routine implements the algoritm of IEEE 1241, sect. 4.1.4.1.,
        fitting a sine of given frequency w0 to the samples given, which are
        assumed equally spaced by a sample period of sample_t
        
        a0 cos(w0 t + theta) + b0 sin(w0 t + theta) + c0
        
        The return value is the triple (a0, b0, c0)
        """
    
    n = samples.size
    t = arange(n) * sample_t
    D0T = matrix(vstack([cos(w0*t), sin(w0*t), cos(w1*t), sin(w1*t), ones(n)]))
    D0 = D0T.T
    x0 = (D0T * D0).I * D0T * matrix(samples).T
    return array(x0).reshape((5,))

def doubleSinefit4matrix(samples, sample_t, w0, w1, tol=1e-12):
    """fit a sampled wave to a sine of unknown frequency
        
        This routine implements the algorithm of IEEE 1241, sect. 4.1.4.3.,
        fitting a sine wave the the samples given, which are assumed equally
        spaced in time by a sample period sample_t. 
        
        a0 cos(w0 t + theta) + b0 sin(w0 t + theta)
        a1 cos(w1 t + theta) + b1 sin(w1 t + theta) + c0
        
        An initial frequency estimate w0 is required to start, and an
        optional relative error in frequency is admitted (1e-4 by default)
        
        The return value is the quadruple (w0, a0, b0, c0)
        """
    
    a0, b0, a1, b1, c0 = doubleSinefit3(samples, sample_t, w0, w1)
    deltaw0 = 0
    deltaw1 = 0
    
    while True:
        w0 += deltaw0
        w1 += deltaw1
        
        n = samples.size
        t = arange(n) * sample_t
        w0t = w0 * t
        w1t = w1 * t
        
        D0T = matrix(vstack([cos(w0t), sin(w0t), cos(w1t), sin(w1t), ones(n),
                             -a0*t*sin(w0t) + b0*t*cos(w0t), -a1*t*sin(w1t)+b1*t*cos(w1t)]))
        D0 = D0T.T
        x0 = (D0T * D0).I * D0T * matrix(samples).T
        x0 = array(x0).reshape((7,))
        a0, b0, a1, b1, c0, deltaw0, deltaw1 = x0
        if max(abs(deltaw1/w1), abs(deltaw0/w0)) < tol:
            return (w0+deltaw0, a0, b0), (w1+deltaw1, a1, b1), c0


def sinefit3(samples, sample_t, w0):
    """fit a sampled wave to a sine of kwnown frequency
        
        This routine implements the algoritm of IEEE 1241, sect. 4.1.4.1.,
        fitting a sine of given frequency w0 to the samples given, which are
        assumed equally spaced by a sample period of sample_t
        
        a0 cos(w0 t + theta) + b0 sin(w0 t + theta) + c0
        
        The return value is the triple (a0, b0, c0)
        """
    
    n = samples.size
    t = w0 * arange(n) * sample_t
    D0T = matrix(vstack([cos(t), sin(t), ones(n)]))
    D0 = D0T.T
    x0 = (D0T * D0).I * D0T * matrix(samples).T
    return array(x0).reshape((3,))

def sinefit4matrix(samples, sample_t, w0, tol=1e-12, imax = 50):
    """fit a sampled wave to a sine of unknown frequency
        
        This routine implements the algorithm of IEEE 1241, sect. 4.1.4.3.,
        fitting a sine wave the the samples given, which are assumed equally
        spaced in time by a sample period sample_t. 
        
        a0 cos(w0 t + theta) + b0 sin(w0 t + theta) + c0
        
        An initial frequency estimate w0 is required to start, and an
        optional relative error in frequency is admitted (1e-4 by default)
        
        The return value is the quadruple (w0, a0, b0, c0)
        """
    
    a0, b0, c0 = sinefit3(samples, sample_t, w0)
    deltaw0 = 0
    #while True:
    for i in range(imax):
        print( 'Sinefit:', i)
        
        w0 += deltaw0
        n = samples.size
        t = arange(n) * sample_t
        w0t = w0 * t
        D0T = matrix(vstack([cos(w0t), sin(w0t), ones(n),
                             -a0*t*sin(w0t) + b0*t*cos(w0t)]))
        D0 = D0T.T
        x0 = (D0T * D0).I * D0T * matrix(samples).T
        x0 = array(x0).reshape((4,))
        a0, b0, c0, deltaw0 = x0
        if abs(deltaw0/w0) < tol:
            return (w0+deltaw0, a0, b0, c0)
    return (w0+deltaw0, a0, b0, c0)

def sinefit4scipy(data, Ts, w0, *args, **kwargs):
    # Target function
    # fitfunc = lambda p, x: p[0]*cos(p[3]*x) +p[1]*sin(p[3]*x) +p[2]

    # Distance to the target function
    errfunc = lambda p, x, y: y - (p[0]*cos(p[3]*x) +p[1]*sin(p[3]*x) +p[2])

    # Initial guess for the parameters
    A, B, C = sinefit3(data, Ts, w0)    
    p0 = [A, B, C, w0];

    # Time serie
    n = data.size
    Tx = arange(n) * Ts

    p1, success = optimize.leastsq(errfunc, p0[:], args=(Tx, data))

    return p1[:4]

def makesine(samples, periods, bits, amplitude=1, noise=0):
    t = arange(samples)/float(samples)
    sine = amplitude * sin(2*pi*periods*t)
    sine += noise * ((t % 0.02) / 0.02 - 0.01)
    sine = (sine * 2**bits + 0.5).astype(int)
    place(sine, sine >=  2**bits, 2**bits)
    place(sine, sine <= -2**bits, -2**bits)
    return sine

sinefit4 = sinefit4matrix

if __name__ == "__main__":
    sine = makesine(20000, 20, 12, 443, 10)
    print (sine)

    dft = 10*log10(abs(fft.rfft(sine)))

    w0, w0index = sineguess(dft, 133, 20000)
    out = sinefit4(sine, 2*pi*(133**-1), w0)

    print (w0, w0index, out)

    orig = makesine(20000, 20, 12, 443, 0);
    noise = sine -orig

    ndft = 10*log10(abs(fft.rfft(noise)))
    print (noise)
    snr = sum(dft**2)/sum(ndft**2)
    print ("SNR:", snr)
