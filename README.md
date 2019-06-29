# alipy_install
alipy address is https://github.com/zzxihep/alipy
python setup.py install

alipy need the f2n
f2n address is https://github.com/zzxihep/f2n
python setup.py install

before run f2n ,you need to install sextractor and a link for sex to sextractor

sudo apt install sextractor
sudo ln `which sextractor` /usr/local/bin/sex

Also f2n need pyfits,you can change f2n.py 'import pyfits as pt'as 'from astropy.io import fits as pt' 
or 'pip install pyfits' in the terminal


