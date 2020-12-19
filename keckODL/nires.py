#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
from copy import deepcopy
import yaml
from astropy import units as u


from .detector_config import IRDetectorConfig
from .instrument_config import InstrumentConfig
from .offset import SkyFrame, InstrumentFrame, TelescopeOffset, OffsetPattern
from .offset import Stare
from .block import ObservingBlock, ObservingBlockList
from .target import Target, DomeFlats


##-------------------------------------------------------------------------
## NIRES Frames
##-------------------------------------------------------------------------
scam = InstrumentFrame(name='NIRES Scam Detector',
                       scale=0.123*u.arcsec/u.pixel)
slit = InstrumentFrame(name='NIRES Slit',
                       scale=0.15*u.arcsec/u.pixel,
                       offsetangle=0*u.deg) # Note this offset angle is wrong

##-------------------------------------------------------------------------
## NIRESDetectorConfig
##-------------------------------------------------------------------------
class NIRESSpecConfig(IRDetectorConfig):
    '''An object to hold information about NIRES detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1, nexp=1):
        super().__init__(exptime=exptime, nexp=nexp, readoutmode=readoutmode,
                         coadds=coadds)
        self.instrument = 'NIRES Spec'
        self.set_name()


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - readoutmode is either CDS or MCDSn where n is 1-32.
        
        Warn:
        '''
        parse_readmode = re.match('(M?)CDS(\d*)', self.readoutmode)
        if parse_readmode is None:
            raise DetectorConfigError(f'Readout Mode "{self.readoutmode}" '
                                      f'is not CDS or MCDSn')
        else:
            nreads = int(parse_readmode.group(2))
            if nreads > 32:
                raise DetectorConfigError(f'MCDS{nreads} not supported '
                                          f'(only 1-32 are supported)')


class NIRESScamConfig(IRDetectorConfig):
    '''An object to hold information about NIRES detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1, nexp=1):
        super().__init__(exptime=exptime, nexp=nexp, readoutmode=readoutmode,
                         coadds=coadds)
        self.instrument = 'NIRES SCAM'
        self.set_name()


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - readoutmode is either CDS or MCDSn where n is 1-32.
        
        Warn:
        '''
        parse_readmode = re.match('(M?)CDS(\d*)', self.readoutmode)
        if parse_readmode is None:
            raise DetectorConfigError(f'Readout Mode "{self.readoutmode}" '
                                      f'is not CDS or MCDSn')
        if parse_readmode.group(1) == '' and parse_readmode.group(2) == '':
            pass
        else:
            nreads = int(parse_readmode.group(2))
            if nreads > 32:
                raise DetectorConfigError(f'MCDS{nreads} not supported '
                                          f'(only 1-32 are supported)')


##-------------------------------------------------------------------------
## NIRESConfig
##-------------------------------------------------------------------------
class NIRESConfig(InstrumentConfig):
    '''An object to hold information about NIRES configuration.
    '''
    def __init__(self, detconfig=None):
        super().__init__(detconfig=detconfig)
        self.name = 'NIRES Instrument Config'

    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


    def arcs(self):
        '''
        '''
        arcs = deepcopy(self)
        arcs.detconfig = NIRESSpecConfig(exptime=120, readoutmode='CDS')
        arcs.domeflatlamp = 'niresarcs'
        arcs.name += f' arclamp'
        return arcs


    def domeflats(self, off=False):
        '''
        '''
        domeflats = deepcopy(self)
        domeflats.detconfig = NIRESSpecConfig(exptime=100, readoutmode='CDS')
        domeflats.domeflatlamp = not off
        lamp_str = {False: 'on', True: 'off'}[off]
        domeflats.name += f' domelamp={lamp_str}'
        return domeflats


    def cals(self):
        '''
        '''
        cals = ObservingBlockList()
        cals.append(ObservingBlock(target=DomeFlats(),
                                   pattern=Stare(repeat=9),
                                   instconfig=self.domeflats()))
        cals.append(ObservingBlock(target=None,
                                   pattern=Stare(repeat=3),
                                   instconfig=self.arcs()))
        return cals


##-------------------------------------------------------------------------
## Pre-Defined Patterns
##-------------------------------------------------------------------------
def ABBA(offset=1.25*u.arcsec, guide=True, repeat=1):
    o1 = TelescopeOffset(dx=0, dy=+offset, posname="A", guide=guide, frame=slit)
    o2 = TelescopeOffset(dx=0, dy=-offset, posname="B", guide=guide, frame=slit)
    o3 = TelescopeOffset(dx=0, dy=-offset, posname="B", guide=guide, frame=slit)
    o4 = TelescopeOffset(dx=0, dy=+offset, posname="A", guide=guide, frame=slit)
    return OffsetPattern([o1, o2, o3, o4], repeat=repeat,
                         name=f'ABBA ({offset:.2f})')
