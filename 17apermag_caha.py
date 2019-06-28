#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
from math import log10
import numpy as np
import pyfits
import matplotlib.pyplot as plt
from termcolor import colored


def get_jd(fn):
    try:
        val = pyfits.getval(fn, 'JD')
        return val
    except KeyError:
        from pyraf import iraf
        iraf.hedit(images=fn, fields='OBSERVAT', value='ca', add='Yes',
                   addonly='Yes', delete='No', verify='No', show='Yes',
                   update='Yes')
        iraf.setjd(images=fn, observatory='ca', date='date-obs',
                   time='date-obs', exposure='exptime', ra='ra', dec='dec',
                   epoch='EQUINOX', utdate='Yes', uttime='Yes')
        val = pyfits.getval(fn, 'JD')
        return val


def read_mag(absMagFileName):
    """
    read the file generated by iraf command phot
    :param absMagFile:
    :return: flux(counts) lst, instrument magitude lst, ins mag err lst
    """
    print absMagFileName
    f = [i.strip() for i in open(absMagFileName).readlines()]
    f = [i for i in f if i[0] != '#']
    f = [i.split() for i in f]
    fluxlst, maglst, magerrlst = [], [], []
    for i in range(4, len(f), 5):
        try:
            magerrlst.append(float(f[i][-3]))
            maglst.append(float(f[i][-4]))
            fluxlst.append(float(f[i][-5]))
        except ValueError, argument:
            print(colored('string to float error' + str(argument), 'red'))
            import datetime
            time = str(datetime.datetime.now())
            fil = open('error.log', 'a')
            fil.write('string to float error: ')
            fil.write(absMagFileName)
            fil.write('  '+time+'\n')
            fil.close()
            fil = open('/media/g/guowj/object/error.log', 'a')
            fil.write('string to float error: ')
            fil.write(absMagFileName+'\n')
            abspath = os.getcwd()
            fil.write(abspath)
            fil.write('  '+time+'\n')
            fil.close()
            raise argument
    maglst = np.array(maglst)
    magerrlst = np.array(magerrlst)
    return fluxlst, maglst, magerrlst


def calmeanstd(mag, err):
    meanmag = sum(mag) / float(len(mag))
    sigma = 0.0
    if len(mag) > 1:
        num = float(len(mag))
        for i in xrange(len(mag)):
            #sigma += 1.0 / (num - 1.0) * (mag[i] - meanmag)**2
            sigma += 1.0 / (num) * (mag[i] - meanmag)**2
        sigma = sigma**0.5
    else:
        sigma = err[0]
    err_mean = 0.0
    for i in xrange(len(err)):
        err_mean += err[i]**2
    err_mean = err_mean**0.5 / float(len(err))
    return meanmag, sigma, err_mean


def summagerr(mag, err):
    def geterr(mag, err):
        sumflux = np.sum(10**(-0.4*mag))
        merr = np.sum((10**(-0.4*mag) / sumflux * err)**2)**0.5
        return merr
    C = 0.0
    mag = np.array(mag)
    err = np.array(err)
    flux = 10**((C-mag)/2.5)
    sumflux = np.sum(flux)
    summag = -2.5 * log10(sumflux) + C
    sumerr = geterr(mag, err)
    return summag, sumerr


def diffmag(fn):
    """
    fn is mag file created by iraf command phot.
    return diff mag, err of every star in fn
    """
    fluxlst, maglst, errlst = read_mag(fn)
    print '*-'*15
    # mmag, tmpsigma, merr = calmeanstd(maglst[:-2], errlst[:-2])
    mmag, merr = summagerr(maglst[:-2], errlst[:-2])
    difmaglst = maglst - mmag
    diferrlst = (errlst**2+merr**2)**0.5
    # diferrlst = (errlst**2+tmpsigma**2)**0.5
    return difmaglst, diferrlst


