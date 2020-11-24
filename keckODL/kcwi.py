#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
from copy import deepcopy
import yaml
from astropy import units as u


from .detector_config import VisibleDetectorConfig
from .instrument_config import InstrumentConfig
from .offset import SkyFrame, InstrumentFrame, TelescopeOffset, OffsetPattern
from .offset import Stare
from .sequence import Sequence, SequenceElement
from .block import ObservingBlock, ObservingBlockList
from .target import Target, DomeFlats


##-------------------------------------------------------------------------
## KCWI Frames
##-------------------------------------------------------------------------
bluedetector = InstrumentFrame(name='Blue Detector',
                               scale=0.1798*u.arcsec/u.pixel)
smallslicer = InstrumentFrame(name='SmallSlicer',
                              scale=0.35*u.arcsec/u.pixel)
mediumslicer = InstrumentFrame(name='MediumSlicer',
                               scale=0.70*u.arcsec/u.pixel)
largeslicer = InstrumentFrame(name='LargeSlicer',
                              scale=1.35*u.arcsec/u.pixel)


##-------------------------------------------------------------------------
## KCWIblueDetectorConfig
##-------------------------------------------------------------------------
class KCWIblueDetectorConfig(VisibleDetectorConfig):
    '''An object to hold information about KCWI Blue detector configuration.
    
    readoutmode corresponds to the KCWI config keyword ccdmodeb
    '''
    def __init__(self, exptime=None, readoutmode=1, ampmode=9,
                 dark=False, binning='1x1', window=None, gain=10):
        super().__init__(instrument='KCWIblue', exptime=exptime,
                         readoutmode=readoutmode, ampmode=ampmode, dark=dark,
                         binning=binning, window=window)
        self.gain = gain


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - exptime is in range 1-3600
        - readoutmode is in range ??
        - ampmode is in range ??
        - dark is boolean
        - binning is one of 1x1, 2x2
        - gain is in range ??

        Warn:
        - Window is not used
        '''
        pass


##-------------------------------------------------------------------------
## KCWIredDetectorConfig
##-------------------------------------------------------------------------
class KCWIredDetectorConfig(VisibleDetectorConfig):
    '''An object to hold information about KCWI Red detector configuration.
    
    readoutmode corresponds to the KCWI config keyword ccdmoder
    '''
    def __init__(self, exptime=None, readoutmode=1, ampmode=9,
                 dark=False, binning='1x1', window=None, gain=10):
        super().__init__(instrument='KCWIred', exptime=exptime,
                         readoutmode=readoutmode, ampmode=ampmode, dark=dark,
                         binning=binning, window=window)
        self.gain = gain


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - exptime is in range 1-3600
        - readoutmode is in range ??
        - ampmode is in range ??
        - dark is boolean
        - binning is one of 1x1, 2x2
        - gain is in range ??

        Warn:
        - Window is not used
        '''
        pass


