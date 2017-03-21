#!/usr/bin/python2.7
# encoding: utf-8

from __future__ import division
import numpy as np
# import numpy.ma as ma
# from numpy.ma import MaskError
# import h5py
from pyseidon_dvt.utilities.miscellaneous import mattime_to_datetime

class _load_drifter:
    """
    **'Variables' subset in Tidegauge class**
    It contains the following numpy arrays: ::

                         _u = u velocity component (m/s), 1D array (ntime)
                        |_v = v velocity component (m/s), 1D array (ntime)
     Drifter.Variables._|_matlabTime = matlab time, 1D array (ntime)
                        |_lon = longitudes (deg.), 1D array (ntime)
                        |_lat = latitudes (deg.), 1D array (ntime)

    """
    def __init__(self,cls, History, debug=False):
        if debug:
            print 'Loading variables...'
        # Pointer to History
        setattr(self, '_History', History)

        # KC: some MATLAB files that contain multiple drifters
        # aggregated into one data structure have spaces between
        # distinct drifters, and when loaded into scipy produce nans...
        # can delete rows since array is small, but smarter to mask the array to
        # avoid slowness allocating new space and copying all the data etc...

        idx_nan = np.squeeze(np.argwhere(np.isnan(cls.Data['u'])))
        # cls.Data = {k: cls.Data[k] for k in cls.Data if not isnan(cls.Data[k])}
        ignore = ['__header__', '__globals__','__version__','trim', 'num_drifts']
        for var in cls.Data.keys():
            # ignore scalar variables from matlab import
            if var in ignore:
                continue
            # create mask for one variable - assumes
            if np.isnan(cls.Data[var]).any():
                idx_nan = np.unique(np.concatenate((idx_nan,
                        np.squeeze(np.argwhere(np.isnan(cls.Data[var]))))))
        # apply to other variables
        for var in cls.Data.keys():
            if var not in ignore:
                cls.Data[var] = np.delete(cls.Data[var], idx_nan)

        # KC: dealing with new drifter formats which have a new structure
        if 'velocity' in cls.Data.keys():
            self.matlabTime = cls.Data['velocity'].vel_time[:]
            #Sorting values with increasing time step
            sortedInd = self.matlabTime.argsort()
            self.matlabTime.sort()
            self.lat = cls.Data['velocity'].vel_lat[sortedInd]
            self.lon = cls.Data['velocity'].vel_lon[sortedInd]
            self.u = cls.Data['velocity'].u[sortedInd]
            self.v = cls.Data['velocity'].v[sortedInd]
        else:
            self.matlabTime = cls.Data['time']
            sortedInd = self.matlabTime.argsort()
            self.matlabTime.sort()
            self.lat = cls.Data['lat'][sortedInd]
            self.lon = cls.Data['lon'][sortedInd]
            self.u = cls.Data['u'][sortedInd]
            self.v = cls.Data['v'][sortedInd]

        #-Append message to History field
        start = mattime_to_datetime(self.matlabTime[0])
        end = mattime_to_datetime(self.matlabTime[-1])
        text = 'Temporal domain from ' + str(start) +\
                ' to ' + str(end)
        self._History.append(text)

        if debug: print '...Passed'

        return