def diffmag2(fn1, fn2=None):
    """
    fn1 and fn2 are mag files created by iraf command phot.
    fn1 is used as the comparison star measure result
    fn2 is used as the object star measure result
    return diff mag, err of every star in fn
    if fn2 is None, return the result of function diffmag
    """
    if fn2 is None:
        return diffmag(fn1)
    print fn2
    fluxlst, maglst, errlst = read_mag(fn1)
    # print 'flag-='
    fluxlst2, maglst2, errlst2 = read_mag(fn2)
    fluxlst[-2] = fluxlst2[-2]
    maglst[-2] = maglst2[-2]
    errlst[-2] = errlst2[-2]
    mmag, tmpsigma, merr = calmeanstd(maglst[:-2], errlst[:-2])
    difmaglst = maglst - mmag
    diferrlst = (errlst**2+merr**2)**0.5
    return difmaglst, diferrlst


def getlightcurve(namelst):
    """
    namelst is mag file name lst created by iraf command phot
    return every star light curve
    return: jdlst, maglst, magerrlst
    """
    jdlst = np.array([get_jd(name) for name in namelst])
    arg = np.argsort(jdlst)
    jdlst = jdlst[arg]
    maglst, magerrlst = [], []
    for name in namelst:
        magname = name.replace('.fits', '.obs')
        magname2 = magname + '2'
        if not os.path.isfile(magname2):
            magname2 = None
            # print 'flag=' * 10
        mag, err = diffmag2(magname, magname2)
        # mag, err = diffmag(magname)
        maglst.append(mag)
        magerrlst.append(err)
    maglst = np.array(maglst)[arg].transpose()
    magerrlst = np.array(magerrlst)[arg].transpose()
    namelst2 = np.array(namelst)
    namelst2 = namelst2[arg]
    for name in namelst2:
        print name
    return jdlst, maglst, magerrlst


def combine_days(jdLst, magLst, magErrLst):
    nJdLst, nMagLst, nMagErrLst = [], [], []
    tmpJd, tmpMag, tmpErr = [], [], []
    for i in range(len(jdLst)):
        if len(tmpJd) == 0 or jdLst[i]-tmpJd[-1] < 0.3:
            tmpJd.append(jdLst[i])
            tmpMag.append(magLst[i])
            tmpErr.append(magErrLst[i])
        if jdLst[i]-tmpJd[-1] >= 0.3 or i == len(jdLst)-1:
            meanJd = np.mean(tmpJd)
            meanMag, sigma, meanErr = calmeanstd(tmpMag, tmpErr)
            newErr = (sigma**2+meanErr**2)**0.5
            nJdLst.append((meanJd))
            nMagLst.append(meanMag)
            nMagErrLst.append(newErr)
            tmpJd, tmpMag, tmpErr = [jdLst[i]], [magLst[i]], [magErrLst[i]]
    return np.array(nJdLst), np.array(nMagLst), np.array(nMagErrLst)


def write_to_file(fn, jdlst, maglst, errlst):
    fil = open(fn, 'w')
    for i, jd in enumerate(jdlst):
        text = '%.4f  %.6e  %.6e' % (jd, maglst[i], errlst[i])
        fil.write(text+'\n')
    fil.close()