##-------------------------------------------------------------------------
## KCWIConfig
##-------------------------------------------------------------------------
class KCWIConfig(InstrumentConfig):
    '''An object to hold information about KCWI Blue+Red configuration.
    '''
    def __init__(self, slicer='medium', 
                 bluegrating='BH3', bluefilter='KBlue',
                 bluecwave=4800, bluepwave=None,
                 bluenandsmask=False, bluefocus=None,
                 redgrating='BH3', redfilter='KRed',
                 redcwave=4800, redpwave=None,
                 rednandsmask=False, redfocus=None,
                 calmirror='Sky', calobj='Dark', arclamp=None,
                 domeflatlamp=None, polarizer='Sky'):
        super().__init__()
        self.instrument = 'KCWIblue'
        self.slicer = slicer
        self.polarizer = polarizer

        # Blue Components
        self.bluegrating = bluegrating
        self.bluefilter = bluefilter
        self.bluecwave = bluecwave
        self.bluepwave = bluecwave-300 if bluepwave is None else bluepwave
        self.bluenandsmask = bluenandsmask
        self.bluefocus = bluefocus

        # Red Components
        self.redgrating = redgrating
        self.redfilter = redfilter
        self.redcwave = redcwave
        self.redpwave = redcwave-300 if redpwave is None else redpwave
        self.rednandsmask = rednandsmask
        self.redfocus = redfocus

        # Calibration Components
        self.calmirror = calmirror
        self.calobj = calobj
        self.arclamp = arclamp
        self.domeflatlamp = domeflatlamp

        # Set config name
        self.name = f'{self.slicer} {self.bluegrating} {self.bluecwave*u.A:.0f}'
        if self.calobj != 'Dark':
            self.name += f' calobj={self.calobj}'
        if self.arclamp is not None:
            self.name += f' arclamp={self.arclamp}'
        if self.domeflatlamp is not None:
            self.name += f' domeflatlamp={self.domeflatlamp}'


    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


    def to_dict(self):
        output = super().to_dict()
        output['slicer'] = self.slicer

        output['bluegrating'] = self.bluegrating
        output['bluefilter'] = self.bluefilter
        output['bluenandsmask'] = self.bluenandsmask
        output['bluefocus'] = self.bluefocus
        output['bluecwave'] = self.bluecwave
        output['bluepwave'] = self.bluepwave

        output['redgrating'] = self.redgrating
        output['redfilter'] = self.redfilter
        output['rednandsmask'] = self.rednandsmask
        output['redfocus'] = self.redfocus
        output['redcwave'] = self.redcwave
        output['redpwave'] = self.redpwave

        output['calmirror'] = self.calmirror
        output['calobj'] = self.calobj
        output['polarizer'] = self.polarizer
        output['arclamp'] = self.arclamp
        output['domeflatlamp'] = self.domeflatlamp
        
        return output


    def arcs(self, lampname):
        '''
        '''
        arcs = deepcopy(self)
        arcs.arclamp = lampname
        arcs.calobj = 'FlatA'
        arcs.name += f' arclamp={arcs.arclamp}'
        arcs.name += f' calobj={arcs.calobj}'
        return arcs


    def contbars(self):
        '''
        '''
        contbars = deepcopy(self)
        contbars.calobj = 'MedBarsA'
        contbars.arclamp = 'CONT'
        contbars.name += f' arclamp={contbars.arclamp}'
        contbars.name += f' calobj={contbars.calobj}'
        return contbars


    def domeflats(self, off=False):
        '''
        '''
        domeflats = deepcopy(self)
        domeflats.domeflatlamp = not off
        domeflats.name += f' domeflatlamp={domeflats.domeflatlamp}'
        return domeflats


    def cals(self, internal=True, domeflats=True):
        '''
        '''
        kcwib_0s_dark = KCWIblueDetectorConfig(exptime=0, dark=True)
        kcwib_6s = KCWIblueDetectorConfig(exptime=6)
        kcwib_30s = KCWIblueDetectorConfig(exptime=30)
        kcwib_45s = KCWIblueDetectorConfig(exptime=45)
        kcwib_100s = KCWIblueDetectorConfig(exptime=100)

        cals = ObservingBlockList()
        if internal is True:
            cals.append(ObservingBlock(target=None,
                                       pattern=Stare(),
                                       detconfig=kcwib_6s,
                                       instconfig=self.contbars(),
                                       repeat=1))
            cals.append(ObservingBlock(target=None,
                                       pattern=Stare(),
                                       detconfig=kcwib_30s,
                                       instconfig=self.arcs('FEAR'),
                                       repeat=1))
            cals.append(ObservingBlock(target=None,
                                       pattern=Stare(),
                                       detconfig=kcwib_45s,
                                       instconfig=self.arcs('THAR'),
                                       repeat=1))
            cals.append(ObservingBlock(target=None,
                                       pattern=Stare(),
                                       detconfig=kcwib_6s,
                                       instconfig=self.arcs('CONT'),
                                       repeat=6))
            cals.append(ObservingBlock(target=None,
                                       pattern=Stare(),
                                       detconfig=kcwib_0s_dark,
                                       instconfig=self,
                                       repeat=7))
        if domeflats is True:
            cals.append(ObservingBlock(target=DomeFlats(),
                                       pattern=Stare(),
                                       detconfig=kcwib_100s,
                                       instconfig=self.domeflats(),
                                       repeat=3))
        return cals


    def seq_cals(self, internal=True, domeflats=True):
        '''
        '''
        kcwib_0s_dark = KCWIblueDetectorConfig(exptime=0, dark=True)
        kcwib_6s = KCWIblueDetectorConfig(exptime=6)
        kcwib_30s = KCWIblueDetectorConfig(exptime=30)
        kcwib_45s = KCWIblueDetectorConfig(exptime=45)
        kcwib_100s = KCWIblueDetectorConfig(exptime=100)

        cals = Sequence()
        if internal is True:
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_6s,
                                        instconfig=self.contbars(),
                                        repeat=1))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_30s,
                                        instconfig=self.arcs('FEAR'),
                                        repeat=1))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_45s,
                                        instconfig=self.arcs('THAR'),
                                        repeat=1))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_6s,
                                        instconfig=self.arcs('CONT'),
                                        repeat=6))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_0s_dark,
                                        instconfig=self,
                                        repeat=7))
        if domeflats is True:
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_100s,
                                        instconfig=self.domeflats(),
                                        repeat=3))
        return cals


    def __str__(self):
        return f'{self.name}'


    def __repr__(self):
        return f'{self.name}'


