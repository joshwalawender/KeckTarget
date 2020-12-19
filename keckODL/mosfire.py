#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
import yaml
from copy import deepcopy
from astropy import units as u


from .detector_config import IRDetectorConfig
from .instrument_config import InstrumentConfig
from .offset import SkyFrame, InstrumentFrame, TelescopeOffset, OffsetPattern
from .offset import Stare
from .block import ObservingBlock, ObservingBlockList
from .target import Target, DomeFlats


##-------------------------------------------------------------------------
## Constants for the Instrument
##-------------------------------------------------------------------------
exptime_for_domeflats = {'Y': 17, 'J': 11, 'H': 11, 'K': 11}


##-------------------------------------------------------------------------
## MOSFIRE Frames
##-------------------------------------------------------------------------
detector = InstrumentFrame(name='MOSFIRE Detector',
                           scale=0.1798*u.arcsec/u.pixel)
slit = InstrumentFrame(name='MOSFIRE Slit',
                       scale=0.1798*u.arcsec/u.pixel,
                       offsetangle=0*u.deg) # Note this offset angle is wrong


##-------------------------------------------------------------------------
## MOSFIREDetectorConfig
##-------------------------------------------------------------------------
class MOSFIREDetectorConfig(IRDetectorConfig):
    '''An object to hold information about NIRES detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1):
        super().__init__(instrument='MOSFIRE', exptime=exptime,
                         readoutmode=readoutmode, coadds=coadds)


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - readoutmode is either CDS or MCDSn where n is 1-32.
        
        Warn:
        '''
        parse_readoutmode = re.match('(M?)CDS(\d*)', self.readoutmode)
        if parse_readoutmode is None:
            raise DetectorConfigError(f'Readout Mode "{self.readoutmode}" '
                                      f'is not CDS or MCDSn')
        else:
            nreads = int(parse_readoutmode.group(2))
            if nreads > 32:
                raise DetectorConfigError(f'MCDS{nreads} not supported '
                                          f'(only 1-16 are supported)')


##-------------------------------------------------------------------------
## MOSFIREInstrumentConfig
##-------------------------------------------------------------------------
class MOSFIREConfig(InstrumentConfig):
    '''An object to hold information about MOSFIRE configuration.
    '''
    def __init__(self, mode='spectroscopy', filter='Y',
                 mask='longslit_46x0.7'):
        super().__init__()
        self.mode = mode
        self.filter = filter
        self.mask = mask
        self.arclamp = None
        self.domeflatlamp = None
        self.name = f'{self.mask} {self.filter}-{self.mode}'
        if self.arclamp is not None:
            self.name += f' arclamp={self.arclamp}'
        if self.domeflatlamp is not None:
            self.name += f' domeflatlamp={self.domeflatlamp}'


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


    def to_dict(self):
        output = super().to_dict()
        output['InstrumentConfigs'][0]['filter'] = self.filter
        output['InstrumentConfigs'][0]['mode'] = self.mode
        output['InstrumentConfigs'][0]['mask'] = self.mask
        output['InstrumentConfigs'][0]['arclamp'] = self.arclamp
        output['InstrumentConfigs'][0]['domeflatlamp'] = self.domeflatlamp
        return output


    def arcs(self, lampname):
        '''
        '''
        ic_for_arcs = deepcopy(self)
        ic_for_arcs.arclamp = lampname
        ic_for_arcs.name += f' arclamp={ic_for_arcs.arclamp}'
        dc_for_arcs = MOSFIREDetectorConfig(exptime=1, readoutmode='CDS')
        arcs = ObservingBlock(target=None,
                              pattern=Stare(repeat=2),
                              instconfig=ic_for_arcs,
                              detconfig=dc_for_arcs,
                             )
        return arcs


    def domeflats(self, off=False):
        '''
        '''
        ic_for_domeflats = deepcopy(self)
        ic_for_domeflats.domeflatlamp = not off
        lamp_str = {False: 'on', True: 'off'}[off]
        ic_for_domeflats.name += f' domelamp={lamp_str}'
        exptime = exptime_for_domeflats[self.filter]
        dc_for_domeflats = MOSFIREDetectorConfig(exptime=exptime,
                                                 readoutmode='CDS')
        domeflats = ObservingBlock(target=DomeFlats(),
                                   pattern=Stare(repeat=7),
                                   instconfig=ic_for_domeflats,
                                   detconfig=dc_for_domeflats,
                                   )
        return domeflats


    def cals(self):
        '''
        '''
        cals = ObservingBlockList([self.domeflats()])
        if self.filter == 'K':
            cals.append(self.domeflats(off=True))
            cals.append(self.arcs('Ne'))
            cals.append(self.arcs('Ar'))
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


def long2pos(guide=True, repeat=1):
    o1 = TelescopeOffset(dx=+45*u.arcsec, dy=-23*u.arcsec, posname="A",
                         guide=guide, frame=detector)
    o2 = TelescopeOffset(dx=+45*u.arcsec, dy=-9*u.arcsec, posname="B",
                         guide=guide, frame=detector)
    o3 = TelescopeOffset(dx=-45*u.arcsec, dy=+9*u.arcsec, posname="A",
                         guide=guide, frame=detector)
    o4 = TelescopeOffset(dx=-45*u.arcsec, dy=+23*u.arcsec, posname="B",
                         guide=guide, frame=detector)
    return OffsetPattern([o1, o2, o3, o4], name=f'long2pos', repeat=repeat)