def plot(jdLst, cmpLst, cmpErrLst, objLst, objErrLst, cJdLst, cObjLst,
         cObjErrLst):
    figCmp = plt.figure(figsize=(12, 6))
    figCmp.suptitle('cmp star')
    num = int(len(cmpLst)**0.5)+1
    for i in range(1, len(cmpLst)+1):
        ax = figCmp.add_subplot(num, num, i)
        ax.errorbar(jdLst, cmpLst[i-1], yerr=cmpErrLst[i-1], fmt='or',
                    linewidth=1)
        fn = 'lightcurve%d.day' % i
        write_to_file(fn, jdLst, cmpLst[i-1], cmpErrLst[i-1])
        ax.invert_yaxis()
        diffmean = np.mean(cmpLst[i-1])
        diffstd = np.std(cmpLst[i-1])
        ax.axhline(diffmean, linestyle='--')
        ax.axhline(diffmean + diffstd, linestyle=':')
        ax.axhline(diffmean - diffstd, linestyle=':')
        ax.text(0.1, 0.9, '%5.3f' % (diffstd), horizontalalignment='left',
                verticalalignment='center', transform=ax.transAxes, size=10)
    picname1 = sys.argv[1].split('.')[0]+'_cmp.png'
    pdfpicname1 = sys.argv[1].split('.')[0]+'_cmp.pdf'
    print 'save fig %s' % picname1
    figCmp.savefig(picname1)
    figCmp.savefig(pdfpicname1)
    picname = sys.argv[1].split('.')[0]+'_obj.png'
    pdfpicname = sys.argv[1].split('.')[0]+'_obj.pdf'
    figObj = plt.figure(figsize=(10, 8))
    for i in range(len(objLst)):
    # for i in [0]:
        numb = 411+2*i
        # numb = 211
        ax1 = figObj.add_subplot(numb)
        ax1.errorbar(jdLst, objLst[i], yerr=objErrLst[i], fmt='o', color='red',
                     linewidth=1)
        diffmean = np.mean(objLst[i])
        diffstd = np.std(objLst[i])
        ax1.invert_yaxis()
        ax1.axhline(diffmean, linestyle='--')
        ax1.axhline(diffmean + diffstd, linestyle=':')
        ax1.axhline(diffmean - diffstd, linestyle=':')
        ax1.text(0.1, 0.9, '%5.3f' % (diffstd), horizontalalignment='left',
                 verticalalignment='center', transform=ax1.transAxes, size=10)
        numb = 412+2*i
        ax2 = figObj.add_subplot(numb)
        ax2.errorbar(cJdLst, cObjLst[i], yerr=cObjErrLst[i], fmt='o',
                     color='blue', linewidth=1)
        ax2.invert_yaxis()
        diffmean = np.mean(cObjLst[i])
        diffstd = np.std(cObjLst[i])
        ax2.axhline(diffmean, linestyle='--')
        ax2.axhline(diffmean + diffstd, linestyle=':')
        ax2.axhline(diffmean - diffstd, linestyle=':')
        ax2.text(0.1, 0.9, '%5.3f' % (diffstd), horizontalalignment='left',
                 verticalalignment='center', transform=ax2.transAxes, size=10)
    print 'save fig %s' % picname
    figObj.savefig(picname)
    figObj.savefig(pdfpicname)
    plt.show()


def main():
    if len(sys.argv) >= 4:
        if sys.argv[3] == '0':
            plt.ion()
    lstname = sys.argv[1]
    namelst = [i.strip() for i in file(lstname) if i.strip()[0] != '#']
    namelst = [i.split()[0].strip() for i in namelst]
    jdlst, maglst, magerrlst = getlightcurve(namelst)
    cmplst = maglst[:-2]
    cmperrlst = magerrlst[:-2]
    objlst = maglst[-2:]
    objerrlst = magerrlst[-2:]
    cmaglstlst = []
    cerrlstlst = []
    for i in range(len(objlst)):
        cjdlst, cmaglst, cerrlst = combine_days(jdlst, objlst[i], magerrlst[i])
        cmaglstlst.append(cmaglst)
        cerrlstlst.append(cerrlst)
    outname = lstname.split('.')[0]+'_lightcurve.day'
    print 'write to file %s' % outname
    fil = open(outname, 'w')
    tmpcmag = np.array(cmaglstlst).transpose()
    tmpcerr = np.array(cerrlstlst).transpose()
    for i, jd in enumerate(cjdlst):
        text = '%f  ' % jd
        print text
        for j, mag in enumerate(tmpcmag[i]):
            text += '%f  %f  ' % (mag, tmpcerr[i][j])
            print text
        text = text.strip()
        fil.write(text+'\n')
    fil.close()
    plot(jdlst, cmplst, cmperrlst, objlst, objerrlst, cjdlst, cmaglstlst,
         cerrlstlst)


if __name__ == '__main__':
    main()