##-------------------------------------------------------------------------
## KCWIblueConfig
##-------------------------------------------------------------------------
# class KCWIblueConfig(InstrumentConfig):
#     '''An object to hold information about KCWI Blue configuration.
#     '''
#     def __init__(self, slicer='medium', grating='BH3', filter='KBlue',
#                  cwave=4800, pwave=None, nandsmask=False, focus=None,
#                  calmirror='Sky', calobj='Dark', arclamp=None,
#                  domeflatlamp=None, polarizer='Sky'):
#         super().__init__()
#         self.instrument = 'KCWIblue'
#         self.slicer = slicer
#         self.grating = grating
#         self.filter = filter
#         self.nandsmask = nandsmask
#         self.focus = focus
#         self.calmirror = calmirror
#         self.calobj = calobj
#         self.arclamp = arclamp
#         self.domeflatlamp = domeflatlamp
#         self.polarizer = polarizer
#         self.cwave = cwave
#         self.pwave = cwave-300 if pwave is None else pwave
#         self.name = f'{self.slicer} {self.grating} {self.cwave*u.A:.0f}'
#         if self.calobj != 'Dark':
#             self.name += f' calobj={self.calobj}'
#         if self.arclamp is not None:
#             self.name += f' arclamp={self.arclamp}'
#         if self.domeflatlamp is not None:
#             self.name += f' domeflatlamp={self.domeflatlamp}'
# 
# 
#     def validate(self):
#         '''Check values and verify that they meet assumptions.
#         
#         Check:
#         
#         Warn:
#         '''
#         pass
# 
# 
#     def to_dict(self):
#         output = super().to_dict()
#         output['slicer'] = self.slicer
#         output['grating'] = self.grating
#         output['filter'] = self.filter
#         output['nandsmask'] = self.nandsmask
#         output['focus'] = self.focus
#         output['calmirror'] = self.calmirror
#         output['calobj'] = self.calobj
#         output['polarizer'] = self.polarizer
#         output['cwave'] = self.cwave
#         output['pwave'] = self.pwave
#         return output
# 
# 
#     def arcs(self, lampname):
#         '''
#         '''
#         arcs = deepcopy(self)
#         arcs.arclamp = lampname
#         arcs.calobj = 'FlatA'
#         arcs.name += f' arclamp={arcs.arclamp}'
#         arcs.name += f' calobj={arcs.calobj}'
#         return arcs
# 
# 
#     def contbars(self):
#         '''
#         '''
#         contbars = deepcopy(self)
#         contbars.calobj = 'MedBarsA'
#         contbars.arclamp = 'CONT'
#         contbars.name += f' arclamp={contbars.arclamp}'
#         contbars.name += f' calobj={contbars.calobj}'
#         return contbars
# 
# 
#     def domeflats(self, off=False):
#         '''
#         '''
#         domeflats = deepcopy(self)
#         domeflats.domeflatlamp = not off
#         domeflats.name += f' domeflatlamp={domeflats.domeflatlamp}'
#         return domeflats
# 
# 
#     def cals(self, internal=True, domeflats=True):
#         '''
#         '''
#         kcwib_0s_dark = KCWIblueDetectorConfig(exptime=0, dark=True)
#         kcwib_6s = KCWIblueDetectorConfig(exptime=6)
#         kcwib_30s = KCWIblueDetectorConfig(exptime=30)
#         kcwib_45s = KCWIblueDetectorConfig(exptime=45)
#         kcwib_100s = KCWIblueDetectorConfig(exptime=100)
# 
#         cals = ObservingBlockList()
#         if internal is True:
#             cals.append(ObservingBlock(target=None,
#                                        pattern=Stare(),
#                                        detconfig=kcwib_6s,
#                                        instconfig=self.contbars(),
#                                        repeat=1))
#             cals.append(ObservingBlock(target=None,
#                                        pattern=Stare(),
#                                        detconfig=kcwib_30s,
#                                        instconfig=self.arcs('FEAR'),
#                                        repeat=1))
#             cals.append(ObservingBlock(target=None,
#                                        pattern=Stare(),
#                                        detconfig=kcwib_45s,
#                                        instconfig=self.arcs('THAR'),
#                                        repeat=1))
#             cals.append(ObservingBlock(target=None,
#                                        pattern=Stare(),
#                                        detconfig=kcwib_6s,
#                                        instconfig=self.arcs('CONT'),
#                                        repeat=6))
#             cals.append(ObservingBlock(target=None,
#                                        pattern=Stare(),
#                                        detconfig=kcwib_0s_dark,
#                                        instconfig=self,
#                                        repeat=7))
#         if domeflats is True:
#             cals.append(ObservingBlock(target=DomeFlats(),
#                                        pattern=Stare(),
#                                        detconfig=kcwib_100s,
#                                        instconfig=self.domeflats(),
#                                        repeat=3))
#         return cals
# 
# 
#     def seq_cals(self, internal=True, domeflats=True):
#         '''
#         '''
#         kcwib_0s_dark = KCWIblueDetectorConfig(exptime=0, dark=True)
#         kcwib_6s = KCWIblueDetectorConfig(exptime=6)
#         kcwib_30s = KCWIblueDetectorConfig(exptime=30)
#         kcwib_45s = KCWIblueDetectorConfig(exptime=45)
#         kcwib_100s = KCWIblueDetectorConfig(exptime=100)
# 
#         cals = Sequence()
#         if internal is True:
#             cals.append(SequenceElement(pattern=Stare(),
#                                         detconfig=kcwib_6s,
#                                         instconfig=self.contbars(),
#                                         repeat=1))
#             cals.append(SequenceElement(pattern=Stare(),
#                                         detconfig=kcwib_30s,
#                                         instconfig=self.arcs('FEAR'),
#                                         repeat=1))
#             cals.append(SequenceElement(pattern=Stare(),
#                                         detconfig=kcwib_45s,
#                                         instconfig=self.arcs('THAR'),
#                                         repeat=1))
#             cals.append(SequenceElement(pattern=Stare(),
#                                         detconfig=kcwib_6s,
#                                         instconfig=self.arcs('CONT'),
#                                         repeat=6))
#             cals.append(SequenceElement(pattern=Stare(),
#                                         detconfig=kcwib_0s_dark,
#                                         instconfig=self,
#                                         repeat=7))
#         if domeflats is True:
#             cals.append(SequenceElement(pattern=Stare(),
#                                         detconfig=kcwib_100s,
#                                         instconfig=self.domeflats(),
#                                         repeat=3))
#         return cals
# 
# 
#     def __str__(self):
#         return f'{self.name}'
# 
# 
#     def __repr__(self):
#         return f'{self.name}'