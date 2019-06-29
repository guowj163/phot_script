#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import shutil
import glob
from pyraf import iraf
from astropy.io import fits as pyfits



def delete_file(namelst):
    for name in namelst:
        if os.path.isfile(name):
            #print 'remove %s' % name
            os.remove(name)


def read_aper():
    """
    read measure apertures, aper1, aper2, aper3
    aper file name: 'aper.txt'
    format: aper1  aper2  aper3
    """
    aperlst = open('../aper.txt').readline().split()
    aperlst = [float(i) for i in aperlst]
    return tuple(aperlst)

        #孔径测光
def aperphot(imgs, posname, aper1, aper2, aper3,):
    postfix = '.obs'
    for i in xrange(len(imgs)):

        basename, exten = os.path.splitext(imgs[i])
        photname = basename + postfix

        meanpsf = 2.0
        std = 70.0

        iraf.display(imgs[i], frame=1)
        iraf.tvmark(frame=1, coords=posname, autolog='No', mark='circle',
                    radii=30, lengths=3, font='raster', color=204, label='No',
                    number='Yes', txsize=3)

        iraf.datapars.ccdread = 'CCDRON'
        iraf.datapars.gain = 'CCDGAIN'
        iraf.datapars.scale = 1.0
        iraf.datapars.fwhmpsf = meanpsf
        iraf.datapars.sigma = std
        iraf.datapars.filter = 'INSFLNAM'
        iraf.datapars.datamax = 1000000.0
        iraf.centerpars.cbox = 8.0
        iraf.centerpars.calgorithm = 'centroid'
        iraf.fitskypars.salgorithm = 'median'
        iraf.fitskypars.annulus = aper2    # ------ important ------
        iraf.fitskypars.dannulus = aper3   # ------ important ------
        #iraf.photpars.apertures = meanpsf  # ------ important ------
        iraf.photpars.apertures = aper1  # ------ important ------

        iraf.phot(image=imgs[i], coords=posname, output=photname,
                  interactive=False, verify=False)
    

def main():
        print '='*50
        print '<<<<<run the aperphot.py >>>>>'

        namelst = glob.glob("*.obs")
        delete_file(namelst)
        print '<<<<<clear all the previous .obs file>>>>>'  

        #读取参数 pos文件需提前写入
        fname = glob.glob('*.fits')
        posname=glob.glob("../*.pos")
        posname=posname[0]

        # --- readling list ---
        imgs = [i.strip() for i in fname ]
        aper1, aper2, aper3 = read_aper()
        iraf.daophot()
        aperphot(imgs, posname, aper1, aper2, aper3)

        print '<<<<< run aperphot.py successfully >>>>>'
        print '='*50

if __name__ == "__main__":
    main()